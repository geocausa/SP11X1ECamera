#!/usr/bin/env python3
import hashlib,json,re
from pathlib import Path
HERE=Path(__file__).resolve().parent
STATIC=HERE.parent/'e003h-windows-parity-transport-static'
FILES={
 'run':HERE/'RUNTIME-CSIDFRAME-0049-RUN.txt',
 'post':HERE/'RUNTIME-CSIDFRAME-0049-POST.txt',
 'dmesg':HERE/'RUNTIME-CSIDFRAME-0049-DMESG.txt',
 'stages':HERE/'RUNTIME-CSIDFRAME-0049-RTCDM-STAGES.txt',
 'golden':HERE/'RUNTIME-CSIDFRAME-0049-GOLDEN-RETURN.txt',
 'auth':HERE/'AUTHORIZATION.json',
 'package':HERE/'package-inspection.json',
 'linux_static':STATIC/'linux-0049-csid1-line-error-frame-readonly-inspection.json',
 'windows_line_oracle':STATIC/'windows-csid1-line-count-error/windows-csid1-line-count-error-oracle.json',
}
EXPECTED={
 'run':'c007c07bd045f05d02c871cbcfc43be42c697ea2c6593708c9286ea7420179e6',
 'post':'b7bd551403efdeb285d711006951beefe1c5d1bff20b0d924662a535661ea970',
 'dmesg':'c601fd004fa76684aafcc14e6870acb7feef964eb06fba48626f84496ab840ab',
 'stages':'24d883ce60f0793f4e31bcd824bd8978c43b2678b3e9822c0a609a6d1d642d2d',
 'golden':'d36e01d738c2fe0366353e7189ade878768149f151d58f10dbfc03b37fb32ade',
 'auth':'54939039e4b884300d5832e46c2f2bb9915404907b4e0c622470a20cb2b8eb19',
 'package':'fa62bdc06eb154f66784491cc6435f27d345bd0edeaf69158251a8ecdfc774d5',
 'linux_static':'e5d53e72e90406023616c2658f413ca80d6c49e9ff1f4622929012299eb17afe',
 'windows_line_oracle':'2081159e5a28a02fa79a933c83fe0838a6efe778f1ccdd85a804c6f3d8ec9b3e',
}
IRQ={2:'ERROR_FIFO_OVERFLOW',3:'CAMIF_EOF',4:'CAMIF_SOF',5:'FRAME_DROP_EOF',6:'FRAME_DROP_EOL',7:'FRAME_DROP_SOL',8:'FRAME_DROP_SOF',9:'INFO_INPUT_EOF',10:'INFO_INPUT_EOL',11:'INFO_INPUT_SOL',12:'INFO_INPUT_SOF',13:'ERROR_PIX_COUNT',14:'ERROR_LINE_COUNT',15:'VCDT_GRP0_SEL',16:'VCDT_GRP1_SEL',17:'VCDT_GRP_CHANGE',18:'FRAME_DROP',19:'OVERFLOW_RECOVERY',20:'ERROR_REC_CCIF_VIOLATION',21:'CAMIF_EPOCH0',22:'CAMIF_EPOCH1',23:'RUP_DONE',24:'ILLEGAL_BATCH_ID',25:'BATCH_END_MISSING_VIOLATION',26:'HEIGHT_VIOLATION',27:'WIDTH_VIOLATION',28:'SENSOR_SWITCH_OUT_OF_SYNC_FRAME_DROP',29:'CCIF_VIOLATION'}
WINDOWS_LIVE=0x00e11ff8
EXPECTED_FRAME=0x08700f00

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def need(t,s,l):
 if s not in t: die(f'{l}: missing {s!r}')
def m(t,p,l):
 x=re.search(p,t,re.I)
 if not x: die('missing '+l)
 return x.groups()
def bits(v): return [b for b in range(32) if v&(1<<b)]
def names(v): return [IRQ.get(b,f'BIT{b}') for b in bits(v)]
def wh(v): return {'width':v&0xffff,'height':(v>>16)&0xffff}

