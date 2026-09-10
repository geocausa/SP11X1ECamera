#!/usr/bin/env python3
from pathlib import Path
import hashlib, json, re

D=Path(__file__).resolve().parent
O=D/'runtime-output'
def need(v,m):
    if not v: raise AssertionError(m)
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

run=(O/'RUN.txt').read_text(errors='replace'); dmesg=(D/'DMESG.txt').read_text(errors='replace'); tx=(O/'CONTROL-TRANSACTION.txt').read_text(errors='replace')
need('HELPER_RC=0' in run,'helper rc')
need('STREAMON_OK_ASYNC' in run and 'STREAMOFF_OK' in run,'stream lifecycle')
need('DB_AEC_SCHEDULE_PASS ACCEPTED_G=1..6 WRITES=3 RELEASE=G1@G2,G2@G3,G3@G4 EFFECT=G4,G5,G6' in run,'schedule pass marker')
need('PINNED_FOR_REBOOT:' not in run,'helper pinned')
for bad in ('DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','DB_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL'):
    need(bad not in run,bad)
for i in range(6):
    need(re.search(rf'DQBUF{i}_INDEX=\d+ BYTESUSED=7778304 SEQUENCE={i}\b',run),f'dqbuf{i}')
    need(f'DB_VIDEO_COMPLETION_PUBLISH G={i+1}' in run,f'video completion G{i+1}')
    need(re.search(rf'TLBG_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=61472\b',run),f'tlbg{i}')
    need(re.search(rf'STATS3A_READ{i}_GENERATION={i+1} SOURCE_SEQ={i+1} SLOT={i&1} BYTES=331840\b',run),f'stats3a{i}')

accept=[]
for m in re.finditer(r'DB_AEC_ACCEPT G=(\d+) REQUEST=(\d+) FLL=(\d+) VB=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) RELEASED_AT_G=(\d+) RELEASE_SOURCE=(\d+) EFFECT=(\d+)',run):
    accept.append(tuple(map(int,m.groups())))
need(len(accept)==6,'six AEC accepts')
for idx,row in enumerate(accept,1):
    g,request,fll,vb,exp,again,dgain,released_at,source,effect=row
    need(g==idx and request==g+3,f'ownership G{g}')
    need(fll>=2160 and vb==fll-2160 and exp>=4 and exp<=((fll-4)&~1),f'control geometry G{g}')
    need(0<=again<=0x3c0 and 0x100<=dgain<=0xf00,f'gain geometry G{g}')
    if g==1 or g>=5: need((released_at,source,effect)==(0,0,0),f'no release G{g}')
    else: need((released_at,source,effect)==(g,g-1,g+2),f'release relation G{g}')

writes=[]
pat=r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+) START_NS=(\d+) END_NS=(\d+) ELAPSED_NS=(\d+) COMPLETED_G=(\d+)'
for m in re.finditer(pat,run): writes.append(tuple(map(int,m.groups())))
need(len(writes)==3,'exactly three sensor writes')
for n,row in enumerate(writes,1):
    source,after,request,effect,fll,exp,again,dgain,start_ns,end_ns,elapsed_ns,completed_g=row
    need((source,after,request,effect)==(n,n+1,n+3,n+3),f'write schedule source{n}')
    need(end_ns>=start_ns and elapsed_ns==end_ns-start_ns,f'write timing source{n}')
    need(completed_g==after,f'exact DQBUF window source{n}')
    gate=re.search(rf'DB_VIDEO_GATE_PASS SOURCE={source} AFTER_G={after} COMPLETED_G=(\d+)',run)
    need(gate and int(gate.group(1))==after,f'dqbuf gate source{source}')
    needle=f'FLL={fll} exposure={exp} again=0x{again:03x} dgain=0x{dgain:04x} ret=0'
    need(needle in tx,f'hardware transaction source{source}: {needle}')

pre=(O/'CONTROLS-AFTER.txt').read_text(errors='replace')
for x in ('vertical_blanking: 1402','exposure: 3554','analogue_gain: 0','digital_gain: 256'): need(x in pre,'bootstrap '+x)
need('FLL=3562 exposure=3554 again=0x000 dgain=0x0100 ret=0' in tx,'bootstrap hardware transaction')
post=(O/'CONTROLS-POST-AEC.txt').read_text(errors='replace')
last=writes[-1]; _,_,_,_,lfll,lexp,lagain,ldgain,*_=last
for x in (f'vertical_blanking: {lfll-2160}',f'exposure: {lexp}',f'analogue_gain: {lagain}',f'digital_gain: {ldgain}'): need(x in post,'post control '+x)
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic'): need(bad.lower() not in dmesg.lower(),'kernel health '+bad)
producer=json.loads((O/'producer/RESULT.json').read_text()); need(producer['status']=='PASS','IQ producer status')
need([(r['generation'],r['request_target']) for r in producer['rows']]==[(1,None),(2,5),(3,6)],'IQ producer request association')
need(producer['rows'][1].get('submitted_live') is True and producer['rows'][2].get('submitted_live') is True,'IQ R5/R6 live')
hashes={'qc10c':[],'tlbg':[],'stats3a':[]}
for i in range(6):
    for key,prefix,size in [('qc10c','QC10C',7778304),('tlbg','TLBG',61472),('stats3a','STATS3A',331840)]:
        p=O/f'{prefix}-{i}.bin'; need(p.is_file() and p.stat().st_size==size,f'{prefix}-{i} file'); hashes[key].append(sha(p))
result={
 'schema':'sp11-e003i-dp-bounded-native-aec-cap-sensor-loop-live-v1','status':'PASS_CAPTURE_DP_CAP',
 'bootstrap':{'frame_length_lines':3562,'vertical_blanking':1402,'exposure_lines':3554,'analogue_gain_code':0,'digital_gain_code':256},
 'generations':[{'generation':r[0],'request_frame':r[1],'frame_length_lines':r[2],'vertical_blanking':r[3],'exposure_lines':r[4],'analogue_gain_code':r[5],'digital_gain_code':r[6],'released_at_generation':r[7],'release_source_generation':r[8],'expected_effect_generation':r[9]} for r in accept],
 'writes':[{'source_generation':r[0],'write_after_generation':r[1],'request_frame':r[2],'expected_effect_generation':r[3],'frame_length_lines':r[4],'exposure_lines':r[5],'analogue_gain_code':r[6],'digital_gain_code':r[7],'start_ns':r[8],'end_ns':r[9],'elapsed_ns':r[10],'completed_generation_after_ioctl':r[11]} for r in writes],
 'write_count':3,'dqbuf_exact_window_gate':True,'release_before_current_generation_aec':True,'streamoff':True,'kernel_health':'PASS','same_boot_retry_performed':False,'capture_sha256':hashes,'golden_return_required':True,
 'scope':'bounded sensor-side AEC only; residual ISP gain is computed by CQ but not applied by DB'
}
(O/'LIVE-RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print('DB_LIVE_GENERATIONS=6'); print('DB_LIVE_WRITES=3')
for r in writes: print('DB_LIVE_WRITE source=%d after=%d request=%d effect=%d FLL=%d EXP=%d AGAIN=%d DGAIN=%d elapsed_ns=%d'% (r[0],r[1],r[2],r[3],r[4],r[5],r[6],r[7],r[10]))
print('DB_DQBUF_EXACT_WINDOWS=3/3 PASS'); print('DB_HARDWARE_TRANSACTIONS=bootstrap+3 matched'); print('DB_STREAMOFF=PASS KERNEL_HEALTH=PASS'); print('DB_CAPTURE_VERIFY=PASS')
