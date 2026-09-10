#!/usr/bin/env python3
from pathlib import Path
import json, math, re, struct
D=Path(__file__).resolve().parent
O=D/'runtime-output'

def need(x,m):
    if not x: raise AssertionError(m)
def f32(x): return struct.unpack('<f',struct.pack('<f',x))[0]
def axis():
    segs=[(0,127,1.0,1.0),(128,255,2.0,129.5),(256,399,8.0,388.5),(400,479,32.0,1552.5),(480,575,128.0,4160.5),(576,767,256.0,16512.5),(768,895,512.0,65792.5),(896,1023,1024.0,131584.5)]
    out=[]
    for a,b,w,c in segs:
        for i in range(a,b+1):
            x=round((c+(i-a)*w)/1024.0,5)
            if i==1023: x=255.5
            out.append(f32(x))
    need(len(out)==1024,'axis len')
    return out
AX=axis()
run=(O/'RUN.txt').read_text()
need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'stream lifecycle')
need('CY_CONTROL_STEP_AFTER_SEQUENCE=0' in run,'step marker')
m=re.search(r'CY_CONTROL_STEP_AFTER_SEQUENCE=0 START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) VBLANK=1394 EXPOSURE=1000 AGAIN=64 DGAIN=272',run)
need(m,'step timing parse')
step_start,step_end,step_elapsed=map(int,m.groups())
need(step_end>=step_start and step_elapsed==step_end-step_start,'step timing relation')
for i in range(6):
    need(f'DQBUF{i}_INDEX=' in run and f'SEQUENCE={i}' in run,'dq sequence '+str(i))
post=(O/'CONTROLS-POST-STEP.txt').read_text()
for s in ['vertical_blanking: 1394','exposure: 1000','analogue_gain: 64','digital_gain: 272']:
    need(s in post,'post ctrl '+s)
tx=(O/'CONTROL-TRANSACTION.txt').read_text()
need('FLL=3554 exposure=3500 again=0x040 dgain=0x0110 ret=0' in tx,'baseline hw transaction')
step_lines=[x for x in tx.splitlines() if 'FLL=3554 exposure=1000 again=0x040 dgain=0x0110 ret=0' in x]
need(len(step_lines)==1,'exactly one live step transaction')
means=[]; peaks=[]; totals=[]
for i in range(6):
    p=O/f'STATS3A-{i}.bin'; b=p.read_bytes(); need(len(b)==331840,p.name+' size')
    need(struct.unpack_from('<I',b,0)[0]==0x54534133,p.name+' magic')
    g=struct.unpack_from('<Q',b,8)[0]; seq=struct.unpack_from('<I',b,16)[0]
    need(g==i+1 and seq==i+1,p.name+' identity')
    off=0x40+0x14000
    counts=[struct.unpack_from('<I',b,off+4*j)[0]&0x01ffffff for j in range(1024)]
    total=sum(counts); need(total==2073600,p.name+' bhist total')
    mean=sum(float(c)*float(AX[j]) for j,c in enumerate(counts))/total
    peak=max(range(1024),key=lambda j:counts[j])
    totals.append(total); means.append(mean); peaks.append(peak)
base=means[0]
need(base>0.0,'nonzero baseline')
first=None
for g in range(2,7):
    if means[g-1] <= base*0.65:
        first=g; break
need(first is not None,'no significant optical/BHist exposure drop')
need(first<=3,'first affected generation later than configured two-frame bound')
need(max(means[3:]) <= base*0.75,'late frames did not retain exposure drop')
result={
 'schema':'sp11-e003i-cy-bounded-imx681-latch-runtime-v1',
 'status':'PASS_CAPTURE',
 'step':{'after_v4l2_sequence':0,'baseline_exposure':3500,'new_exposure':1000,'vblank':1394,'again':64,'dgain':272,'start_ns':step_start,'end_ns':step_end,'elapsed_ns':step_elapsed,'hardware_step_transaction_count':len(step_lines)},
 'bhist':{'total_pixels':2073600,'means':means,'peak_bins':peaks,'first_significant_drop_generation':first,'drop_threshold_ratio':0.65},
 'mapping':{'v4l2_sequence_to_stats_generation':'generation = sequence + 1','first_optically_affected_generation':first},
 'interpretation':'diagnostic capture only; exact Windows request optical label must combine this hardware boundary with CX/AW scheduling',
 'golden_return_required':True
}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print('CY_STEP_ELAPSED_NS='+str(step_elapsed))
for i,x in enumerate(means,1): print(f'CY_G{i}_BHIST_MEAN={x:.9f} PEAK={peaks[i-1]}')
print('CY_FIRST_SIGNIFICANT_DROP_GENERATION='+str(first))
print('CY_STEP_HW_TRANSACTION_COUNT=1')
print('CY_CAPTURE_VERIFY=PASS')
