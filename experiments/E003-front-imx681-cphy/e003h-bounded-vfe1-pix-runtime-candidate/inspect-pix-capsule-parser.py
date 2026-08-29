#!/usr/bin/env python3
import argparse, hashlib, json, subprocess
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*a): return subprocess.check_output(a,text=True,errors='replace')
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--object',type=Path,required=True); ap.add_argument('--module',type=Path,required=True); ap.add_argument('-o','--output',type=Path); a=ap.parse_args()
 s=a.source.read_text(); start=s.index(' * E003h disposable PIX oracle-capsule parser'); end=s.index(' * Allocate a caller-sized coherent arena',start); block=s[start:end]
 req=['"E3HPIX01"','CAMSS_X1E_PIX_CAPSULE_SECTION_COUNT\t36','get_unaligned_le64(data + 0x2c)','camss_rtcdm1_corpus_validate_input(&out->startup)','camss_rtcdm1_corpus_validate_input(&out->priming)','camss_x1e_epoch0_validate_input(&out->steady, &variant)','camss_x1e_pix_capsule_recipe __used']
 for x in req:
  if x not in block: die('missing '+x)
 for bad in ['writel','readl','dma_alloc','dma_free','request_firmware','enable_irq','disable_irq','fifo0_commit']:
  if bad in block: die('parser block contains '+bad)
 nm=run('nm','-an',str(a.object)); rel=run('objdump','-r',str(a.object)); vm=run('modinfo','-F','vermagic',str(a.module)).strip()
 for name in ['camss_x1e_pix_capsule_parse','camss_x1e_pix_capsule_recipe']:
  if sum(ln.endswith(' '+name) for ln in nm.splitlines())!=1: die(name+' symbol count')
 keep=[ln for ln in rel.splitlines() if 'R_AARCH64_ABS64' in ln and 'camss_x1e_pix_capsule_parse' in ln]
 refs=[ln for ln in rel.splitlines() if 'camss_x1e_pix_capsule_recipe' in ln]
 if len(keep)!=1 or refs: die('retention/reference topology')
 if not vm.startswith('7.1.5-sp11-render-parity-v4+ '): die('vermagic')
 out={'accepted':True,'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),'vermagic':vm,'capsule_magic':'E3HPIX01','section_count':36,'request_id_width_bits':64,'maps':['startup corpus input','priming corpus input','steady epoch0 named-module input'],'calls_existing_fail_closed_validators':True,'mmio_or_dma_in_parser':False,'parser_abs64_relocations':keep,'recipe_runtime_references':0,'runtime_reachable':False}
 txt=json.dumps(out,indent=2,sort_keys=True)+'\n'; (a.output.write_text(txt) if a.output else print(txt,end='')); print('PASS: capsule parser retained-only; structural mapping reaches existing validators, no MMIO/DMA')
if __name__=='__main__':main()
