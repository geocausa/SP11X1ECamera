#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess
D=Path(__file__).resolve().parent; O=D/'runtime-output'
def need(v,m):
    if not v: raise AssertionError(m)
need((D/'ATTEMPT1-CONSUMED.marker').is_file(),'consumed');need(not (D/'ATTEMPT1-FAILURE.json').exists(),'failure exists')
# Route must begin neutral, run rear-only, and finish neutral.
for p,e in ((D/'LOAD-MEDIA.txt','neutral'),(O/'ROUTE-REAR-ON.txt','rear-only'),(O/'FINAL-NEUTRAL.txt','neutral')):
    cp=subprocess.run([str(D/'route-state.py'),str(p),'--expect',e],text=True,capture_output=True);need(cp.returncode==0,p.name+' '+cp.stdout+cp.stderr)
# Three camera entities coexist in the graph.
media=(D/'LOAD-MEDIA.txt').read_text(errors='replace')
for ent in ('sp11-vd55g0 2-0060 (1 pad, 1 link, 0 routes)','ov13858 3-0010 (1 pad, 1 link, 0 routes)','imx681 1-0010 (1 pad, 1 link, 0 routes)'):need(ent in media,'entity '+ent)
# Exact rear oracle regression.
cb=O/'rear-colorbar.raw';need(cb.stat().st_size==14321824,'colorbar size');need(hashlib.sha256(cb.read_bytes()).hexdigest()=='6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','colorbar hash')
t=(O/'REAR-NORMAL8.txt').read_text(errors='replace');need('NORMAL8_RC=0' in t,'normal rc')
seq=[int(x) for x in re.findall(r'seq:\s*(\d+)\s+bytesused:\s*14321824',t)];need(seq==list(range(8)),'sequence '+repr(seq))
ts=[float(x) for x in re.findall(r'ts:\s*([0-9]+\.[0-9]+)',t)];fps=None
if len(ts)==8:
    fps=1/(sum(b-a for a,b in zip(ts,ts[1:]))/7);need(28.5<=fps<=31.5,'fps '+str(fps))
for f,prefix in ((O/'PRE-STREAM-SUSPEND.txt','PRE_STREAM'),(O/'POST-STREAM-SUSPEND.txt','POST_STREAM')):
    s=f.read_text();
    for x in ('IR','REAR','FRONT'):need(f'{x}_{prefix}_SUSPEND=PASS' in s,f'{x} {prefix}')
# The IR gate is armed but MUST NOT select on rear CSIPHY1.
need(subprocess.check_output(['sudo','-n','cat','/sys/module/qcom_camss/parameters/e004j_ir_dphy_windows_parity'],text=True).strip()=='Y','CAMSS param')
log=(D/'DMESG.txt').read_text(errors='replace')
need('SP11_VD55G0_NATIVE_WINDOWS_STATE=PASS writes=596' in log,'IR bind authority')
for bad in ('E004J_CSIPHY0_DPHY_WINDOWS_PARITY','E004T_RECEIVER_','E004T_CSIPHY0_','MODE_SELECT=1 front transmission started','SP11_VD55G0_NATIVE_STREAM_BLOCK','ILLUMINATION_ON','TLB sync timed out -- SMMU may be deadlocked','vblank wait timed out','Internal error: Oops','soft lockup','Kernel panic','Unhandled fault','WARNING:','Call trace:'):
    need(bad.lower() not in log.lower(),'forbidden dmesg '+bad)
res={'schema':'sp11-camera-e004dq-attempt1-pass-v1','status':'PASS_REAR_RGB_UNDER_THREE_CAMERA_AUTHORITY','candidate_consumed':True,'same_boot_retry_performed':False,'golden_return_required':True,'boot_id':Path('/proc/sys/kernel/random/boot_id').read_text().strip(),'three_sensor_entities_bound':True,'rear_colorbar_exact':True,'rear_colorbar_sha256':'6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','rear_frames':8,'rear_sequences':seq,'rear_mean_fps':fps,'final_route_state':'neutral','all_three_runtime_suspended_before':True,'all_three_runtime_suspended_after':True,'camss_e004j_parameter_armed':True,'csiphy0_ir_gate_selected':False,'front_stream_performed':False,'ir_stream_performed':False,'receiver_harness_performed':False,'illumination_performed':False,'linux_secureisp':False,'kernel_health':'PASS'}
(D/'ATTEMPT1-PASS.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
print('E004DQ_VERIFY=PASS REAR_COLORBAR=EXACT NORMAL8=0..7 FPS='+('NA' if fps is None else f'{fps:.6f}')+' FINAL=NEUTRAL')
print('E004DQ_COEXIST=THREE_BOUND IR_GATE_SELECTED=NO FRONT_STREAM=NO IR_STREAM=NO ILLUMINATION=NO SECUREISP=NO')
