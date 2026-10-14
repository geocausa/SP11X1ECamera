#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build and compare only the isolated sensor-domain DTB; never install."""
from pathlib import Path
import hashlib,json,subprocess,shutil,sys
R=Path(__file__).resolve().parents[4]
Q=Path(__file__).resolve().parent
B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01'
C=Path(sys.argv[1]).resolve() if len(sys.argv)==2 else B/'candidate-29/sensor-domain-qual01'
S=C/'source';O=C/'build01'
BASE=B/'candidate-26/final-qual02/build'
TARGET='qcom/x1e80100-microsoft-denali-oled-front-camera.dtb'
def need(v,msg):
 if not v:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(args,label):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True)
 (C/(label+'.log')).write_text(p.stdout+p.stderr)
 need(p.returncode==0,label+': '+p.stderr[-1200:])
 return p.stdout
def main():
 need(not O.exists(),'build identity occupied')
 m=json.loads((Q/'manifest.json').read_text())
 need(sha(S/m['changed_file'])==m['output_sha256'],'source pin')
 for n,h in m['parent_pins'].items():
  if n!=m['changed_file']:need(sha(S/n)==h,'parent pin '+n)
 O.mkdir()
 shutil.copyfile(BASE/'.config',O/'.config')
 args=['make','-C',S,'O='+str(O),'ARCH=arm64','LOCALVERSION=-sp11-upstream-front26']
 run(args+['olddefconfig'],'config01')
 need(sha(O/'.config')==sha(BASE/'.config'),'config drift')
 run(args+['-j8','W=1',TARGET],'dtb01')
 ko=O/'arch/arm64/boot/dts'/TARGET
 old=BASE/'arch/arm64/boot/dts'/TARGET
 need(sha(old)=='2168463ae4b8bab65f47b1ee2c86e5710c6d78004f6edc9dba751cac8297bddf','baseline DTB')
 a=run(['dtc','-I','dtb','-O','dts',old],'before-dts')
 b=run(['dtc','-I','dtb','-O','dts',ko],'after-dts')
 import difflib
 diff=''.join(difflib.unified_diff(a.splitlines(True),b.splitlines(True),fromfile='kernel26',tofile='sensor-domain29'))
 (C/'semantic-difference.diff').write_text(diff)
 changed=[l for l in diff.splitlines() if l.startswith(('+','-')) and not l.startswith(('+++','---'))]
 need(len(changed)==1 and changed[0].startswith('+') and 'power-domains' in changed[0],'unexpected semantic change')
 sensor='/soc@0/cci@ac16000/i2c-bus@1/camera@10'
 cci='/soc@0/cci@ac16000'
 sensor_pd=run(['fdtget','-t','x',ko,sensor,'power-domains'],'sensor-domain').strip()
 cci_pd=run(['fdtget','-t','x',ko,cci,'power-domains'],'cci-domain').strip()
 need(sensor_pd==cci_pd and sensor_pd.split()[-1]=='5','TITAN_TOP supplier mismatch')
 for n,h in m['parent_pins'].items():need(sha(B/'candidate-28/lifecycle-qual01/source'/n)==h,'protected parent drift '+n)
 check=run(['perl',S/'scripts/checkpatch.pl','--no-signoff',Q/'0001-sensor-runtime-domain.patch'],'checkpatch-final')
 need('total: 0 errors, 0 warnings' in check,'patch diagnostics')
 result={'status':'PASS_SENSOR_DOMAIN_DTB_SOURCE_ONLY','source_candidate':29,'parent_source_candidate':28,'full_kernel_candidate':26,'source_head':subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip(),'changed_source_sha256':m['output_sha256'],'dtb_path':str(ko),'dtb_sha256':sha(ko),'dtb_bytes':ko.stat().st_size,'config_sha256':sha(O/'.config'),'semantic_changes':changed,'sensor_domain_matches_retained_cci1_domain':True,'parent_pins_preserved':len(m['parent_pins']),'kernel_modules_unchanged':True,'binding_schema_qualified':False,'hardware_qualified':False,'installed':False,'scope':'standard genpd claim for the sensor; one property only; no register or sensor sequence change'}
 (C/'QUALIFIED.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result))
if __name__=='__main__':main()
