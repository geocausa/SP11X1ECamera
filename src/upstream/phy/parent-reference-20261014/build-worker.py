#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import subprocess,hashlib,json,shutil,re
R=Path(__file__).resolve().parents[4];Q=Path(__file__).resolve().parent
B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01';C=B/'candidate-31/phy-parent-ref-qual01';S=C/'source';O=C/'build01';BASE=B/'candidate-26/final-qual02/build'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,name):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True)
 (C/(name+'.log')).write_text(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(name+': '+p.stderr[-1800:])
 return p.stdout+p.stderr
def main():
 if O.exists():raise RuntimeError('occupied output')
 m=json.loads((Q/'manifest.json').read_text())
 if sha(S/m['changed_file'])!=m['output_sha256']:raise RuntimeError('source pin')
 O.mkdir();shutil.copyfile(BASE/'.config',O/'.config')
 args=['make','-C',S,'O='+str(O),'ARCH=arm64','LOCALVERSION=-sp11-upstream-front26']
 run(args+['olddefconfig'],'config01')
 if sha(O/'.config')!=sha(BASE/'.config'):raise RuntimeError('config drift')
 run(args+['-j8','modules_prepare'],'prepare01');shutil.copyfile(BASE/'Module.symvers',O/'Module.symvers')
 mo=C/'phy-module01';mo.mkdir()
 log=run(args+['-j8','M='+str(S/'drivers/phy/qualcomm'),'MO='+str(mo),'W=1','KCFLAGS=-Werror','phy-qcom-mipi-csi2.ko'],'phy01')
 if re.search(r'\b(warning|error):',log):raise RuntimeError('strict diagnostics')
 ko=mo/'phy-qcom-mipi-csi2.ko';v=run(['modinfo','-F','vermagic',ko],'vermagic').strip()
 if not v.startswith('7.2.0-sp11-upstream-front26 '):raise RuntimeError('vermagic')
 result={'status':'PASS_PHY_PARENT_REFERENCE_MODULE_ARM64_W1_WERROR','source_candidate':31,'full_kernel_candidate':26,'module_path':str(ko),'sha256':sha(ko),'bytes':ko.stat().st_size,'vermagic':v,'source_sha256':m['output_sha256'],'config_sha256':sha(O/'.config'),'strict_warnings':0,'strict_errors':0,'installed':False,'hardware_qualified':False}
 (C/'BUILD.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
