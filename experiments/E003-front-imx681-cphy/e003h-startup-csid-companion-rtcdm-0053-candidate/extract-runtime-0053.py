#!/usr/bin/env python3
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
NEW=ROOT/'experiments/E003-front-imx681-cphy/e003h-startup-csid-companion-rtcdm-0053-candidate'
OLD=ROOT/'experiments/E003-front-imx681-cphy/e003h-csid1-clock-rate-0052-candidate'
STATIC=ROOT/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
FILES={
 'run':NEW/'RUNTIME-CSIDCOMP-0053-RUN.txt','post':NEW/'RUNTIME-CSIDCOMP-0053-POST.txt',
 'dmesg':NEW/'RUNTIME-CSIDCOMP-0053-DMESG.txt','stages':NEW/'RUNTIME-CSIDCOMP-0053-RTCDM-STAGES.txt',
 'auth':NEW/'AUTHORIZATION.json','package':NEW/'package-inspection.json',
 'static':STATIC/'linux-0053-startup-csid-companion-rtcdm-transport-inspection.json',
 'oracle':STATIC/'csid1-startup-companion-transport-0053/startup-companion-transport-0053-oracle.json',
 'runtime0052':OLD/'runtime-0052-analysis.json','dmesg0052':OLD/'RUNTIME-CSIDCLK-0052-DMESG.txt'}
EXPECTED={'run':'ee9223ea56c103db203b479043a0f5870d04eee8a0d6c7d71587f45705d05400','post':'caf641604214c660e513e91bb37e533eee197380ca076bcc0ab0da480eccfe8c','dmesg':'44c45f71265a74ae28c264c43b1a59e97f7699a66818a1659258ee62bb7007b5','stages':'47101a8613cdd26fe62566daf8f8adebdf883622187a48ebe1bf526f204dfba4','auth':'ce172a7b39ef88c0c5f57531dd77b296338bcd9431e38152c072cd1714bcc3fc','package':'d283bbe2884aa1a31189c3cbb5c65fdeb9ee7c50e59190b3f55da0bce45bcedb','static':'72ceb0880f673bc1d17698eb228612a88b8bf4683b8f034a9de4f1b784120fea','oracle':'4b70a61a2e226b37d9310b4b4dee4d77c7516f975498973ee89dc29d772e2e5c','runtime0052':'4367b9fe31552baf59cd7212743585fc990a07638794a81da178a22e1591ddba'}
IRQ={3:'CAMIF_EOF',4:'CAMIF_SOF',6:'FRAME_DROP_EOL',7:'FRAME_DROP_SOL',9:'INFO_INPUT_EOF',10:'INFO_INPUT_EOL',11:'INFO_INPUT_SOL',12:'INFO_INPUT_SOF',13:'ERROR_PIX_COUNT',14:'ERROR_LINE_COUNT',21:'CAMIF_EPOCH0',22:'CAMIF_EPOCH1',23:'RUP_DONE'}
def readb(p):
 try:return Path(p).read_bytes()
 except PermissionError:return subprocess.check_output(['sudo','-n','cat',str(p)])
def readt(p):return readb(p).decode()
def sha(p):return hashlib.sha256(readb(p)).hexdigest()
def die(s):raise SystemExit('FAIL: '+s)
def bits(v):return [n for b,n in IRQ.items() if v&(1<<b)]
def wh(v):return {'width':v&0xffff,'height':(v>>16)&0xffff}
def seq(text):
 out=[]
 for m in re.finditer(r'ipp-seq\[(\d+)\]=([0-9a-fA-F]{8})/([0-9a-fA-F]{8})',text):
  s=int(m.group(2),16); a=int(m.group(3),16)
  out.append({'index':int(m.group(1)),'status_hex':f'0x{s:08x}','bits':bits(s),'actual_hex':f'0x{a:08x}','actual_geometry':wh(a)})
 return out
def lineerr(text):
 m=re.search(r'ipp-history=([0-9a-fA-F]{8})/([0-9a-fA-F]{8})/(\d+) line-error=([0-9a-fA-F]{8})/([0-9a-fA-F]{8})/([0-9a-fA-F]{8})',text)
 if not m:die('line-error absent')
 return {'history_or':'0x'+m.group(1).lower(),'history_last':'0x'+m.group(2).lower(),'history_count':int(m.group(3)),'actual':'0x'+m.group(4).lower(),'hbi':'0x'+m.group(5).lower(),'vbi':'0x'+m.group(6).lower()}
