#!/usr/bin/env python3
"""E012F fresh candidate-only exact already-proven OV13858 visible RGB profile.

Only standard V4L2 exposure/analogue_gain/digital_gain controls on the
currently discovered rear RGB sensor are touched. No raw register writes, IR,
illumination, frame-timing/VBLANK change or hidden control. The candidate
requires the exact previously accepted baseline and advertised bounds, writes
one exact previously physically tested 30-fps profile, verifies readback, and
can restore the precise baseline. Any mismatch fails closed to the enclosing
one-shot's Golden return.
"""
from __future__ import annotations
import argparse,json,os,re,subprocess
from pathlib import Path
ROOT=Path('/var/lib/sp11-camera-rgb')
BASE={'exposure':1600,'analogue_gain':128,'digital_gain':1024}
TARGET={'exposure':3200,'analogue_gain':512,'digital_gain':2048}
NAMES=('exposure','analogue_gain','digital_gain')
def run(*a:str)->str:
 r=subprocess.run(a,check=True,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,timeout=8)
 return r.stdout
def node()->str:
 if os.geteuid()!=0 or 'sp11_camera_rgb_product=1' not in Path('/proc/cmdline').read_text().split():
  raise RuntimeError('EXACT_PRODUCT_BOOT_ROOT_REQUIRED')
 d=json.loads((ROOT/'output/UNIFIED.json').read_text()); n=d['rear_sensor_device']
 if not re.fullmatch(r'/dev/v4l-subdev[0-9]+',n) or not Path(n).is_char_device():
  raise RuntimeError('REAR_SENSOR_NODE_INVALID')
 return n
def read(n:str)->dict[str,int]:
 o={}
 for k in NAMES:
  m=re.fullmatch(rf'{k}:\s*([0-9]+)',run('v4l2-ctl','-d',n,'--get-ctrl',k).strip())
  if not m: raise RuntimeError('CONTROL_READBACK_INVALID')
  o[k]=int(m.group(1))
 return o
def bounds(n:str)->dict[str,dict[str,int]]:
 text=run('v4l2-ctl','-d',n,'--list-ctrls'); o={}
 for line in text.splitlines():
  m=re.match(r'\s*(exposure|analogue_gain|digital_gain)\s+0x[0-9a-f]+\s+\(int\)\s*:',line)
  if not m: continue
  k=m.group(1); row={}
  for field in ('min','max','step'):
   q=re.search(rf'\b{field}=(-?[0-9]+)',line)
   if not q: raise RuntimeError('CONTROL_BOUNDS_INCOMPLETE')
   row[field]=int(q.group(1))
  o[k]=row
 if set(o)!=set(NAMES): raise RuntimeError('CONTROL_BOUNDS_MISSING')
 for k,v in TARGET.items():
  z=o[k]
  if z['step']<=0 or not z['min']<=v<=z['max'] or (v-z['min'])%z['step']:
   raise RuntimeError('TARGET_OUTSIDE_ADVERTISED_BOUNDS')
 return o
def set_exact(n:str,v:dict[str,int])->None:
 if v not in (BASE,TARGET): raise RuntimeError('UNAPPROVED_PROFILE')
 run('v4l2-ctl','-d',n,'--set-ctrl',','.join(f'{k}={v[k]}' for k in NAMES))
def main()->int:
 p=argparse.ArgumentParser();p.add_argument('action',choices=('apply','restore','status'));a=p.parse_args();n=node();before=read(n); b=bounds(n)
 if a.action=='status': print(json.dumps({'status':'OK','node':n,'controls':before,'bounds':b},sort_keys=True));return 0
 expected=BASE if a.action=='apply' else TARGET; target=TARGET if a.action=='apply' else BASE
 if before!=expected: raise RuntimeError('UNEXPECTED_PRE_PROFILE_READBACK')
 set_exact(n,target); after=read(n)
 if after!=target: raise RuntimeError('PROFILE_READBACK_MISMATCH')
 print(json.dumps({'status':'PASS','action':a.action,'before':before,'after':after,'bounds':b,
  'driver_supported_v4l2_controls_only':True,'raw_register_writes':False,'ir_or_illumination':False,
  'frame_timing_changed':False},sort_keys=True));return 0
if __name__=='__main__': raise SystemExit(main())
