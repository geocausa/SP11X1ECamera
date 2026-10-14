#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reuse prior scalar oracle and producers; qualify missing startup fields only."""
from pathlib import Path
import hashlib,importlib.util,json,random,resource,struct,subprocess,sys
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
Q=Path(__file__).resolve().parent;R=Q.parents[3]
PRE=R/'experiments/E004-front-ir-vd55g0'
OLD=PRE/'e011ai-rear-neutral-scalar-full-integration/native-private.py'
PROD=PRE/'e012k-rear-neutral-scalar-clean-producer'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
spec=importlib.util.spec_from_file_location('retained_scalar_native',OLD)
old=importlib.util.module_from_spec(spec);spec.loader.exec_module(old)
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
class Fixture:
 def __init__(self):
  self.native=old.Native();self.u=self.native.u;self.base=self.native.base
  pe=old.pefile.PE(str(old.DLL))
  self.original=bytes(self.u.mem_read(self.base,pe.OPTIONAL_HEADER.SizeOfImage))
  self.arena=0x78000000;self.u.mem_map(self.arena,0x20000)
  self.phase='idle';self.count=0;self.observed=[]
  self.global_cells=[(0x1798f20,4),(0x1686ed8,2),(0x1795ccc,4),(0x1795cc8,4)]
  for rva,n in self.global_cells:
   sec=pe.get_section_by_rva(rva)
   assert sec.Characteristics&0x80000000 and not sec.Characteristics&0x20000000
  self.u.hook_add(UC_HOOK_CODE,self.code)
  self.u.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def code(self,u,address,size,unused):
  if self.phase=='idle':return
  self.count+=1
  if self.phase=='common':return # Actual retained Native.call owns this proof.
  if self.phase=='builder' and address==self.base+0x85ee78:
   cmd,reg,count,values=(u.reg_read(x) for x in [UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3])
   assert cmd==self.cmd and (reg,count) in [(0x3b60,1),(0x3b68,12)]
   assert values==self.image+(0 if count==1 else 4)
   self.observed.append((reg,count,bytes(u.mem_read(values,count*4))))
   u.reg_write(UC_ARM64_REG_X0,0);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return
  lo,hi=(0xb42840,0xb42a30) if self.phase=='packer' else (0xb41ff0,0xb42160)
  assert self.base+lo<=address<self.base+hi,'unmodeled source branch'
 def write(self,u,access,address,size,value,unused):
  if self.phase=='idle':return
  if self.phase=='common':
   if self.base<=address<self.base+len(self.original):
    assert (address-self.base,size) in self.global_cells,'unowned PE global write'
   else:
    assert (self.native.heap<=address and address+size<=self.native.heap+0x30000) or (self.native.stack<=address and address+size<=self.native.stack+0x10000)
   return
  stack=self.native.stack
  if stack<=address and address+size<=stack+0x10000:return
  assert self.phase=='packer' and self.image<=address and address+size<=self.image+52,'unowned source write'
 def invoke(self,rva,phase):
  u=self.u;self.phase=phase
  regs=[globals()['UC_ARM64_REG_X'+str(i)] for i in range(19,30)]
  values=[0x12300000+i*0x101 for i in range(11)]
  floats=[globals()['UC_ARM64_REG_D'+str(i)] for i in range(8,16)]
  fv=[0x3ff0000000000000+i for i in range(8)]
  for reg,value in zip(regs+floats,values+fv):u.reg_write(reg,value)
  sp=self.native.stack+0xf000
  for reg,val in [(UC_ARM64_REG_X0,self.obj),(UC_ARM64_REG_X1,self.desc),
   (UC_ARM64_REG_X2,self.meta if phase=='packer' else 0),(UC_ARM64_REG_SP,sp),(UC_ARM64_REG_LR,self.native.end)]:
   u.reg_write(reg,val)
  u.emu_start(self.base+rva,self.native.end,count=100000)
  assert u.reg_read(UC_ARM64_REG_PC)==self.native.end and u.reg_read(UC_ARM64_REG_X0)==0
  assert u.reg_read(UC_ARM64_REG_SP)==sp
  assert [u.reg_read(reg) for reg in regs+floats]==values+fv
  self.phase='idle'
 def vector(self,placement,common,seed=0):
  u=self.u;a=self.arena+placement
  self.obj=a+0x100;self.desc=a+0x1000;self.image=a+0x5000
  self.common=a+0x6000;self.meta=a+0x7000;self.cmd=a+0x8000
  u.mem_write(self.arena,bytes(0x20000))
  u.mem_write(self.obj+32,struct.pack('<Q',self.image))
  # Own named public addresses. No native constructor/register-binding claim.
  u.mem_write(self.obj+80,struct.pack('<2I',0x3b60,0x3b68))
  u.mem_write(self.desc+16,struct.pack('<Q',self.common))
  u.mem_write(self.desc+80,struct.pack('<Q',self.cmd))
  u.mem_write(self.common,common)
  u.mem_write(self.image-16,b'\xa5'*16);u.mem_write(self.image+52,b'\x5a'*16)
  u.mem_write(self.image,struct.pack('<13I',*([seed]*13)))
  obj=bytes(u.mem_read(self.obj,128));desc=bytes(u.mem_read(self.desc,0x2020))
  self.invoke(0xb42840,'packer')
  image=bytes(u.mem_read(self.image,52))
  self.observed=[];self.invoke(0xb41ff0,'builder')
  assert self.observed==[(0x3b60,1,image[:4]),(0x3b68,12,image[4:])]
  assert bytes(u.mem_read(self.obj,128))==obj and bytes(u.mem_read(self.desc,0x2020))==desc
  assert bytes(u.mem_read(self.common,52))==common and bytes(u.mem_read(self.image,52))==image
  assert bytes(u.mem_read(self.image-16,16))==b'\xa5'*16 and bytes(u.mem_read(self.image+52,16))==b'\x5a'*16
  return struct.pack('<2I',0x0300000c,0x3b68)+image[4:]
 def derived(self,gain,channel):
  case={'demux_gain':gain,'bls':[0.0]*4,'channel':channel}
  self.phase='common';q=self.native.call(0x998e70,case);self.phase='idle'
  common=bytes(self.u.mem_read(self.native.heap+0x10000,52))
  h=struct.unpack('<26H',common)
  assert h[0]==1 and h[1]==0 and struct.unpack_from('<2I',common,4)==(0x9c,0xca)
  assert h[6:10]==q and not any(h[10:]) and all(1<=x<=0x7fff for x in q)
  return common,list(q)
 def unchanged(self):
  current=bytearray(self.u.mem_read(self.base,len(self.original)))
  for rva,n in self.global_cells:current[rva:rva+n]=self.original[rva:rva+n]
  assert bytes(current)==self.original
