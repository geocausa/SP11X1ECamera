#!/usr/bin/env python3
"""E012J bounded rear visible-RGB digital-gain ladder.

Fresh candidate only. Uses only OV13858 standard V4L2 exposure,
analogue_gain and digital_gain controls, never VBLANK/test pattern/IR/raw I2C.
Every tuple is inside current driver-advertised bounds and preserves the
accepted 30-fps frame timing. The ladder stops as soon as output luma is in a
bounded useful range or backs down on clipping. It leaves the selected tuple
active only long enough for one private optical render; a separate restore
action requires exact readback and returns the original baseline.
"""
from __future__ import annotations
import argparse,json,os,re,subprocess,time
from pathlib import Path
ROOT=Path('/var/lib/sp11-camera-rgb')
NAMES=('exposure','analogue_gain','digital_gain')
PROFILES=[
 {'name':'baseline','exposure':1600,'analogue_gain':128,'digital_gain':1024},
 {'name':'mid','exposure':3200,'analogue_gain':1024,'digital_gain':5632},
]
W,H=3840,2160

def cmd(*a:str)->str:
 r=subprocess.run(a,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=8,close_fds=True)
 return r.stdout

def sensor()->str:
 if os.geteuid()!=0 or 'sp11_camera_rgb_product=1' not in Path('/proc/cmdline').read_text().split(): raise RuntimeError('PRODUCT_BOOT_ROOT_REQUIRED')
 d=json.loads((ROOT/'output/UNIFIED.json').read_text());n=d['rear_sensor_device']
 if not re.fullmatch(r'/dev/v4l-subdev[0-9]+',n) or not Path(n).is_char_device(): raise RuntimeError('REAR_SENSOR_NODE_INVALID')
 return n

def read(n:str)->dict[str,int]:
 o={}
 for k in NAMES:
  m=re.fullmatch(rf'{k}:\s*([0-9]+)',cmd('v4l2-ctl','-d',n,'--get-ctrl',k).strip())
  if not m: raise RuntimeError('CONTROL_READBACK_INVALID')
  o[k]=int(m.group(1))
 return o

def bounds(n:str)->dict[str,dict[str,int]]:
 t=cmd('v4l2-ctl','-d',n,'--list-ctrls');o={}
 for line in t.splitlines():
  m=re.match(r'\s*(exposure|analogue_gain|digital_gain)\s+0x[0-9a-f]+\s+\(int\)\s*:',line)
  if not m: continue
  k=m.group(1);z={}
  for f in ('min','max','step'):
   q=re.search(rf'\b{f}=(-?[0-9]+)',line)
   if not q: raise RuntimeError('CONTROL_BOUNDS_INCOMPLETE')
   z[f]=int(q.group(1))
  o[k]=z
 if set(o)!=set(NAMES): raise RuntimeError('CONTROL_BOUNDS_MISSING')
 for p in PROFILES:
  for k in NAMES:
   z=o[k];v=p[k]
   if z['step']<=0 or not z['min']<=v<=z['max'] or (v-z['min'])%z['step']: raise RuntimeError('PROFILE_OUTSIDE_BOUNDS')
 # Fixed current 4K VTS-8 exposure envelope already proven: never alter timing.
 if o['exposure']['max']!=3206: raise RuntimeError('REAR_FIXED_FPS_EXPOSURE_ENVELOPE_DRIFT')
 return o

def set_profile(n:str,p:dict)->None:
 if p not in PROFILES: raise RuntimeError('PROFILE_NOT_PINNED')
 cmd('v4l2-ctl','-d',n,'--set-ctrl',','.join(f'{k}={p[k]}' for k in NAMES))
 if read(n)!={k:p[k] for k in NAMES}: raise RuntimeError('PROFILE_READBACK_MISMATCH')

