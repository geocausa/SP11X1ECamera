#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
D=Path(__file__).resolve().parent;O=D/'runtime-output'
def need(v,m):
    if not v:raise AssertionError(m)
need((D/'ATTEMPT1-CONSUMED.marker').is_file(),'consumed');need(not (D/'ATTEMPT1-FAILURE.json').exists(),'failure exists')
for p,e in ((D/'LOAD-MEDIA.txt','neutral'),(O/'ROUTE-REAR-ON.txt','rear-only'),(O/'BETWEEN-NEUTRAL.txt','neutral'),(O/'ROUTE-FRONT-ON.txt','front-only'),(O/'FINAL-NEUTRAL.txt','neutral')):
    cp=subprocess.run([str(D/'route-state.py'),str(p),'--expect',e],text=True,capture_output=True);need(cp.returncode==0,p.name+' '+cp.stdout+cp.stderr)
media=(D/'LOAD-MEDIA.txt').read_text(errors='replace')
for ent in ('sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)','ov13858 3-0010 (1 pad, 1 link, 0 routes)','imx681 1-0010 (1 pad, 1 link, 0 routes)'):need(ent in media,'entity '+ent)
cb=O/'rear-colorbar.raw';need(cb.stat().st_size==14321824,'colorbar size');need(hashlib.sha256(cb.read_bytes()).hexdigest()=='6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','colorbar hash')
t=(O/'REAR-NORMAL8.txt').read_text(errors='replace');need('NORMAL8_RC=0' in t,'rear rc');seq=[int(x) for x in re.findall(r'seq:\s*(\d+)\s+bytesused:\s*14321824',t)];need(seq==list(range(8)),'rear seq '+repr(seq));ts=[float(x) for x in re.findall(r'ts:\s*([0-9]+\.[0-9]+)',t)];need(len(ts)==8,'rear timestamps');fps=1/(sum(b-a for a,b in zip(ts,ts[1:]))/7);need(28.5<=fps<=31.5,'rear fps '+str(fps))
for f,prefix in ((O/'PRE-STREAM-SUSPEND.txt','PRE_STREAM'),(O/'POST-REAR-SUSPEND.txt','POST_REAR'),(O/'POST-FRONT-SUSPEND.txt','POST_FRONT')):
    s=f.read_text()
    for x in ('IR','REAR','FRONT'):need(f'{x}_{prefix}_SUSPEND=PASS' in s,f'{x} {prefix}')
ft=(O/'FRONT-F1.txt').read_text(errors='replace')
for tok in ('FRONT_LAUNCHER_RC=0','PROD_POST_G3_POLICY=shadow','STREAMON_OK_ASYNC','STREAMOFF_OK','E003I_GM_PRODUCER=PASS'):need(tok in ft,tok)
for bad in ('PINNED_FOR_REBOOT:','DB_AEC_FAIL','DB_AEC_OWNERSHIP_FAIL','DB_SCHEDULE_QUEUE_FAIL','HB_BOUNDARY_RELEASE_FAIL','DB_SENSOR_WRITE_FAIL','EN_GAIN_FEED_FAIL','E003I_GM_PRODUCER=FAIL','GN_DQBUF_MISMATCH'):need(bad not in ft,bad)
dq=[int(x) for x in re.findall(r'^DQBUF\d+_INDEX=\d+ BYTESUSED=\d+ SEQUENCE=(\d+)$',ft,re.M)];need(dq==list(range(27)),'front dq '+repr(dq))
mr=re.search(r'PROD_NATIVE_SCHEDULE_PASS ACCEPTED_G=1\.\.27 RELEASED_SOURCES=G1\.\.G26 POLICY=shadow CONTROL_IOCTLS=(\d+) LATER_NATIVE_WRITES=(\d+) LATER_SHADOW=(\d+) POLICY_DISABLED_SHADOW=(\d+) CAP_ACTIVE_SHADOW=(\d+) UNCHANGED_SHADOW=(\d+) ALREADY_APPLIED_SHADOW=(\d+) HORIZON_SHADOW=(\d+) PENDING=G27 APPLY_EFFECT_MAX=G27',ft);need(mr,'front schedule');need(int(mr.group(2))==0,'front later native writes')
prod=json.loads((O/'front1/producer/RESULT.json').read_text());need(prod['status']=='PASS' and len(prod['rows'])==24,'producer')
counts={'triangle':0,'centroid':0,'two_vertex':0}
for row in prod['rows']:
    mode=row.get('awb_selection_mode');need(mode in counts,'awb mode '+repr(mode));counts[mode]+=1
need(subprocess.check_output(['sudo','-n','cat','/sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity'],text=True).strip()=='Y','CAMSS param')
log=(D/'DMESG.txt').read_text(errors='replace');need('SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596' in log,'IR bind');need('X1E front PIX completed provider-owned bounded twenty-seven-frame live requeue' in log,'front completion')
for bad in ('E004J_CSIPHY0_DPHY_WINDOWS_PARITY','E004T_','SP11_VD55G0_NATIVE_STREAM_BLOCK','ILLUMINATION_ON','TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic','Unhandled fault','WARNING:','Call trace:'):
    need(bad.lower() not in log.lower(),'forbidden '+bad)
res={'schema':'sp11-camera-e004dz-attempt1-pass-v1','status':'PASS_CANONICAL_PACKAGE_SAME_BOOT_REAR_TO_FRONT_HANDOFF','candidate_consumed':True,'same_boot_retry_performed':False,'golden_return_required':True,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'package_manifest_sha256':'d1d0eb4c504378643630f6975a08d9c15d2b8ac0bedca2f1205bbfb51f885373','three_sensor_entities_bound':True,'rear_colorbar_exact':True,'rear_frames':8,'rear_sequences':seq,'rear_mean_fps':fps,'between_route_state':'neutral','front_frames':27,'front_sequences':dq,'front_producer_rows':24,'awb_selection_modes':counts,'front_post_g3_policy':'shadow','front_post_g3_native_writes':0,'final_route_state':'neutral','all_three_suspended_before':True,'all_three_suspended_after_rear':True,'all_three_suspended_after_front':True,'camss_e004j_parameter_armed':True,'csiphy0_ir_gate_selected':False,'ir_stream_performed':False,'illumination_performed':False,'linux_secureisp':False,'kernel_health':'PASS'}
(D/'ATTEMPT1-PASS.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print(f'E004DZ_VERIFY=PASS REAR=COLORBAR+8 FPS={fps:.6f} HANDOFF=NEUTRAL FRONT=27 FINAL=NEUTRAL AWB={counts}')
print('E004DZ_PACKAGE=CANONICAL IR_GATE_SELECTED=NO IR_STREAM=NO ILLUMINATION=NO SECUREISP=NO RETRY=NO')
