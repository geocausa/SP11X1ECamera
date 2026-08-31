#!/usr/bin/env python3
import hashlib, json, re, subprocess
from pathlib import Path

ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera')
NEW=ROOT/'experiments/E003-front-imx681-cphy/e003h-csid1-first-irq-geometry-0050-candidate'
STATIC=ROOT/'experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static'
WIN=STATIC/'windows-csid1-first-ipp-geometry/E003H_FIRST_IPP_GEOMETRY_CHECKPOINT_20260831.txt'
INSPECT=STATIC/'linux-0050-csid1-first-irq-geometry-readonly-inspection.json'
FILES={
 'run':NEW/'RUNTIME-CSIDSEQ-0050-RUN.txt',
 'post':NEW/'RUNTIME-CSIDSEQ-0050-POST.txt',
 'dmesg':NEW/'RUNTIME-CSIDSEQ-0050-DMESG.txt',
 'stages':NEW/'RUNTIME-CSIDSEQ-0050-RTCDM-STAGES.txt',
 'auth':NEW/'AUTHORIZATION.json',
 'windows_checkpoint':WIN,
 'static_inspection':INSPECT,
}
EXPECTED={
 'run':'941987950cc6613be669a05c938bc0f4fa9c7db36e4fe1a5f86389a73676cbc4',
 'post':'2b4d0fb09080f9937731c05c2d3e3421f9b621cb5061d2b21880dab62280c17d',
 'dmesg':'6c790899e99d82e9bb35925c6286e43afb26ba0fa9c422cfdfc54f0796b63b82',
 'stages':'336512fc2098ec1d4a913a14050bd0e024d381a3585e359f0ce375afbbabac57',
 'auth':'016ede970efbc7653ab390fbdc5bc72d503cc2dc5068059dd2c5ca72968039ac',
 'windows_checkpoint':'0276623cbf63290bad79afb5ce6ce3acf3f7981c6502bbcfcb629e092c545fe6',
 'static_inspection':'6ccfd7e88586721dbc1b4050e041e8b128a8409d8ee2f1dd40fd0030f70a047d',
}
IRQ={2:'ERROR_FIFO_OVERFLOW',3:'CAMIF_EOF',4:'CAMIF_SOF',5:'FRAME_DROP_EOF',6:'FRAME_DROP_EOL',7:'FRAME_DROP_SOL',8:'FRAME_DROP_SOF',9:'INFO_INPUT_EOF',10:'INFO_INPUT_EOL',11:'INFO_INPUT_SOL',12:'INFO_INPUT_SOF',13:'ERROR_PIX_COUNT',14:'ERROR_LINE_COUNT',15:'VCDT_GRP0_SEL',16:'VCDT_GRP1_SEL',17:'VCDT_GRP_CHANGE',18:'FRAME_DROP',19:'OVERFLOW_RECOVERY',20:'ERROR_REC_CCIF_VIOLATION',21:'CAMIF_EPOCH0',22:'CAMIF_EPOCH1',23:'RUP_DONE',24:'ILLEGAL_BATCH_ID',25:'BATCH_END_MISSING_VIOLATION',26:'HEIGHT_VIOLATION',27:'WIDTH_VIOLATION',28:'SENSOR_SWITCH_OUT_OF_SYNC_FRAME_DROP',29:'CCIF_VIOLATION'}

def readb(p):
    p=Path(p)
    try: return p.read_bytes()
    except PermissionError: return subprocess.check_output(['sudo','-n','cat',str(p)])
def readt(p): return readb(p).decode('utf-8')
def sha(p): return hashlib.sha256(readb(p)).hexdigest()
def die(s): raise SystemExit('FAIL: '+s)
def bits(v): return [name for bit,name in IRQ.items() if v & (1<<bit)]
def wh(v): return {'width':v & 0xffff, 'height':(v>>16)&0xffff}

