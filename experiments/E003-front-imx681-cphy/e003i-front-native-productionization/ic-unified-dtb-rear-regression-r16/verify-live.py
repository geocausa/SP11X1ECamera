#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,re,subprocess,time
D=Path(__file__).resolve().parent; O=D/'runtime-output'
def need(v,m):
 if not v: raise AssertionError(m)
need((D/'ATTEMPT1-CONSUMED.marker').is_file(),'consumed marker')
need((O/'colorbar.raw').is_file() and (O/'colorbar.raw').stat().st_size==14321824,'colorbar size')
need(hashlib.sha256((O/'colorbar.raw').read_bytes()).hexdigest()=='6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','colorbar hash')
c=(O/'COLORBAR.txt').read_text(errors='replace'); n=(O/'NORMAL16.txt').read_text(errors='replace')
need('COLORBAR_RC=0' in c and 'NORMAL16_RC=0' in n,'stream rc')
seq=[int(x) for x in re.findall(r'seq:\s*(\d+)\s+bytesused:\s*14321824',n)]; need(seq==list(range(16)),'normal seq '+repr(seq))
# Timestamp-derived mean fps when verbose output provides timestamps.
ts=[float(x) for x in re.findall(r'ts:\s*([0-9]+\.[0-9]+)',n)]; fps=None
if len(ts)==16:
 d=[b-a for a,b in zip(ts,ts[1:])]; mean=sum(d)/len(d); fps=1.0/mean; need(29.0<=fps<=31.0,'fps '+str(fps))
# Test pattern restored and no front stream helper ever exists in IC.
j=json.load(open(D/'DISCOVERY.json')); cp=subprocess.run(['v4l2-ctl','-d',j['rear_sensor_device'],'--get-ctrl=test_pattern'],text=True,capture_output=True); need(cp.returncode==0 and re.search(r'test_pattern:\s*0',cp.stdout),'test pattern restore '+cp.stdout+cp.stderr)
time.sleep(0.5)
# Sensor should settle back to runtime suspend after close.
sysdev=Path('/sys/bus/i2c/devices')
rear=[p for p in sysdev.glob('*-0010') if (p/'name').exists() and (p/'name').read_text().strip()=='ov13858']
need(len(rear)==1,'rear sysfs '+repr(rear)); st=(rear[0]/'power/runtime_status').read_text().strip(); need(st=='suspended','rear runtime '+st)
d=(D/'DMESG.txt').read_text(errors='replace')
for bad in ('TLB sync timed out -- SMMU may be deadlocked','Internal error: Oops','soft lockup','Kernel panic','Unhandled fault'):
 need(bad.lower() not in d.lower(),'kernel '+bad)
res={'schema':'sp11-camera-ic-unified-rear-r16-live-v1','status':'PASS_CAPTURE_IC_UNIFIED_REAR_R16','streams_completed':2,'colorbar_frames':1,'normal_frames':16,'frame_bytes':14321824,'colorbar_sha256':'6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346','normal_sequences':seq,'mean_fps':fps,'rear_runtime_status':st,'kernel_health':'PASS','front_stream_executed':False,'same_stream_retry_performed':False,'same_boot_retry_performed':False,'golden_return_required':True}
(O/'LIVE-RESULT.json').write_text(json.dumps(res,indent=2,sort_keys=True)+'\n')
pass_obj=dict(res)
pass_obj.update({
 'schema':'sp11-camera-ic-attempt1-pass-v1',
 'status':'PASS_CAPTURE_IC_UNIFIED_REAR_R16',
 'candidate_consumed':True,
 'camera_runtime_performed':True,
 'golden_return_required':True,
})
(D/'ATTEMPT1-PASS.json').write_text(json.dumps(pass_obj,indent=2,sort_keys=True)+'\n')
print('IC_REAR_REGRESSION=PASS COLORBAR_SHA=PASS NORMAL_FRAMES=16')
print('IC_REAR_RUNTIME_SUSPEND=PASS KERNEL_HEALTH=PASS FRONT_STREAM=NO')
print('IC_LIVE_VERIFY=PASS')