def main():
 for k,p in FILES.items():
  if not p.is_file(): die('missing '+str(p))
  if sha(p)!=EXPECTED[k]: die(f'{k} identity drift {sha(p)} != {EXPECTED[k]}')
 run=FILES['run'].read_text(errors='replace'); post=FILES['post'].read_text(errors='replace'); dm=FILES['dmesg'].read_text(errors='replace'); stages=FILES['stages'].read_text(errors='replace'); golden=FILES['golden'].read_text(errors='replace')
 for s in ('HELPER_INVOCATION_COUNT=1','RUN_RC=1','write trigger: Connection timed out'): need(run,s,'run')
 for s in ('RUN_RC=1','QC10C_OUTPUT=absent','SENSOR_PM=suspended','CAMSS_PM=suspended','fifo_seq=17','faulted=0','name=stopped'): need(post,s,'post')
 for s in ('fifo_seq=17','faulted=0','name=stopped'): need(stages,s,'stages')
 for bad in ('BUG:','Oops:','Kernel panic','SError Interrupt','Unhandled fault'):
  if bad in dm: die('kernel fault marker '+bad)
 for s in ('MODE_SELECT=1 front transmission started','MODE_SELECT=0 front transmission stopped'): need(dm,s,'sensor lifecycle')
 for s in ('KERNEL=7.1.5-sp11-render-parity-v4+','BOOT_IMAGE=/boot/sp11-7.1.5-audio-fullio-v19c/','saved_entry=sp11-audio-fullio-v19c','next_entry=','qcom_camss=absent','imx681=absent','ov13858=absent','HEAD=31117d6165ead0282c46da239167f9a0f6b86c29','ORIGIN=31117d6165ead0282c46da239167f9a0f6b86c29'): need(golden,s,'golden')
 top=m(dm,r'E003h VFE1 epoch0-timeout top=([0-9a-f]{8})/([0-9a-f]{8}) mask=([0-9a-f]{8})/([0-9a-f]{8}) bus=([0-9a-f]{8})/([0-9a-f]{8}) bmask=([0-9a-f]{8})/([0-9a-f]{8})','VFE top/bus')
 if top!=('00000000','00030003','0007f051','00000000','00000000','00000000','d0000000','00000000'): die('VFE boundary drift '+repr(top))
 rx=m(dm,r'E003h CSID1 epoch0-timeout rx=([0-9a-f]{8})/([0-9a-f]{8}) cfg=([0-9a-f]{8})/([0-9a-f]{8}) pkts=([0-9a-f]{8}) ecc=([0-9a-f]{8}) crc=([0-9a-f]{8})','CSID RX')
 ipp=m(dm,r'E003h CSID1 epoch0-timeout ipp=([0-9a-f]{8})/([0-9a-f]{8}) ctrl=([0-9a-f]{8}) cfg=([0-9a-f]{8})/([0-9a-f]{8}) z324=([0-9a-f]{8}) z330=([0-9a-f]{8}) epoch=([0-9a-f]{8})','CSID IPP')
 hist=m(dm,r'E003h CSID1 epoch0-timeout ipp-history=([0-9a-f]{8})/([0-9a-f]{8})/([0-9]+) line-error=([0-9a-f]{8})/([0-9a-f]{8})/([0-9a-f]{8})','history/error')
 tail=m(dm,r'E003h CSID1 epoch0-timeout crop=([0-9a-f]{8})/([0-9a-f]{8}).*measure=([0-9a-f]{8})/([0-9a-f]{8})','crop/measure')
 if rx[4:]!=('00009098','00000000','00000000'): die('CSI ingress drift')
 if ipp[:5]!=('00011e00','3cbc601c','00000001','802b2000','00007241'): die('IPP config drift '+repr(ipp))
 seen,last,count,actual,hbi,vbi=int(hist[0],16),int(hist[1],16),int(hist[2]),int(hist[3],16),int(hist[4],16),int(hist[5],16)
 if (seen,last,count)!=(0x00e15ff8,0x00004ee8,4): die('IRQ history drift')
 if not (seen&(1<<14)): die('line-count bit missing')
 for bit in (3,4,21,22,23):
  if not (seen&(1<<bit)): die('critical CSID history bit missing '+IRQ[bit])
 if int(tail[3],16)!=EXPECTED_FRAME: die('expected format-measure drift')
 if actual!=0x0a500f00: die(f'error-time actual frame drift 0x{actual:08x}')
 awh=wh(actual); ewh=wh(EXPECTED_FRAME)
 if awh!={'width':3840,'height':2640} or ewh!={'width':3840,'height':2160}: die('frame decode drift')
 if awh['height']-ewh['height']!=480 or awh['width']!=ewh['width']: die('mismatch geometry drift')
 w=json.loads(FILES['windows_line_oracle'].read_text())
 sw=w['same_machine_windows_live']
 if sw['expected_equals_actual'] is not True or int(sw['expected_frame_size_register'],16)!=EXPECTED_FRAME or int(sw['actual_frame_size_register'],16)!=EXPECTED_FRAME: die('Windows live format oracle drift')
 out={
  'schema':'sp11-e003h-csid1-line-error-frame-0049-runtime-result-v1','accepted':True,'date':'2026-08-30',
  'authorization_consumed':True,'helper_invocations':1,'same_boot_retry':False,'run_rc':1,'qc10c_output':False,'golden_return_verified':True,
  'evidence_sha256':EXPECTED,
  'rtcdm':{'fifo_bl_completed':17,'faulted':False,'final_stage':'stopped'},
  'sensor':{'mode_select_on_seen':True,'mode_select_off_seen':True,'transport_width':3840,'transport_height':2640,'clean_csi_packets':int(rx[4],16),'ecc_errors':0,'crc_errors':0},
  'csid1':{'irq_history_or':f'0x{seen:08x}','irq_history_bits':names(seen),'irq_history_last':f'0x{last:08x}','irq_history_count':count,'camif_sof_seen':True,'camif_eof_seen':True,'camif_epoch0_seen':True,'camif_epoch1_seen':True,'rup_done_seen':True,'line_count_error_seen':True,'error_time_actual_frame':f'0x{actual:08x}','error_time_actual_width':awh['width'],'error_time_actual_height':awh['height'],'error_time_hbi':f'0x{hbi:08x}','error_time_vbi':f'0x{vbi:08x}','programmed_expected_frame':f'0x{EXPECTED_FRAME:08x}','programmed_expected_width':ewh['width'],'programmed_expected_height':ewh['height'],'height_delta_lines':awh['height']-ewh['height'],'crop_readback_h':'0x'+tail[0],'crop_readback_v':'0x'+tail[1]},
  'vfe1':{'raw_epoch0_seen':False,'top_status1':'0x'+top[1],'bus_status1':'0x'+top[5]},
  'windows_comparison':{'live_ipp_status':f'0x{WINDOWS_LIVE:08x}','live_ipp_bit14':False,'live_expected_frame':'0x08700f00','live_actual_frame':'0x08700f00','live_actual_width':3840,'live_actual_height':2160,'historical_bit14_observed':None,'historical_bit14_absence_proven':False,'reason':'Windows live IRQ status is not a historical OR; qccamisp services/clears CSID IRQs, so a transient Windows bit14 remains unresolved.'},
  'classification':{'linux_error_geometry_proven':True,'error_is_width_mismatch':False,'error_is_line_count_mismatch':True,'extra_lines':480,'sensor_mode_change_justified':False,'crop_register_readback_matches_windows':True,'causal_link_to_vfe_epoch0_proven':False,'failure_boundary':'Linux CSID1 receives 3840x2640 cleanly and reaches CAMIF/RUP/Epoch, but at least one IPP IRQ measures 3840x2640 while expected/cropped geometry is 3840x2160; VFE1 raw Epoch0 remains absent.'},
  'next_gate':'Capture same-machine Windows CSID1 historical IPP bit14 dynamically during normal front startup; if bit14 occurs, capture +0x388/+0x38c/+0x390/+0x394 at that exact IRQ. Do not infer historical absence from Windows live status.',
  'runtime_authorized':False,
 }
 txt=json.dumps(out,indent=2,sort_keys=True)+'\n'
 (HERE/'runtime-0049-analysis.json').write_text(txt)
 (HERE/'RUNTIME-CSIDFRAME-0049-ANALYSIS.log').write_text(txt)
 print(txt,end='')
if __name__=='__main__': main()
