#!/usr/bin/env python3
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
NEW=ROOT/'experiments/E003-front-imx681-cphy/e003h-csid1-clock-rate-0052-candidate'
OLD=ROOT/'experiments/E003-front-imx681-cphy/e003h-csid1-rupdone-no-regupdate-0051-candidate'
STATIC=ROOT/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
FILES={
 'run':NEW/'RUNTIME-CSIDCLK-0052-RUN.txt',
 'post':NEW/'RUNTIME-CSIDCLK-0052-POST.txt',
 'dmesg':NEW/'RUNTIME-CSIDCLK-0052-DMESG.txt',
 'stages':NEW/'RUNTIME-CSIDCLK-0052-RTCDM-STAGES.txt',
 'auth':NEW/'AUTHORIZATION.json',
 'static_inspection':STATIC/'linux-0052-x1e-front-link-clock-rate-inspection.json',
 'runtime0051':OLD/'runtime-0051-analysis.json',
 'dmesg0051':OLD/'RUNTIME-RUPCLEAR-0051-DMESG.txt',
 'clock_oracle':STATIC/'x1e-csid-clock-hbi-correlation/x1e-csid-clock-hbi-correlation-oracle.json',
 'windows_hbi':STATIC/'windows-csid1-bit14-history/windows-csid1-bit14-history-oracle.json',
 'eof_oracle':STATIC/'windows-linux-first-eof-geometry-boundary/first-eof-geometry-boundary-oracle.json',
}
EXPECTED={
 'run':'c4789f028cc07ab996cb580fb791737d379416fb2496bfaca7c94d8f6e16962a',
 'post':'e908b1ac89f8b8914c1c7daf8b0228e16f82664685615877fda889c58811eaef',
 'dmesg':'f485f4de07df1fd69414a0176d45a9e061f3209513bd657f32ef00e38c23f98f',
 'stages':'49d30540c8094c14a4d19365f36685a31e0323ef18df6c1259533619014a6569',
 'auth':'c56294a7eea290d8e9ee37c19bd0c5da9734209d81afbddbb26266feab64f28b',
 'static_inspection':'e20bf446fde42298988c586b941e4c96ec8017f8c67bc4a396b824f359f676ad',
 'runtime0051':'2e1fbd740073b98e9e86ef477f1986d9b7e94a26a5e486f4386197b8e331f9d1',
 'dmesg0051':'b65b5869238f072bed4a1aab8c1ee6c0c1933f7ae49ec1790e2e4e8c6a3c8df4',
 'clock_oracle':'f913e0dd3766077cfa9cf6875f77d7494bfe60a1bceea0ffe9f9c928d7d00dd0',
 'windows_hbi':'f7523499e06332e588418218bb4eac71069e01c237c0c35f27c3bec6968f3db5',
 'eof_oracle':'db4476e159872f9005a127d84ea41032191402de2709a0835d2c2c5fbc9dffde',
}
IRQ={2:'ERROR_FIFO_OVERFLOW',3:'CAMIF_EOF',4:'CAMIF_SOF',5:'FRAME_DROP_EOF',6:'FRAME_DROP_EOL',7:'FRAME_DROP_SOL',8:'FRAME_DROP_SOF',9:'INFO_INPUT_EOF',10:'INFO_INPUT_EOL',11:'INFO_INPUT_SOL',12:'INFO_INPUT_SOF',13:'ERROR_PIX_COUNT',14:'ERROR_LINE_COUNT',15:'VCDT_GRP0_SEL',16:'VCDT_GRP1_SEL',17:'VCDT_GRP_CHANGE',18:'FRAME_DROP',19:'OVERFLOW_RECOVERY',20:'ERROR_REC_CCIF_VIOLATION',21:'CAMIF_EPOCH0',22:'CAMIF_EPOCH1',23:'RUP_DONE',24:'ILLEGAL_BATCH_ID',25:'BATCH_END_MISSING_VIOLATION',26:'HEIGHT_VIOLATION',27:'WIDTH_VIOLATION',28:'SENSOR_SWITCH_OUT_OF_SYNC_FRAME_DROP',29:'CCIF_VIOLATION'}
def readb(p):
 try:return Path(p).read_bytes()
 except PermissionError:return subprocess.check_output(['sudo','-n','cat',str(p)])
