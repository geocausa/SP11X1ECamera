#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re, subprocess, tempfile
ROOT=Path(__file__).resolve().parents[4]
D=Path(__file__).resolve().parent
BASE=ROOT/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization'
CW=BASE/'cw-imx681-atomic-dynamic-control-cluster'
AP=BASE/'ap-bounded-imx681-control-runtime'
H=D/'e003i-cy-six-frame-latch.c'

def need(x,m):
    if not x: raise AssertionError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
need(subprocess.check_output(['git','-C',str(ROOT),'rev-parse','--abbrev-ref','HEAD'],text=True).strip()=='experiment/e003-front-imx681-cphy','branch')
need(json.loads((CW/'RESULT.json').read_text())['status']=='PASS_OFFLINE','CW parent')
ap=json.loads((AP/'RESULT.json').read_text())
need(ap.get('status')=='PASS_LIVE_CONTROLS_AND_PAIRED_AUDIT','AP tracked status')
need(ap.get('golden_return')=='PASS','AP tracked Golden return')
need(ap.get('same_boot_retry_performed') is False,'AP no same-boot retry')
s=H.read_text()
for x in ['CY_STEP_EXPOSURE 1000','CY_BASE_VBLANK 1394','CY_FIXED_AGAIN 64','CY_FIXED_DGAIN 272','if (i == 0)','set_sensor_step(sfd)','VIDIOC_S_EXT_CTRLS']:
    need(x in s,x)
need(s.count('set_sensor_step(sfd)')==1,'one live step call')
need('if (target == 2)' in s and 'atomic_load_explicit(&cy_step_done, memory_order_acquire)' in s,'G2 waits for completed control step')
need(s.count('atomic_store_explicit(&cy_step_done, 1, memory_order_release)')==1,'one step-done publication')
need('V4L2_CID_VBLANK' in s and 'V4L2_CID_EXPOSURE' in s and 'V4L2_CID_ANALOGUE_GAIN' in s and 'V4L2_CID_DIGITAL_GAIN' in s,'four controls')
need(1000 <= ((2160+1394-4)&~1),'step relation')
with tempfile.TemporaryDirectory() as td:
    out=Path(td)/'cy'
    subprocess.run(['gcc','-O2','-std=c11','-Wall','-Wextra','-Werror','-pthread',str(H),'-o',str(out)],check=True)
entry=(D/'99zh_sp11_camera_e003i_cy_latch').read_text()
for x in ['sp11-camera-e003i-cy-latch-one-shot','sp11_camera_e003i_cy_latch=1','modprobe.blacklist=qcom_camss,imx681,ov13858']:
    need(x in entry,x)
print('CY_PARENT_CW=b767514')
print('CY_BASELINE=FLL3554_EXP3500_AGAIN64_DGAIN272')
print('CY_STEP=after_DQBUF0_FLL3554_EXP1000_AGAIN64_DGAIN272')
print('CY_HELPER_WERROR=PASS')
print('CY_ONE_SHOT_UNARMED=1')
print('CY_VERIFY=PASS')
