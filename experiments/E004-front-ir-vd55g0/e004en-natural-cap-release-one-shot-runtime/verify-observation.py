#!/usr/bin/env python3
from pathlib import Path
import json,re
D=Path(__file__).resolve().parent; O=D/'runtime-output'; F=O/'FRONT-SHADOW.txt'
def need(v,m):
    if not v: raise AssertionError(m)
t=F.read_text()
dq=[int(x) for x in re.findall(r'DQBUF\d+_INDEX=\d+ BYTESUSED=\d+ SEQUENCE=(\d+)',t)]; need(dq==list(range(27)),('sequences',dq))
need('PROD_G4_STARTUP_FILL_ALLOW' not in t,'startup-fill path forbidden')
allow=[tuple(map(int,x)) for x in re.findall(r'HB_NATIVE_CAP_RELEASE_ALLOW SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) CONV=(\d+) CAP=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+)',t)]
writes=[tuple(map(int,x)) for x in re.findall(r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+)',t)]
m=re.search(r'PROD_NATIVE_SCHEDULE_PASS ACCEPTED_G=1\.\.27 RELEASED_SOURCES=G1\.\.G26 POLICY=cap-release-one-shot CONTROL_IOCTLS=(\d+) STARTUP_FILL_WRITES=(\d+) LATER_NATIVE_WRITES=(\d+) LATER_SHADOW=(\d+) POLICY_DISABLED_SHADOW=(\d+) CAP_ACTIVE_SHADOW=(\d+) UNCHANGED_SHADOW=(\d+) ALREADY_APPLIED_SHADOW=(\d+) HORIZON_SHADOW=(\d+) PENDING=G27 APPLY_EFFECT_MAX=G27',t); need(m,'schedule')
io,sf,lw,ls,pd,ca,un,aa,ho=map(int,m.groups()); need(sf==0 and lw in (0,1),'write counts'); need(io==3+lw,'ioctls'); need(ls+lw==23,'release accounting'); need(pd+ca+un+aa+ho==ls,'shadow accounting'); need(ho==2,'horizon')
need(len(allow)==lw,('allow/lw',allow,lw)); need([x[0] for x in writes[:3]]==[1,2,3],writes); need(len(writes)==3+lw,'write total')
if lw:
    a=allow[0]; need(a[0]>=4 and a[0]<=24,'allow source'); need(a[4] < a[5],'allow must be below cap'); need(writes[-1][0]==a[0] and writes[-1][2]==a[2],'write matches allow'); status='PASS_ONE_NATURAL_CAP_RELEASE_WRITE'
else:
    status='PASS_NO_CAP_RELEASE_SCENE_SHIFTED'
dmesg=(D/'DMESG.txt').read_text(errors='replace'); need(not re.search(r'BUG:|Oops:|Kernel panic|Call trace:',dmesg,re.I),'kernel health')
for f in ('PRE-STREAM-SUSPEND.txt','POST-STREAM-SUSPEND.txt'): need((O/f).read_text().count('SUSPEND=PASS')==3,f)
need((O/'FINAL-NEUTRAL.txt').is_file(),'final route')
res={'schema':'sp11-camera-e004en-natural-cap-release-one-shot-observation-v1','status':status,'candidate_consumed':True,'same_boot_retry_performed':False,'synthetic_control_delta':False,'control_ioctls':io,'startup_fill_writes':sf,'later_native_writes':lw,'later_shadow_count':ls,'policy_disabled_shadow_count':pd,'cap_active_shadow_count':ca,'unchanged_shadow_count':un,'already_applied_shadow_count':aa,'horizon_shadow_count':ho,'allow_rows':[{'source':x[0],'after_g':x[1],'request':x[2],'effect_g':x[3],'conv':x[4],'cap':x[5],'fll':x[6],'exp':x[7],'again':x[8],'dgain':x[9]} for x in allow],'front_frames':27,'front_sequences':dq,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'kernel_health':'PASS','all_three_suspended_before':True,'all_three_suspended_after':True,'final_route_state':'neutral'}
(D/'ATTEMPT1-OBSERVATION.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print('E004EN_OBSERVATION='+status+' ALLOW_SOURCES='+(','.join(str(x[0]) for x in allow) if allow else 'NONE'))
print(f'E004EN_COUNTS IOCTLS={io} LATER_WRITES={lw} CAP_ACTIVE={ca} UNCHANGED={un} ALREADY={aa} HORIZON={ho}')
