#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(cond, msg):
    if not cond:
        raise SystemExit(msg)


def main():
    ap=argparse.ArgumentParser(description='Fail-closed E003i-Q generation-tagged TL_BG static inspector')
    ap.add_argument('--source-root', type=Path, default=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/e003i-front-production-src'))
    ap.add_argument('--module', type=Path)
    ap.add_argument('--output', type=Path)
    args=ap.parse_args()
    here=Path(__file__).resolve().parent
    manifest=json.loads((here/'BUILD-MANIFEST.json').read_text())
    patch=here/'0011-media-qcom-camss-expose-generation-tagged-tlbg.patch'
    require(sha(patch)==manifest['patch_sha256'], 'patch SHA mismatch')
    require(sha(here/'BUILD.log')==manifest['build_log_sha256'], 'build log SHA mismatch')
    require(sha(here/'CHECKPATCH.log')==manifest['checkpatch_log_sha256'], 'checkpatch log SHA mismatch')
    check=(here/'CHECKPATCH.log').read_text()
    require('0 errors, 0 warnings, 0 checks' in check, 'checkpatch not clean')

    texts={}
    for rel, hashes in manifest['source_files'].items():
        p=args.source_root/rel
        require(p.is_file(), f'missing source {p}')
        require(sha(p)==hashes['new'], f'new source SHA mismatch: {rel}')
        texts[rel]=p.read_text()

    vh=texts['drivers/media/platform/qcom/camss/camss-video.h']
    vc=texts['drivers/media/platform/qcom/camss/camss-video.c']
    vfe=texts['drivers/media/platform/qcom/camss/camss-vfe-680.c']
    camss=texts['drivers/media/platform/qcom/camss/camss.c']

    require('#define CAMSS_X1E_TLBG_RAW_BYTES\t\t0x00025800' in vh, 'raw byte contract missing')
    require('#define CAMSS_X1E_TLBG_SNAPSHOT_HEADER_BYTES\t32' in vh, 'header byte contract missing')
    require('static_assert(sizeof(struct camss_x1e_tlbg_snapshot_header) ==' in vc, 'header ABI static_assert missing')
    require('V4L2_CID_QCOM_CAMSS_X1E_TLBG_SNAPSHOT' in vc, 'TL_BG V4L2 control missing')
    require('.type = V4L2_CTRL_TYPE_U8' in vc, 'TL_BG control is not U8 compound')
    require('.flags = V4L2_CTRL_FLAG_READ_ONLY | V4L2_CTRL_FLAG_VOLATILE' in vc, 'TL_BG control not read-only volatile')
    require('.g_volatile_ctrl = video_x1e_tlbg_g_volatile_ctrl' in vc, 'volatile getter missing')
    require('header.generation = cpu_to_le64(video->x1e_tlbg_generation);' in vc, 'snapshot generation missing')
    require('header.source_seq = cpu_to_le32(video->x1e_tlbg_source_seq);' in vc, 'source completion sequence missing')
    require('raw_size != CAMSS_X1E_TLBG_RAW_BYTES' in vc, 'publish exact-size gate missing')

    require('slot->pending_mask & VFE680_X1E_DONE_TINTLESS_BG' in vfe, 'TL_BG ownership-pending gate missing')
    require('*size = CAMSS_X1E_TLBG_RAW_BYTES;' in vfe, 'TL_BG accessor exact-size return missing')

    expected=[(1,0),(2,1),(3,0),(4,1),(5,0),(6,1)]
    observed=[]
    for k,slot in expected:
        gate=f'csid680_x1e_front_poll_all_done(csid, video_seq + {k},'
        pub=f'camss_x1e_pix_publish_tlbg(req->live_video, pix, {slot}, video_seq + {k});'
        retire=f'vfe680_x1e_pix_runtime_retire_aux(pix, {slot});'
        gp=camss.find(gate)
        pp=camss.find(pub, gp)
        rp=camss.find(retire, pp)
        nextg=camss.find('csid680_x1e_front_poll_all_done(', gp+len(gate))
        require(gp>=0 and pp>gp and rp>pp, f'completion/publish/retire ordering missing for generation {k}')
        require(nextg<0 or rp<nextg, f'retire crossed next completion gate for generation {k}')
        observed.append({'source_seq_delta':k,'slot':slot})
    require(camss.count('camss_x1e_pix_publish_tlbg(req->live_video')==6, 'unexpected publication call count')

    # Reconstruct the exact pre-Q source by reversing this patch from the
    # current source, then reapply it and require byte-identical new hashes.
    with tempfile.TemporaryDirectory(prefix='e003i-q-roundtrip-') as td:
        td=Path(td)
        for rel in manifest['source_files']:
            dst=td/rel
            dst.parent.mkdir(parents=True,exist_ok=True)
            shutil.copy2(args.source_root/rel,dst)
        subprocess.run(['patch','-R','-p1','--batch','-i',str(patch)],cwd=td,check=True,
                       stdout=subprocess.DEVNULL)
        for rel, hashes in manifest['source_files'].items():
            require(sha(td/rel)==hashes['base'], f'reverse patch base SHA mismatch: {rel}')
        subprocess.run(['patch','-p1','--batch','-i',str(patch)],cwd=td,check=True,
                       stdout=subprocess.DEVNULL)
        for rel, hashes in manifest['source_files'].items():
            require(sha(td/rel)==hashes['new'], f'forward patch new SHA mismatch: {rel}')

    added=[]
    for line in patch.read_text().splitlines():
        if line.startswith('+') and not line.startswith('+++'):
            added.append(line[1:])
    mmio_reads=[x for x in added if re.search(r'\breadl(?:_relaxed)?\s*\(',x)]
    mmio_writes=[x for x in added if re.search(r'\bwritel(?:_relaxed)?\s*\(',x)]
    require(not mmio_reads, f'new MMIO reads found: {mmio_reads}')
    require(not mmio_writes, f'new MMIO writes found: {mmio_writes}')

    module_result=None
    if args.module:
        require(args.module.is_file(), f'module missing: {args.module}')
        require(sha(args.module)==manifest['module']['sha256'], 'module SHA mismatch')
        vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(args.module)],text=True).strip()
        srcversion=subprocess.check_output(['modinfo','-F','srcversion',str(args.module)],text=True).strip()
        require(vermagic==manifest['module']['vermagic'], f'vermagic mismatch: {vermagic}')
        require(srcversion==manifest['module']['srcversion'], f'srcversion mismatch: {srcversion}')
        module_result={'sha256':sha(args.module),'vermagic':vermagic,'srcversion':srcversion}

    result={
      'schema':1,'status':'PASS','patch_sha256':sha(patch),
      'source_hashes':{rel:sha(args.source_root/rel) for rel in manifest['source_files']},
      'raw_tlbg_bytes':manifest['raw_tlbg_bytes'],'snapshot_header_bytes':manifest['snapshot_header_bytes'],
      'snapshot_total_bytes':manifest['snapshot_total_bytes'],'publication_sequence':observed,
      'new_direct_mmio_reads':len(mmio_reads),'new_direct_mmio_writes':len(mmio_writes),
      'latest_generation_semantics':True,'request_delay_authority':False,
      'patch_roundtrip':'PASS','inspector_sha256':sha(Path(__file__).resolve()),'module':module_result
    }
    text=json.dumps(result,indent=2,sort_keys=True)+'\n'
    if args.output: args.output.write_text(text)
    else: print(text,end='')

if __name__=='__main__': main()
