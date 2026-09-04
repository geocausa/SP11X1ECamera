#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, struct
from pathlib import Path

def sha(b):return hashlib.sha256(b).hexdigest()
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);assert spec.loader;spec.loader.exec_module(m);return m

def generate(emu,request:int,live:dict,s):
 uc=emu.uc;TMC=emu.heap;OUT=emu.heap+0x10000;LOC=emu.heap+0x20000
 PU=s.BASE+s.RVA['mode2_domain'];PF=s.BASE+s.RVA['titan_x_grid']
 uc.mem_write(TMC,b'\0'*0x8000);uc.mem_write(TMC,live['tmc'])
 uc.mem_write(TMC+0x6328,struct.pack('<f',0.25)*((0x7228-0x6328)//4));uc.mem_write(OUT,b'\0'*0x1200)
 emu.run(s.RVA['mode2_cubic_map'],[TMC+0x5104,TMC+0x5120,TMC+0x51B0,PU,OUT,0x100])
 emu.run(s.RVA['tmc_domain_map'],[PU,OUT,TMC,TMC+0x6228,12,0,0x100],[1.0])
 mapped=struct.unpack('<257f',bytes(uc.mem_read(OUT,0x404)))
 local=b''.join(struct.pack('<d',float(max(0.0,v))) for v in mapped);uc.mem_write(LOC,local)
 emu.run(s.RVA['final_adaptive_map'],[LOC,1,10,12,PU],[1.0,0.8500000238418579])
 ld=struct.unpack('<257d',bytes(uc.mem_read(LOC,257*8)));xg=struct.unpack('<257f',bytes(uc.mem_read(PF,257*4)))
 packed=bytearray()
 for i in range(256):
  base=int(ld[i]+0.5)
  dx=int(s.f32(xg[i+1]-xg[i])) if i<255 else (0x3fff-int(xg[i]))+1
  slope=0.0 if dx<1 or ld[i+1]==ld[i] else s.f32(s.f32(ld[i+1]-ld[i])/float(dx))
  if abs(slope)>=0.5:raise RuntimeError(f'R{request} exponent-30 bound drift index {i}')
  shift=30;scaled=s.f32(s.f32((2.0**shift)*slope)+0.5);si=int(scaled);cl=max(-0x2000000,min(0x1ffffff,si))
  word=(base&0x3fffff)|((cl&0x3ffffff)<<22)|((shift&0x1f)<<48);packed+=struct.pack('<Q',word)
 out=bytes(packed)
 # Captured GTM_OUT is validation only, never used in calculation above.
 if out!=live['out']:raise RuntimeError(f'R{request} generated GTM != captured validation target')
 return out

def main():
 here=Path(__file__).resolve().parent;repo=here.parents[3]
 prod=repo/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
 ap=argparse.ArgumentParser();ap.add_argument('--capture-dir',type=Path,default=prod/'windows-adaptive-live-20260902')
 ap.add_argument('--device-mft',type=Path,default=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'))
 ap.add_argument('--output-dir',type=Path,default=Path('/tmp/e003i-native-gtm'));ap.add_argument('--manifest',type=Path)
 a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
 s=load(prod/'prove-gtm-live-exact-replay.py','e003i_gtm_proof')
 if s.sha256_file(a.device_mft)!=s.DEVICE_MFT_SHA256:raise RuntimeError('DeviceMFT identity drift')
 emu=s.SurfaceEmu(a.device_mft)
 manifest={'schema':'sp11-e003i-native-gtm-backend-v1','accepted':True,
   'capture_session':'E003H_ADAPTIVE_0073_LIVE_20260902','equals_0076_compatibility_session':False,
   'captured_gtm_out_is_validation_only':True,
   'generated_from':['captured TMC state','captured trigger/geometry state','exact DeviceMFT mode2/TMC adaptive helpers','Titan680 setting math'],
   'requests':{},'safety':{'offline_only':True,'linux_camera_runtime':False}}
 for req in (4,5,6):
  live=s.decode_live_request(a.capture_dir,req);out=generate(emu,req,live,s)
  got=sha(out);want=s.EXPECTED_OUT_SHA256[req]
  if got!=want:raise RuntimeError(f'R{req} GTM SHA {got} != {want}')
  (a.output_dir/f'R{req}_GTM0.bin').write_bytes(out)
  manifest['requests'][str(req)]={'sha256':got,'bytes':len(out),'triggers':live['triggers']}
  print(f'R{req} PASS GTM0={got}')
 mp=a.manifest or a.output_dir/'MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 print('NATIVE_GTM_BACKEND=PASS');print('MANIFEST',mp)
if __name__=='__main__':main()
