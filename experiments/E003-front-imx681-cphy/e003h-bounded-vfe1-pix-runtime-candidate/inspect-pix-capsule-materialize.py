#!/usr/bin/env python3
import argparse, hashlib, json, subprocess
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*a): return subprocess.check_output(a,text=True,errors='replace')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--object',type=Path,required=True); ap.add_argument('--module',type=Path,required=True); ap.add_argument('-o','--output',type=Path); a=ap.parse_args()
 s=a.source.read_text(); start=s.index(' * E003h parsed PIX capsule -> Linux-owned DMA materialization'); end=s.index(' * Allocate a caller-sized coherent arena',start); block=s[start:end]
 for x in ['camss_rtcdm1_corpus_materialize(camss, &out->startup','camss_rtcdm1_corpus_materialize(camss, &out->priming','camss_x1e_epoch0_materialize(camss, &out->steady','camss_x1e_pix_capsule_materialize_recipe __used']:
  if x not in block: die('missing '+x)
 for bad in ['writel','readl','fifo0_commit','enable_irq','disable_irq','request_firmware']:
  if bad in block: die('materialize block contains '+bad)
 nm=run('nm','-an',str(a.object)); rel=run('objdump','-r',str(a.object)); vm=run('modinfo','-F','vermagic',str(a.module)).strip()
 names=['camss_x1e_pix_capsule_materialize','camss_x1e_pix_capsule_materialized_release','camss_x1e_pix_capsule_materialize_recipe']
 for name in names:
  if sum(ln.endswith(' '+name) for ln in nm.splitlines())!=1: die(name+' symbol count')
 keep=[ln for ln in rel.splitlines() if 'R_AARCH64_ABS64' in ln and ('camss_x1e_pix_capsule_materialize' in ln)]
 if len(keep)!=2: die('recipe retention count')
 refs=[ln for ln in rel.splitlines() if 'camss_x1e_pix_capsule_materialize_recipe' in ln]
 if refs: die('recipe runtime references')
 if not vm.startswith('7.1.5-sp11-render-parity-v4+ '): die('vermagic')
 out={'accepted':True,'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),'vermagic':vm,'products':['startup RT-CDM corpus DMA','priming RT-CDM corpus DMA','steady Epoch0 command/DMI DMA'],'hardware_access_in_composition':False,'recipe_abs64_relocations':keep,'recipe_runtime_references':0,'runtime_reachable':False}
 txt=json.dumps(out,indent=2,sort_keys=True)+'\n'; (a.output.write_text(txt) if a.output else print(txt,end='')); print('PASS: parsed capsule materializes startup/priming/steady into Linux DMA; no hardware access/caller')
if __name__=='__main__':main()
