#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
NEW=ROOT/'experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-candidate'
OLD=ROOT/'experiments/E003-front-imx681-cphy/e003h-startup-csid-companion-rtcdm-0053-candidate'
STATIC=ROOT/'experiments/E003-front-imx681-cphy/e003h-imx681-mode2-parity-0054-static'
W=ROOT/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
FILES={
 'run':NEW/'RUNTIME-MODE2-0054-RUN.txt','post':NEW/'RUNTIME-MODE2-0054-POST.txt','dmesg':NEW/'RUNTIME-MODE2-0054-DMESG.txt',
 'stages':NEW/'RUNTIME-MODE2-0054-RTCDM-STAGES.txt','golden':NEW/'RUNTIME-MODE2-0054-GOLDEN-RETURN.txt','auth':NEW/'AUTHORIZATION.json',
 'package':NEW/'package-inspection.json','static':STATIC/'0054-static-inspection.json','runtime0053':OLD/'runtime-0053-analysis.json',
 'dmesg0053':OLD/'RUNTIME-CSIDCOMP-0053-DMESG.txt','windows_bit14':W/'windows-csid1-bit14-history/windows-csid1-bit14-history-oracle.json',
 'windows_first_note':W/'windows-csid1-first-ipp-geometry/E003H_FIRST_IPP_GEOMETRY_CHECKPOINT_20260831.txt',
 'windows_first_oracle':W/'windows-csid1-first-ipp-geometry/ORACLE-CURRENT.txt'}
EXPECTED={
 'run':'2b66e80fe427301b5717fe6b59804fde1a1e6b5ec4b8d926f95c080337727c19',
 'post':'925fa563dd29ce1844a354f2bb8d4090d289915f2660d5f2120c4124cb6cb3a3',
 'dmesg':'a155e3fc39fd9be15beea143b1d27e54d647961315ad83ed5b5380366a3ee864',
 'stages':'5c5f4c12f4b20b8d50fedd374675d0791cc39448d7783cee3ddb1b3bd5f5e08a',
 'golden':'d020c0e387fc57d0291208155b52f5d1f990c9d4d48fc9602280c1bb8c030af4',
 'auth':'e49515cc44a471231af0344c64edf3a22c336d6a1b15e504f761167fc0459696',
 'package':'1d1039e5b02b762955f443ad8a1cb42d9aedb6a664f74035075b222e741d6b37',
 'static':'19f6fddf77d323507bfe4ad390c5f1ae3e70ed983dd574a6ecfec0bd83645231',
 'runtime0053':'7ae66c8bcd725f193ab59b4d4a1f4c6e5688e72fc206960fad53de21c9ba3e22',
 'windows_bit14':'f7523499e06332e588418218bb4eac71069e01c237c0c35f27c3bec6968f3db5',
 'windows_first_note':'0276623cbf63290bad79afb5ce6ce3acf3f7981c6502bbcfcb629e092c545fe6',
 'windows_first_oracle':'21f4365815e614012d8140c6b6027acb26abeebbe6ffd50d8ba13046a2efb27e'}
IRQ={3:'CAMIF_EOF',4:'CAMIF_SOF',6:'FRAME_DROP_EOL',7:'FRAME_DROP_SOL',9:'INFO_INPUT_EOF',10:'INFO_INPUT_EOL',11:'INFO_INPUT_SOL',12:'INFO_INPUT_SOF',13:'ERROR_PIX_COUNT',14:'ERROR_LINE_COUNT',21:'CAMIF_EPOCH0',22:'CAMIF_EPOCH1',23:'RUP_DONE'}
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def need(x,s):
 if not x: raise SystemExit('FAIL: '+s)
def bits(v): return [n for b,n in IRQ.items() if v&(1<<b)]
def wh(v): return {'width':v&0xffff,'height':(v>>16)&0xffff}
def seq(text):
 out=[]
 for m in re.finditer(r'ipp-seq\[(\d+)\]=([0-9a-fA-F]{8})/([0-9a-fA-F]{8})',text):
  st=int(m.group(2),16); actual=int(m.group(3),16)
  out.append({'index':int(m.group(1)),'status_hex':f'0x{st:08x}','bits':bits(st),'actual_hex':f'0x{actual:08x}','actual_geometry':wh(actual),'error_line_count':bool(st&(1<<14))})
 return out
