#!/usr/bin/env python3
from __future__ import annotations
import argparse,hashlib,json,struct
from pathlib import Path

EXPECTED={4:'656d35c87e95b376f3d6b4eac7624c3387e1857100cf5529f5ae7e2a87ec7f43',5:'9e54b3b16a6a146f9f1f448150a88a929c2ffe3cd4c8aa93e98e5498afb0216e',6:'89bc45b890f6508912bad1b543c7f7ad56e20b6794fdc908455e9f47c967cf95'}
DOMAIN_SHA256='b33525b102690e0894d55245a0af56e655f10615fe6b144cbfca2cb9e5836325'

def f32(v): return struct.unpack('<f',struct.pack('<f',float(v)))[0]
def sha(b): return hashlib.sha256(b).hexdigest()
def F(buf,off): return struct.unpack_from('<f',buf,off)[0]
def U32(buf,off): return struct.unpack_from('<I',buf,off)[0]
def U16(buf,off): return struct.unpack_from('<H',buf,off)[0]

def load_domain(here:Path):
 b=(here/'mode2-domain-257-f32le.bin').read_bytes()
 if len(b)!=257*4 or sha(b)!=DOMAIN_SHA256: raise RuntimeError('mode2 domain constant drift')
 return struct.unpack('<257f',b)

def decode_request(cap:Path,req:int):
 mod=(cap/f'REQ{req}_GTM_MODULE.bin').read_bytes();tmc=(cap/f'REQ{req}_GTM_TMC.bin').read_bytes();out=(cap/f'REQ{req}_GTM_OUT.bin').read_bytes()
 if len(mod)<0x128 or len(tmc)<0x6328 or len(out)!=0x800: raise RuntimeError(f'R{req} fixture size drift')
 common=mod[0xa8:0x128]
 actual=(U32(tmc,8),U32(tmc,0xc),U32(tmc,0x10),U32(tmc,0x74),U32(common,0x34),U16(common,0x2a),common[0x70])
 if actual!=(5,0x60800,1,2,0x60800,1,1): raise RuntimeError(f'R{req} GTM branch drift {actual!r}')
 if struct.pack('<f',F(common,0x74))!=struct.pack('<f',0.8500000238418579): raise RuntimeError(f'R{req} strength drift')
 if struct.pack('<f',F(common,0x78))!=struct.pack('<f',1.0): raise RuntimeError(f'R{req} power drift')
 if tmc[0x109c:0x10a4]!=b'\0'*8: raise RuntimeError(f'R{req} nonzero TMC blend unsupported')
 return tmc,out

def mode2_cubic(tmc:bytes,domain):
 src=struct.unpack_from('<7f',tmc,0x5104);dst=struct.unpack_from('<7f',tmc,0x5120);coef=struct.unpack_from('<15f',tmc,0x51b0)
 first=src[1];low=f32(dst[1]/first);out=[]
 for x in domain:
  y=f32(0.0)
  if first<x:
   seg=2
   while seg<7:
    if x<=src[seg]:
     ci=(seg-2)*3;dx=f32(x-src[seg-1]);t=f32(f32(coef[ci+2]*dx)+coef[ci+1]);t=f32(f32(t*dx)+coef[ci]);y=f32(f32(t*dx)+dst[seg-1]);break
    seg+=1
  else:y=f32(x*low)
  top=f32(1.0) if f32(1.0)<y else y;cl=f32(0.0) if not(f32(0.0)<y) else top;den=x if x!=f32(0.0) else f32(1.0);r=f32(cl/den);lim=r if r<=low else low;out.append(lim if f32(1.0)<r else f32(1.0))
 if len(out)>=2:out[0]=out[1]
 return out

def tmc_domain_zero_blend(ratios,domain,shift=12):
 scale=float(1<<(shift&31));out=[]
 for r,x in zip(ratios,domain):
  y=f32(r*x);top=f32(1.0) if f32(1.0)<y else y;cl=f32(0.0) if not(f32(0.0)<y) else top;q=f32(cl/x);out.append(f32(q*scale))
 return out

def final_power1(mapped,domain):
 src=[float(v) for v in mapped];limit=float(f32(float(1<<22)-f32(1.0)));out=[];one=f32(1.0);zero=f32(0.0)
 for i,x in enumerate(domain):
  coord=one if one<x else x
  if not(zero<x):coord=zero
  d=src[i];j=1
  while j<257:
   if coord<domain[j]:
    x1=domain[j];x0=domain[j-1];a=f32(x1-coord);b=f32(coord-x0);den=f32(x1-x0);num=src[j-1]*float(x0)*float(a)+src[j]*float(x1)*float(b);d=float(f32((num/float(den))/float(coord)));break
   j+=1
  if d>limit:d=limit
  if not(0.0<d):d=0.0
  out.append(d)
 for i in range(1,256):
  if out[i-1]<=out[i]:out[i]=out[i-1]
 return out

def titan_grid(domain):
 return [float(max(0,int(f32(f32(x*16384.0)+f32(0.5)))-1)) for x in domain]

def pack_gtm(curve,grid):
 out=bytearray()
 for i in range(256):
  base=int(curve[i]+0.5)
  dx=int(f32(grid[i+1]-grid[i])) if i<255 else (0x3fff-int(grid[i]))+1
  slope=0.0 if dx<1 or curve[i+1]==curve[i] else f32(f32(curve[i+1]-curve[i])/float(dx))
  if abs(slope)>=0.5: raise RuntimeError(f'exponent-30 bound drift index {i}')
  scaled=f32(f32((2.0**30)*slope)+0.5);si=int(scaled);cl=max(-0x2000000,min(0x1ffffff,si));word=(base&0x3fffff)|((cl&0x3ffffff)<<22)|(30<<48);out+=struct.pack('<Q',word)
 return bytes(out)

def generate(tmc:bytes,domain):
 cubic=mode2_cubic(tmc,domain);mapped=tmc_domain_zero_blend(cubic,domain);curve=final_power1(mapped,domain);return pack_gtm(curve,titan_grid(domain))

def main():
 here=Path(__file__).resolve().parent;repo=here.parents[3];prod=repo/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
 ap=argparse.ArgumentParser();ap.add_argument('--capture-dir',type=Path,default=prod/'windows-adaptive-live-20260902');ap.add_argument('--output-dir',type=Path,default=Path('/tmp/e003i-cleanroom-gtm'));a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True);domain=load_domain(here);manifest={'schema':'sp11-e003i-cleanroom-gtm-v1','accepted':True,'device_mft_required':False,'unicorn_required':False,'requests':{}}
 for req in (4,5,6):
  tmc,want=decode_request(a.capture_dir,req);got=generate(tmc,domain)
  if got!=want: raise RuntimeError(f'R{req} clean GTM != Windows')
  h=sha(got)
  if h!=EXPECTED[req]:raise RuntimeError(f'R{req} GTM hash drift {h}')
  (a.output_dir/f'R{req}_GTM0.bin').write_bytes(got);manifest['requests'][str(req)]={'sha256':h,'bytes':len(got)};print(f'R{req} CLEANROOM_GTM PASS {h}')
 (a.output_dir/'MANIFEST.json').write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n');print('CLEANROOM_GTM_BACKEND=PASS')
if __name__=='__main__':main()