def readt(p):return readb(p).decode()
def sha(p):return hashlib.sha256(readb(p)).hexdigest()
def die(s):raise SystemExit('FAIL: '+s)
def bits(v):return [n for b,n in IRQ.items() if v&(1<<b)]
def wh(v):return {'width':v&0xffff,'height':(v>>16)&0xffff}
def seq_from(text):
 out=[]
 for m in re.finditer(r'ipp-seq\[(\d+)\]=([0-9a-fA-F]{8})/([0-9a-fA-F]{8})',text):
  st=int(m.group(2),16); ac=int(m.group(3),16)
  out.append({'index':int(m.group(1)),'status_hex':f'0x{st:08x}','bits':bits(st),'actual_hex':f'0x{ac:08x}','actual_geometry':wh(ac)})
 return out
def lineerr(text):
 m=re.search(r'ipp-history=([0-9a-fA-F]{8})/([0-9a-fA-F]{8})/(\d+) line-error=([0-9a-fA-F]{8})/([0-9a-fA-F]{8})/([0-9a-fA-F]{8})',text)
 if not m:die('line-error record absent')
 return {'history_or':'0x'+m.group(1).lower(),'history_last':'0x'+m.group(2).lower(),'history_count':int(m.group(3)),
         'actual':'0x'+m.group(4).lower(),'hbi':'0x'+m.group(5).lower(),'vbi':'0x'+m.group(6).lower()}
