#!/usr/bin/env python3
from pathlib import Path
import json,re
D=Path(__file__).resolve().parent; O=D/'runtime-output'; F=O/'FRONT-SHADOW.txt'
def need(v,m):
    if not v: raise AssertionError(m)
t=F.read_text()
# 27 video frames and exact route/suspend evidence are checked by run-once; verify stored sequence too.
dq=[int(x) for x in re.findall(r'DQBUF\d+_INDEX=\d+ BYTESUSED=\d+ SEQUENCE=(\d+)',t)]
need(dq==list(range(27)),('sequences',dq))
# Exactly one guarded G4 allow and exactly one physical source4 write.
a=re.findall(r'PROD_G4_STARTUP_FILL_ALLOW SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) CONV=(\d+) CAP=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+)',t)
need(len(a)==1,('g4 allow count',a))
need(a[0][0:4]==('4','5','7','7'),('g4 identity',a[0]))
need(int(a[0][4])>=int(a[0][5]),('g4 convergence below cap unexpectedly',a[0]))
need(a[0][5:]==('6133333088','7116','7108','960','1471'),('g4 exact capped tuple',a[0]))
w=re.findall(r'DB_SENSOR_WRITE_OK SOURCE=(\d+) AFTER_G=(\d+) REQUEST=(\d+) EFFECT_G=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+)',t)
need([x[0] for x in w]==['1','2','3','4'],('writes',w)); need(w[-1]==('4','5','7','7','7116','7108','960','1471'),('g4 write',w[-1]))
# New accounting line: 4 ioctls, one startup fill, zero later writes, 22 later shadows.
m=re.search(r'PROD_NATIVE_SCHEDULE_PASS ACCEPTED_G=1\.\.27 RELEASED_SOURCES=G1\.\.G26 POLICY=g4-startup-fill-shadow CONTROL_IOCTLS=(\d+) STARTUP_FILL_WRITES=(\d+) LATER_NATIVE_WRITES=(\d+) LATER_SHADOW=(\d+) POLICY_DISABLED_SHADOW=(\d+) CAP_ACTIVE_SHADOW=(\d+) UNCHANGED_SHADOW=(\d+) ALREADY_APPLIED_SHADOW=(\d+) HORIZON_SHADOW=(\d+) PENDING=G27 APPLY_EFFECT_MAX=G27',t)
need(m,'schedule'); io,sf,lw,ls,pd,ca,un,aa,ho=map(int,m.groups()); need((io,sf,lw,ls)==(4,1,0,22),(io,sf,lw,ls)); need(pd+ca+un+aa+ho==ls,'shadow accounting'); need(ho==2,'horizon')
# Later decision-4 opportunities are observation only under this policy.
apply=[tuple(map(int,x)) for x in re.findall(r'PROD_POST_G3_POLICY_SHADOW SOURCE=(\d+) AFTER_G=(\d+) POLICY=g4-startup-fill-shadow CONV=(\d+) CAP=(\d+) FLL=(\d+) EXP=(\d+) AGAIN=(\d+) DGAIN=(\d+)',t)]
shadow=[tuple(map(int,x)) for x in re.findall(r'HB_NATIVE_CAP_RELEASE_SHADOW SOURCE=(\d+) AFTER_G=(\d+) DECISION=(\d+) CONV=(\d+) CAP=(\d+)',t)]
horizon=[tuple(map(int,x)) for x in re.findall(r'HC_CAP_RELEASE_HORIZON_SHADOW SOURCE=(\d+) AFTER_G=(\d+) CONV=(\d+) CAP=(\d+)',t)]
need(all(s>=5 for s,*_ in apply),'no G4 policy shadow'); need(all(s>=5 for s,*_ in shadow),'no G4 HA shadow'); need([x[0] for x in horizon]==[25,26],horizon)
# Kernel and physical-state gates.
dmesg=(D/'DMESG.txt').read_text(errors='replace'); need(not re.search(r'BUG:|Oops:|Kernel panic|Call trace:',dmesg,re.I),'kernel health')
for f in ('PRE-STREAM-SUSPEND.txt','POST-STREAM-SUSPEND.txt'):
    need((O/f).read_text().count('SUSPEND=PASS')==3,f)
need((O/'FINAL-NEUTRAL.txt').is_file(),'final route')
status='PASS_G4_STARTUP_FILL_APPLY_OPPORTUNITY_OBSERVED' if apply else 'PASS_G4_STARTUP_FILL_NO_LATER_APPLY_OPPORTUNITY'
res={'schema':'sp11-camera-e004el-g4-startup-fill-shadow-observation-v1','status':status,'candidate_consumed':True,'same_boot_retry_performed':False,'synthetic_control_delta':False,'startup_fill_write_source':4,'startup_fill_write_count':sf,'later_native_writes':lw,'control_ioctls':io,'policy_disabled_shadow_count':pd,'cap_active_shadow_count':ca,'unchanged_shadow_count':un,'already_applied_shadow_count':aa,'horizon_shadow_count':ho,'apply_one_native_sources':[x[0] for x in apply],'apply_one_native_rows':[{'source':x[0],'after_g':x[1],'conv':x[2],'cap':x[3],'fll':x[4],'exp':x[5],'again':x[6],'dgain':x[7]} for x in apply],'shadow_decisions':[{'source':x[0],'decision':x[2],'conv':x[3],'cap':x[4]} for x in shadow],'front_frames':27,'front_sequences':dq,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'kernel_health':'PASS','all_three_suspended_before':True,'all_three_suspended_after':True,'final_route_state':'neutral'}
(D/'ATTEMPT1-OBSERVATION.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print('E004EL_OBSERVATION='+status+' APPLY_SOURCES='+(','.join(map(str,res['apply_one_native_sources'])) if apply else 'NONE'))
print(f'E004EL_COUNTS IOCTLS={io} STARTUP_FILL={sf} LATER_WRITES={lw} POLICY_DISABLED={pd} CAP_ACTIVE={ca} UNCHANGED={un} HORIZON={ho}')
