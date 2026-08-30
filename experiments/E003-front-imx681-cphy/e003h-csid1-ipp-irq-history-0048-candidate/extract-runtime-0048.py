#!/usr/bin/env python3
import hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
STATIC=HERE.parent/'e003h-windows-parity-transport-static'
FILES={
 'run':HERE/'RUNTIME-CSIDIRQ-0048-RUN.txt',
 'post':HERE/'RUNTIME-CSIDIRQ-0048-POST.txt',
 'dmesg':HERE/'RUNTIME-CSIDIRQ-0048-DMESG.txt',
 'stages':HERE/'RUNTIME-CSIDIRQ-0048-RTCDM-STAGES.txt',
 'golden':HERE/'RUNTIME-CSIDIRQ-0048-GOLDEN-RETURN.txt',
 'auth':HERE/'AUTHORIZATION.json',
 'package':HERE/'package-inspection.json',
 'observer':STATIC/'windows-linux-irq-observer-integrity/irq-observer-integrity-oracle.json',
 'linux_static':STATIC/'linux-0048-csid1-ipp-irq-history-inspection.json',
}
EXPECTED={
 'run':'0aa806d4274c589e68abf0ca97976cdd215ba6a3b13de05977634ccb79a522c5',
 'post':'4ecbf70abb7d82c5700bb800393eaf244a43f9ad8bde93b1098dafeac67613f6',
 'dmesg':'1c6aac0f80bb3bd6e43dd8d0238973d6403e537f8c83191edd09f0abd17afbf8',
 'stages':'2c5a23faf00439f566843e4358e2e6b9c204359fc3c875f207cdbcd8258379fa',
 'golden':'3353e34bd4f8fdcb9e9c06213d55fc541db006fc91f6f179008732b5480967f7',
 'auth':'f76ca42c08493a321bd482f2c9a4389186b071ea3e6e06a9325e41548e7c1b8a',
 'package':'b4f03e0775da5deaf03fd29196c57e0781f256261ccd12d40af86b4460e339cd',
 'observer':'23bc970a9bacff901e1336208282904cb9c0add0dfd5bea311194caeacb5451d',
 'linux_static':'6e98360aa0a83c8c61db1e67bd5c12f4fb6c7856698f48aea404a23100de8eb2',
}
IRQ={
 2:'ERROR_FIFO_OVERFLOW',3:'CAMIF_EOF',4:'CAMIF_SOF',5:'FRAME_DROP_EOF',6:'FRAME_DROP_EOL',7:'FRAME_DROP_SOL',8:'FRAME_DROP_SOF',
 9:'INFO_INPUT_EOF',10:'INFO_INPUT_EOL',11:'INFO_INPUT_SOL',12:'INFO_INPUT_SOF',13:'ERROR_PIX_COUNT',14:'ERROR_LINE_COUNT',15:'VCDT_GRP0_SEL',
 16:'VCDT_GRP1_SEL',17:'VCDT_GRP_CHANGE',18:'FRAME_DROP',19:'OVERFLOW_RECOVERY',20:'ERROR_REC_CCIF_VIOLATION',21:'CAMIF_EPOCH0',
 22:'CAMIF_EPOCH1',23:'RUP_DONE',24:'ILLEGAL_BATCH_ID',25:'BATCH_END_MISSING_VIOLATION',26:'HEIGHT_VIOLATION',27:'WIDTH_VIOLATION',
 28:'SENSOR_SWITCH_OUT_OF_SYNC_FRAME_DROP',29:'CCIF_VIOLATION',
}
WINDOWS_LIVE=0x00e11ff8
CRITICAL=(3,4,21,22,23)

