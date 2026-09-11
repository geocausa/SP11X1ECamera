#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,os,re,subprocess,tempfile

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
A=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fu/attempt1-pass-eighteen-frame-20260911T1822')
FU=BASE/'fu-eighteen-frame-live-r5-r18'
FY=BASE/'fy-calibrated-awb-selector-replay'/'RESULT.json'
FW=BASE/'fw-windows-r4-r21-combined-awb-lsc-oracle'/'RESULT.json'
GTM_SHA='074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa'
ARCHIVE_MANIFEST_SHA='a02b7b0916c1a5b56e2ce2d0555ff1ccd2904193bf63d7edf9448a54868a6d9b'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def need(v,m):
    if not v:
        raise AssertionError(m)

def run(c,**kw):
    return subprocess.run(c,check=True,text=True,**kw)

need(A.is_dir(),'FU archive absent')
need(sha(A/'MANIFEST.sha256')==ARCHIVE_MANIFEST_SHA,'FU archive manifest drift')

fu=json.loads((FU/'ATTEMPT1-PASS.json').read_text())
need(fu['status']=='PASS_CAPTURE_FU_EIGHTEEN_FRAME_R5_R18','FU authority')
need(fu['stream_attempts']==1 and fu['same_boot_stream_retry_performed'] is False,'FU retry invariant')
need(fu['golden_return'] is True and fu['candidate_retired'] is True,'FU closure invariant')

fy=json.loads(FY.read_text())
need(fy['status']=='PASS_FX_SELECTOR_OBJECT_AND_EG_FA_FH_FW_BIT_EXACT','FY AWB selector authority')
need(fy['windows_replays']['FW']['requests']==list(range(4,22)),'FY FW R4-R21 coverage')
need(fy['windows_replays']['FW']['bit_exact']=='18/18','FY FW AWB replay authority')

fw=json.loads(FW.read_text())
need(fw['status']=='PASS_WINDOWS_COMBINED_R4_R21_AWB_LSC','FW combined authority')
need(fw['requests']==list(range(4,22)) and fw['windows_stream_count']==1,'FW R4-R21 one-stream coverage')
need(fw['same_stream_awb_and_lsc'] is True and fw['combined_r21_completion'] is True,'FW same-stream R21 closure')
need(fw['awb_result']['bit_exact']=='18/18','FW AWB authority')
need(fw['lsc_result']['clean_lsc_replay']=='18/18 byte-exact LSC0/LSC1/LSC2/GIC','FW LSC authority')

src=(HERE/'offline-iq-probe.py').read_text()
need("choices=('offline',)" in src,'probe must be CLI-offline-only')
need('for gen in (1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18):' in src,'G1..G18 probe loop')
need('elif gen in (4,5,6,7,8,9,10,11,12,13,14,15,16,17,18):' in src,'R7..R21 extended branch')

g={}
run_text=(A/'runtime-output/RUN.txt').read_text()
for m in re.finditer(r'DZ_AEC_ACCEPT G=(\d+) REQUEST=(\d+).*?ISP=0x([0-9a-fA-F]{8})',run_text):
    gen,req,b=m.groups()
    gen=int(gen); req=int(req)
    if gen<=18:
        need(req==gen+3,f'gain identity G{gen}')
        g[str(gen)]=f'0x{b.lower()}'
need(set(g)=={str(i) for i in range(1,19)},'FU G1..G18 gain coverage')

