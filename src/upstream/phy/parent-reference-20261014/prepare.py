#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
R=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01';P=B/'candidate-30/phy-power-qual01/source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 C=Path(sys.argv[1]).resolve() if len(sys.argv)==2 else B/'candidate-31/phy-parent-ref-qual01'
 if C.exists():raise RuntimeError('occupied source identity')
 m=json.loads((Q/'manifest.json').read_text())
 for n,h in m['parent_pins'].items():
  if sha(P/n)!=h:raise RuntimeError(n)
 C.mkdir(parents=True);S=C/'source';S.mkdir()
 for item in P.iterdir():
  if item.name!='drivers':(S/item.name).symlink_to(item,target_is_directory=item.is_dir())
 (S/'drivers').mkdir()
 for item in (P/'drivers').iterdir():
  if item.name!='phy':(S/'drivers'/item.name).symlink_to(item,target_is_directory=item.is_dir())
 (S/'drivers/phy').mkdir()
 for item in (P/'drivers/phy').iterdir():
  if item.name=='qualcomm':
   shutil.copytree(item,S/'drivers/phy'/item.name,copy_function=os.link,symlinks=True,ignore=shutil.ignore_patterns('*.o','*.ko','*.cmd','*.mod','*.mod.c','Module.symvers','modules.order'))
  else:(S/'drivers/phy'/item.name).symlink_to(item,target_is_directory=item.is_dir())
 p=S/m['changed_file'];data=p.read_bytes();p.unlink();p.write_bytes(data)
 r=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(Q/'0001-parent-reference-release.patch')],cwd=S,capture_output=True,text=True)
 if r.returncode or any(x in r.stdout.lower() for x in ['offset','fuzz']):raise RuntimeError(r.stdout+r.stderr)
 if sha(p)!=m['output_sha256']:raise RuntimeError('output pin')
 (C/'PREPARED.json').write_text(json.dumps(dict(m,source=str(S)),indent=2)+'\n');print('prepared',C)
if __name__=='__main__':main()