def main():
 for k,p in FILES.items():
  got=sha(p)
  if got!=EXPECTED[k]:die(f'{k} hash drift {got} != {EXPECTED[k]}')
 run,post,dm,stages=(readt(FILES[x]) for x in ('run','post','dmesg','stages'))
 if 'HEAD=73847668047aa120ee0e5966e458d641135fff07' not in run:die('authorization commit/run HEAD drift')
 if 'HELPER_INVOCATION_COUNT=1' not in run or 'RUN_RC=1' not in run or 'write trigger: Connection timed out' not in run:die('single timeout run drift')
 for x in ('SENSOR_PM=suspended','CAMSS_PM=suspended','QC10C_OUTPUT=absent','name=stopped','faulted=0'):
  if x not in post:die('postcondition missing '+x)
 if 'fifo_seq=17' not in stages or 'faulted=0' not in stages:die('RT-CDM evidence drift')
 seq=seq_from(dm)
 expected=[('0x00811dd0','0x00000f00'),('0x00600cc0','0x00000f00'),('0x00000cc0','0x00000f00'),('0x00004ee8','0x0a500f00')]
 if [(x['status_hex'],x['actual_hex']) for x in seq]!=expected:die('0052 sequence drift')
 old=json.loads(readt(FILES['runtime0051']))
 oldseq=[(x['status_hex'],x['actual_hex']) for x in old['linux_sequence']]
 if oldseq!=expected:die('0051 baseline sequence drift')
 le=lineerr(dm); oldle=lineerr(readt(FILES['dmesg0051']))
 if le!={'history_or':'0x00e15ff8','history_last':'0x00004ee8','history_count':4,'actual':'0x0a500f00','hbi':'0x03b203ad','vbi':'0x00000000'}:die('0052 line-error/HBI drift '+repr(le))
 if oldle['actual']!='0x0a500f00' or oldle['hbi']!='0x02c502c0':die('0051 line-error/HBI baseline drift')
 win=json.loads(readt(FILES['windows_hbi']))
 whbi=win['bounded_end']['hbi'].lower()
 if whbi!='0x03b203ad' or le['hbi']!=whbi:die('Windows/0052 HBI exact parity missing')
 clk=json.loads(readt(FILES['clock_oracle']))
 if not clk['classification']['linux_x1e_front_csid_300mhz_request_proven']:die('clock oracle baseline drift')
 if not clk['classification']['linux_link_derived_required_rate_is_400mhz']:die('clock oracle required-rate drift')
 if clk['classification']['direct_windows_400mhz_clock_vote_observed'] is not False:die('Windows direct-vote classification drift')
 required=('crop=0eff0000/086f0000','measure=0000001f/08700f00','pkts=00009098 ecc=00000000 crc=00000000','VFE1 epoch0-timeout top=00000000/00030003','bus=00000000/00000000 bmask=d0000000/00000000')
 for x in required:
  if x not in dm:die('dmesg invariant missing '+x)
 cmd=Path('/proc/cmdline').read_text()
 if 'sp11_entry=7.1.5-sp11-fullio-v19c' not in cmd:die('not Golden')
 env=subprocess.check_output(['grub-editenv','list'],text=True)
 if 'saved_entry=sp11-audio-fullio-v19c' not in env or re.search(r'^next_entry=.+',env,re.M):die('Golden grub state drift')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists():die('candidate module remains '+m)
 out={
  'schema':'sp11-e003h-runtime-0052-x1e-csid-clock-rate-v1','accepted':True,'evidence_sha256':EXPECTED,
  'execution':{'helper_invocations':1,'helper_result':'ETIMEDOUT surfaced as Connection timed out / RUN_RC=1','same_boot_retry':False,'qc10c_output':False,'rtcdm_fifo_last':17,'rtcdm_faulted':False,'sensor_runtime_suspended_after':True,'camss_runtime_suspended_after':True,'golden_return_verified':True},
  'linux_sequence':seq,
  'line_error':{'0051':oldle,'0052':le,'windows_bounded_normal_hbi':whbi},
  'comparison_0051':{'sequence_identical':True,'critical_csid_geometry_identical':True,'vfe_epoch0_boundary_identical':True,'hbi_changed':True,'hbi_0051':'0x02c502c0','hbi_0052':'0x03b203ad','hbi_0052_exact_windows_sample':True},
  'classification':{
   '0052_behavior_executed':'exact X1E80100 front CSID1 + CSIPHY2 + one-trio C-PHY clocks csid/csid_csiphy_rx use existing link-derived rate selection, changing request 300MHz -> 400MHz',
   'x1e_300mhz_clock_selection_was_real_bug':True,
   'clock_correction_is_causal_for_hbi_mismatch':True,
   'hbi_normalized_exactly_to_windows_sample':True,
   'direct_windows_400mhz_vote_proven':False,
   'clock_correction_is_causal_for_vertical_crop_failure':False,
   'first_completed_eof_geometry_improved':False,
   'line_count_error_removed':False,
   'vfe1_raw_epoch0_advanced':False,
   'vertical_crop_failure_remains':'CSID readback crop=0x0eff0000/0x086f0000 and expected=0x08700f00, but first completed EOF remains actual=0x0a500f00 (3840x2640) with ERROR_LINE_COUNT',
   'speculative_crop_register_write_justified':False,
  },
  'next_gate':'Keep the 0052 X1E clock correction because it causally fixes the HBI timing-domain mismatch, but retire clock rate as the crop cause. Statically close CSID680 active vertical-crop/latch semantics: compare Windows qccamisp ordering and values for IPP CFG0/VCROP/CTRL, RUP/AUP/update commands and LUT/active-bank selection against Linux. The strongest remaining fact is identical programmed/readback crop and expected size while Linux completed-frame measurement ignores the 480-line vertical crop. No further runtime until a concrete active-bank/update/lifecycle delta is proven.'
 }
 blob=json.dumps(out,indent=2,sort_keys=True)+'\n'
 (NEW/'runtime-0052-analysis.json').write_text(blob)
 (NEW/'EXTRACT-RUNTIME-0052.txt').write_text(blob)
 print(blob,end='')
if __name__=='__main__':main()
