#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,time
D=Path(__file__).resolve().parent; O=D/'runtime-output'
def need(v,m):
    if not v: raise AssertionError(m)
need((D/'ATTEMPT1-CONSUMED.marker').is_file(),'consumed')
for n in (1,2,3):
    for f,e in [(f'ROUTE-R{n}-ON.txt','rear-only'),(f'NEUTRAL-AFTER-R{n}.txt','neutral'),(f'ROUTE-F{n}-ON.txt','front-only'),(f'NEUTRAL-AFTER-F{n}.txt','neutral')]:
        cp=subprocess.run([str(D/'route-state.py'),str(O/f),'--expect',e],text=True,capture_output=True); need(cp.returncode==0,f+cp.stdout+cp.stderr)
cp=subprocess.run([str(D/'route-state.py'),str(O/'FINAL-NEUTRAL.txt'),'--expect','neutral'],text=True,capture_output=True);need(cp.returncode==0,'final neutral')
cb=O/'rear-colorbar.raw'; need(cb.stat().st_size==14321824,'colorbar size'); need(hashlib.sha256(cb.read_bytes()).hexdigest()=='6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','colorbar hash')
rear_fps=[]
for n in (1,2,3):
    t=(O/f'REAR-R{n}-NORMAL8.txt').read_text(errors='replace'); need('NORMAL8_RC=0' in t,f'rear{n} rc')
    seq=[int(x) for x in re.findall(r'seq:\s*(\d+)\s+bytesused:\s*14321824',t)]; need(seq==list(range(8)),f'rear{n} seq {seq}')
    ts=[float(x) for x in re.findall(r'ts:\s*([0-9]+\.[0-9]+)',t)]
    if len(ts)==8:
        fps=1/(sum(b-a for a,b in zip(ts,ts[1:]))/7); need(28.5<=fps<=31.5,f'rear{n} fps {fps}'); rear_fps.append(fps)
    need('REAR_RUNTIME_SUSPEND=PASS' in (O/f'REAR-R{n}-SUSPEND.txt').read_text(),f'rear{n} suspend')
front_frames=[]
for n in (1,2,3):
    t=(O/f'FRONT-F{n}.txt').read_text(errors='replace')
    for tok in ('FRONT_LAUNCHER_RC=0','PROD_POST_G3_POLICY=shadow','STREAMON_OK_ASYNC','STREAMOFF_OK','E003I_GM_PRODUCER=PASS'): need(tok in t,f'front{n} {tok}')
    for bad in ('PINNED_FOR_REBOOT:','DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','HB_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','EN_GAIN_FEED_FAIL','E003I_GM_PRODUCER=FAIL','GN_DQBUF_MISMATCH'): need(bad not in t,f'front{n} {bad}')
    dq=[int(x) for x in re.findall(r'^DQBUF\d+_INDEX=\d+ BYTESUSED=\d+ SEQUENCE=(\d+)$',t,re.M)]; need(dq==list(range(27)),f'front{n} dq {dq}')
    m=re.search(r'PROD_NATIVE_SCHEDULE_PASS .*LATER_NATIVE_WRITES=(\d+)',t); need(m and int(m.group(1))==0,f'front{n} native writes')
    prod=json.loads((O/f'front{n}/producer/RESULT.json').read_text()); need(prod['status']=='PASS' and len(prod['rows'])==24,f'front{n} producer')
    need('FRONT_RUNTIME_SUSPEND=PASS' in (O/f'FRONT-F{n}-SUSPEND.txt').read_text(),f'front{n} suspend')
    front_frames.append(len(dq))
final=(O/'FINAL-SUSPEND.txt').read_text(); need('OV13858_FINAL_SUSPEND=PASS' in final and 'IMX681_FINAL_SUSPEND=PASS' in final,'final suspend')
d=(D/'DMESG.txt').read_text(errors='replace')
for bad in ('TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic','Unhandled fault'): need(bad.lower() not in d.lower(),'kernel '+bad)
need(d.count('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue')>=3,'front completion count')
need(len([x for x in d.splitlines() if 'AM request controls:' in x])>=12,'front control transactions')
res={'schema':'sp11-camera-e004dk-live-v1','status':'PASS_CAPTURE_E004DK_RGB_ALTERNATING_SOAK','runtime_performed':True,'legs':['rear','front','rear','front','rear','front'],'cross_camera_transitions':5,'neutral_between_every_leg':True,'final_route_state':'neutral','rear_streams':3,'rear_frames_each':8,'rear_mean_fps':rear_fps,'rear_colorbar_exact':True,'front_streams':3,'front_frames_each':front_frames,'front_post_g3_policy':'shadow','front_post_g3_native_writes':0,'all_source_runtime_suspend':True,'kernel_health':'PASS','same_boot_retry_performed':False,'golden_return_required':True}
(O/'LIVE-RESULT.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n'); p=dict(res);p.update({'schema':'sp11-camera-e004dk-attempt1-pass-v1','candidate_consumed':True});(D/'ATTEMPT1-PASS.json').write_text(json.dumps(p,indent=2,sort_keys=True)+'\n')
print('E004DK_RGB_SOAK=PASS LEGS=6 TRANSITIONS=5 FINAL=NEUTRAL')