def common_for(words):
 q,bi,bo=words[:4],words[4:8],words[8:]
 h=[1,0,0x9c,0,0xca,0,*q]+[0]*16
 for i in range(4):h[10+2*i]=bo[i];h[11+2*i]=bi[i]
 return struct.pack('<26H',*h)
def main():
 O=Path(sys.argv[1]);O.mkdir()
 rng=random.Random(681141);fixture=Fixture();records=[];producer=0
 inputs=[(g,[1.0]*4) for g in [0.5,1.0,2.0,4.0]]
 inputs += [(1.0,[0.5,1.0,2.0,3.0]),(2.0,[2.0,0.5,1.0,3.0])]
 for i in range(64):inputs.append((rng.choice([0.5,1.0,2.0,4.0]),[rng.uniform(0.5,3.9) for j in range(4)]))
 vectors=[[1024]*4+[0]*8,[0x7fff]*4+[0x3fff]*8,[1,2,3,4]+list(range(1,9))]
 for f in range(4):
  for bit in range(15):
   w=[1]*4+[0]*8;w[f]=1<<bit;vectors.append(w)
 for f in range(8):
  for bit in range(14):
   w=[1024]*4+[0]*8;w[4+f]=1<<bit;vectors.append(w)
 for i in range(64):vectors.append([rng.randrange(1,0x8000) for j in range(4)]+[rng.randrange(0x4000) for j in range(8)])
 for placement in [0,128,512]:
  for gain,channel in inputs:
   values=struct.unpack('<5f',struct.pack('<5f',gain,*channel))
   common,q=fixture.derived(values[0],list(values[1:]))
   w=q+[0]*8;oracle=fixture.vector(placement,common)
   records.append(struct.pack('<I5f12I',1,*values,*w)+oracle);producer+=1
  for w in vectors:
   oracle=fixture.vector(placement,common_for(w))
   records.append(struct.pack('<I5f12I',2,1.0,1.0,1.0,1.0,1.0,*w)+oracle)
 # Explicit old-image counterexample: native retains lower unnamed bits.
 clean=fixture.vector(0,common_for([1024]*4+[0]*8))
 inherited=fixture.vector(0,common_for([1024]*4+[0]*8),0xffffffff)
 assert clean!=inherited
 words=struct.unpack('<12I',inherited[8:])
 assert all((w&0x3ffff)==0x3ffff for w in words[4:])
 fixture.unchanged()
 headers={
  'sp11-front-channel-gain.h':Q/'sp11-front-channel-gain.h',
  'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
  'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
  'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():(O/n).write_bytes(p.read_bytes())
 for p in [PROD/'rear-neutral-scalar.h',PROD/'rear-neutral-scalar.c',R/'src/native-rgb/native-front-params.h',Q/'test-native-c.c']:
  (O/p.name).write_bytes(p.read_bytes())
 original=(Q/'sp11-front-channel-gain.h').read_text()
 mutations={
  'wrong_pattern':original.replace('words[0] = 0xcaU;','words[0] = 0x9cU;'),
  'reverse_gain_order':original.replace('state->gain_q10[3] << 16','state->gain_q10[2] << 16'),
  'wrong_black_shift':original.replace('state->black_in14[i] << 18','state->black_in14[i] << 16'),
  'early_publication':original.replace('\tif (!out || !policy || !state)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy || !state)',1),
  'bypass_policy':original.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;')}
 assert all(x!=original for x in mutations.values())
 data=b''.join(records);runs=[]
 for cc in ['gcc','clang']:
  for label,source in [('actual',original),*mutations.items()]:
   (O/'sp11-front-channel-gain.h').write_text(source);exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror',
    '-fsanitize=address,undefined','-fno-omit-frame-pointer','-ffp-contract=off','-I'+str(O),
    str(O/'test-native-c.c'),str(O/'rear-neutral-scalar.c'),'-lm','-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2500:]
   p=subprocess.run([str(exe)],input=data,capture_output=True,timeout=20)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2500:].decode()
    res=json.loads(p.stdout);assert res['native_vectors']==len(records) and res['prior_producer_vectors']==producer
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':res})
   else:assert p.returncode!=0,'unsafe compiled mutation survived '+label
 (O/'sp11-front-channel-gain.h').write_text(original)
 refs=[str(OLD.relative_to(R)),str((PROD/'rear-neutral-scalar.h').relative_to(R)),
 str((PROD/'rear-neutral-scalar.c').relative_to(R)),'src/native-rgb/native-front-params.h',
 'experiments/E004-front-ir-vd55g0/e006z-rear-clean-scalar-bank-providers/camss-e006z-clean-scalar-bank.inc']
 result={'schema':'sp11-channel-gain-native-config-v1',
 'status':'PASS_RETAINED_PRODUCERS_AND_NORMAL_SLOT_NATIVE_CONFIGURATION',
 'original_PE_sha256':old.DLL_SHA,'original_executable_and_other_image_bytes_immutable':True,'original_PE_exported':False,
 'source_owned_writable_nonexecuting_data_cells':[{'rva':hex(rva),'bytes':n} for rva,n in fixture.global_cells],
 'native_cases':len(records),'prior_producer_cases':producer,'native_instructions':fixture.count,
 'placements':3,'SP_callee_saved_restored':True,'image_canaries_intact':True,
 'native_entries':{'common':'0x998e70','packer':'0xb42840','builder':'0xb41ff0'},
 'intercepted_helpers':['0x85ee78 command arguments observer/success status'],
 'packing_arithmetic_or_field_shims':False,'constructor_executed':False,
 'public_address_metadata_owned':{'module':'0x3b60','configuration':'0x3b68'},
 'scope':{'descriptor_slots':[0,0],'source_bayer':2,'period':0,'initial_register_image':'zero',
 'producer_black_offsets':[0,0,0,0],'producer_max_gain_below_normalization':True},
 'nonzero_old_image_counterexample_checked':True,
 'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),
 'header_pins':{n:sha(p) for n,p in headers.items()},'prior_reference_pins':{n:sha(R/n) for n in refs},
 'private_profile_read':False,'private_tuning_read':False,'pixels_read':False,
 'calibration_remeasured':False,'runtime_changed':False,'hardware':False,
 'limits':['Source-only startup configuration; no live front Bayer/pattern/precision/domain proof',
 'Builder address metadata is owned public input, not a source constructor binding',
 'Zero initial image/lower unnamed bits/neutral channel BLS are independent policies, not inherited tuning equivalence',
 'Existing producer is reused only in the non-normalizing synthetic zero-BLS domain',
 'No module activation or separate DEMUX0x3968/0x396c setup or runtime loader replacement']}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','native_cases','prior_producer_cases','native_instructions','runtime_changed']}))
if __name__=='__main__':main()