def sha(path): return hashlib.sha256(path.read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def bits(v): return [b for b in range(32) if v & (1<<b)]
def names(v): return [IRQ.get(b,f'BIT{b}') for b in bits(v)]
def need(txt,s,label):
 if s not in txt: die(f'{label}: missing {s!r}')
def match(txt,pat,label):
 m=re.search(pat,txt,re.I)
 if not m: die('missing '+label)
 return m.groups()

def main():
 for k,path in FILES.items():
  if not path.is_file(): die('missing '+str(path))
  got=sha(path)
  if got!=EXPECTED[k]: die(f'{k} identity drift {got} != {EXPECTED[k]}')
 run=FILES['run'].read_text(errors='replace'); post=FILES['post'].read_text(errors='replace')
 dm=FILES['dmesg'].read_text(errors='replace'); stages=FILES['stages'].read_text(errors='replace'); golden=FILES['golden'].read_text(errors='replace')
 for s in ('HELPER_INVOCATION_COUNT=1','RUN_RC=1','write trigger: Connection timed out'): need(run,s,'run')
 for s in ('RUN_RC=1','QC10C_OUTPUT=absent','SENSOR_PM=suspended','CAMSS_PM=suspended','fifo_seq=17','faulted=0','name=stopped'): need(post,s,'post')
 for s in ('fifo_seq=17','faulted=0','name=stopped'): need(stages,s,'stages')
 for bad in ('BUG:','Oops:','Kernel panic','SError Interrupt','Unhandled fault'):
  if bad in dm: die('kernel fault marker '+bad)
 for s in ('MODE_SELECT=1 front transmission started','MODE_SELECT=0 front transmission stopped'): need(dm,s,'sensor lifecycle')
 for s in ('KERNEL=7.1.5-sp11-render-parity-v4+','BOOT_IMAGE=/boot/sp11-7.1.5-audio-fullio-v19c/','saved_entry=sp11-audio-fullio-v19c','next_entry=','qcom_camss=absent','imx681=absent','ov13858=absent','HEAD=7a1659e874064d5c23b6d67a274c8d1241e013f1','ORIGIN=7a1659e874064d5c23b6d67a274c8d1241e013f1'): need(golden,s,'golden')
 top=match(dm,r'E003h VFE1 epoch0-timeout top=([0-9a-f]{8})/([0-9a-f]{8}) mask=([0-9a-f]{8})/([0-9a-f]{8}) bus=([0-9a-f]{8})/([0-9a-f]{8}) bmask=([0-9a-f]{8})/([0-9a-f]{8})','VFE top/bus')
 if top!=('00000000','00030003','0007f051','00000000','00000000','00000000','d0000000','00000000'): die('VFE boundary drift '+repr(top))
 route=match(dm,r'E003h CSID1 epoch0-timeout route=([0-9a-f]{8}) regupd=([0-9a-f]{8}) top=([0-9a-f]{8})/([0-9a-f]{8}) buf=([0-9a-f]{8})/([0-9a-f]{8})','CSID route')
 rx=match(dm,r'E003h CSID1 epoch0-timeout rx=([0-9a-f]{8})/([0-9a-f]{8}) cfg=([0-9a-f]{8})/([0-9a-f]{8}) pkts=([0-9a-f]{8}) ecc=([0-9a-f]{8}) crc=([0-9a-f]{8})','CSID rx')
 ipp=match(dm,r'E003h CSID1 epoch0-timeout ipp=([0-9a-f]{8})/([0-9a-f]{8}) ctrl=([0-9a-f]{8}) cfg=([0-9a-f]{8})/([0-9a-f]{8}) z324=([0-9a-f]{8}) z330=([0-9a-f]{8}) epoch=([0-9a-f]{8})','CSID ipp')
 hist=match(dm,r'E003h CSID1 epoch0-timeout ipp-history=([0-9a-f]{8})/([0-9a-f]{8})/([0-9]+)','CSID ipp history')
 if route!=('00000101','00000000','00000000','00000001','00000000','0001ffff'): die('CSID route/mask drift '+repr(route))
 if rx[4:]!=('00009098','00000000','00000000'): die('CSID ingress not clean '+repr(rx))
 if ipp[:5]!=('00011e00','3cbc601c','00000001','802b2000','00007241'): die('CSID final IPP config drift '+repr(ipp))
 seen=int(hist[0],16); last=int(hist[1],16); count=int(hist[2])
 if (seen,last,count)!=(0x00e15ff8,0x00004ee8,4): die(f'IRQ history drift {seen:08x}/{last:08x}/{count}')
 for bit in CRITICAL:
  if not (seen & (1<<bit)): die('critical history bit absent: '+IRQ[bit])
 win_missing=WINDOWS_LIVE & ~seen
 linux_extra=seen & ~WINDOWS_LIVE
 if win_missing: die(f'Linux history missing Windows-live bit(s): 0x{win_missing:08x}')
 if linux_extra!=0x00004000: die(f'unexpected Linux-vs-Windows history delta 0x{linux_extra:08x}')
 if names(linux_extra)!=['ERROR_LINE_COUNT']: die('bit14 decode drift')
 out={
  'schema':'sp11-e003h-csid1-ipp-irq-history-0048-runtime-result-v1','accepted':True,'date':'2026-08-30',
  'authorization_consumed':True,'helper_invocations':1,'same_boot_retry':False,'run_rc':1,'qc10c_output':False,'golden_return_verified':True,
  'evidence_sha256':EXPECTED,
  'rtcdm':{'fifo_bl_completed':17,'faulted':False,'final_stage':'stopped'},
  'sensor':{'mode_select_on_seen':True,'mode_select_off_seen':True,'clean_csi_packets':int(rx[4],16),'ecc_errors':0,'crc_errors':0},
  'vfe1_timeout':{'top_status0':'0x'+top[0],'top_status1':'0x'+top[1],'top_mask0':'0x'+top[2],'top_mask1':'0x'+top[3],'bus_status0':'0x'+top[4],'bus_status1':'0x'+top[5],'bus_mask0':'0x'+top[6],'bus_mask1':'0x'+top[7],'raw_epoch0_seen':bool(int(top[5],16)&(1<<21))},
  'csid1':{
   'final_ipp_status':'0x'+ipp[0],'final_ipp_status_bits':names(int(ipp[0],16)),'ipp_mask':'0x'+ipp[1],
   'irq_history_or':f'0x{seen:08x}','irq_history_or_bits':names(seen),'irq_history_last':f'0x{last:08x}','irq_history_last_bits':names(last),'irq_history_count':count,
   'camif_sof_seen':bool(seen&(1<<4)),'camif_eof_seen':bool(seen&(1<<3)),'camif_epoch0_seen':bool(seen&(1<<21)),'camif_epoch1_seen':bool(seen&(1<<22)),'rup_done_seen':bool(seen&(1<<23)),
   'line_count_error_seen':bool(seen&(1<<14)),
  },
  'windows_live_comparison':{
   'accepted_windows_live_ipp_status':f'0x{WINDOWS_LIVE:08x}','accepted_windows_live_bits':names(WINDOWS_LIVE),
   'linux_history_missing_windows_live':f'0x{win_missing:08x}','linux_history_extra_vs_windows_live':f'0x{linux_extra:08x}','linux_history_extra_bits':names(linux_extra),
  },
  'supersedes':{
   'scope':'0042-0047 historical interpretation only; raw final snapshots remain valid',
   'old_inference':'final IPP_IRQ_STATUS=0x00011e00 proved CAMIF_SOF/CAMIF_EOF/CAMIF_EPOCH0/CAMIF_EPOCH1/RUP_DONE never occurred',
   'new_fact':'in-ISR OR history proves all five events occurred before timeout and were cleared by the normal CSID ISR',
  },
  'classification':{
   'sensor_to_csid_rx_clean':True,'csid_camif_progression_seen':True,'csid_epoch_progression_seen':True,'csid_rup_done_seen':True,
   'vfe1_epoch0_seen':False,'transient_csid_line_count_error_seen':True,
   'failure_boundary':'after CSID1 CAMIF/RUP/Epoch progression and before VFE1 raw BUS Epoch0; Linux history also contains transient CSID bit14 ERROR_LINE_COUNT absent from accepted Windows live status',
  },
  'next_gate':'Statically close CSID1 bit14 ERROR_LINE_COUNT provenance/Windows handling and the CSID1-to-VFE1 CAMIF handoff/start-state before any further Linux runtime.',
  'runtime_authorized':False,
 }
 txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
 (HERE/'runtime-0048-analysis.json').write_text(txt)
 (HERE/'RUNTIME-CSIDIRQ-0048-ANALYSIS.log').write_text(txt)
 print(txt,end='')
if __name__=='__main__': main()
