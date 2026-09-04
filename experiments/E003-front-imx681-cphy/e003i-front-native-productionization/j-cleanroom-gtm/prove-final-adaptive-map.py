#!/usr/bin/env python3
from pathlib import Path
import importlib.util,struct

def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);assert s.loader;s.loader.exec_module(m);return m

def main():
 here=Path(__file__).resolve().parent;repo=here.parents[3];prod=repo/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
 S=load(prod/'prove-gtm-live-exact-replay.py','gtm_oracle3');C=load(here/'cleanroom-gtm-helpers.py','gtm_clean3')
 dll=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll');cap=prod/'windows-adaptive-live-20260902'
 for req in (4,5,6):
  live=S.decode_live_request(cap,req);n=S.SurfaceEmu(dll);c=S.SurfaceEmu(dll)
  for e in (n,c):
   T=e.heap;O=T+0x10000;L=T+0x20000;e.uc.mem_write(T,b'\0'*0x8000);e.uc.mem_write(T,live['tmc']);e.uc.mem_write(T+0x6328,struct.pack('<f',0.25)*((0x7228-0x6328)//4));e.uc.mem_write(O,b'\0'*0x1200)
   C.mode2_cubic_map(e.uc,T+0x5104,T+0x5120,T+0x51b0,S.BASE+S.RVA['mode2_domain'],O,0x100)
   C.tmc_domain_map_zero_blend(e.uc,S.BASE+S.RVA['mode2_domain'],O,T,12,0x100,1.0)
   vals=struct.unpack('<257f',bytes(e.uc.mem_read(O,0x404)));e.uc.mem_write(L,b''.join(struct.pack('<d',float(max(0.0,v))) for v in vals))
  n.run(S.RVA['final_adaptive_map'],[n.heap+0x20000,1,10,12,S.BASE+S.RVA['mode2_domain']],[1.0,0.8500000238418579])
  C.final_adaptive_map_power1(c.uc,c.heap+0x20000,1,10,12,S.BASE+S.RVA['mode2_domain'],1.0,0.8500000238418579)
  nb=bytes(n.uc.mem_read(n.heap+0x20000,257*8));cb=bytes(c.uc.mem_read(c.heap+0x20000,257*8))
  if nb!=cb:
   idx=[i for i in range(257) if nb[i*8:(i+1)*8]!=cb[i*8:(i+1)*8]];print('R',req,'double_diffs',len(idx),'first',idx[:20])
   for i in idx[:10]: print(i,struct.unpack_from('<d',nb,i*8)[0],nb[i*8:i*8+8].hex(),struct.unpack_from('<d',cb,i*8)[0],cb[i*8:i*8+8].hex())
   raise SystemExit(1)
  print(f'R{req} FINAL_ADAPTIVE_MAP PASS 257/257')
 print('CLEANROOM_GTM_FINAL_ADAPTIVE_MAP=PASS')
if __name__=='__main__':main()