def main():
 for k,p in FILES.items():
  if k=='dmesg0052':continue
  g=sha(p)
  if g!=EXPECTED[k]:die(f'{k} hash drift {g}')
 run,post,dm,stages=(readt(FILES[x]) for x in ('run','post','dmesg','stages'))
 if 'HEAD=d7fb66a16f9788d4f0f5d9dd302a64bb6f8b6c34' not in run or 'HELPER_INVOCATION_COUNT=1' not in run or 'RUN_RC=1' not in run or 'Connection timed out' not in run:die('run contract drift')
 for x in ('SENSOR_PM=suspended','CAMSS_PM=suspended','QC10C_OUTPUT=absent','fifo_seq=25','faulted=0'):
  if x not in post+stages:die('post/stages invariant missing '+x)
 curseq=seq(dm); oldseq=seq(readt(FILES['dmesg0052']))
 expected=[('0x00811dd0','0x00000f00'),('0x00600cc0','0x00000f00'),('0x00000cc0','0x00000f00'),('0x00004ee8','0x0a500f00')]
 if [(x['status_hex'],x['actual_hex']) for x in curseq]!=expected:die('0053 sequence drift')
 if [(x['status_hex'],x['actual_hex']) for x in oldseq]!=expected:die('0052 baseline sequence drift')
 le=lineerr(dm); oldle=lineerr(readt(FILES['dmesg0052']))
 expectedle={'history_or':'0x00e15ff8','history_last':'0x00004ee8','history_count':4,'actual':'0x0a500f00','hbi':'0x03b203ad','vbi':'0x00000000'}
 if le!=expectedle or oldle!=expectedle:die('line-error baseline/result drift')
 for x in ('crop=0eff0000/086f0000','measure=0000001f/08700f00','pkts=00009098 ecc=00000000 crc=00000000','VFE1 epoch0-timeout top=00000000/00030003','bus=00000000/00000000 bmask=d0000000/00000000'):
  if x not in dm:die('dmesg invariant missing '+x)
 st=json.loads(readt(FILES['static'])); oracle=json.loads(readt(FILES['oracle'])); old=json.loads(readt(FILES['runtime0052']))
 if not st['accepted'] or not oracle['accepted'] or not old['accepted']:die('proof acceptance drift')
 if st['proved']['startup_rtcdm_commits_per_packet']!=4 or st['proved']['cpu_startup_companion_calls_removed']!=4:die('transport static contract drift')
 if st['classification']['crop_failure_causality_proven'] is not False:die('pre-run causality provenance drift')
 if 'fifo_seq=25' not in stages:die('0053 did not complete expected 25 FIFO submissions')
 if old['execution']['rtcdm_fifo_last']!=17:die('0052 FIFO baseline drift')
 cmd=Path('/proc/cmdline').read_text(); env=subprocess.check_output(['grub-editenv','list'],text=True)
 if 'sp11_entry=7.1.5-sp11-fullio-v19c' not in cmd or 'saved_entry=sp11-audio-fullio-v19c' not in env or re.search(r'^next_entry=.+',env,re.M):die('Golden state drift')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists():die('candidate module remains '+m)
 out={'schema':'sp11-e003h-runtime-0053-startup-csid-companion-rtcdm-v1','accepted':True,'evidence_sha256':EXPECTED,
  'execution':{'helper_invocations':1,'same_boot_retry':False,'helper_result':'ETIMEDOUT / RUN_RC=1','qc10c_output':False,'rtcdm_fifo_last_0052':17,'rtcdm_fifo_last_0053':25,'rtcdm_fifo_delta':8,'rtcdm_faulted':False,'sensor_runtime_suspended_after':True,'camss_runtime_suspended_after':True,'golden_return_verified':True},
  'linux_sequence':curseq,'line_error_0052':oldle,'line_error_0053':le,
  'comparison_0052':{'sequence_identical':True,'completed_eof_geometry_identical':True,'line_error_identical':True,'hbi_identical':True,'vfe1_raw_epoch0_advanced':False,'qc10c_advanced':False,'rtcdm_fifo_count_increased_exactly_by_expected_8':True},
  'classification':{'0053_transport_delta_executed':True,'transport_ownership_mismatch_was_real':True,'transport_correction_causal_for_vertical_crop_failure':False,'first_completed_eof_geometry_improved':False,'line_count_error_removed':False,'vfe1_raw_epoch0_advanced':False,'speculative_crop_register_write_justified':False,
   'vertical_crop_failure_remains':'programmed/readback crop=0x0eff0000/0x086f0000 and expected=0x08700f00; completed frame still 0x0a500f00 (3840x2640) with ERROR_LINE_COUNT'},
  'next_gate':'Retire startup companion transport as crop cause. Return to static active-state/lifecycle analysis. Find a concrete Windows/Linux delta in CSID1 path enable/update/latch semantics or upstream pixel-path selection; no new runtime until proven.'}
 blob=json.dumps(out,indent=2,sort_keys=True)+'\n'; (NEW/'runtime-0053-analysis.json').write_text(blob); (NEW/'EXTRACT-RUNTIME-0053.txt').write_text(blob); print(blob,end='')
if __name__=='__main__':main()
