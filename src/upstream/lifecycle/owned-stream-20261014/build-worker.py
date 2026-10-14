#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import hashlib,json,shutil,subprocess,os
R=Path(__file__).resolve().parents[4]
B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01'
C=B/'candidate-28/lifecycle-qual01'
S=C/'source';O=C/'build01';M=C/'module01'
OLD=B/'candidate-26/final-qual02/build'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(label,args):
 p=subprocess.run([str(x) for x in args],text=True,capture_output=True)
 (C/(label+'.log')).write_text(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(label+': '+p.stderr[-2000:])
 return p.stdout
def main():
 head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()
 subprocess.run(['bash',str(R/'tools/camera-overlap-guard.sh'),'--require-golden','--require-no-camera-process','--expect-head',head,'--expect-origin',head],check=True)
 assert not O.exists() and not M.exists()
 prep=json.loads((C/'PREPARED.json').read_text())
 for n,h in prep['source_sha256'].items():assert sha(S/'drivers/media/platform/qcom/camss'/n)==h,n
 O.mkdir();M.mkdir()
 shutil.copyfile(OLD/'.config',O/'.config')
 args=['make','-C',S,'O='+str(O),'ARCH=arm64','LOCALVERSION=-sp11-upstream-front26','-j12']
 result={'status':'FAILED_LIFECYCLE_MODULE_BUILD','source_head':head,'source_candidate':28,'full_kernel_candidate':26,'installed':False}
 try:
  run('config01',args+['olddefconfig'])
  assert sha(O/'.config')==sha(OLD/'.config')
  run('prepare01',args+['modules_prepare'])
  shutil.copyfile(OLD/'Module.symvers',O/'Module.symvers')
  run('camss01',args+['M='+str(S/'drivers/media/platform/qcom/camss'),'MO='+str(M),'W=1','KCFLAGS=-Werror','modules'])
  assert not any(x in (C/'camss01.log').read_text() for x in ['warning:','error:'])
  ko=M/'qcom-camss.ko'
  vm=run('vermagic01',['modinfo','-F','vermagic',ko]).strip()
  assert vm.split()[0]=='7.2.0-sp11-upstream-front26'
  assert run('namespace01',['modinfo','-F','import_ns',ko]).strip()=='DMA_BUF'
  result.update(status='PASS_LIFECYCLE_MODULE_ARM64_W1_WERROR',module_sha256=sha(ko),module_bytes=ko.stat().st_size,module_path=str(ko),vermagic=vm,config_sha256=sha(O/'.config'),strict_warnings=0,strict_errors=0,qualification_scope='X1E RDI allocator-owned MMAP lifecycle; imported DMA-BUF and PIX excluded')
 except Exception as e:result['error']=str(e);raise
 finally:(C/'BUILD.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result))
if __name__=='__main__':main()
