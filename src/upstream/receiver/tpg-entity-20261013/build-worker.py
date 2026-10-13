#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build a one-line TPG classification correction; retain original kernel/source."""
from pathlib import Path
import hashlib,json,os,shutil,subprocess
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-upstream')
B=R.parents[1]/'02-kernel/upstream-ife-base-build-20261011-01'
P=B/'candidate-26/source'
OLD=B/'candidate-26/final-qual02/build'
C=B/'candidate-27/tpg-qual01'
S=C/'source'
O=C/'build'
KREL='7.2.0-sp11-upstream-front26'
FILE='drivers/media/platform/qcom/camss/camss-tpg.c'
OLDPIN='f17719e34631e91a780aafcc288526dd1682372d70d4aa991f75ccafc498aaaa'
def need(v,why):
 if not v:raise RuntimeError(why)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def run(label,args):
 p=subprocess.run([str(x) for x in args],capture_output=True,text=True)
 (C/(label+'.log')).write_text(p.stdout+p.stderr)
 need(p.returncode==0,label+': '+p.stderr[-1500:])
 return p.stdout
def main():
 head=subprocess.check_output(['git','-C',str(R),'rev-parse','HEAD'],text=True).strip()
 subprocess.run(['bash',str(R/'tools/camera-overlap-guard.sh'),'--require-golden','--require-no-camera-process','--expect-head',head,'--expect-origin',head],check=True)
 need(not C.exists(),'candidate stage exists; reconcile')
 manifest=json.loads((R/'docs/UPSTREAM-FRONT-GRAPH-BUILD-20261013.json').read_text())
 for n,h in manifest['source_sha256'].items():need(sha(R/n)==h,'repository source drift: '+n)
 pins=json.loads((R/manifest['source_manifest']).read_text())['output_source_sha256']
 for n,h in pins.items():need(sha(P/n)==h,'parent source drift: '+n)
 need(sha(P/FILE)==OLDPIN,'TPG parent drift')
 need(shutil.disk_usage(B).free>500*2**20,'build space')
 C.mkdir(parents=True)
 result=dict(status='FAILED_TPG_MODULE_BUILD',source_head=head,kernel_release=KREL,installed=False,hardware_qualified=False)
 try:
  shutil.copytree(P,S,copy_function=os.link,symlinks=True)
  p=S/FILE;data=p.read_text();old='\tsd->entity.ops = &tpg_media_ops;'
  need(data.count(old)==1,'registration context')
  data=data.replace(old,'\tsd->entity.function = MEDIA_ENT_F_CAM_SENSOR;\n'+old)
  p.unlink();p.write_text(data)
  diff=subprocess.run(['diff','-u','--label','a/'+FILE,'--label','b/'+FILE,str(P/FILE),str(p)],text=True,capture_output=True)
  need(diff.returncode==1,'single change diff')
  (C/'tpg.patch').write_text('Subject: [PATCH] media: qcom: camss: classify the single-pad test generator\n\nThe retained TPG registers with an unknown entity function. Classify\nthis single-source-pad generator as a synthetic camera sensor, as VIMC\ndoes. This removes the registration warning without changing pads,\nstream operations or link selection.\n\n---\n'+diff.stdout)
  O.mkdir();shutil.copyfile(OLD/'.config',O/'.config')
  args=['make','-C',S,'O='+str(O),'ARCH=arm64','LOCALVERSION=-sp11-upstream-front26','-j12']
  run('config',args+['olddefconfig'])
  need(sha(O/'.config')==sha(OLD/'.config'),'config changed')
  run('prepare',args+['modules_prepare'])
  shutil.copyfile(OLD/'Module.symvers',O/'Module.symvers')
  run('camss',args+['M=drivers/media/platform/qcom/camss','W=1','KCFLAGS=-Werror','modules'])
  log=(C/'camss.log').read_text()
  need('warning:' not in log and 'error:' not in log,'strict diagnostics')
  ko=S/'drivers/media/platform/qcom/camss/qcom-camss.ko'
  vermagic=run('vermagic',['modinfo','-F','vermagic',ko]).strip()
  need(vermagic.split()[0]==KREL,'module ABI release')
  for n,h in pins.items():need(sha(P/n)==h,'parent altered: '+n)
  need(sha(P/FILE)==OLDPIN,'parent TPG changed')
  check=run('checkpatch',[S/'scripts/checkpatch.pl','--no-signoff','--strict',C/'tpg.patch'])
  result.update(status='PASS_TPG_CLASSIFICATION_MODULE_SOURCE_ONLY',source_candidate=27,
    parent_source_preserved=True,config_sha256=sha(O/'.config'),
    module_sha256=sha(ko),module_bytes=ko.stat().st_size,vermagic=vermagic,
    before_source_sha256=OLDPIN,after_source_sha256=sha(p),
    patch_sha256=sha(C/'tpg.patch'),strict_warnings=0,strict_errors=0,
    parent_kernel_candidate=26,module_only=True,stage=str(C),
    provenance='Retained one-source-pad TPG classified like GPL kernel VIMC synthetic sensor; newer public CAMSS two-pad formatter is a different pad ABI')
 except Exception as e:
  result['error']=str(e);raise
 finally:(C/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result))
if __name__=='__main__':main()
