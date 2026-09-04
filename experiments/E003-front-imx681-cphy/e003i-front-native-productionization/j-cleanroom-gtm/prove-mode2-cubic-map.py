#!/usr/bin/env python3
from pathlib import Path
import importlib.util,struct

def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m

def main():
 here=Path(__file__).resolve().parent;repo=here.parents[3];prod=repo/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
 S=load(prod/'prove-gtm-live-exact-replay.py','gtm_oracle');C=load(here/'cleanroom-gtm-helpers.py','gtm_clean')
 dll=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll');cap=prod/'windows-adaptive-live-20260902'
 for req in (4,5,6):
  live=S.decode_live_request(cap,req);n=S.SurfaceEmu(dll);c=S.SurfaceEmu(dll)
  for e in (n,c):
   e.uc.mem_write(e.heap,b'\0'*0x8000);e.uc.mem_write(e.heap,live['tmc']);e.uc.mem_write(e.heap+0x10000,b'\0'*0x1200)
  args=[n.heap+0x5104,n.heap+0x5120,n.heap+0x51b0,S.BASE+S.RVA['mode2_domain'],n.heap+0x10000,0x100]
  n.run(S.RVA['mode2_cubic_map'],args)
  C.mode2_cubic_map(c.uc,c.heap+0x5104,c.heap+0x5120,c.heap+0x51b0,S.BASE+S.RVA['mode2_domain'],c.heap+0x10000,0x100)
  nb=bytes(n.uc.mem_read(n.heap+0x10000,0x404));cb=bytes(c.uc.mem_read(c.heap+0x10000,0x404))
  if nb!=cb:
   dif=[i for i,(a,b) in enumerate(zip(nb,cb)) if a!=b]
   fi=sorted(set(i//4 for i in dif));
   print('R',req,'byte_diffs',len(dif),'float_diffs',len(fi),'first',fi[:12])
   for i in fi[:8]:
    print(i,struct.unpack_from('<f',nb,i*4)[0],nb[i*4:i*4+4].hex(),struct.unpack_from('<f',cb,i*4)[0],cb[i*4:i*4+4].hex())
   raise SystemExit(1)
  print(f'R{req} MODE2_CUBIC_MAP PASS 257/257')
 print('CLEANROOM_GTM_MODE2_CUBIC_MAP=PASS')
if __name__=='__main__':main()