def hist(text):
 m=re.search(r'ipp-history=([0-9a-fA-F]{8})/([0-9a-fA-F]{8})/(\d+) line-error=([0-9a-fA-F]{8})/([0-9a-fA-F]{8})/([0-9a-fA-F]{8})',text); need(m,'IPP history/line-error line absent')
 o,last=int(m.group(1),16),int(m.group(2),16)
 return {'history_or':f'0x{o:08x}','history_last':f'0x{last:08x}','history_count':int(m.group(3)),'history_or_error_line_count':bool(o&(1<<14)),'history_last_error_line_count':bool(last&(1<<14)),'line_error_actual':'0x'+m.group(4).lower(),'line_error_hbi':'0x'+m.group(5).lower(),'line_error_vbi':'0x'+m.group(6).lower()}
def snap(text):
 out={}
 pats={
 'vfe_top':r'VFE1 epoch0-timeout top=([^\n]+)',
 'csid_route':r'CSID1 epoch0-timeout route=([^\n]+)',
 'csid_rx':r'CSID1 epoch0-timeout rx=([^\n]+)',
 'csid_ipp':r'CSID1 epoch0-timeout ipp=([^\n]+)',
 'crop':r'CSID1 epoch0-timeout crop=([^\n]+)'}
 for k,p in pats.items():
  m=re.search(p,text); need(m,k+' snapshot absent'); out[k]=m.group(1).strip()
 return out
