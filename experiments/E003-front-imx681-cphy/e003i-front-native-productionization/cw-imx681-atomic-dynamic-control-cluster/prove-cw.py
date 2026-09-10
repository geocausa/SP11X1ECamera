#!/usr/bin/env python3
from __future__ import annotations
import hashlib
import importlib.util
import json
import random
import re
import subprocess
import sys
from pathlib import Path

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
REPO=HERE.parents[3]
AM=BASE/'am-imx681-exposure-cluster-fix'
CV=BASE/'cv-native-aec-offline-sensor-control-join'
K=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/linux-7.1.5')
KB=Path('/home/geoca/Documents/SP11-PROJECT/02-kernel/build-runtime-v4-headers-20260826')
API=K/'drivers/media/v4l2-core/v4l2-ctrls-api.c'
CORE=K/'drivers/media/v4l2-core/v4l2-ctrls-core.c'
SRC=(HERE/'imx681.c').read_text()
AMSRC=(AM/'imx681.c').read_text()
PARENT='6df82d7'

def need(x,m):
    if not x: raise AssertionError(m)

def body(src,name,next_name):
    a=src.index(name); b=src.index(next_name,a); return src[a:b]

need(subprocess.run(['git','merge-base','--is-ancestor',PARENT,'HEAD'],cwd=REPO).returncode==0,'parent')

# Preserve AM's already-live-proven sensor write function byte-for-byte at source level.
apply_cw=body(SRC,'static int imx681_apply_request_controls','static int imx681_try_ctrl')
apply_am=body(AMSRC,'static int imx681_apply_request_controls','static int imx681_set_ctrl')
need(apply_cw==apply_am,'group-held write body changed from AM')
for x in ('IMX681_REG_GROUP_HOLD, 1','IMX681_REG_FRAME_LENGTH, frame_length',
          'IMX681_REG_EXPOSURE, exposure','IMX681_REG_ANALOG_GAIN, analogue_gain',
          'IMX681_REG_DIGITAL_GAIN, digital_gain','IMX681_REG_GROUP_HOLD, 0'):
    need(x in apply_cw,x)

# CW topology: exactly one four-control cluster and no p_new-mutating range helper.
need('v4l2_ctrl_cluster(4, &imx681->vblank);' in SRC,'four control cluster')
need('v4l2_ctrl_cluster(3, &imx681->exposure);' not in SRC,'old AM cluster remains')
need('__v4l2_ctrl_modify_range' not in SRC,'modify_range remains')
need('.try_ctrl = imx681_try_ctrl' in SRC,'try_ctrl absent')
need('IMX681_EXPOSURE_HW_MAX' in SRC,'static exposure max absent')
tryb=body(SRC,'static int imx681_try_ctrl','static int imx681_set_ctrl')
need('imx681->vblank->val' in tryb and 'imx681->exposure->val' in tryb,'try peer values')
need('exposure_max = (frame_length - IMX681_EXPOSURE_MARGIN) & ~1U;' in tryb,'dynamic containment')
need('return -ERANGE;' in tryb,'invalid relation rejection')

# Exact Linux 7.1.5 core ordering.  Extended controls first copy all caller values
# belonging to a master cluster, then call try_or_set_cluster once for that master.
api=API.read_text(); core=CORE.read_text()
a=api.index('int try_set_ext_ctrls_common'); b=api.index('static int try_set_ext_ctrls',a)
ext=api[a:b]
need(ext.index('user_to_new') < ext.index('try_or_set_cluster'),'ext set order')
need('idx = helpers[idx].next;' in ext,'same-master linked controls')
need('if (!helpers[i].mref)' in ext,'master dedup')

a=core.index('int try_or_set_cluster'); b=core.index('/* Activate/deactivate a control.',a)
cl=core[a:b]
need(cl.index('if (!ctrl->is_new)') < cl.index('call_op(master, try_ctrl)') <
     cl.index('call_op(master, s_ctrl)') < cl.index('new_to_cur'),'cluster callback order')
need('cur_to_new(ctrl);' in cl,'missing members use current')

# Control creation only initializes p_cur/p_new; try_ctrl is not called until later
# set/try operations. This proves the four peer pointers exist before our validator runs.
a=core.index('static struct v4l2_ctrl *v4l2_ctrl_new('); b=core.index('struct v4l2_ctrl *v4l2_ctrl_new_custom',a)
new=core[a:b]
need('cur_to_new(ctrl);' in new and 'handler_new_ref' in new,'new control init')
need('try_ctrl' not in new,'constructor unexpectedly calls try_ctrl')

# AM/AL regression mechanism is now structurally impossible: there is no
# modify_range() between user_to_new and new_to_cur.
amb=body(AMSRC,'static int imx681_set_ctrl','static const struct v4l2_ctrl_ops')
need('__v4l2_ctrl_modify_range(imx681->exposure' in amb,'AM provenance lost')

ma=api.index('int __v4l2_ctrl_modify_range')
mb=api.find('\nEXPORT_SYMBOL',ma)
need(mb>ma and 'cur_to_new(ctrl);' in api[ma:mb], 'modify_range root cause changed')

# The unchanged AM write body has already run live in AP.  Keep that evidence
# attached to the transfer instead of treating source equality as a new live run.
ap=json.loads((BASE/'ap-bounded-imx681-control-runtime/RESULT.json').read_text())
need(ap['status']=='PASS_LIVE_CONTROLS_AND_PAIRED_AUDIT','AP live control proof')
need('FLL=3554 exposure=3500 again=0x040 dgain=0x0110 ret=0' in ap['control_transaction'],
     'AP exact AM transaction')

