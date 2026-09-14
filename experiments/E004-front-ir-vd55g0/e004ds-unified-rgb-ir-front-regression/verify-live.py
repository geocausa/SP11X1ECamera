#!/usr/bin/env python3
from pathlib import Path
import json,re,subprocess
D=Path(__file__).resolve().parent;O=D/'runtime-output'
def need(v,m):
    if not v:raise AssertionError(m)
need((D/'ATTEMPT1-CONSUMED.marker').is_file(),'consumed');need(not (D/'ATTEMPT1-FAILURE.json').exists(),'failure exists')
for p,e in ((D/'LOAD-MEDIA.txt','neutral'),(O/'ROUTE-FRONT-ON.txt','front-only'),(O/'FINAL-NEUTRAL.txt','neutral')):
 cp=subprocess.run([str(D/'route-state.py'),str(p),'--expect',e],text=True,capture_output=True);need(cp.returncode==0,p.name+' '+cp.stdout+cp.stderr)
media=(D/'LOAD-MEDIA.txt').read_text(errors='replace')
for ent in ('sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)','ov13858 3-0010 (1 pad, 1 link, 0 routes)','imx681 1-0010 (1 pad, 1 link, 0 routes)'):need(ent in media,'entity '+ent)
for ff,prefix in ((O/'PRE-STREAM-SUSPEND.txt','PRE_STREAM'),(O/'POST-STREAM-SUSPEND.txt','POST_STREAM')):
 t=ff.read_text()
 for x in ('IR','REAR','FRONT'):need(f'{x}_{prefix}_SUSPEND=PASS' in t,x+' '+prefix)
t=(O/'FRONT-F1.txt').read_text(errors='replace')
for tok in ('FRONT_LAUNCHER_RC=0','PROD_POST_G3_POLICY=shadow','STREAMON_OK_ASYNC','STREAMOFF_OK','E003I_GM_PRODUCER=PASS'):need(tok in t,tok)
for bad in ('PINNED_FOR_REBOOT:','DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','HB_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','EN_GAIN_FEED_FAIL','E003I_GM_PRODUCER=FAIL','GN_DQBUF_MISMATCH'):need(bad not in t,bad)
dq=[int(x) for x in re.findall(r'^DQBUF\d+_INDEX=\d+ BYTESUSED=\d+ SEQUENCE=(\d+)$',t,re.M)];need(dq==list(range(27)),'dq '+repr(dq))
m=re.search(r'PROD_NATIVE_SCHEDULE_PASS .*LATER_NATIVE_WRITES=(\d+)',t);need(m and int(m.group(1))==0,'native writes')
prod=json.loads((O/'front1/producer/RESULT.json').read_text());need(prod['status']=='PASS' and len(prod['rows'])==24,'producer')
counts={'triangle':0,'centroid':0,'two_vertex':0}
for row in prod['rows']:
 mode=row.get('awb_selection_mode');need(mode in counts,'AWB mode '+repr(mode));counts[mode]+=1
need(subprocess.check_output(['sudo','-n','cat','/sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity'],text=True).strip()=='Y','CAMSS param')
log=(D/'DMESG.txt').read_text(errors='replace')
need('SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596' in log,'IR bind')
need('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue' in log,'front completion')
need(len([x for x in log.splitlines() if 'AM request controls:' in x])>=4,'front controls')
for bad in ('E004J_CSIPHY0_DPHY_WINDOWS_PARITY','E004T_','SP11_VD55G0_NATIVE_STREAM_BLOCK','ILLUMINATION_ON','TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic','Unhandled fault','WARNING:','Call trace:'):need(bad.lower() not in log.lower(),'forbidden '+bad)
res={'schema':'sp11-camera-e004ds-attempt1-pass-v1','status':'PASS_FRONT_RGB_UNDER_THREE_CAMERA_AUTHORITY','candidate_consumed':True,'same_boot_retry_performed':False,'golden_return_required':True,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'three_sensor_entities_bound':True,'front_frames':27,'front_sequences':dq,'front_post_g3_policy':'shadow','front_post_g3_native_writes':0,'awb_selection_modes':counts,'awb_fallback_rows':counts['centroid']+counts['two_vertex'],'all_three_runtime_suspended_before':True,'all_three_runtime_suspended_after':True,'final_route_state':'neutral','camss_e004j_parameter_armed':True,'csiphy0_ir_gate_selected':False,'rear_stream_performed':False,'ir_stream_performed':False,'illumination_performed':False,'linux_secureisp':False,'kernel_health':'PASS'}
(D/'ATTEMPT1-PASS.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print('E004DS_VERIFY=PASS FRONT_R27=27 FINAL=NEUTRAL AWB_MODES='+json.dumps(counts,sort_keys=True))
print('E004DS_COEXIST=THREE_BOUND IR_GATE_SELECTED=NO REAR_STREAM=NO IR_STREAM=NO ILLUMINATION=NO SECUREISP=NO')
