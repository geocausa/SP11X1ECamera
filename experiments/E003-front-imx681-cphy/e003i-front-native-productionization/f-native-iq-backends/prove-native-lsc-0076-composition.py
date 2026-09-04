#!/usr/bin/env python3
from __future__ import annotations
import hashlib,importlib.util,subprocess,tempfile,shutil
from pathlib import Path

def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);assert spec.loader;spec.loader.exec_module(m);return m

def sha(b):return hashlib.sha256(b).hexdigest()

def main():
 here=Path(__file__).resolve().parent;repo=here.parents[3]
 raw=repo.parent/'.local-oracles/oracle-live-20260904-front-atomic'
 # repo.parent is 06-camera; local oracle lives beside SP11X1ECamera.
 if not raw.is_dir():raise SystemExit('missing local 44-file front-atomic fixture: '+str(raw))
 e=load(repo/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/e-template-free-capsule/build-template-free-0076-capsules.py','e003i_e_composer')
 tmp=Path(tempfile.mkdtemp(prefix='e003i-f-native-lsc-'))
 try:
  ldir=tmp/'lsc';man=tmp/'lsc.json'
  subprocess.run([str(here/'generate-native-front-lsc-wire.py'),'--capture-dir',str(raw),'--output-dir',str(ldir),'--manifest',str(man)],check=True)
  wires={}
  for r in (4,5,6):
   wires[r]=[(ldir/f'R{r}_{n}.bin').read_bytes() for n in ('LSC0','LSC1','LSC2','GIC')]
  def generated_lsc(root,req,packer):
   return {'source':'native sequential Tintless output -> direct Q10/Titan680 wire','request':req},wires[req]
  # Replace only E's old staging adapter; the capsule composer itself is unchanged.
  e.atomic_lsc=generated_lsc
  prod=repo/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
  packer=e.load_py(prod/'prove-lsc-live-staging-pack.py','unused_shape_adapter')
  _,variant,main,raw4,slot4,startup,payloads,sp,pp=e.static_recipe(repo)
  for req in (4,5,6):
   st=e.request_state(repo,req,variant,raw4,slot4,packer)
   cap,_=e.compose(req,main,startup,payloads,sp,pp,st)
   got=sha(cap);want=e.EXPECTED[req]
   if got!=want:raise RuntimeError(f'R{req} native-LSC composition mismatch {got} != {want}')
   print(f'R{req} NATIVE_LSC_COMPOSER PASS {got}')
 finally:shutil.rmtree(tmp)
 print('NATIVE_LSC_0076_COMPOSITION=PASS')
 print('CAPTURED_LSC_STAGING_AS_INPUT=false')
 print('LINUX_CAMERA_RUNTIME=false')
if __name__=='__main__':main()