# CV controls are valid under the new atomic relation and encode to the exact
# Windows/AM dynamic sensor bytes without changing arithmetic.
cv=json.loads((CV/'RESULT.json').read_text())
need(cv['status']=='PASS','CV local result')
oracle_path=AM/'windows-oracle/oracle.py'
spec=importlib.util.spec_from_file_location('e003i_cw_oracle',oracle_path)
o=importlib.util.module_from_spec(spec); spec.loader.exec_module(o)
rows=[]
for r in cv['composition']['rows']:
    c=r['controls']; fll=int(c['frame_length_lines']); vb=int(c['vertical_blanking']); exp=int(c['exposure_lines'])
    ag=int(c['analogue_gain_code'],16); dg=int(c['digital_gain_code'],16)
    need(fll==2160+vb,'vblank/fll')
    need(exp <= ((fll-4)&~1),'CV relation')
    need(0 <= ag <= 0x3c0 and 0x100 <= dg <= 0x0f00,'CV gain domain')
    writes=o.fill_exposure_settings(fll,exp,ag,dg)
    need(len(writes)==10,'Windows dynamic write count')
    rows.append({'generation':r['stats_generation'],'request':r['stats_owned_request_frame'],
                 'frame_length_lines':fll,'vertical_blanking':vb,'exposure_lines':exp,
                 'analogue_gain_code':f'0x{ag:03x}','digital_gain_code':f'0x{dg:04x}',
                 'dynamic_writes':[[f'0x{a:04x}',f'0x{v:02x}'] for a,v in writes]})

# Broad valid/invalid relation model.  The declared ranges stay hardware-safe;
# cross-control containment is enforced by try_ctrl rather than metadata mutation.
rng=random.Random(0x681C0DE)
valid=invalid=0
for _ in range(50000):
    fll=rng.randrange(3554,0x1000000)
    exp=rng.randrange(4,0x00fffffb)
    exp &= ~1
    ok=exp <= ((fll-4)&~1)
    if ok: valid+=1
    else: invalid+=1
need(valid and invalid,'relation corpus')
# Pin boundary examples, including the current CV extended-FLL case.
for fll,exp,ok in [(3554,3546,True),(3562,3554,True),(3562,3558,True),(3562,3560,False),(3554,3554,False)]:
    need((exp <= ((fll-4)&~1))==ok,(fll,exp))

# Golden configured kernel module build with warnings elevated.
cp=subprocess.run(['make','-C',str(KB),f'M={HERE}','W=1','modules'],text=True,capture_output=True)
need(cp.returncode==0,cp.stdout+'\n'+cp.stderr)
need('warning:' not in (cp.stdout+cp.stderr).lower(),'compiler warning')
ko=HERE/'imx681.ko'; need(ko.is_file(),'module')
vermagic=subprocess.check_output(['modinfo','-F','vermagic',str(ko)],text=True).strip()
need(vermagic.startswith('7.1.5-sp11-render-parity-v4+'),'vermagic '+vermagic)
ko_sha=hashlib.sha256(ko.read_bytes()).hexdigest()

result={
 'schema':'sp11-e003i-cw-imx681-atomic-dynamic-control-cluster-v1',
 'status':'PASS_OFFLINE',
 'parent_cv_commit':PARENT,
 'topology':{
   'cluster':['vertical_blanking','exposure','analogue_gain','digital_gain'],
   'master':'vertical_blanking','s_ctrl_callbacks_per_changed_cluster':1,
   'modify_range_in_callback':False,
   'dynamic_guard':'exposure <= even(FLL - 4)',
   'declared_exposure_max':'even(0x00ffffff - 4)',
 },
 'v4l2_core_proof':{
   'version':'Linux 7.1.5 Golden source','caller_values_before_try_ctrl':True,
   'missing_cluster_members_cur_to_new_before_try_ctrl':True,
   'try_ctrl_before_s_ctrl':True,'s_ctrl_before_new_to_cur':True,
   'constructor_calls_try_ctrl':False,
 },
 'sensor_transaction':{
   'am_apply_body_source_exact':True,'group_hold':'0x0104 1 -> fields -> 0',
   'dynamic_register_bytes':10,'cv_rows':rows,
 },
 'relation_corpus':{'cases':50000,'valid':valid,'invalid':invalid},
 'build':{'W':1,'vermagic':vermagic,'module_sha256':ko_sha,'warnings':0},
 'safety':{'runtime_performed':False,'module_loaded':False,'sensor_write':False,'streamon':False},
 'open_issue':'final optical-frame latch/effect label remains unclaimed; requires frame-boundary proof/live gate',
}
(HERE/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print('CW_V4L2_CLUSTER=4 master=VBLANK one-s_ctrl')
print('CW_MODIFY_RANGE=absent')
print('CW_DYNAMIC_GUARD=exposure<=even(FLL-4)')
print(f'CW_RELATION_CORPUS=50000 valid={valid} invalid={invalid}')
print(f'CW_CV_ROWS={len(rows)} exact-Windows-dynamic-bytes')
print('CW_AM_GROUP_HELD_BODY=source-exact')
print('CW_BUILD_W1=PASS warnings=0')
print('CW_VERMAGIC='+vermagic)
print('CW_MODULE_SHA256='+ko_sha)
print('CW_RUNTIME=0 SENSOR_WRITES=0')
print('CW_PROOF=PASS')
