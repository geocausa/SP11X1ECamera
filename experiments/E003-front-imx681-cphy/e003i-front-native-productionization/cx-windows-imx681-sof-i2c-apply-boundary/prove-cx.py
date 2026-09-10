#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, subprocess

ROOT=Path(__file__).resolve().parents[4]
SYS=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamfrontsensor8380.inf_arm64_747e2ddb5eb5a22b/surfacecamfrontsensor8380.sys')
SYS_SHA='80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03'
CW=ROOT/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/cw-imx681-atomic-dynamic-control-cluster'
AV=ROOT/'experiments/E003-front-imx681-cphy/e003i-front-native-productionization/av-windows-imx681-sensor-delay'
PUB=[ROOT.parent/'public-reference/imx681-linux-surface/pr164-imx681.c', ROOT.parent/'public-reference/imx681-linux-surface/pr176-imx681.c']

def need(x,msg):
    if not x: raise AssertionError(msg)
def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def dis(a,b):
    return subprocess.check_output(['llvm-objdump','-d',f'--start-address={hex(a)}',f'--stop-address={hex(b)}',str(SYS)],text=True)

need(SYS.is_file() and sh(SYS)==SYS_SHA,'front KMD SHA')
# NotifySOF stores request/subrequest/hdrMode at +430/+438/+440.
sof=dis(0x1400058ac,0x140005920)
for s in ['stp\tx23, x22, [x8]','str\tw20, [x19, #0x440]']:
    need(s in sof,s)
# Exact ordinary hdrMode=1 queue selection: queued req - current SOF == 1.
sel=dis(0x140008350,0x140008510)
for s in [
    'ldr\tx12, [x8]', 'ldp\tw10, w11, [x9, #0xc]', 'sub\tx8, x10, x12',
    'cmp\tx8, #0x1', 'ldr\tw8, [x19, #0x440]', 'cmp\tw8, #0x1',
    'ldr\tx1, [sp]', 'add\tx0, x19, #0x28', 'bl\t0x140009860'
]: need(s in sel,s)
# Selected packet is synchronously walked as register/data pairs.
walk=dis(0x140009860,0x140009a70)
for s in [
    'ldrh\tw1, [x20, #0xc]', 'ldrh\tw0, [x20, #0x8]', 'bl\t0x14000abc8',
    'cmp\tw19, w8', 'b.lt\t0x140009998'
]: need(s in walk,s)
# Low-level single-register helper builds request and calls the transport wrapper before returning.
submit=dis(0x14000abc8,0x14000ad60)
need('bl\t0x14000b7a8' in submit,'I2C request submit call')
transport=dis(0x14000b7a8,0x14000b7e8)
need('bl\t0x140003aa0' in transport,'transport callback wrapper')
callback=dis(0x140003aa0,0x140003b24)
for s in ['blr\tx17','blr\tx15','ret']:
    need(s in callback,s)
# Exact diagnostic strings name the queue record and consumed request coordinate.
raw=SYS.read_bytes()
for s in [
 b'CameraSensorDriver_ProcessExposureUpdate() DeQueued exp update buffer in AsyncThread',
 b'SensorLastConsumedReqId:%d sensorLastConsumedSubReqId:%d after applying exposure update',
 b'CameraSensorDriver_NotifySOF() Setting SOF signal for Req ID: %d, SubRequest ID:%d and hdrMode:%d',
 b'CameraSensorDriver_SubmitI2CCmd() i2cCmd[%d] = (0x%x, 0x%x)'
]: need(s in raw,s.decode(errors='ignore'))
# Linux-side atomic group-hold transport is already closed by CW.
cw=(CW/'RESULT.json')
need(cw.is_file(),'CW RESULT')
cwj=json.loads(cw.read_text())
need(cwj.get('status')=='PASS_OFFLINE','CW status')
src=(CW/'imx681.c').read_text()
need('CCI_REG8(0x0104)' in src and 'v4l2_ctrl_cluster(4, &imx681->vblank);' in src,'CW group-hold cluster')
a=src.index('cci_write(imx681->cci, IMX681_REG_GROUP_HOLD, 1, &ret);')
b=src.index('cci_write(imx681->cci, IMX681_REG_FRAME_LENGTH, frame_length, &ret);')
c=src.index('cci_write(imx681->cci, IMX681_REG_GROUP_HOLD, 0, NULL);')
need(a < b < c,'CW hold order')
# AV keeps maxPipeline=2 separate from optical latch labeling.
av=(AV/'README.md').read_text()
need('two-frame sensor application pipeline' in av and 'final optical-frame label/latch statement is intentionally kept separate' in av,'AV bounded timing claim')
# Independent IMX681 Linux sources corroborate 0x0104 as group parameter hold, but do not define frame visibility.
for p in PUB:
    t=p.read_text()
    need('CCI_REG8(0x0104)' in t and 'Group hold ON' in t and 'Group hold OFF' in t,p.name)

out={
 'schema':'sp11-e003i-cx-windows-imx681-sof-i2c-apply-boundary-v1',
 'status':'PASS',
 'frontsensor_sys_sha256':SYS_SHA,
 'windows':{
  'notify_sof_state':{'request':'+0x430','subrequest':'+0x438','hdr_mode':'+0x440'},
  'hdrmode1_selection_law':'queued_request - current_SOF_request == 1',
  'packet_apply_coordinate':'packet F selected while current SOF request is F-1',
  'selected_apply_call':'0x140008488 -> 0x140009860',
  'register_pair_submit':'0x1400099b4/0x1400099b8 -> 0x14000abc8',
  'transport_call_chain':'0x14000abc8 -> 0x14000b7a8 -> 0x140003aa0 -> callback -> return',
  'consumed_bookkeeping':'after selected packet apply path'
 },
 'linux_cw':{'group_hold_register':'0x0104','cluster_controls':4,'one_s_ctrl_transaction':True},
 'optical_frame_label_claimed':False,
 'open_issue':'sensor-side group-hold release to first optically affected frame remains unproven'
}
(Path(__file__).with_name('RESULT.json')).write_text(json.dumps(out,indent=2)+'\n')
print('CX_KMD_SHA256='+SYS_SHA)
print('CX_WINDOWS_SELECT=packet_F_at_SOF_F_minus_1')
print('CX_SELECTED_PACKET_WALK=register_pairs_to_I2C_submit_sync')
print('CX_LINUX_GROUP_HOLD=0x0104_atomic_CW')
print('CX_OPTICAL_FRAME_CLAIMED=0')
print('CX_RUNTIME=0 SENSOR_WRITES=0')
print('CX_PROOF=PASS')
