#!/usr/bin/env python3
import argparse, hashlib, json, re, subprocess
from pathlib import Path

def die(s): raise SystemExit('FAIL: '+s)
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def run(*a): return subprocess.check_output(a,text=True,errors='replace')

def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--source',type=Path,required=True); ap.add_argument('--object',type=Path,required=True); ap.add_argument('--module',type=Path,required=True); ap.add_argument('-o','--output',type=Path); a=ap.parse_args()
 s=a.source.read_text(); required=[
  '#define VFE680_X1E_RAW_EPOCH0\tBIT(21)', '#define VFE680_X1E_RAW_VIDEO\tBIT(0)',
  'readl_relaxed_poll_timeout(reg, status, status & bit, 10, timeout_us)',
  'writel_relaxed(s->top0, vfe->base + VFE_TOP_IRQn_CLEAR(vfe, 0));',
  'writel_relaxed(s->top1, vfe->base + VFE_TOP_IRQn_CLEAR(vfe, 1));',
  'vfe->base + VFE_TOP_IRQ_CMD(vfe));',
  'writel_relaxed(s->bus0, vfe->base + VFE_BUS_IRQn_CLEAR(vfe, 0));',
  'writel_relaxed(s->bus1, vfe->base + VFE_BUS_IRQn_CLEAR(vfe, 1));',
  'writel_relaxed(1, vfe->base + VFE_BUS_IRQ_GLOBAL_CLEAR(vfe));',
  'vfe680_x1e_raw_irq_recipe __used = {', '.epoch0 = vfe680_x1e_poll_epoch0,', '.video = vfe680_x1e_poll_video,']
 for x in required:
  if x not in s: die('missing source anchor '+x)
 # New block must not program IRQ masks or claim other bits.
 block=s[s.index(' * E003h raw VFE1 PIX event polling'):s.index(' * E003h PIX frame-bundle ownership')]
 if 'VFE_TOP_IRQn_MASK' in block or 'VFE_BUS_IRQn_MASK' in block: die('raw helper writes/reads IRQ mask')
 if re.search(r'BIT\((?!0\)|21\))\d+\)', block): die('unexpected raw event bit')
 nm=run('nm','-an',str(a.object)); rel=run('objdump','-r',str(a.object)); modinfo=run('modinfo','-F','vermagic',str(a.module)).strip()
 syms={}
 for name in ['vfe680_x1e_poll_epoch0','vfe680_x1e_poll_video','vfe680_x1e_raw_irq_recipe']:
  hits=[ln for ln in nm.splitlines() if ln.endswith(' '+name)]
  if len(hits)!=1: die(name+' symbol count')
  syms[name]=hits[0]
 helper_reloc=[ln for ln in rel.splitlines() if 'R_AARCH64_ABS64' in ln and ('vfe680_x1e_poll_epoch0' in ln or 'vfe680_x1e_poll_video' in ln)]
 if len(helper_reloc)!=2: die('retention relocation count')
 recipe_refs=[ln for ln in rel.splitlines() if 'vfe680_x1e_raw_irq_recipe' in ln]
 if recipe_refs: die('recipe has runtime relocation reference')
 if not modinfo.startswith('7.1.5-sp11-render-parity-v4+ '): die('vermagic drift')
 out={'accepted':True,'source_sha256':sha(a.source),'object_sha256':sha(a.object),'module_sha256':sha(a.module),'vermagic':modinfo,'raw_events':{'epoch0':'BUS status1 bit21','video':'TOP status1 bit0'},'clear':'TOP status0/1 -> clear0/1 -> global clear; BUS status0/1 -> clear0/1 -> global clear','timeout':'caller-owned microseconds','helper_abs64_relocations':helper_reloc,'recipe_runtime_references':0,'symbols':syms,'runtime_reachable':False}
 txt=json.dumps(out,indent=2,sort_keys=True)+'\n';
 if a.output:a.output.write_text(txt)
 else:print(txt,end='')
 print('PASS: raw Epoch0/VIDEO polling retained-only, exact bits/clear sequence, Golden vermagic')
if __name__=='__main__':main()
