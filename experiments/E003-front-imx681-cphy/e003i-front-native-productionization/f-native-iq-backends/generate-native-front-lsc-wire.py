#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, importlib.util, json, math, struct
from pathlib import Path
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_READ, UC_HOOK_MEM_WRITE
from unicorn.arm64_const import UC_ARM64_REG_X0, UC_ARM64_REG_X2, UC_ARM64_REG_X18

EXPECTED={
 4:{'lsc0':'eb41b13a2049ecfe835266fefedd2d41c3e15564a8826ee06437f48a533234e5','lsc1':'c140edeb7b40eaefa5f904116cc4ce25478494bc9508160742cdc18881bfc676'},
 5:{'lsc0':'1033e0732a1f2edf2263351be7ad213a98864ba0b9feb0a1d2eb27fbcf31953c','lsc1':'eab65d435c04a768bc53009c0cfdf05055168213b50c83385459679dfc790590'},
 6:{'lsc0':'94dda0dd0c221da88a1087b13305c1cbe440cd314b3f0f6e324504494aab758e','lsc1':'5322633904bc97e2d647cf27c9f4f21a92b532272d063a4175028b3a8ad90076'},
}
ZERO_SHA='6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e'

def sha(b):return hashlib.sha256(b).hexdigest()
def load(path,name):
 spec=importlib.util.spec_from_file_location(name,path); m=importlib.util.module_from_spec(spec); assert spec.loader; spec.loader.exec_module(m); return m

def q10(v:float)->int:
 x=int(math.floor(v*1024.0+0.5)); return max(0x400,min(0x3fff,x))

def wire_from_output(output:bytes):
 vals=struct.unpack('<884f',output[:0xdd0])
 ch=[[q10(v) for v in vals[i*221:(i+1)*221]] for i in range(4)]
 if ch[1]!=ch[2]: raise RuntimeError('green planes diverged; accepted channel ambiguity no longer valid')
 l0=b''.join(struct.pack('<I',(ch[0][i]&0x3fff)|((ch[1][i]&0x3fff)<<14)) for i in range(221))
 l1=b''.join(struct.pack('<I',(ch[3][i]&0x3fff)|((ch[2][i]&0x3fff)<<14)) for i in range(221))
 l2=b'\0'*0x374
 alias=(l0+l1)[0x22e:0x42e]
 return l0,l1,l2,alias

def generate(cap:Path,dll:Path,proof,surface,fill:int):
 e=surface.SurfaceEmu(dll);u=e.uc
 IFACE=0x260000000000;WRAP=0x260000001000;X1=0x260000003000
 X2={4:0x260000010000,5:0x260000030000,6:0x260000050000}
 D3={4:0x260000070000,5:0x260000072000,6:0x260000074000}
 D4={4:0x260000071000,5:0x260000073000,6:0x260000075000}
 CORE=0x260000100000;STUB=0x62000000
 def amap(addr,size):
  base=addr&~0xfff; end=(addr+size+0xfff)&~0xfff
  try:u.mem_map(base,end-base)
  except Exception as exc:
   if 'UC_ERR_MAP' not in str(exc):raise
 def put(addr,name,pad=0):
  b=(cap/name).read_bytes();amap(addr,max(len(b),pad));u.mem_write(addr,b);return b
 teb=0x70000000;amap(teb,0x1000);u.mem_write(teb+0x10,e.stack.to_bytes(8,'little'));u.reg_write(UC_ARM64_REG_X18,teb)
 amap(IFACE,0x1000);u.mem_write(IFACE,b'\0'*0x1000);u.mem_write(IFACE+0x18,WRAP.to_bytes(8,'little'))
 amap(STUB,0x1000);u.mem_write(STUB,b'\xc0\x03\x5f\xd6');u.mem_write(surface.BASE+proof.ALLOC_IAT_RVA,STUB.to_bytes(8,'little'))
 allocations=[]
 def alloc_hook(uc,address,size,user_data):
  n=uc.reg_read(UC_ARM64_REG_X2);allocations.append(n)
  if n!=proof.CORE_BYTES or len(allocations)!=1:raise RuntimeError(f'allocator sequence {allocations}')
  amap(CORE,proof.CORE_BYTES);uc.mem_write(CORE,bytes([fill])*proof.CORE_BYTES);uc.reg_write(UC_ARM64_REG_X0,CORE)
 u.hook_add(UC_HOOK_CODE,alloc_hook,begin=STUB,end=STUB)
 interface_reads=[]
 def iface_hook(uc,access,address,size,value,user_data):
  if IFACE<=address<IFACE+0x1000:interface_reads.append((address-IFACE,size))
 u.hook_add(UC_HOOK_MEM_READ,iface_hook)
 out={}
 for req in (4,5,6):
  if req==4: put(WRAP,'req4_wrapper_pre.bin')
  else:
   # Captured pre-state is validation only; generated previous state is never reseeded.
   wantw=(cap/f'req{req}_wrapper_pre.bin').read_bytes();wantc=(cap/f'req{req}_core_pre.bin').read_bytes()
   gotw=bytes(u.mem_read(WRAP,len(wantw))); gotc=bytes(u.mem_read(CORE,len(wantc)))
   # Wrapper differs only in allocator pointer because backend uses its own deterministic address.
   w=bytearray(wantw); w[0x128:0x130]=CORE.to_bytes(8,'little')
   if gotw!=bytes(w):raise RuntimeError(f'R{req} generated wrapper carry mismatch')
   # Core is pointer-independent on this proven path.
   if gotc!=wantc:raise RuntimeError(f'R{req} generated core carry mismatch')
  put(X1,f'req{req}_x1_config.bin',0x1000);put(X2[req],f'req{req}_x2_stats.bin',0x14000)
  put(D3[req],f'req{req}_x3_desc.bin');put(D4[req],f'req{req}_x4_desc.bin')
  in_addr=proof.desc_ptr(cap,req,3);out_addr=proof.desc_ptr(cap,req,4)
  put(in_addr,f'req{req}_input_mesh.bin'); pre=put(out_addr,f'req{req}_output_mesh_pre.bin')
  e.run(proof.CALLBACK_RVA,xargs=(IFACE,X1,X2[req],D3[req],D4[req]),instruction_limit=200_000_000)
  ret=u.reg_read(UC_ARM64_REG_X0)&0xffffffff
  got=bytes(u.mem_read(out_addr,len(pre)))
  if ret:raise RuntimeError(f'R{req} Tintless return {ret}')
  # Validation only: the generated output must equal the captured post authority.
  want=(cap/f'req{req}_output_mesh_post.bin').read_bytes()
  if got!=want:raise RuntimeError(f'R{req} generated output != captured authority')
  l0,l1,l2,gic=wire_from_output(got)
  obs={'lsc0':sha(l0),'lsc1':sha(l1)}
  if obs!=EXPECTED[req]:raise RuntimeError(f'R{req} wire mismatch {obs}')
  if sha(l2)!=ZERO_SHA:raise RuntimeError(f'R{req} LSC2 nonzero')
  out[req]={'output':got,'lsc0':l0,'lsc1':l1,'lsc2':l2,'gic':gic,
            'output_sha256':sha(got),'lsc0_sha256':sha(l0),'lsc1_sha256':sha(l1),'gic_sha256':sha(gic)}
 if allocations!=[proof.CORE_BYTES] or len(interface_reads)!=3 or set(interface_reads)!={(0x18,8)}:
  raise RuntimeError('native interface/allocation contract drift')
 return out

