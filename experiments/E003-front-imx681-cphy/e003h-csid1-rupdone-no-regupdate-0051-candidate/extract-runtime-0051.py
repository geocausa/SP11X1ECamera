#!/usr/bin/env python3
import hashlib,json,re,subprocess
from pathlib import Path
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
NEW=ROOT/'experiments/E003-front-imx681-cphy/e003h-csid1-rupdone-no-regupdate-0051-candidate'
OLD=ROOT/'experiments/E003-front-imx681-cphy/e003h-csid1-first-irq-geometry-0050-candidate'
STATIC=ROOT/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
FILES={
 'run':NEW/'RUNTIME-RUPCLEAR-0051-RUN.txt','post':NEW/'RUNTIME-RUPCLEAR-0051-POST.txt','dmesg':NEW/'RUNTIME-RUPCLEAR-0051-DMESG.txt','stages':NEW/'RUNTIME-RUPCLEAR-0051-RTCDM-STAGES.txt','auth':NEW/'AUTHORIZATION.json','static_inspection':STATIC/'linux-0051-csid1-rupdone-no-regupdate-write-inspection.json','runtime0050':OLD/'runtime-0050-analysis.json'}
EXPECTED={'run':'ed770846b70457f65cb731a2b829928590e8153cec4bc38c151e7fa29455c179','post':'446e528ac7b5047acca936141f7cf9b2619570e6cc7c492a48dfdbdf1b4ea307','dmesg':'b65b5869238f072bed4a1aab8c1ee6c0c1933f7ae49ec1790e2e4e8c6a3c8df4','stages':'d11355abc2d749656d12a054b1c4256c78830a5d33354f9a082e485992411fd5','auth':'0f4837282f952a38b53d1ec99dd940594b52203cc0e830f48ca0e98058e847b5','static_inspection':'a0595d75392871542812ec185e632af37e8da889d6758e61cea794f25517d132','runtime0050':'bc8c2fd7033121592e540e3eedde134e56cab6d2525526f7771a74ec7b424459'}
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
def main():
 for k,p in FILES.items():
  g=sha(p)
  if g!=EXPECTED[k]:die(f'{k} hash drift {g} != {EXPECTED[k]}')
 run,post,dm,stages=(readt(FILES[x]) for x in ('run','post','dmesg','stages'))
 if 'HELPER_INVOCATION_COUNT=1' not in run or 'RUN_RC=1' not in run or 'write trigger: Connection timed out' not in run:die('single timeout run drift')
 for x in ('SENSOR_PM=suspended','CAMSS_PM=suspended','QC10C_OUTPUT=absent','name=stopped','faulted=0'):
  if x not in post:die('postcondition missing '+x)
 if 'fifo_seq=17' not in stages or 'faulted=0' not in stages:die('RT-CDM evidence drift')
 seq=seq_from(dm)
 expected=[('0x00811dd0','0x00000f00'),('0x00600cc0','0x00000f00'),('0x00000cc0','0x00000f00'),('0x00004ee8','0x0a500f00')]
 if [(x['status_hex'],x['actual_hex']) for x in seq]!=expected:die('0051 sequence drift')
 old=json.loads(readt(FILES['runtime0050']))
 oldseq=[(x['status_hex'],x['actual_hex']) for x in old['linux_sequence']]
 if oldseq!=expected:die('0050 baseline sequence drift')
 required=('ipp-history=00e15ff8/00004ee8/4 line-error=0a500f00/02c502c0/00000000','crop=0eff0000/086f0000','measure=0000001f/08700f00','pkts=00009098 ecc=00000000 crc=00000000','VFE1 epoch0-timeout top=00000000/00030003','bus=00000000/00000000 bmask=d0000000/00000000')
 for x in required:
  if x not in dm:die('dmesg invariant missing '+x)
 cmd=Path('/proc/cmdline').read_text()
 if 'sp11_entry=7.1.5-sp11-fullio-v19c' not in cmd:die('not Golden')
 for m in ('qcom_camss','imx681','ov13858'):
  if Path('/sys/module/'+m).exists():die('candidate module remains '+m)
 out={'schema':'sp11-e003h-runtime-0051-rupdone-no-regupdate-v1','accepted':True,'evidence_sha256':EXPECTED,
 'execution':{'helper_invocations':1,'helper_result':'ETIMEDOUT surfaced as Connection timed out / RUN_RC=1','same_boot_retry':False,'qc10c_output':False,'rtcdm_fifo_last':17,'rtcdm_faulted':False,'sensor_runtime_suspended_after':True,'camss_runtime_suspended_after':True,'golden_return_verified':True},
 'linux_sequence':seq,
 'comparison_0050':{'sequence_identical':True,'critical_csid_geometry_identical':True,'vfe_epoch0_boundary_identical':True},
 'classification':{'0051_behavior_executed':'front-mode0 RUP_DONE software shadow clear without post-RUP REG_UPDATE_CMD +0x18 write','post_rup_zero_write_was_real_parity_bug':True,'post_rup_zero_write_is_causal_for_crop_failure':False,'first_epoch_geometry_improved':False,'line_count_error_removed':False,'vfe1_raw_epoch0_advanced':False,'failure_boundary':'unchanged: after matching first RUP_DONE and by immediately following Epoch0/1 IRQ; Linux first Epoch height remains zero and later completes uncropped 3840x2640 with bit14','speculative_crop_register_write_justified':False},
 'next_gate':'Keep 0051 ownership correction, but do not build on it as crop cause. Statically compare the exact event/active-update semantics that can distinguish Windows first Epoch 0x00600228 (EOF-class events, cropped 2160) from Linux 0x00600cc0 (SOL/EOL-class events, height incomplete) despite identical first RUP_DONE status/config/readbacks. No new runtime until a concrete programming or lifecycle delta is proven.'}
 blob=json.dumps(out,indent=2,sort_keys=True)+'\n'
 (NEW/'runtime-0051-analysis.json').write_text(blob)
 (NEW/'EXTRACT-RUNTIME-0051.txt').write_text(blob)
 print(blob,end='')
if __name__=='__main__':main()
