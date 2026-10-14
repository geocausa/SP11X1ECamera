#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Run pinned Titan680 field routines on synthetic state, on SP11 only.
No private profile, tuning, captures, disassembly or tables are exported.
The original PE stays private; the report contains derived field facts only.
"""
from pathlib import Path
import hashlib,json,struct,sys,random
import pefile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE
from unicorn.arm64_const import *
Q=Path(__file__).resolve().parent;R=Q.parents[3]
P=R.parents[1]
DLL=P/'00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'
PIN='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
def main():
 O=Path(sys.argv[1]);O.mkdir()
 b=DLL.read_bytes();assert hashlib.sha256(b).hexdigest()==PIN
 pe=pefile.PE(data=b);im=pe.get_memory_mapped_image();base=pe.OPTIONAL_HEADER.ImageBase
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
 u.mem_map(base,(len(im)+4095)&~4095);u.mem_write(base,im)
 arena=0x200000000;u.mem_map(arena,0x100000)
 obj=arena+0x1000;inp=arena+0x3000;out=arena+0x5000
 image=arena+0x7000;cmd=arena+0x9000;stop=arena+0xff000
 allowed=[0,0];calls=[]
 def code(uc,addr,size,data):
  if addr==base+0x85ee78:
   reg=uc.reg_read(UC_ARM64_REG_X1);count=uc.reg_read(UC_ARM64_REG_X2)
   ptr=uc.reg_read(UC_ARM64_REG_X3)
   assert count in [1,3] and image<=ptr and ptr+4*count<=image+32
   calls.append((reg,struct.unpack('<'+'I'*count,uc.mem_read(ptr,4*count))))
   uc.emu_stop()
  elif not allowed[0]<=addr<allowed[1]:
   raise AssertionError('unexpected native control transfer')
 u.hook_add(UC_HOOK_CODE,code)
 def reset(rva,end):
  u.mem_write(arena+0x1000,bytes(0x9000));calls.clear()
  # Reset volatile and saved GPRs; no field/calculation/branch shims.
  for i in range(29):u.reg_write(UC_ARM64_REG_X0+i,0)
  u.reg_write(UC_ARM64_REG_X0,obj);u.reg_write(UC_ARM64_REG_X1,inp)
  u.reg_write(UC_ARM64_REG_X2,out);u.reg_write(UC_ARM64_REG_X3,out)
  u.reg_write(UC_ARM64_REG_SP,arena+0xf0000);u.reg_write(UC_ARM64_REG_LR,stop)
  u.reg_write(UC_ARM64_REG_NZCV,0);allowed[:]=[base+rva,base+end]
 def run(rva):
  u.emu_start(base+rva,stop,count=1000)
  assert u.reg_read(UC_ARM64_REG_PC)==stop or calls,'bounded run did not return'
 modules=[
  ('PDPC',0xb3cac0,56,0x3d58,3,0x3d60),
  ('GIC',0xb4b670,32,0x4758,3,0x4760),
  ('LCAC',0xb3acc0,32,0x5460,1,0x5460),
  ('GTM',0xb5aa80,32,0x5a60,1,0x5a60)]
 seeds=[0,0xffffffff,0xa596c3f0]+[1<<i for i in range(32)]
 module_cases=0
 for name,rva,member,reg,count,target in modules:
  for seed in seeds:
   for enable in [0,1,2,3]:
    reset(rva,rva+0x100)
    u.mem_write(obj+member,struct.pack('<Q',image))
    u.mem_write(inp+80,struct.pack('<Q',cmd))
    u.mem_write(image,struct.pack('<8I',*[seed]*8))
    u.mem_write(out,struct.pack('<I',enable))
    run(rva);assert len(calls)==1
    got_reg,words=calls[0];assert got_reg==reg and len(words)==count
    index=(target-reg)//4
    assert words[index]==(seed&0xfffffffe)|(enable&1)
    assert all(w==seed for i,w in enumerate(words) if i!=index)
    module_cases+=1
 # BLS121 exact native selector branches; all data is synthetic.
 rng=random.Random(681)
 offsets=sorted({0,1,2,3,6596,0x3ffff,*[1<<i for i in range(18)],
                 *[rng.randrange(0x40000) for i in range(256)]})
 bls_cases=0;fraction_cases=0
 for selector,shift,width in [(13,14,18),(199,20,12)]:
  mask=((1<<width)-1)<<shift
  for seed in [0,0xffffffff,0xa596c3f0]:
   for offset in offsets:
    reset(0xb4bf30,0xb4c180)
    u.mem_write(obj+32,struct.pack('<I',selector))
    u.mem_write(obj+40,struct.pack('<Q',image))
    u.mem_write(obj+48,struct.pack('<Q',image))
    u.mem_write(image,struct.pack('<7I',*[seed]*7))
    u.mem_write(inp,struct.pack('<8I',0,offset,0x835,0,10,20,30,40))
    run(0xb4bf30);assert not calls
    words=struct.unpack('<7I',u.mem_read(image,28))
    assert words[1]==((seed&~mask)|((offset<<shift)&mask))
    assert words[2]==((seed&~0x1ffff)|0x835)
    assert u.reg_read(UC_ARM64_REG_W0)==0
    bls_cases+=1
 for fraction in range(4):
  old=fraction<<14
  overridden=(old&0xffff)|(1649<<16)
  assert (overridden>>14)==(1649<<2)|fraction
  fraction_cases+=1
 refs=[
  R/'experiments/E004-front-ir-vd55g0/e006t-rear-disabled-small-iq-providers/README.md',
  R/'experiments/E004-front-ir-vd55g0/e006t-rear-disabled-small-iq-providers/camss-e006t-small-iq.inc',
  R/'experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/SURFACE-TITAN680-STEADY-PACKERS.md',
  R/'src/native-rgb/front-ae/tuning/imx681-front-open-regs.txt']
 h=P/'02-kernel/upstream-public-vfe680-20261011-01/source/drivers/media/platform/qcom/camss/camss-vfe-680-pp-regs.h'
 assert hashlib.sha256(h.read_bytes()).hexdigest()=='bce9607bac5b46ce907a1434b3a772c5c40b753b1c933db7d37822b9c26e020e'
 result={
  'status':'PASS_SYNTHETIC_EXACT_NATIVE_FIELD_ROUTINES',
  'original_PE_sha256':PIN,'original_PE_exported':False,
  'private_profile_read':False,'private_tuning_read':False,'pixels_read':False,
  'module_cases':module_cases,'bls_cases':bls_cases,
  'old_mask_fraction_cases':fraction_cases,
  'prior_reused_source_pins':{str(f.relative_to(R)):hashlib.sha256(f.read_bytes()).hexdigest() for f in refs},
  'public_address_header_sha256':hashlib.sha256(h.read_bytes()).hexdigest(),
  'native_module_subcommand_anchors':[{'name':n,'rva':hex(v),'control_register':hex(t)} for n,v,m,r,c,t in modules],
  'native_BLS121_packer_rva':'0xb4bf30',
  'bls_layouts':{'13':{'offset_bits':18,'offset_shift':14},'199':{'offset_bits':12,'offset_shift':20}},
  'old_mask_low16_explanation':'low14 preserved bits plus low2 of IFE18 offset',
  'candidate_policy':{'module_cold_images':'zero','integer_black_offset16':1649,'fraction2':0},
  'native_execution_shims':'none; intercept the CDM builder only to observe synthetic command arguments',
  'cold_zero_source_evidence':'E006t exact Titan680 LCAC source audit reused; synthetic zero images in all four native subcommand routines',
  'constructor_executed':False,
  'bls_selector13_native_front_runtime_observed':False,
  'complete_startup':False,'hardware':False,'calibration_remeasured':False,
  'remaining':'Qualify selector/domain and chosen fraction/cold policies on original calibrated front mode; surrounding functional startup/own tables remain'}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','module_cases','bls_cases','old_mask_fraction_cases','hardware','calibration_remeasured']}))
if __name__=='__main__':main()
