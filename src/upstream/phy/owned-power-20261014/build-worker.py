#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import hashlib,json,subprocess,shutil,re,sys
R=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01'
C=B/'candidate-30/phy-power-qual01';S=C/'source';ATTEMPT=sys.argv[1] if len(sys.argv)==2 else '02';O=C/('build'+ATTEMPT);BASE=B/'candidate-26/final-qual02/build'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def need(v,msg):
 if not v:raise RuntimeError(msg)
def run(args,label):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True)
 (C/(label+'-'+ATTEMPT+'.log')).write_text(p.stdout+p.stderr)
 need(not p.returncode,label+': '+p.stderr[-1800:])
 return p.stdout+p.stderr
def main():
 need(not O.exists(),'occupied build identity')
 m=json.loads((Q/'manifest.json').read_text())
 for n,h in m['output_sha256'].items():need(sha(S/n)==h,'source pin '+n)
 for n,h in m['input_sha256'].items():need(sha(B/'candidate-29/sensor-domain-qual01/source'/n)==h,'parent pin '+n)
 O.mkdir();shutil.copyfile(BASE/'.config',O/'.config')
 make=['make','-C',S,'O='+str(O),'ARCH=arm64','LOCALVERSION=-sp11-upstream-front26']
 run(make+['olddefconfig'],'config01');need(sha(O/'.config')==sha(BASE/'.config'),'config drift')
 run(make+['-j8','modules_prepare'],'prepare01')
 shutil.copyfile(BASE/'Module.symvers',O/'Module.symvers')
 artifacts={}
 for label,relative,target in [('phy','drivers/phy/qualcomm','phy-qcom-mipi-csi2.ko'),('camss','drivers/media/platform/qcom/camss','qcom-camss.ko')]:
  mo=C/(label+'-module'+ATTEMPT);mo.mkdir()
  log=run(make+['-j8','M='+str(S/relative),'MO='+str(mo),'W=1','KCFLAGS=-Werror',target],label+'01')
  need(not re.search(r'\b(?:warning|error):',log),'strict diagnostics '+label)
  p=mo/target;need(p.is_file(),'artifact '+label)
  vermagic=run(['modinfo','-F','vermagic',p],label+'-vermagic').strip()
  need(vermagic.startswith('7.2.0-sp11-upstream-front26 '),'ABI '+label)
  artifacts[label]={'module_path':str(p),'sha256':sha(p),'bytes':p.stat().st_size,'vermagic':vermagic,'strict_warnings':0,'strict_errors':0}
 result={'status':'PASS_OWNED_PHY_AND_CAMSS_MODULES_ARM64_W1_WERROR','source_candidate':30,'full_kernel_candidate':26,'source_sha256':m['output_sha256'],'config_sha256':sha(O/'.config'),'artifacts':artifacts,'installed':False,'hardware_qualified':False}
 (C/'BUILD.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
