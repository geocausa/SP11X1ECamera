#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Create a fresh sparse source overlay; never overwrite a shared archive."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
R=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 C=Path(sys.argv[1]).resolve() if len(sys.argv)==2 else B/'candidate-35/cdm-owner-qual01'
 if C.exists():raise RuntimeError('occupied source identity')
 m=json.loads((Q/'manifest.json').read_text());P=Path(m['parent'])
 if sha(Q/'0001-cdm21-coherent-program-owner.patch')!=m['patch_sha256']:raise RuntimeError('patch pin')
 for n,h in m['parent_pins'].items():
  if sha(P/n)!=h:raise RuntimeError('parent pin '+n)
 C.mkdir(parents=True);S=C/'source';S.mkdir()
 def branch(src,dest,parts):
  for item in src.iterdir():
   out=dest/item.name
   if item.name!=parts[0]:out.symlink_to(item,target_is_directory=item.is_dir())
   elif len(parts)>1:
    out.mkdir();branch(item,out,parts[1:])
   else:shutil.copytree(item,out,copy_function=os.link,symlinks=True,ignore=shutil.ignore_patterns('*.o','*.ko','*.cmd','*.mod','*.mod.c','Module.symvers','modules.order'))
 branch(P,S,['drivers','media','platform','qcom','camss'])
 for n in m['output_sha256']:
  p=S/n
  if p.exists():
   data=p.read_bytes();p.unlink();p.write_bytes(data)
 p=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(Q/'0001-cdm21-coherent-program-owner.patch')],cwd=S,capture_output=True,text=True)
 if p.returncode or any(x in p.stdout.lower() for x in ['offset','fuzz']):raise RuntimeError(p.stdout+p.stderr)
 for n,h in m['output_sha256'].items():
  if sha(S/n)!=h:raise RuntimeError('output pin '+n)
 for n,h in m['parent_pins'].items():
  if sha(P/n)!=h:raise RuntimeError('parent changed '+n)
 (C/'PREPARED.json').write_text(json.dumps(dict(m,source=str(S)),indent=2)+'\n')
 print('PASS_SPARSE_REPLAY_PARENT_AND_OUTPUT_PINS',C)
if __name__=='__main__':main()
