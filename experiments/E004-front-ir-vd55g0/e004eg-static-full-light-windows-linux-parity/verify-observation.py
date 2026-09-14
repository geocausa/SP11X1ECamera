#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent;O=D/'runtime-output'
def need(v,m):
    if not v: raise AssertionError(m)
need((D/'ATTEMPT1-CONSUMED.marker').is_file(),'consumed');need(not (D/'ATTEMPT1-FAILURE.json').exists(),'failure')
for p,e in ((D/'LOAD-MEDIA.txt','neutral'),(O/'ROUTE-FRONT-ON.txt','front-only'),(O/'FINAL-NEUTRAL.txt','neutral')):
    cp=subprocess.run([str(D/'route-state.py'),str(p),'--expect',e],text=True,capture_output=True);need(cp.returncode==0,p.name)
t=(O/'FRONT-SHADOW.txt').read_text(errors='replace')
for tok in ('FRONT_LAUNCHER_RC=0','PROD_POST_G3_POLICY=shadow','STREAMON_OK_ASYNC','STREAMOFF_OK','E003I_GM_PRODUCER=PASS'): need(tok in t,tok)
dq=[int(x) for x in re.findall(r'^DQBUF\d+_INDEX=\d+ BYTESUSED=\d+ SEQUENCE=(\d+)$',t,re.M)];need(dq==list(range(27)),'dq')
# A true APPLY_ONE_NATIVE opportunity under shadow policy is logged here instead of being written.
apply=[]
for m in re.finditer(r'PROD_POST_G3_POLICY_SHADOW SOURCE=(\d+) AFTER_G=(\d+) POLICY=shadow CONV=(\d+) CAP=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+)',t):
    apply.append(tuple(map(int,m.groups())))
shadow=[]
for m in re.finditer(r'HB_NATIVE_CAP_RELEASE_SHADOW SOURCE=(\d+) AFTER_G=(\d+) DECISION=(\d+) CONV=(\d+) CAP=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+)',t):
    shadow.append(tuple(map(int,m.groups())))
horizon=[tuple(map(int,m.groups())) for m in re.finditer(r'HC_CAP_RELEASE_HORIZON_SHADOW SOURCE=(\d+) AFTER_G=(\d+) CONV=(\d+) CAP=(\d+) EFFECT_G=(\d+)',t)]
need([x[0] for x in horizon]==[25,26],'horizon')
covered=sorted([x[0] for x in apply]+[x[0] for x in shadow]);need(covered==list(range(4,25)),'eligible coverage '+repr(covered))
# Shadow-only run must never perform a later write.
mr=re.search(r'PROD_NATIVE_SCHEDULE_PASS ACCEPTED_G=1\.\.27 RELEASED_SOURCES=G1\.\.G26 POLICY=shadow CONTROL_IOCTLS=(\d+) LATER_NATIVE_WRITES=(\d+) LATER_SHADOW=(\d+) POLICY_DISABLED_SHADOW=(\d+) CAP_ACTIVE_SHADOW=(\d+) UNCHANGED_SHADOW=(\d+) ALREADY_APPLIED_SHADOW=(\d+) HORIZON_SHADOW=(\d+) PENDING=G27 APPLY_EFFECT_MAX=G27',t);need(mr,'schedule')
ci,lw,ls,pds,cas,us,aas,hs=map(int,mr.groups());need(lw==0,'later write occurred');need(pds==len(apply),'apply count mismatch');need(hs==2,'horizon count')
prod=json.loads((O/'front1/producer/RESULT.json').read_text());need(prod['status']=='PASS' and len(prod['rows'])==24,'producer')
log=(D/'DMESG.txt').read_text(errors='replace')
for bad in ('E004J_CSIPHY0_DPHY_WINDOWS_PARITY','E004T_','SP11_VD55G0_NATIVE_STREAM_BLOCK','ILLUMINATION_ON','WARNING:','Call trace:','Kernel panic','Unhandled fault'):
    need(bad.lower() not in log.lower(),'forbidden '+bad)
for f,prefix in ((O/'PRE-STREAM-SUSPEND.txt','PRE_STREAM'),(O/'POST-STREAM-SUSPEND.txt','POST_STREAM')):
    s=f.read_text()
    for x in ('IR','REAR','FRONT'):need(f'{x}_{prefix}_SUSPEND=PASS' in s,x+' '+prefix)
status='PASS_STATIC_FULL_LIGHTS_APPLY_ONE_NATIVE_AVAILABLE' if apply else 'PASS_STATIC_FULL_LIGHTS_NO_APPLY_ONE_NATIVE'
res={'schema':'sp11-camera-e004eg-fully-lit-shadow-observation-v1','status':status,'candidate_consumed':True,'same_boot_retry_performed':False,'native_write_authorized':False,'native_write_performed':False,'lighting':'static_empty_room_full_lights','boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'front_frames':27,'front_sequences':dq,'apply_one_native_sources':[x[0] for x in apply],'apply_one_native_rows':[{'source':x[0],'after_g':x[1],'conv':x[2],'cap':x[3],'fll':x[4],'exp':x[5],'again':x[6],'dgain':x[7]} for x in apply],'shadow_decisions':[{'source':x[0],'decision':x[2],'conv':x[3],'cap':x[4]} for x in shadow],'policy_disabled_shadow_count':pds,'cap_active_shadow_count':cas,'unchanged_shadow_count':us,'already_applied_shadow_count':aas,'horizon_shadow_count':hs,'later_native_writes':lw,'final_route_state':'neutral','all_three_suspended_before':True,'all_three_suspended_after':True,'kernel_health':'PASS'}
(D/'ATTEMPT1-OBSERVATION.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print('E004EG_OBSERVATION='+status+' APPLY_SOURCES='+','.join(map(str,res['apply_one_native_sources'])) if apply else 'E004EG_OBSERVATION='+status+' APPLY_SOURCES=NONE')
print(f'E004EG_COUNTS POLICY_DISABLED={pds} CAP_ACTIVE={cas} UNCHANGED={us} ALREADY={aas} HORIZON={hs} LATER_WRITES={lw}')
