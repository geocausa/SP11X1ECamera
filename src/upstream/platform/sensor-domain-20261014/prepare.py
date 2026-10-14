#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reproduce the one-property port in a fresh isolated source workspace."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess,sys
R=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01'
P=B/'candidate-28/lifecycle-qual01/source'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise RuntimeError(msg)
def main():
 C=Path(sys.argv[1]).resolve() if len(sys.argv)==2 else B/'candidate-29/sensor-domain-qual01'
 need(not C.exists(),'occupied candidate identity')
 m=json.loads((Q/'manifest.json').read_text())
 for n,h in m['parent_pins'].items():need(sha(P/n)==h,n)
 head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()
 subprocess.run(['bash',str(R/'tools/camera-overlap-guard.sh'),'--require-golden','--require-no-camera-process','--expect-head',head,'--expect-origin',head],check=True)
 C.mkdir(parents=True)
 S=C/'source'
 shutil.copytree(P,S,copy_function=os.link,symlinks=True,ignore=shutil.ignore_patterns('*.o','*.ko','*.cmd','*.mod','*.mod.c','Module.symvers','modules.order'))
 # Detach the one changed hardlink before patch writes.
 p=S/m['changed_file'];data=p.read_bytes();p.unlink();p.write_bytes(data)
 r=subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(Q/'0001-sensor-runtime-domain.patch')],cwd=S,capture_output=True,text=True)
 need(not r.returncode and not any(x in r.stdout.lower() for x in ['fuzz','offset']),r.stdout+r.stderr)
 need(sha(p)==m['output_sha256'],'patch output pin')
 for n,h in m['parent_pins'].items():need(sha(P/n)==h,'parent changed '+n)
 (C/'PREPARED.json').write_text(json.dumps(dict(m,source=str(S),build=str(C/'build01'),source_head=head),indent=2)+'\n')
 print('prepared',C)
if __name__=='__main__':main()
