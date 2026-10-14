#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reproduce the owned PHY port without duplicating the immutable kernel tree."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
R=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01';P=B/'candidate-29/sensor-domain-qual01/source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise RuntimeError(msg)
def branch(parent,target,parts):
 target.mkdir(exist_ok=True)
 for item in parent.iterdir():
  if item.name==parts[0]:
   if len(parts)>1:branch(item,target/item.name,parts[1:])
   else:shutil.copytree(item,target/item.name,copy_function=os.link,symlinks=True,ignore=shutil.ignore_patterns('*.o','*.ko','*.cmd','*.mod','*.mod.c','Module.symvers','modules.order'))
  else:(target/item.name).symlink_to(item,target_is_directory=item.is_dir())
def main():
 C=Path(sys.argv[1]).resolve() if len(sys.argv)==2 else B/'candidate-30/phy-power-qual01'
 need(not C.exists(),'occupied source identity')
 m=json.loads((Q/'manifest.json').read_text())
 for n,h in m['parent_pins'].items():need(sha(P/n)==h,n)
 head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()
 subprocess.run(['bash',str(R/'tools/camera-overlap-guard.sh'),'--require-golden','--require-no-camera-process','--expect-head',head,'--expect-origin',head],check=True)
 C.mkdir(parents=True);S=C/'source';S.mkdir()
 for item in P.iterdir():
  if item.name!='drivers':(S/item.name).symlink_to(item,target_is_directory=item.is_dir())
 (S/'drivers').mkdir()
 for item in (P/'drivers').iterdir():
  if item.name=='phy':branch(item,S/'drivers/phy',['qualcomm'])
  elif item.name=='media':branch(item,S/'drivers/media',['platform','qcom','camss'])
  else:(S/'drivers'/item.name).symlink_to(item,target_is_directory=item.is_dir())
 for n in m['output_sha256']:
  p=S/n;data=p.read_bytes();p.unlink();p.write_bytes(data)
 r=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(Q/'0001-owned-phy-power.patch')],cwd=S,capture_output=True,text=True)
 need(not r.returncode and not any(x in r.stdout.lower() for x in ['fuzz','offset']),r.stdout+r.stderr)
 for n,h in m['output_sha256'].items():need(sha(S/n)==h,'output '+n)
 for n,h in m['parent_pins'].items():need(sha(P/n)==h,'parent drift '+n)
 (C/'PREPARED.json').write_text(json.dumps(dict(m,source=str(S),source_head=head),indent=2)+'\n');print('prepared',C)
if __name__=='__main__':main()
