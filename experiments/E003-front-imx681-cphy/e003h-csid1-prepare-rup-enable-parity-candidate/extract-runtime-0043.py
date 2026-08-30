#!/usr/bin/env python3
import hashlib, json, re
from pathlib import Path
HERE=Path(__file__).resolve().parent
OLD=HERE.parent/'e003h-csid1-ipp-start-parity-candidate'
FILES={
 'run': HERE/'RUNTIME-CSID1-0043-RUN.txt',
 'post': HERE/'RUNTIME-CSID1-0043-POST.txt',
 'dmesg': HERE/'RUNTIME-CSID1-0043-DMESG.txt',
 'stages': HERE/'RUNTIME-CSID1-0043-RTCDM-STAGES.txt',
 'load': HERE/'RUNTIME-CSID1-0043-LOAD.txt',
}
EXPECTED={
 'run':'994b21d07481a3590ddefebcc10cb4c13940a245b555c1956dba361a6fa21ac6',
 'post':'fb0095beb35193f941c902e7adf9727781bdf5c3f24d618f7f7227f26e2e26b7',
 'dmesg':'ab2f5df944dd60a8be716eb52703ba46f654386fa65c2f1308811d7ee5403abd',
 'stages':'800ac8fd8ef054491b02416561ca14109c744f7155d74ef711017f7763743248',
 'load':'2a7f156b464f370ef8a03efc222972110eea1ab6955faee0c05594130a21227b',
}
OLD_ANALYSIS=OLD/'runtime-0042-analysis.json'
OLD_ANALYSIS_SHA='83e6945ca44402e6aaea1974cedc52d9f843216c08e69a6da02e389181f9df8c'

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
for k,p in FILES.items():
    if sha(p)!=EXPECTED[k]: die(f'{k} hash drift')
if sha(OLD_ANALYSIS)!=OLD_ANALYSIS_SHA: die('0042 analysis drift')
run=FILES['run'].read_text(); post=FILES['post'].read_text(); dmesg=FILES['dmesg'].read_text(); stages=FILES['stages'].read_text()
for needle in ('HELPER_INVOCATION_COUNT=1','RUN_RC=1','Connection timed out'):
    if needle not in run: die('run contract drift: '+needle)
for needle in ('QC10C_OUTPUT=absent','SENSOR_PM=suspended','CAMSS_PM=suspended','fifo_seq=13','faulted=0'):
    if needle not in post+stages: die('post/stage drift: '+needle)
if dmesg.count('MODE_SELECT=1 front transmission started') != 1: die('sensor-on count drift')
if dmesg.count('MODE_SELECT=0 front transmission stopped') != 1: die('sensor-off count drift')
pat={
 'route': r'E003h CSID1 epoch0-timeout route=([0-9a-f]{8}) regupd=([0-9a-f]{8}) top=([0-9a-f]{8})/([0-9a-f]{8}) buf=([0-9a-f]{8})/([0-9a-f]{8})',
 'rx': r'E003h CSID1 epoch0-timeout rx=([0-9a-f]{8})/([0-9a-f]{8}) cfg=([0-9a-f]{8})/([0-9a-f]{8}) pkts=([0-9a-f]{8}) ecc=([0-9a-f]{8}) crc=([0-9a-f]{8})',
 'ipp': r'E003h CSID1 epoch0-timeout ipp=([0-9a-f]{8})/([0-9a-f]{8}) ctrl=([0-9a-f]{8}) cfg=([0-9a-f]{8})/([0-9a-f]{8}) z324=([0-9a-f]{8}) z330=([0-9a-f]{8}) epoch=([0-9a-f]{8})',
 'tail': r'E003h CSID1 epoch0-timeout crop=([0-9a-f]{8})/([0-9a-f]{8}) drop=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8}) measure=([0-9a-f]{8})/([0-9a-f]{8}) obs=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})',
}
v={}
for k,p in pat.items():
    m=re.search(p,dmesg,re.I)
    if not m: die('missing telemetry '+k)
    v[k]=[int(x,16) for x in m.groups()]