def main():
 for k,p in FILES.items():
  if k=='dmesg0053': continue
  need(sha(p)==EXPECTED[k],f'{k} SHA drift {sha(p)}')
 run=FILES['run'].read_text(); post=FILES['post'].read_text(); dm=FILES['dmesg'].read_text(); stages=FILES['stages'].read_text(); golden=FILES['golden'].read_text()
 need('HEAD=68252b6491305b135f2a222288e438c637a49c27' in run and 'HELPER_INVOCATION_COUNT=1' in run and 'RUN_RC=1' in run and 'Connection timed out' in run,'one-shot RUN contract')
 for s in ('SENSOR_PM=suspended','CAMSS_PM=suspended','QC10C_OUTPUT=absent','fifo_seq=25','faulted=0'):
  need(s in post+stages,'post/stages '+s)
 need('name=fifo-done fifo_seq=25' in stages and 'name=stopped fifo_seq=25' in stages,'25 FIFO completion/stopped')
 need('UNAME=7.1.5-sp11-render-parity-v4+' in golden and 'sp11_entry=7.1.5-sp11-fullio-v19c' in golden and 'saved_entry=sp11-audio-fullio-v19c;next_entry=;' in golden and 'CAMERA_MODULES=\n' in golden,'Golden return evidence')
 need('selected mode2=68 programmed in standby' in dm and 'MODE_SELECT=1 front transmission started' in dm,'mode2 execution')
 cur=seq(dm); old=seq(FILES['dmesg0053'].read_text())
 expect_first4=[('0x00811dd0','0x00000f00'),('0x00600cc0','0x00000f00'),('0x00000cc0','0x00000f00'),('0x00000ee8','0x08700f00')]
 need([(x['status_hex'],x['actual_hex']) for x in cur[:4]]==expect_first4,'0054 first four IRQ/geometry sequence')
 need(len(cur)==8,'0054 retained sequence count')
 need(all(x['actual_hex']=='0x08700f00' for x in cur[3:]),'all complete/subsequent measured geometry 3840x2160')
 need(not any(x['error_line_count'] for x in cur),'bit14 present in 0054 retained sequence')
 oldexp=[('0x00811dd0','0x00000f00'),('0x00600cc0','0x00000f00'),('0x00000cc0','0x00000f00'),('0x00004ee8','0x0a500f00')]
 need([(x['status_hex'],x['actual_hex']) for x in old]==oldexp,'0053 baseline sequence')
 ch=hist(dm); oh=hist(FILES['dmesg0053'].read_text())
 need(ch=={'history_or':'0x00e11ff8','history_last':'0x00000ee8','history_count':43,'history_or_error_line_count':False,'history_last_error_line_count':False,'line_error_actual':'0x00000000','line_error_hbi':'0x00000000','line_error_vbi':'0x00000000'},'0054 history/line-error')
 need(oh['history_last']=='0x00004ee8' and oh['history_count']==4 and oh['history_or_error_line_count'] is True and oh['line_error_actual']=='0x0a500f00','0053 line-error baseline')
 for s in ('crop=0eff0000/086f0000','measure=0000001f/08700f00','ecc=00000000 crc=00000000','VFE1 epoch0-timeout top=00000000/00030003','bus=00000000/00000000 bmask=d0000000/00000000'):
  need(s in dm,'0054 dmesg invariant '+s)
 si=json.loads(FILES['static'].read_text()); au=json.loads(FILES['auth'].read_text()); olda=json.loads(FILES['runtime0053'].read_text()); w=json.loads(FILES['windows_bit14'].read_text())
 need(si['accepted'] and si['sensor']['windows_pair_equality'] and si['sensor']['changed_values']==7 and si['camss']['new_mmio_writes']==0,'0054 static proof binding')
 need(au['accepted'] and au['runtime_authorized'] and au['execution_contract']['root_helper_invocation_count']==1 and au['execution_contract']['same_boot_retry'] is False,'0054 authorization binding')
 need(olda['accepted'] and olda['line_error_0053']['actual']=='0x0a500f00','0053 analysis binding')
 need(w['accepted'] and w['bounded_end']['actual_frame']=='0x08700f00' and w['bounded_end']['ipp_bit14'] is False and w['bounded_end']['height']==2160,'Windows bounded CSID comparison')
 need(FILES['windows_first_oracle'].read_text().startswith('FAIL: raw KD log missing:'),'Windows first-IPP raw provenance gap unexpectedly closed/changed')
 package=json.loads(FILES['package'].read_text()); need(package['accepted'] and package['runtime_authorized'] is False,'package evidence binding')
 current_snap=snap(dm); old_snap=snap(FILES['dmesg0053'].read_text())
 out={
  'schema':'sp11-e003h-runtime-0054-windows-selected-imx681-mode2-v1','accepted':True,
  'evidence_sha256':EXPECTED,
  'execution':{'authorized_helper_invocations':1,'observed_helper_invocations':1,'same_boot_retry':False,'helper_result':'ETIMEDOUT / RUN_RC=1','rtcdm_fifo_last':25,'rtcdm_faulted':False,'qc10c_output':False,'sensor_runtime_suspended_after':True,'camss_runtime_suspended_after':True,'golden_return_verified':True},
  'mode2':{'windows_resolution_index':2,'geometry':'3840x2160@30','windows_pair_equality':True,'mode_pairs':68,'changed_values_from_old_linux_mode0':7,'programming_executed':True},
  'linux_sequence':cur,'history_0054':ch,'history_0053':oh,
  'comparison_0053':{
   'first_three_precomplete_samples_identical':[(x['status_hex'],x['actual_hex']) for x in cur[:3]]==[(x['status_hex'],x['actual_hex']) for x in old[:3]],
   'first_completed_geometry_old':'3840x2640','first_completed_geometry_new':'3840x2160','first_completed_status_old':'0x00004ee8','first_completed_status_new':'0x00000ee8',
   'error_line_count_old':True,'error_line_count_new':False,'line_error_snapshot_old':'0x0a500f00','line_error_snapshot_new':'0x00000000','retained_irq_count_old':4,'retained_irq_count_new':8,
   'vfe1_epoch0_timeout_persists':True,'qc10c_output_still_absent':True,'rtcdm_fifo_count_identical':True},
  'windows_comparison':{
   'bounded_windows_end_geometry':'3840x2160','bounded_windows_bit14':False,'linux_0054_completed_geometry_matches_bounded_windows':True,'linux_0054_bit14_matches_bounded_windows_absence':True,
   'windows_first_ipp_sequence_reported_but_raw_log_missing':True,'raw_first_ipp_sequence_byte_exact_comparison_authorized':False,'provenance_note_sha256':EXPECTED['windows_first_note']},
  'timeout_snapshots':{'linux_0054':current_snap,'linux_0053':old_snap},
  'classification':{
   'windows_selected_mode2_executed':True,'sensor_mode_mismatch_was_causal_for_old_csid_line_count_fault':True,'csid_first_completed_frame_geometry_fixed':True,'csid_error_line_count_removed':True,
   'csid_retains_multiple_subsequent_3840x2160_samples':True,'csid_rx_ecc_crc_errors_seen':False,'vfe1_raw_epoch0_advanced':False,'qc10c_advanced':False,
   'old_csid_line_count_fault_was_causal_for_missing_vfe1_epoch0':False,'production_parity_reached':False,'speculative_new_hardware_write_justified':False,
   'remaining_failure_boundary':'after healthy CSID1 3840x2160 frame reception and before VFE1 raw Epoch0 / FULL output'},
  'next_gate':'Freeze/consume 0054. With sensor and CSID geometry healthy, compare exact Windows VFE1/IFE input-path, reg-update/GEN_IRQ and startup-state ownership against Linux timeout snapshot. Do not authorize another runtime candidate until a concrete downstream Windows/Linux delta is mechanically proven.'}
 blob=json.dumps(out,indent=2,sort_keys=True)+'\n'; (NEW/'runtime-0054-analysis.json').write_text(blob); (NEW/'EXTRACT-RUNTIME-0054.txt').write_text(blob); print(blob,end='')
if __name__=='__main__':main()
