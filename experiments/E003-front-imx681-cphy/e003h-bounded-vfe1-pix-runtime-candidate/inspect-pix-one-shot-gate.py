#!/usr/bin/env python3
import argparse, hashlib, json, shutil, subprocess, tempfile
from pathlib import Path

BASE_CAMSS_SHA='2a94daa17493af214335e541853ff733251410f0b0d6fe3e8ba9ab6aed90a237'
CAPSULE_SHA='6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20'
CAPSULE_BYTES=41088

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(s,*xs):
    for x in xs:
        if x not in s: die('missing source contract: '+x[:100])

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--video',type=Path,required=True)
    ap.add_argument('--object',type=Path,required=True)
    ap.add_argument('--module',type=Path,required=True)
    ap.add_argument('--patch',type=Path,required=True)
    ap.add_argument('--base-source',type=Path,required=True)
    ap.add_argument('--capsule',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()
    s=a.source.read_text(); v=a.video.read_text()
    if sha(a.base_source)!=BASE_CAMSS_SHA: die('0033 base source drift')
    if len(a.capsule.read_bytes())!=CAPSULE_BYTES or sha(a.capsule)!=CAPSULE_SHA: die('capsule identity drift')
    need(s,
      '#define CAMSS_X1E_PIX_GATE_CAPSULE_BYTES\t41088',
      '#define CAMSS_X1E_PIX_GATE_QC10C_BYTES\t\t0x0076b000',
      '#define CAMSS_X1E_PIX_GATE_VFE1_BASE\t\t0x0ac71000',
      '#define CAMSS_X1E_PIX_GATE_VFE1_BYTES\t\t0x0000f000',
      '#define CAMSS_X1E_PIX_GATE_RTCDM1_BASE\t\t0x0ac26000',
      'static atomic_t camss_x1e_pix_gate_once = ATOMIC_INIT(0);',
      'vb->state != VB2_BUF_STATE_DEQUEUED',
      'video->vb2_q.streaming || video->vb2_q.start_streaming_called',
      'atomic_read(&video->vb2_q.owned_by_drv_count)',
      'fmt->pixelformat != V4L2_PIX_FMT_QC10C',
      'fmt->width != CAMSS_X1E_PIX_GATE_QC10C_WIDTH',
      'fmt->plane_fmt[0].sizeimage != CAMSS_X1E_PIX_GATE_QC10C_BYTES',
      'vfe1 = platform_get_resource_byname(pdev, IORESOURCE_MEM, "vfe1")',
      'rtcdm1 = platform_get_resource_byname(pdev, IORESOURCE_MEM, "rt_cdm1")',
      'media_pad_remote_pad_first(&camss->csiphy[1].pads[MSM_CSIPHY_PAD_SINK])',
      'if (atomic_cmpxchg(&camss_x1e_pix_gate_once, 0, 1))',
      'return camss_x1e_pix_runner_once(camss, &req->runner, result);',
      'camss_x1e_pix_gate_recipe __used = {',
      '.run_once = camss_x1e_pix_gate_run_once,')
    if 'camss_x1e_pix_gate' in v: die('gate referenced by camss-video')
    if 'EXPORT_SYMBOL' in '\n'.join(x for x in s.splitlines() if 'camss_x1e_pix_gate' in x): die('gate exported')

    nm=subprocess.check_output(['nm','-an',str(a.object)],text=True)
    for sym in ('camss_x1e_pix_gate_once','camss_x1e_pix_gate_recipe','camss_x1e_pix_gate_run_once','camss_x1e_pix_runner_once'):
        if sym not in nm: die('missing object symbol '+sym)
    rel=subprocess.check_output(['objdump','-r',str(a.object)],text=True)
    gate_reloc=[x for x in rel.splitlines() if 'camss_x1e_pix_gate_run_once' in x]
    if len(gate_reloc)!=1 or 'R_AARCH64_ABS64' not in gate_reloc[0]: die('gate retention relocation drift')
    recipe_refs=[x for x in rel.splitlines() if 'camss_x1e_pix_gate_recipe' in x]
    if recipe_refs: die('gate recipe has runtime reference')

    with tempfile.TemporaryDirectory() as td:
        td=Path(td); tree=td/'tree'; (tree/'drivers/media/platform/qcom/camss').mkdir(parents=True)
        shutil.copy2(a.base_source,tree/'drivers/media/platform/qcom/camss/camss.c')
        subprocess.run(['patch','-p1','-i',str(a.patch.resolve())],cwd=tree,check=True,stdout=subprocess.DEVNULL)
        fwd=tree/'drivers/media/platform/qcom/camss/camss.c'
        if sha(fwd)!=sha(a.source): die('forward reconstruction mismatch')
        subprocess.run(['patch','-R','-p1','-i',str(a.patch.resolve())],cwd=tree,check=True,stdout=subprocess.DEVNULL)
        if sha(fwd)!=BASE_CAMSS_SHA: die('reverse reconstruction mismatch')

    out={
      'accepted':True,
      'schema':'sp11-e003h-pix-one-shot-runtime-gate-unarmed-v1',
      'base_0033_source_sha256':BASE_CAMSS_SHA,
      'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),
      'patch_sha256':sha(a.patch),'capsule_sha256':CAPSULE_SHA,'capsule_bytes':CAPSULE_BYTES,
      'one_shot_latch':'atomic cmpxchg 0->1 before validation; never reset until module reload/reboot',
      'buffer_contract':'two distinct DEQUEUED non-streaming VFE1 PIX QC10C vb2 buffers, 2560x1440 stride3584 size0x76b000, page-aligned 32-bit non-overlapping DMA',
      'resource_contract':'VFE1 0x0ac71000/0xf000 and RT-CDM1 0x0ac26000/0x1000, mapped/present',
      'front_only_contract':'CSIPHY1 sink has no remote rear sensor link; exact front links are revalidated by 0033 runner',
      'capsule_digest_semantics':'caller-reported SHA-256 must equal separately verified local capsule digest; kernel gate does not implement cryptographic hashing',
      'gate_recipe_relocations':1,'gate_recipe_runtime_references':0,
      'generic_vb2_auto_start_reference':False,'runtime_reachable':False,
      'runtime_authorized':False,
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: one-shot PIX caller/preflight gate is exact, reconstructable and unreferenced')
if __name__=='__main__': main()