route,regupd,top_s,top_m,buf_s,buf_m=v['route']
rx_s,rx_m,rx0,rx1,pkts,ecc,crc=v['rx']
ipp_s,ipp_m,ctrl,cfg0,cfg1,z324,z330,epoch=v['ipp']
hc,vc,*tail=v['tail']; drop=tail[:6]; meas0,meas1,obs340,obs398,obs39c=tail[6:]
expected_exact={
 'route':0x00000101,'regupd':0,'top_status':0,'top_mask':1,'buf_status':0,'buf_mask':1,
 'rx_status':0x17,'rx_mask':0x019fb800,'rx0':0x11300000,'rx1':1,'packets':37016,'ecc':0,'crc':0,
 'ipp_status':0x00011e00,'ipp_mask':0x3cbc601c,'ctrl':1,'cfg0':0x802b2000,'cfg1':0x00007241,
 'z324':0,'z330':0,'epoch':0x00130013,'hc':0x0eff0000,'vc':0x086f0000,
 'meas0':0x1f,'meas1':0x08700f00,'obs340':0x48000a08,
}
actual={'route':route,'regupd':regupd,'top_status':top_s,'top_mask':top_m,'buf_status':buf_s,'buf_mask':buf_m,
'rx_status':rx_s,'rx_mask':rx_m,'rx0':rx0,'rx1':rx1,'packets':pkts,'ecc':ecc,'crc':crc,
'ipp_status':ipp_s,'ipp_mask':ipp_m,'ctrl':ctrl,'cfg0':cfg0,'cfg1':cfg1,'z324':z324,'z330':z330,'epoch':epoch,
'hc':hc,'vc':vc,'meas0':meas0,'meas1':meas1,'obs340':obs340}
for k,x in expected_exact.items():
    if actual[k]!=x: die(f'{k} differs from expected repeated boundary: {actual[k]:x}!={x:x}')
old=json.loads(OLD_ANALYSIS.read_text())
oldc=old['linux_csid1']
comparison={
 'rx_packets_identical': pkts==oldc['rx_packets'],
 'rx_irq_status_identical': f'0x{rx_s:08x}'==oldc['rx_irq_status'],
 'ipp_irq_status_identical': f'0x{ipp_s:08x}'==oldc['ipp_irq_status'],
 'ipp_irq_mask_identical': f'0x{ipp_m:08x}'==oldc['ipp_irq_mask'],
 'ipp_cfg_identical': f'0x{cfg0:08x}'==oldc['ipp_cfg0'] and f'0x{cfg1:08x}'==oldc['ipp_cfg1'],
 'epoch_cfg_identical': f'0x{epoch:08x}'==oldc['epoch_cfg'],
 'obs_0x340_identical': f'0x{obs340:08x}'==oldc['obs_0x340'],
}
if not all(comparison.values()): die('0043 no longer reproduces the 0042 boundary exactly')
warning='WARNING: drivers/media/v4l2-core/v4l2-subdev.c:484 at call_s_stream' in dmesg
if not warning: die('expected teardown lifecycle warning missing')
out={
 'schema':'sp11-e003h-csid1-0043-runtime-analysis-v1','accepted':True,
 'source_hashes':EXPECTED,'0042_analysis_sha256':OLD_ANALYSIS_SHA,
 'run':{'helper_invocations':1,'run_rc':1,'trigger_errno_text':'Connection timed out','qc10c_output':False,'same_boot_retry':False},
 'rtcdm':{'fifo0_completions':13,'faulted':False,'terminal_stage':'stopped'},
 'sensor':{'mode_select_on_seen':True,'mode_select_off_seen':True},
 'linux_csid1':{
  'route':f'0x{route:08x}','reg_update_readback':f'0x{regupd:08x}','rx_irq_status':f'0x{rx_s:08x}','rx_irq_mask':f'0x{rx_m:08x}',
  'rx_cfg0':f'0x{rx0:08x}','rx_cfg1':f'0x{rx1:08x}','rx_packets':pkts,'ecc_errors':ecc,'crc_errors':crc,
  'ipp_irq_status':f'0x{ipp_s:08x}','ipp_irq_mask':f'0x{ipp_m:08x}','ipp_ctrl':f'0x{ctrl:08x}',
  'ipp_cfg0':f'0x{cfg0:08x}','ipp_cfg1':f'0x{cfg1:08x}','epoch_cfg':f'0x{epoch:08x}','obs_0x340':f'0x{obs340:08x}',
 },
 'comparison_to_0042':comparison,
 'classification':{
  '0043_prepare_rup_enable_order_changed_hardware_boundary':False,
  'failure_boundary':'identical to 0042: after clean CSI packet/input-frame ingress and before CSID CAMIF/RUP/Epoch output progression into VFE1',
  'simple_shadow_stage_order_hypothesis_closed':True,
  'wrong_rtcdm_target_not_implied_by_this_run':True,
 },
 'teardown':{
  'sensor_suspended':True,'camss_suspended':True,'v4l2_call_s_stream_warning_seen':True,
  'warning_occurs_after_epoch0_timeout':True,
  'warning_is_not_accepted_as_failure_cause':True,
  'next_static_cleanup':'fix prepared-state rollback bookkeeping before any future runtime candidate',
 },
 'runtime_authorized':False,
 'next_gate':'No repeat runtime. Enumerate every exact Windows CSID1 common/path configure write and lifecycle prerequisite, compare against Linux prepare, and separately fix teardown bookkeeping. Only a proven static delta can reopen runtime authorization.'
}
(HERE/'runtime-0043-analysis.json').write_text(json.dumps(out,indent=2)+'\n')
print(json.dumps(out,indent=2))
