#!/usr/bin/env python3
import csv, hashlib, json, re
from pathlib import Path

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
DMESG=HERE/'RUNTIME-CSID1-0042-DMESG.txt'
RUN=HERE/'RUNTIME-CSID1-0042-RUN.txt'
POST=HERE/'RUNTIME-CSID1-0042-POST.txt'
STAGES=HERE/'RUNTIME-CSID1-0042-RTCDM-STAGES.txt'
ROUTE=REPO/'experiments/E003-front-imx681-cphy/e003g-windows-csid-vfe-oracle/csid1-route-live-nonzero.csv'
OUT=HERE/'runtime-0042-analysis.json'
EXPECTED={
 'dmesg':'32b2236f38977564936e9f69942c5892008375a45e3e87328eec2ca50538d201',
 'run':'7278407c3dddacec05a3deb1acb1f8258680109e5ed40ef85aef76810eab7db8',
 'post':'d53c198e9b856f00735eb01b5220aff0c26f67595733eeadd46f416ab1f97f58',
 'stages':'3371d2b9645223c4de47cdd54d4dc3939c75a5d43532b1586475ef7944a28e8e',
 'route':'95e26dd7d116fdc48b7281a153222a7b4edd11294703b555d81e25c2251b1238',
}
IRQ={
 2:'ERROR_FIFO_OVERFLOW',3:'CAMIF_EOF',4:'CAMIF_SOF',5:'FRAME_DROP_EOF',6:'FRAME_DROP_EOL',7:'FRAME_DROP_SOL',8:'FRAME_DROP_SOF',
 9:'INFO_INPUT_EOF',10:'INFO_INPUT_EOL',11:'INFO_INPUT_SOL',12:'INFO_INPUT_SOF',13:'ERROR_PIX_COUNT',14:'ERROR_LINE_COUNT',15:'VCDT_GRP0_SEL',
 16:'VCDT_GRP1_SEL',17:'VCDT_GRP_CHANGE',18:'FRAME_DROP',19:'OVERFLOW_RECOVERY',20:'ERROR_REC_CCIF_VIOLATION',21:'CAMIF_EPOCH0',
 22:'CAMIF_EPOCH1',23:'RUP_DONE',24:'ILLEGAL_BATCH_ID',25:'BATCH_END_MISSING_VIOLATION',26:'HEIGHT_VIOLATION',27:'WIDTH_VIOLATION',
 28:'SENSOR_SWITCH_OUT_OF_SYNC_FRAME_DROP',29:'CCIF_VIOLATION',
}
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
for k,p in [('dmesg',DMESG),('run',RUN),('post',POST),('stages',STAGES),('route',ROUTE)]:
 if sha(p)!=EXPECTED[k]: die(f'{k} identity drift')
run=RUN.read_text(); post=POST.read_text(); dmesg=DMESG.read_text(); stages=STAGES.read_text()
if 'HELPER_INVOCATION_COUNT=1' not in run or 'RUN_RC=1' not in run or 'Connection timed out' not in run: die('run contract/result drift')
if 'QC10C_OUTPUT=absent' not in post or 'SENSOR_PM=suspended' not in post or 'CAMSS_PM=suspended' not in post: die('post state drift')
if 'fifo_seq=13' not in stages or 'faulted=0' not in stages or 'name=stopped' not in stages: die('RT-CDM terminal state drift')
patterns={
 'route':r'E003h CSID1 epoch0-timeout route=([0-9a-f]{8}) regupd=([0-9a-f]{8}) top=([0-9a-f]{8})/([0-9a-f]{8}) buf=([0-9a-f]{8})/([0-9a-f]{8})',
 'rx':r'E003h CSID1 epoch0-timeout rx=([0-9a-f]{8})/([0-9a-f]{8}) cfg=([0-9a-f]{8})/([0-9a-f]{8}) pkts=([0-9a-f]{8}) ecc=([0-9a-f]{8}) crc=([0-9a-f]{8})',
 'ipp':r'E003h CSID1 epoch0-timeout ipp=([0-9a-f]{8})/([0-9a-f]{8}) ctrl=([0-9a-f]{8}) cfg=([0-9a-f]{8})/([0-9a-f]{8}) z324=([0-9a-f]{8}) z330=([0-9a-f]{8}) epoch=([0-9a-f]{8})',
 'tail':r'E003h CSID1 epoch0-timeout crop=([0-9a-f]{8})/([0-9a-f]{8}) drop=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8}) measure=([0-9a-f]{8})/([0-9a-f]{8}) obs=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})',
}
vals={}
for k,pat in patterns.items():
 m=re.search(pat,dmesg,re.I)
 if not m: die('missing '+k+' telemetry')
 vals[k]=[int(x,16) for x in m.groups()]
route,regupd,top_s,top_m,buf_s,buf_m=vals['route']
rx_s,rx_m,rx0,rx1,pkts,ecc,crc=vals['rx']
ipp_s,ipp_m,ctrl,cfg0,cfg1,z324,z330,epoch=vals['ipp']
hc,vc,*tail=vals['tail']
drop=tail[:6]; meas0,meas1,obs340,obs398,obs39c=tail[6:]
# Exact Windows live values from the accepted same-machine route CSV.
win={}
with ROUTE.open() as f:
 for r in csv.DictReader(f):
  off=int(r['offset'],16)
  if off in (0x80,0x8c,0x90,0x9c,0xa0,0xac,0xb0,0x200,0x204,0x300,0x304,0x310,0x334,0x35c,0x360,0x368,0x370,0x378,0x37c,0x384,0x388,0x340,0x39c):
   win[off]=int(r['live1'],16)
