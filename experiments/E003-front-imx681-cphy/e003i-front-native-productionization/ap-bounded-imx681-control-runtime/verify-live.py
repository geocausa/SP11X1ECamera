#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re
HERE=Path(__file__).resolve().parent; O=HERE/'runtime-output'
def need(v,m):
    if not v: raise SystemExit('FAIL: '+m)
def sh(p): return hashlib.sha256(p.read_bytes()).hexdigest()
run=(O/'RUN.txt').read_text(); ctl=(O/'CONTROLS-AFTER.txt').read_text(); tx=(O/'CONTROL-TRANSACTION.txt').read_text(); dmesg=(HERE/'DMESG.txt').read_text()
need('HELPER_RC=0' in run,'helper rc'); need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'stream lifecycle'); need('AO_PAIR_AUDIT_THREAD_READY ORDER=3A_THEN_TLBG TARGETS=1..6' in run,'AO collector ready'); need('PASS: six-frame regression plus producer-derived R5/R6 and paired TL_BG/3A generations 1..6 (AO collector)' in run,'AO helper pass')
for i in range(6):
    need(re.search(rf'DQBUF{i}_INDEX=\d+ BYTESUSED=7778304 SEQUENCE={i}\b',run),f'frame {i}')
    need(re.search(rf'TLBG_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=61472\b',run),f'tlbg {i}')
    need(re.search(rf'STATS3A_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=331840\b',run),f'3a {i}')
need('vertical_blanking: 1394' in ctl and 'exposure: 3500' in ctl and 'analogue_gain: 64' in ctl and 'digital_gain: 272' in ctl,'cached controls')
needle='AM request controls: FLL=3554 exposure=3500 again=0x040 dgain=0x0110 ret=0'; need(needle in tx,'exact AM transaction')
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup'): need(bad.lower() not in dmesg.lower(),f'kernel health: {bad}')
p=json.loads((O/'producer/RESULT.json').read_text()); need(p['status']=='PASS','producer status'); need([(r['generation'],r['request_target']) for r in p['rows']]==[(1,None),(2,5),(3,6)],'producer association'); need(p['rows'][1].get('submitted_live') is True and p['rows'][2].get('submitted_live') is True,'R5/R6 submitted')
frames=[]
for i in range(6):
    f=O/f'QC10C-{i}.bin'; need(f.is_file() and f.stat().st_size==7778304,f'frame file {i}'); frames.append(sh(f))
result={'schema':'sp11-e003i-ap-live-imx681-control-result-v1','status':'PASS_LIVE_CONTROLS_AND_PAIRED_AUDIT','exact_control_transaction':needle,'controls':{'vertical_blanking':1394,'frame_length':3554,'exposure':3500,'analogue_gain_code':64,'digital_gain_code':272},'frame_count':6,'frame_sha256':frames,'paired_generations':[1,2,3,4,5,6],'r5_sha256':sh(O/'producer/R5-dynamic.bin'),'r6_sha256':sh(O/'producer/R6-dynamic.bin'),'kernel_health':'PASS','same_boot_retry':False}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print('AP_LIVE_VERIFY=PASS'); print(json.dumps(result,indent=2))