with tempfile.TemporaryDirectory(prefix='e003i-fv-snapshot-') as ts:
    snap=Path(ts)/'snapshot'
    snap.mkdir()
    for gen in range(1,19):
        for prefix in ('STATS3A','TLBG'):
            srcp=A/'runtime-output'/f'{prefix}-{gen-1}.bin'
            dst=snap/srcp.name
            with dst.open('wb') as f:
                subprocess.run(['sudo','-n','cat',str(srcp)],check=True,stdout=f)
            need(dst.stat().st_size==srcp.stat().st_size,f'{prefix} G{gen} materialize size')

    def one(td:Path):
        out=td/'out'; out.mkdir()
        gm=td/'gain.json'; mf=td/'manifest.json'
        gm.write_text(json.dumps({'cq_gain_bits':g})+'\n')
        cp=subprocess.run([
            str(HERE/'offline-iq-probe.py'),'--mode','offline',
            '--snapshot-dir',str(snap),
            '--gain-manifest',str(gm),
            '--output-dir',str(out),
            '--manifest',str(mf),
        ],text=True,capture_output=True)
        if cp.returncode:
            print(cp.stdout); print(cp.stderr)
            raise SystemExit(cp.returncode)
        need('E003I_FV_OFFLINE_PROBE=PASS' in cp.stdout,'FV pass marker')
        m=json.loads(mf.read_text())
        need(m['schema']=='sp11-e003i-fv-r5-r21-offline-probe-v1' and m['status']=='PASS','FV manifest')
        need([(r['generation'],r['request_target']) for r in m['rows']]==
             [(1,None)]+[(x,x+3) for x in range(2,19)],'G1..G18 mapping')
        return out,m

    with tempfile.TemporaryDirectory(prefix='e003i-fv-a-') as ta, tempfile.TemporaryDirectory(prefix='e003i-fv-b-') as tb:
        oa,ma=one(Path(ta)); ob,mb=one(Path(tb))

        live_reg={}
        for req in range(5,19):
            got=sha(oa/f'R{req}-dynamic.bin')
            exp=sha(A/'runtime-output/producer'/f'R{req}-dynamic.bin')
            need(got==exp,f'R{req} FU live regression')
            need(got==sha(ob/f'R{req}-dynamic.bin'),f'R{req} two-run determinism')
            live_reg[str(req)]=got

        new_hash={}
        for req in range(19,22):
            pa=oa/f'R{req}-dynamic.bin'; pb=ob/f'R{req}-dynamic.bin'
            need(pa.is_file() and pa.stat().st_size==41088,f'R{req} capsule shape')
            h=sha(pa)
            need(h==sha(pb),f'R{req} two-run determinism')
            new_hash[str(req)]=h

        ra={r['request_target']:r for r in ma['rows'] if r['request_target']}
        rb={r['request_target']:r for r in mb['rows'] if r['request_target']}
        for req in range(5,22):
            for k in ('generation','request_target','final_xy_bits','final_cct_bits',
                      'published_cct','awb_calibration_slot','awb_calibration_region',
                      'awb_triangle','awb_published_gain_bits','capsule_sha256'):
                need(ra[req][k]==rb[req][k],f'R{req} deterministic {k}')
            need(ra[req]['demux_bls']==rb[req]['demux_bls'],f'R{req} deterministic IQ meta')
            la={k:v for k,v in ra[req]['lsc'].items() if not k.endswith('_ms')}
            lb={k:v for k,v in rb[req]['lsc'].items() if not k.endswith('_ms')}
            need(la==lb,f'R{req} deterministic LSC state')

        for req in range(19,22):
            row=ra[req]
            need(row['demux_bls']['gtm_sha256']==GTM_SHA,f'R{req} GTM stable law')
            need(row['lsc']['aec_selector_mode']=='lower_aec',f'R{req} AEC LSC selector')
            need(row['lsc']['cct_selector_mode']=='leaf_0x4bd',f'R{req} CCT LSC selector')

        seq=[ra[r] for r in (18,19,20,21)]
        awb_regs=[json.dumps(r['demux_bls']['awb_regs'],sort_keys=True) for r in seq]
        tint=[r['lsc']['tintless_output_sha256'] for r in seq]
        lsc0=[r['lsc']['lsc0_sha256'] for r in seq]
        lsc1=[r['lsc']['lsc1_sha256'] for r in seq]
        gic=[r['lsc']['gic_sha256'] for r in seq]

        rows={}
        for req in range(18,22):
            row=ra[req]
            rows[str(req)]={
                'generation':row['generation'],
                'capsule_sha256':sha(oa/f'R{req}-dynamic.bin'),
                'awb_calibration_slot':row['awb_calibration_slot'],
                'awb_calibration_region':row['awb_calibration_region'],
                'awb_triangle':row['awb_triangle'],
                'awb_regs':row['demux_bls']['awb_regs'],
                'published_cct':row['published_cct'],
                'gtm_sha256':row['demux_bls']['gtm_sha256'],
                'lsc':{k:row['lsc'][k] for k in (
                    'aec_selector_mode','cct_selector_mode','x22_sha256',
                    'pretintless_sha256','tintless_output_sha256',
                    'lsc0_sha256','lsc1_sha256','lsc2_sha256','gic_sha256')},
            }

        result={
            'schema':'sp11-e003i-fv-r19-r21-continuation-authority-v1',
            'status':'PASS_OFFLINE_R19_R21_COMPOSABLE_AUTHORITY_CLOSED',
            'source':'immutable FU attempt1 archive G1..G18 stats + AEC gain observations',
            'fu_archive_manifest_sha256':ARCHIVE_MANIFEST_SHA,
            'r5_r18_live_regression':'14/14 exact FU live capsule hashes',
            'r19_r21_deterministic':'3/3 two-run capsule hashes exact',
            'r19_r21_capsule_sha256':new_hash,
            'gtm_post_r6_stable_through_probe':True,
            'awb_windows_authority_through_request':21,
            'awb_windows_authority_source':'FY calibrated selector + FW Windows R4-R21 18/18 bit-exact',
            'lsc_windows_authority_through_request':21,
            'lsc_windows_authority_source':'FW Windows R4-R21 clean-room 18/18 byte-exact',
            'r19_r21_awb_windows_differential':True,
            'r19_r21_lsc_windows_differential':True,
            'awb_evolving_r18_r21':len(set(awb_regs))>1,
            'tintless_evolving_r18_r21':len(set(tint))>1,
            'lsc_gic_evolving_r18_r21':len(set(lsc0))>1 or len(set(lsc1))>1 or len(set(gic))>1,
            'linux_live_r19_plus_allowed':True,
            'linux_live_scope':'bounded fresh R5-R21 successor only; one stream; no continuous/unrestricted AEC claim',
            'camera_runtime_performed':False,
            'continuous_aec_claimed':False,
            'rows_r18_r21':rows,
        }
        (HERE/'RESULT.json').write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
        print(json.dumps(result,indent=2,sort_keys=True))
