#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exact BLS factory -> packer -> command arguments on synthetic state only.
Runs on SP11; original code, profiles, tuning and disassembly stay private.
The original code is immutable. Only bounded allocation and the command
observer are intercepted; no field, branch, constructor or packing shim.
"""
from pathlib import Path
import hashlib,json,struct,random,subprocess,resource,sys,collections
import pefile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_PROT_READ,UC_PROT_ALL
from unicorn.arm64_const import *
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
Q=Path(__file__).resolve().parent;R=Q.parents[3];P=R.parents[1]
DLL=P/'00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll'
PIN='c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
class Factory:
 def __init__(self):
  b=DLL.read_bytes();assert hashlib.sha256(b).hexdigest()==PIN
  pe=pefile.PE(data=b);self.base=pe.OPTIONAL_HEADER.ImageBase
  self.image=pe.get_memory_mapped_image()
  self.u=Uc(UC_ARCH_ARM64,UC_MODE_ARM)
  self.u.mem_map(self.base,(len(self.image)+4095)&~4095);self.u.mem_write(self.base,self.image)
  self.arena=0x78000000;self.extent=0x100000;self.u.mem_map(self.arena,self.extent)
  # Partial owned source context: selector at20, hardware-version at
  # 0x17eb0. The source adds0x17000 before its0xeb0 read. The declared
  # 0x60800 Titan680 value is reused from the retained scalar proof.
  self.allowed=(0,0);self.allocations=[];self.commands=[];self.count=0
  self.u.hook_add(UC_HOOK_CODE,self.code);self.u.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def owned(self,p,n):
  return any(a<=p and p+n<=a+z for a,z in self.allocations)
 def write(self,u,access,p,n,v,data):
  assert not self.base<=p<self.base+len(self.image),'original image modification'
  assert (self.stack<=p and p+n<=self.stack+0x10000) or self.owned(p,n) or \
   (self.output<=p and p+n<=self.output+256) or \
   (self.meta<=p and p+n<=self.meta+16),('unowned native store',hex(p-self.arena),n)
 def code(self,u,p,n,data):
  self.count+=1
  if p==self.base+0xcae740:
   z=u.reg_read(UC_ARM64_REG_X0);assert z in [88,28]
   a=self.next+32;self.next=a+((z+31)&~31)+32
   assert self.next<self.stack
   self.allocations.append((a,z));u.mem_write(a,bytes([self.poison])*z)
   u.reg_write(UC_ARM64_REG_X0,a);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return
  if p==self.base+0x85ee78:
   reg=u.reg_read(UC_ARM64_REG_W1);z=u.reg_read(UC_ARM64_REG_W2);a=u.reg_read(UC_ARM64_REG_X3)
   assert z in [1,6] and self.owned(a,z*4)
   assert u.reg_read(UC_ARM64_REG_X0)==self.command_buffer
   self.commands.append((reg,tuple(struct.unpack('<'+'I'*z,u.mem_read(a,z*4)))))
   u.reg_write(UC_ARM64_REG_X0,0);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return
  assert self.allowed[0]<=p<self.allowed[1],'unexpected native code boundary'
 def reset(self,placement,selector):
  u=self.u;a=self.arena;u.mem_write(a,bytes([0xa5])*self.extent)
  self.input=a+0x20000+placement;self.output=a+0x1000+placement
  self.parameters=a+0x3000+placement;self.common=a+0x5000+placement
  self.meta=a+0x6000+placement;self.command_buffer=a+0x9000+placement
  self.next=a+0x60000+placement;self.stack=a+0xe0000
  self.end=self.stack+0xff00;self.poison=0x3c if placement&128 else 0xa5
  self.allocations=[];self.commands=[]
  u.mem_write(self.input,bytes(0x18000));u.mem_write(self.input+20,struct.pack('<I',selector))
  u.mem_write(self.input+0x17eb0,struct.pack('<I',0x60800))
  u.mem_write(self.output,bytes(256));u.mem_write(self.parameters,bytes(128));u.mem_write(self.meta,bytes(16))
  u.mem_write(self.parameters+80,struct.pack('<Q',self.command_buffer))
 def call(self,start,end,args):
  u=self.u;self.allowed=(self.base+start,self.base+end)
  for i in range(31):u.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0)
  for i in range(19,30):u.reg_write(globals()['UC_ARM64_REG_X'+str(i)],0x31415900+i)
  for i in range(8,16):u.reg_write(globals()['UC_ARM64_REG_D'+str(i)],0x125000+i)
  saved=[globals()['UC_ARM64_REG_X'+str(i)] for i in range(19,30)]
  saved += [globals()['UC_ARM64_REG_D'+str(i)] for i in range(8,16)]
  before={r:u.reg_read(r) for r in saved}
  for i,v in enumerate(args):u.reg_write(globals()['UC_ARM64_REG_X'+str(i)],v)
  u.reg_write(UC_ARM64_REG_SP,self.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,self.end)
  u.emu_start(self.base+start,self.end,count=5000)
  assert u.reg_read(UC_ARM64_REG_PC)==self.end and u.reg_read(UC_ARM64_REG_W0)==0
  assert u.reg_read(UC_ARM64_REG_SP)==self.stack+0xf000
  assert all(u.reg_read(r)==v for r,v in before.items()),'native ABI restore'
 def vector(self,placement,selector,offset,gain,thresholds):
  self.reset(placement,selector);u=self.u
  self.call(0xa19140,0xa19550,[self.output,self.input])
  assert [z for a,z in self.allocations]==[88,28]
  obj=struct.unpack('<Q',u.mem_read(self.output+8,8))[0]
  assert obj==self.allocations[0][0]
  image,n=self.allocations[1];assert bytes(u.mem_read(image,n))==bytes(28),'native cold image not zero'
  expected_reg=0x4b60 if selector==13 else 0x2260
  assert struct.unpack('<I',u.mem_read(obj+32,4))[0]==selector
  assert struct.unpack('<I',u.mem_read(obj+80,4))[0]==expected_reg
  member=40 if selector==13 else 48
  assert struct.unpack('<Q',u.mem_read(obj+member,8))[0]==image
  # Source common-output fields -> public THRESHOLD_CFG_0..3 ordering.
  t0,t1,t2,t3=thresholds
  u.mem_write(self.common,struct.pack('<8I',0,offset,gain,0,t3,t1,t0,t2))
  self.call(0xb4bf30,0xb4c180,[obj,self.common,self.meta])
  self.call(0xb4b980,0xb4ba60,[obj,self.parameters,0])
  shift,width=(14,18) if selector==13 else (20,12)
  want=[offset<<shift,gain,*[v<<shift for v in thresholds]]
  assert self.commands==[(expected_reg,(0,)),(expected_reg+8,tuple(want))]
  assert all(0<=v<(1<<width) for v in [offset,*thresholds])
  for a,z in self.allocations:
   assert bytes(u.mem_read(a-32,32))==b'\xa5'*32 and bytes(u.mem_read(a+z,32))==b'\xa5'*32
  assert bytes(u.mem_read(self.input+0x17eb0,4))==struct.pack('<I',0x60800)
  # Independent GPL-compatible REG_CONT serialization of observed arguments.
  return struct.pack('<8I',0x03000006,expected_reg+8,*want)
 def unchanged(self):
  assert bytes(self.u.mem_read(self.base,len(self.image)))==self.image
def main():
 O=Path(sys.argv[1]);O.mkdir()
 rng=random.Random(681121)
 vectors=[(1649<<2,0x835,[0,0,0,0]),(0,0,[0]*4),(0x3ffff,0x1ffff,[0x3ffff]*4)]
 for fraction in range(4):vectors.append(((1649<<2)|fraction,0x835,[0]*4))
 for field in range(5):
  for bit in range(18):
   values=[0]*5;values[field]=1<<bit
   vectors.append((values[0],0x835,values[1:]))
 for bit in range(17):vectors.append((0,1<<bit,[0]*4))
 for _ in range(64):vectors.append((rng.randrange(0x40000),rng.randrange(0x20000),[rng.randrange(0x40000) for i in range(4)]))
 native=Factory();data=bytearray();primary=0;other=0
 for placement in [0,128,512,1024]:
  for offset,gain,thresholds in vectors:
   oracle=native.vector(placement,13,offset,gain,thresholds)
   data+=struct.pack('<6I',offset,gain,*thresholds)+oracle;primary+=1
  for offset,gain,t in [(0,0,[0]*4),(4095,0x1ffff,[1,2,3,4095])]:
   native.vector(placement,199,offset,gain,t);other+=1
 native.unchanged()
 headers={
 'sp11-front-bls121.h':Q/'sp11-front-bls121.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for name,p in headers.items():(O/name).write_bytes(p.read_bytes())
 (O/'test-native-c.c').write_bytes((Q/'test-native-c.c').read_bytes())
 original=(Q/'sp11-front-bls121.h').read_text()
 mutations={
 'wrong_register':original.replace('0x4b68U','0x4b6cU'),
 'truncate_gain':original.replace('words[1] = state->gain17;','words[1] = state->gain17 & 0xffffU;'),
 'reverse_thresholds':original.replace('&words[2 + i]','&words[5 - i]'),
 'publish_before_validation':original.replace('\tif (!out || !state)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !state)',1),
 'bypass_calibration_policy':original.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;')}
 assert all(s!=original for s in mutations.values())
 runs=[]
 for cc in ['gcc','clang']:
  for label,h in [('actual',original),*mutations.items()]:
   (O/'sp11-front-bls121.h').write_text(h)
   exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-fno-omit-frame-pointer','-I'+str(O),str(O/'test-native-c.c'),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2000:]
   p=subprocess.run([str(exe)],input=bytes(data),capture_output=True,timeout=15)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2000:].decode()
    result=json.loads(p.stdout);assert result['native_vectors']==primary
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':result})
   else:assert p.returncode!=0,'compiled unsafe mutation survived '+label
 (O/'sp11-front-bls121.h').write_text(original)
 reference_paths=[
  'src/upstream/isp-config/cold-front-fields-20261014/test-native.py',
  'experiments/E004-front-ir-vd55g0/e011cz-original-runtime-helpers/README.md',
  'experiments/E004-front-ir-vd55g0/e011ai-rear-neutral-scalar-full-integration/native-private.py',
  'src/native-rgb/front-ae/tuning/imx681-front-open-regs.txt']
 result={
 'schema':'sp11-bls121-native-factory-command-bridge-v1',
 'status':'PASS_EXACT_NATIVE_FACTORY_PACKER_COMMAND_ARGUMENTS_AND_C_ENCODER',
 'original_PE_sha256':PIN,'original_PE_exported':False,'original_image_immutable':True,
 'native_primary_cases':primary,'native_other_layout_cases':other,'native_instructions':native.count,
 'native_factory_entry':'0xa19140','native_packer_entry':'0xb4bf30','native_command_entry':'0xb4b980',
 'source_bound_selector_registers':{'13':{'module_register':'0x4b60','configuration_register':'0x4b68','offset_shift':14,'offset_width':18},
                                  '199':{'module_register':'0x2260','configuration_register':'0x2268','offset_shift':20,'offset_width':12}},
 'cold_register_image_zero_from_poisoned_allocation':True,'allocation_sizes':[88,28],
 'placements':4,'original_callee_saved_and_SP_restored':True,'allocation_canaries_intact':True,
 'hardware_environment':'Owned partial source context: selector at20 and hardware-version0x60800 at0x17eb0; not observed Windows/physical context',
 'original_helpers_intercepted':['0xcae740 bounded allocator','0x85ee78 observed command arguments/success status'],
 'field_or_constructor_or_branch_shims':False,
 'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),
 'header_pins':{n:sha(p) for n,p in headers.items()},
 'prior_reference_pins':{n:sha(R/n) for n in reference_paths},
 'private_profile_read':False,'private_tuning_read':False,'pixels_read':False,
 'calibration_remeasured':False,'runtime_changed':False,'hardware':False,
 'limits':['Native source bridge only; live front BLS object/precision not observed',
 'Cold fraction0/threshold0 policy requires original-domain physical validation',
 'Configuration-only compiler emits no module-enable command; surrounding startup/DMI/loader remain']}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','native_primary_cases','native_other_layout_cases','native_instructions','runtime_changed']}))
if __name__=='__main__':main()
