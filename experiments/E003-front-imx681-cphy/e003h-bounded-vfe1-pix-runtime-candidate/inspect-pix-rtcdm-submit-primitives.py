#!/usr/bin/env python3
import argparse, hashlib, json, subprocess
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*a): return subprocess.check_output(a,text=True,errors='replace')

def between(s,a,b):
    i=s.index(a); j=s.index(b,i); return s[i:j]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--object',type=Path,required=True); ap.add_argument('--module',type=Path,required=True); ap.add_argument('-o','--output',type=Path); a=ap.parse_args()
    s=a.source.read_text()
    block=between(s,' * E003h bounded PIX RT-CDM submission primitives',' * Allocate a caller-sized coherent arena')
    req=[
      'camss_rtcdm1_windows_open_init(camss)', 'camss_rtcdm1_windows_start(camss)',
      'corpus->packet_len[packet] - 1', 'steady->bl_len[i] - 1',
      'camss_rtcdm1_windows_stop(camss)', 'camss_x1e_pix_rtcdm_close_sw(camss)',
      'camss_x1e_pix_rtcdm_recipe __used = {',
      '.open_start = camss_x1e_pix_rtcdm_open_start,',
      '.submit_corpus_packet = camss_x1e_pix_rtcdm_submit_corpus_packet,',
      '.submit_epoch0_batch = camss_x1e_pix_rtcdm_submit_epoch0_batch,',
      '.stop_close = camss_x1e_pix_rtcdm_stop_close,']
    for x in req:
        if x not in block: die('missing '+x)
    close=between(block,'static void camss_x1e_pix_rtcdm_close_sw','static int camss_x1e_pix_rtcdm_open_start')
    if 'disable_irq(rt->irq)' not in close or 'WRITE_ONCE(rt->irq_armed, false)' not in close: die('software close does not unarm IRQ')
    for bad in ['writel','readl']:
        if bad in close: die('software close contains RT-CDM MMIO primitive '+bad)
    openb=between(block,'static int camss_x1e_pix_rtcdm_open_start','static int camss_x1e_pix_rtcdm_submit_corpus_packet')
    # No direct register operations in wrapper; delegate exact existing recipe.
    for bad in ['writel','readl','FIFO0_BASE','FIFO0_LEN','FIFO0_STORE']:
        if bad in openb: die('open wrapper contains new hardware primitive '+bad)
    stopb=between(block,'static void camss_x1e_pix_rtcdm_stop_close','struct camss_x1e_pix_rtcdm_static_ops')
    for bad in ['writel','readl']:
        if bad in stopb: die('stop wrapper contains direct MMIO '+bad)
    nm=run('nm','-an',str(a.object)); rel=run('objdump','-r',str(a.object)); vm=run('modinfo','-F','vermagic',str(a.module)).strip()
    names=['camss_x1e_pix_rtcdm_open_start','camss_x1e_pix_rtcdm_submit_corpus_packet','camss_x1e_pix_rtcdm_submit_epoch0_batch','camss_x1e_pix_rtcdm_stop_close','camss_x1e_pix_rtcdm_recipe']
    for name in names:
        if sum(ln.endswith(' '+name) for ln in nm.splitlines())!=1: die(name+' symbol count')
    keep=[ln for ln in rel.splitlines() if 'R_AARCH64_ABS64' in ln and any(n in ln for n in names[:-1])]
    if len(keep)!=4: die('recipe retention relocation count')
    refs=[ln for ln in rel.splitlines() if 'camss_x1e_pix_rtcdm_recipe' in ln]
    if refs: die('recipe runtime relocation reference')
    if not vm.startswith('7.1.5-sp11-render-parity-v4+ '): die('vermagic drift')
    out={'accepted':True,'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),'vermagic':vm,
         'open_start':'delegates existing Windows open_init then start','corpus_fifo_length':'byte_count - 1','steady_fifo_length':'byte_count - 1 for each of five BLs',
         'stop':'existing Windows IRQ0 mask-only stop then Linux software IRQ unarm','software_close_rtcdm_mmio':False,'recipe_abs64_relocations':keep,'recipe_runtime_references':0,'runtime_reachable':False}
    txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
    if a.output:a.output.write_text(txt)
    else:print(txt,end='')
    print('PASS: PIX RT-CDM wrappers exact-length, delegated hardware recipe, software-only close, retained/unreachable')
if __name__=='__main__': main()