def measure()->dict:
 import gi
 gi.require_version('Gst','1.0')
 from gi.repository import Gst
 Gst.init(None)
 pipe=Gst.parse_launch(f'v4l2src device=/dev/video90 io-mode=mmap num-buffers=8 ! video/x-raw,format=NV12,width={W},height={H},framerate=30/1 ! appsink name=s sync=false max-buffers=2 drop=false')
 sink=pipe.get_by_name('s');bus=pipe.get_bus();chosen=None;seen=0;begin=time.monotonic()
 try:
  if pipe.set_state(Gst.State.PLAYING)==Gst.StateChangeReturn.FAILURE: raise RuntimeError('LOOPBACK_MEASURE_START_FAILED')
  while seen<8 and time.monotonic()-begin<15:
   sm=sink.emit('try-pull-sample',Gst.SECOND)
   if sm is None:
    if bus.pop_filtered(Gst.MessageType.ERROR): raise RuntimeError('LOOPBACK_MEASURE_GST_ERROR')
    continue
   b=sm.get_buffer()
   if seen==6:
    ok,m=b.map(Gst.MapFlags.READ)
    if not ok: raise RuntimeError('LOOPBACK_MAP_FAILED')
    try: chosen=bytes(m.data)
    finally: b.unmap(m)
   seen+=1
  if seen!=8 or chosen is None or len(chosen)<W*H: raise RuntimeError('LOOPBACK_MEASURE_FRAME_INVALID')
  msg=bus.timed_pop_filtered(3*Gst.SECOND,Gst.MessageType.EOS|Gst.MessageType.ERROR)
  if msg is None or msg.type!=Gst.MessageType.EOS: raise RuntimeError('LOOPBACK_MEASURE_NO_EOS')
 finally: pipe.set_state(Gst.State.NULL)
 y=chosen[:W*H];hist=[0]*256;total=0
 # Full luma histogram is deterministic and still only scalar evidence leaves the frame.
 for v in y: hist[v]+=1;total+=v
 n=len(y)
 def q(frac:float)->int:
  target=int((n-1)*frac);c=0
  for i,v in enumerate(hist):
   c+=v
   if c>target:return i
  return 255
 return {'frames':seen,'y_mean':total/n,'y_p01':q(.01),'y_p50':q(.5),'y_p95':q(.95),'y_p99':q(.99),
         'fraction_y_ge96':sum(hist[96:])/n,'fraction_y_ge235':sum(hist[235:])/n}

def main()->int:
 a=argparse.ArgumentParser();a.add_argument('action',choices=('run','restore'));o=a.parse_args();n=sensor();b=bounds(n)
 base={k:PROFILES[0][k] for k in NAMES}
 if o.action=='restore':
  before=read(n)
  if before not in [{k:p[k] for k in NAMES} for p in PROFILES]: raise RuntimeError('RESTORE_FROM_UNKNOWN_PROFILE_REFUSED')
  set_profile(n,PROFILES[0]);print(json.dumps({'status':'PASS_RESTORED','before':before,'after':read(n)},sort_keys=True));return 0
 if read(n)!=base: raise RuntimeError('BASELINE_READBACK_REQUIRED')
 rows=[];selected=PROFILES[0]
 for i,p in enumerate(PROFILES):
  if i: set_profile(n,p);time.sleep(1.0)
  m=measure();row={'profile':p['name'],'controls':{k:p[k] for k in NAMES},**m};rows.append(row)
  # Hard clipping guard: back down one known step immediately.
  if m['fraction_y_ge235']>=0.005 or m['y_p99']>=230:
   selected=PROFILES[max(0,i-1)];set_profile(n,selected);break
  selected=p
  # Same-night Windows rear p95=152/p99=160. Stop once close enough for visual review.
  if m['y_p95']>=120 and m['y_p99']<=220: break
 result={'status':'PASS_BOUNDED_REAR_DIGITAL_GAIN_LADDER','bounds':b,'measurements':rows,
         'selected_profile':selected['name'],'selected_controls':{k:selected[k] for k in NAMES},
         'same_night_windows_target_nv12':{'y_mean':56.99194,'y_p95':152,'y_p99':160},
         'driver_supported_v4l2_controls_only':True,'frame_timing_changed':False,
         'raw_register_writes':False,'ir_or_illumination':False,'continuous_autoexposure_claimed':False}
 print(json.dumps(result,sort_keys=True));return 0
if __name__=='__main__': raise SystemExit(main())