def main():
 here=Path(__file__).resolve().parent; repo=here.parents[3]
 prod=repo/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static'
 ap=argparse.ArgumentParser();ap.add_argument('--capture-dir',type=Path,default=repo.parent/'.local-oracles/oracle-live-20260904-front-atomic')
 ap.add_argument('--device-mft',type=Path,default=Path('/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'))
 ap.add_argument('--output-dir',type=Path,default=Path('/tmp/e003i-native-lsc'));ap.add_argument('--manifest',type=Path)
 a=ap.parse_args();a.output_dir.mkdir(parents=True,exist_ok=True)
 proof=load(prod/'prove-lsc-front-atomic-tintless-replay.py','e003i_front_tintless_proof')
 surface=load(prod/'prove-gtm-live-exact-replay.py','e003i_surface_emu_lsc')
 proof.verify_capture(a.capture_dir,prod/'FRONT-ATOMIC-TINTLESS-STAGING-20260904.json');proof.verify_device_bytes(a.device_mft,surface)
 runs={fill:generate(a.capture_dir,a.device_mft,proof,surface,fill) for fill in (0x00,0xa5)}
 manifest={'schema':'sp11-e003i-native-front-lsc-backend-v1','accepted':True,'capture_post_is_validation_only':True,
  'generated_from':['req4 constructor/pre-state','per-request x1 config','per-request x2 Tintless stats','per-request descriptors','per-request pre-Tintless input mesh','sequential generated wrapper/core carry','exact DeviceMFT Tintless callback'],
  'requests':{},'allocator_fills_tested':['0x00','0xa5'],'safety':{'offline_only':True,'linux_camera_runtime':False}}
 for req in (4,5,6):
  a0=runs[0][req];a5=runs[0xa5][req]
  for k in ('output','lsc0','lsc1','lsc2','gic'):
   if a0[k]!=a5[k]:raise RuntimeError(f'R{req} allocator-fill output drift {k}')
  for name in ('lsc0','lsc1','lsc2','gic'):(a.output_dir/f'R{req}_{name.upper()}.bin').write_bytes(a0[name])
  manifest['requests'][str(req)]={k:v for k,v in a0.items() if k.endswith('sha256')}
  print('R%d PASS output=%s LSC0=%s LSC1=%s'%(req,a0['output_sha256'],a0['lsc0_sha256'],a0['lsc1_sha256']))
 mp=a.manifest or a.output_dir/'MANIFEST.json';mp.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
 print('NATIVE_FRONT_LSC_BACKEND=PASS');print('MANIFEST',mp)
if __name__=='__main__':main()
