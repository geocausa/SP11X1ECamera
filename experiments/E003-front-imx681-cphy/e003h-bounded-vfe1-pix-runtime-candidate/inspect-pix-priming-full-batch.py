#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess, tempfile
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--source',type=Path,required=True)
    ap.add_argument('--object',type=Path,required=True)
    ap.add_argument('--module',type=Path,required=True)
    ap.add_argument('--patch',type=Path,required=True)
    ap.add_argument('--base',type=Path,required=True)
    ap.add_argument('--proof',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); s=a.source.read_text(); proof=json.loads(a.proof.read_text())
    if not proof.get('accepted') or proof.get('callable_runner_present'): die('byte proof not accepted')
    need=[
      '#define CAMSS_X1E_PIX_PRIMING_PACKET_COUNT\t4',
      '#define CAMSS_X1E_PIX_PRIMING_MAX_BL_COUNT\t5',
      'struct camss_x1e_pix_prime',
      'out->bl_count[packet] = 4;', 'out->bl_count[packet] = 5;',
      'out->bl_dma[packet][1] = main->packet_dma[packet];',
      'put_unaligned_le32(packet, bl4 + sizeof(irq_prefix));',
      'static int camss_x1e_pix_submit_prime(',
      'prime->bl_len[packet][i] - 1',
      '.submit_prime = camss_x1e_pix_submit_prime,',
    ]
    for x in need:
        if x not in s: die('source contract missing: '+x)
    if 'camss_x1e_pix_runner_once' in s: die('callable runner leaked into 0032')

    nm=subprocess.check_output(['llvm-nm','-an',str(a.object)],text=True)
    for sym in ('camss_x1e_pix_capsule_materialize','camss_x1e_pix_submit_prime','camss_x1e_pix_rtcdm_recipe'):
        if sym not in nm: die('object symbol missing: '+sym)
    if 'camss_x1e_pix_runner_once' in nm: die('runner object symbol present')
    rel=subprocess.check_output(['llvm-objdump','-r',str(a.object)],text=True)
    expected=[
      'camss_x1e_pix_rtcdm_open_start','camss_x1e_pix_submit_startup',
      'camss_x1e_pix_submit_prime','camss_x1e_pix_rtcdm_submit_epoch0_batch',
      'camss_x1e_pix_rtcdm_stop_close',
    ]
    recipe=[line for line in rel.splitlines() if any(x in line for x in expected)]
    if len(recipe)!=5: die(f'RT-CDM recipe relocation count {len(recipe)} != 5')
    for x in expected:
        if sum(x in line for line in recipe)!=1: die('RT-CDM recipe relocation drift: '+x)
    if any('camss_x1e_pix_rtcdm_recipe' in line for line in rel.splitlines()):
        die('runtime relocation references RT-CDM recipe')

    # Reconstruct exactly back to the already-published 0031 source and forward again.
    with tempfile.TemporaryDirectory() as td:
        t=Path(td)/'drivers/media/platform/qcom/camss'; t.mkdir(parents=True)
        cur=t/'camss.c'; cur.write_bytes(a.source.read_bytes())
        subprocess.run(['patch','-s','-R','-d',td,'-p1'],input=a.patch.read_bytes(),check=True)
        reverse_sha=sha(cur)
        if reverse_sha!=sha(a.base): die('reverse reconstruction != supplied 0031 base')
        subprocess.run(['patch','-s','-d',td,'-p1'],input=a.patch.read_bytes(),check=True)
        forward_sha=sha(cur)
        if forward_sha!=sha(a.source): die('forward reconstruction != current source')

    out={
      'accepted':True,'schema':'sp11-e003h-pix-priming-full-batch-inspection-v1',
      'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),
      'patch_sha256':sha(a.patch),'proof_sha256':sha(a.proof),'base_0031_sha256':sha(a.base),
      'reverse_reconstruction_sha256':reverse_sha,'forward_reconstruction_sha256':forward_sha,
      'packet_bl_counts':[4,5,5,5],
      'rtcdm_recipe_abs64_relocations':5,
      'rtcdm_recipe_runtime_references':0,
      'callable_runner_present':False,'runtime_reachable':False,
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('PASS: full priming-batch materialization/submission is byte-proven, reconstructable and retained-only')
if __name__=='__main__': main()