def main():
    for k,p in FILES.items():
        got=sha(p)
        if got!=EXPECTED[k]: die(f'{k} hash drift {got} != {EXPECTED[k]}')
    run=readt(FILES['run']); post=readt(FILES['post']); dm=readt(FILES['dmesg']); stages=readt(FILES['stages']); win=readt(WIN)
    if 'HELPER_INVOCATION_COUNT=1' not in run or 'RUN_RC=1' not in run or 'write trigger: Connection timed out' not in run: die('single timeout run contract drift')
    for x in ('SENSOR_PM=suspended','CAMSS_PM=suspended','QC10C_OUTPUT=absent','name=stopped','faulted=0'):
        if x not in post: die('postcondition missing '+x)
    if 'fifo_seq=17' not in stages or 'name=stopped' not in stages or 'faulted=0' not in stages: die('RT-CDM completion/stop evidence drift')
    seq=[]
    for m in re.finditer(r'ipp-seq\[(\d+)\]=([0-9a-fA-F]{8})/([0-9a-fA-F]{8})',dm):
        seq.append({'index':int(m.group(1)),'status':int(m.group(2),16),'actual':int(m.group(3),16)})
    exp=[(0,0x00811dd0,0x00000f00),(1,0x00600cc0,0x00000f00),(2,0x00000cc0,0x00000f00),(3,0x00004ee8,0x0a500f00)]
    got=[(x['index'],x['status'],x['actual']) for x in seq]
    if got!=exp: die('ordered IPP sequence drift '+repr(got))
    for x in seq:
        x['status_hex']=f"0x{x['status']:08x}"; x['bits']=bits(x['status']); x['actual_hex']=f"0x{x['actual']:08x}"; x.update({'actual_geometry':wh(x['actual'])})
        del x['status']; del x['actual']
    required_dm={
      'history':'ipp-history=00e15ff8/00004ee8/4',
      'line_error':'line-error=0a500f00/02c502c0/00000000',
      'crop':'crop=0eff0000/086f0000',
      'measure':'measure=0000001f/08700f00',
      'rx':'pkts=00009098 ecc=00000000 crc=00000000',
      'vfe':'bus=00000000/00000000 bmask=d0000000/00000000',
    }
    for k,v in required_dm.items():
        if v not in dm: die(f'dmesg {k} drift')
    if 'status 0x00811dd0' not in win or 'status 0x00600228' not in win or 'actual=0x08700f00 = 3840x2160' not in win: die('Windows checkpoint content drift')
    if 'raw KD log file was not found' not in win: die('Windows raw-log provenance warning lost')
    cmdline=Path('/proc/cmdline').read_text()
    if 'sp11_entry=7.1.5-sp11-fullio-v19c' not in cmdline: die('not returned to Golden')
    for mod in ('qcom_camss','imx681','ov13858'):
        if Path('/sys/module/'+mod).exists(): die('candidate module still loaded '+mod)
    out={
      'schema':'sp11-e003h-runtime-0050-ordered-first-ipp-geometry-v1','accepted':True,
      'evidence_sha256':EXPECTED,
      'execution':{'helper_invocations':1,'helper_result':'ETIMEDOUT surfaced as write trigger: Connection timed out / RUN_RC=1','same_boot_retry':False,'qc10c_output':False,'golden_return_verified':True,'sensor_runtime_suspended_after':True,'camss_runtime_suspended_after':True,'rtcdm_fifo_last':17,'rtcdm_faulted':False},
      'linux_sequence':seq,
      'windows_checkpoint':{'raw_kd_bytes_local_present':False,'provenance_fail_closed':True,'first_matching_status':'0x00811dd0','first_matching_geometry_state':'width 3840 initialized; height incomplete','first_epoch_status':'0x00600228','first_epoch_actual':'0x08700f00','first_epoch_geometry':{'width':3840,'height':2160}},
      'classification':{
        'first_irq_match_status':True,
        'first_irq_match_geometry_phase':True,
        'linux_first_epoch_status':'0x00600cc0',
        'linux_first_epoch_actual':'0x00000f00',
        'linux_first_epoch_geometry':{'width':3840,'height':0},
        'windows_first_epoch_status':'0x00600228',
        'windows_first_epoch_actual':'0x08700f00',
        'windows_first_epoch_geometry':{'width':3840,'height':2160},
        'divergence_boundary':'after the matching first RUP_DONE IRQ 0x00811dd0 and by the immediately following Epoch0/1-bearing IRQ',
        'linux_later_line_error_actual':'0x0a500f00',
        'linux_later_line_error_geometry':{'width':3840,'height':2640},
        'vertical_crop_active_by_first_epoch_on_windows':True,
        'vertical_crop_active_by_first_epoch_on_linux':False,
        'sensor_timing_delta_justified':False,
        'speculative_crop_register_write_justified':False,
      },
      'next_gate':'Statically audit the exact RUP_DONE-to-first-Epoch ownership transition, especially any Linux-only CSID +0x18 REG_UPDATE_CMD write after RUP_DONE. Do not add a new crop/register command until that ownership is closed.'
    }
    print(json.dumps(out,indent=2,sort_keys=True))
if __name__=='__main__': main()