expected_cfg={0x80:top_m,0x90:buf_m,0xa0:rx_m,0xb0:ipp_m,0x200:rx0,0x204:rx1,0x300:cfg0,0x304:ctrl,0x310:cfg1,0x334:epoch,0x35c:hc,0x360:vc,0x368:drop[1],0x370:drop[3],0x378:drop[5],0x37c:1,0x384:meas0,0x388:meas1,0x340:obs340,0x39c:obs39c}
for off,lv in expected_cfg.items():
 if off in win and win[off]!=lv: die(f'Linux config/readback +0x{off:x} differs from Windows: {lv:08x}!={win[off]:08x}')
if (z324,z330)!=(0,0): die('proven zero write drift')
if (ecc,crc)!=(0,0) or pkts==0: die('CSI RX not clean')
def bits(v): return [b for b in range(32) if v & (1<<b)]
def names(v): return [IRQ.get(b,f'BIT{b}') for b in bits(v)]
win_ipp=win[0xac]
missing=win_ipp & ~ipp_s
linux_only=ipp_s & ~win_ipp
critical=['CAMIF_SOF','CAMIF_EOF','CAMIF_EPOCH0','CAMIF_EPOCH1','RUP_DONE']
for name in critical:
 b=next(k for k,v in IRQ.items() if v==name)
 if ipp_s & (1<<b): die(name+' unexpectedly present in Linux timeout status')
 if not (win_ipp & (1<<b)): die(name+' unexpectedly absent from Windows live status')
errors={2,13,14,19,20,24,25,26,27,28,29}
if any(ipp_s&(1<<b) for b in errors): die('Linux IPP status contains error bit')
analysis={
 'schema':'sp11-e003h-csid1-0042-runtime-analysis-v1','accepted':True,
 'source_hashes':EXPECTED,
 'run':{'helper_invocations':1,'run_rc':1,'trigger_errno_text':'Connection timed out','qc10c_output':False,'same_boot_retry':False},
 'rtcdm':{'fifo0_completions':13,'faulted':False,'terminal_stage':'stopped'},
 'sensor':{'mode_select_on_seen':True,'mode_select_off_seen':True},
 'linux_csid1':{
  'route':f'0x{route:08x}','reg_update_readback':f'0x{regupd:08x}','rx_irq_status':f'0x{rx_s:08x}','rx_irq_mask':f'0x{rx_m:08x}',
  'rx_cfg0':f'0x{rx0:08x}','rx_cfg1':f'0x{rx1:08x}','rx_packets':pkts,'ecc_errors':ecc,'crc_errors':crc,
  'ipp_irq_status':f'0x{ipp_s:08x}','ipp_irq_bits':names(ipp_s),'ipp_irq_mask':f'0x{ipp_m:08x}','ipp_ctrl':f'0x{ctrl:08x}',
  'ipp_cfg0':f'0x{cfg0:08x}','ipp_cfg1':f'0x{cfg1:08x}','epoch_cfg':f'0x{epoch:08x}','obs_0x340':f'0x{obs340:08x}',
 },
 'windows_live_comparison':{
  'ipp_irq_status':f'0x{win_ipp:08x}','ipp_irq_bits':names(win_ipp),'buf_done_status':f'0x{win[0x8c]:08x}',
  'missing_from_linux_status':f'0x{missing:08x}','missing_bits':names(missing),'linux_only_status':f'0x{linux_only:08x}',
  'critical_missing':['CAMIF_EOF','CAMIF_SOF','CAMIF_EPOCH0','CAMIF_EPOCH1','RUP_DONE'],
 },
 'classification':{
  'sensor_to_csid_rx_clean':True,'complete_input_frame_boundaries_seen':True,'ipp_config_and_enable_windows_matched':True,
  'csid_camif_output_events_seen':False,'csid_epoch_events_seen':False,'csid_rup_done_seen':False,'vfe1_epoch0_seen':False,
  'failure_boundary':'after clean CSI packet/input-frame ingress and before CSID CAMIF/RUP/Epoch output progression into VFE1',
 },
 'public_register_reference':{
  'repo':'https://github.com/qualcomm-linux/camera-driver','commit':'0f16924ff6a7f9bb56a7e958016da2ed8a174f2f',
  'file':'camera/drivers/cam_isp/isp_hw_mgr/isp_hw/ife_csid_hw/cam_ife_csid680.h',
  'ipp_rup_aup_mask':'0x00010001','rup_aup_cmd_offset':'0x018',
  'evidence_class':'LINUX_IMPLEMENTATION/reference only; not yet Windows behavioral proof',
 },
 'next_gate':'Recover exact same-machine Windows CSID1 RUP/AUP command value and ordering; do not authorize another Linux runtime before this is closed.'
}
OUT.write_text(json.dumps(analysis,indent=2)+'\n')
print(json.dumps(analysis,indent=2))
