#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.util,subprocess,tempfile,shutil
from pathlib import Path

def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);assert spec.loader;spec.loader.exec_module(m);return m
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 here=Path(__file__).resolve().parent;repo=here.parents[3];raw=repo.parent/'.local-oracles/oracle-live-20260904-front-atomic';e=load(repo/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/e-template-free-capsule/build-template-free-0076-capsules.py','e003i_h_composer')
 tmp=Path(tempfile.mkdtemp(prefix='e003i-h-chain-'))
 try:
  ldir=tmp/'wire';subprocess.run([str(here/'generate-integrated-front-lsc-wire.py'),'--capture-dir',str(raw),'--output-dir',str(ldir),'--manifest',str(tmp/'chain.json')],check=True)
  wires={r:[(ldir/f'R{r}_{n}.bin').read_bytes() for n in ('LSC0','LSC1','LSC2','GIC')] for r in (4,5,6)}
  e.atomic_lsc=lambda root,req,packer:({'source':'clean-room upstream -> native sequential Tintless -> direct wire','request':req},wires[req])
  prod=repo/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static';packer=e.load_py(prod/'prove-lsc-live-staging-pack.py','e003i_h_unused_adapter');_,variant,main,raw4,slot4,startup,payloads,sp,pp=e.static_recipe(repo)
  for req in (4,5,6):
   st=e.request_state(repo,req,variant,raw4,slot4,packer);cap,_=e.compose(req,main,startup,payloads,sp,pp,st);got=sha(cap);want=e.EXPECTED[req]
   if got!=want:raise RuntimeError(f'R{req} integrated composition mismatch {got} != {want}')
   print(f'R{req} INTEGRATED_LSC_COMPOSER PASS {got}')
 finally:shutil.rmtree(tmp)
 print('INTEGRATED_LSC_0076_COMPOSITION=PASS');print('CAPTURED_PRETINTLESS_INPUT=false');print('CAPTURED_OUTPUT_PRE_INPUT=false');print('CAPTURED_LSC_STAGING_INPUT=false');print('LINUX_CAMERA_RUNTIME=false')
if __name__=='__main__':main()
