#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Original Gamma151 fields and argument handoff; reuse native mapping."""
from pathlib import Path
import importlib.util,json,struct,subprocess,sys
Q=Path(__file__).resolve().parent;R=Q.parents[3]
PRE=R/'src/upstream/isp-config/front-scaler-config-20261014/test-native.py'
s=importlib.util.spec_from_file_location('retained_source_fixture',PRE)
retained=importlib.util.module_from_spec(s);s.loader.exec_module(retained)
sha=retained.sha
class Fixture(retained.Fixture):
 def code(self,u,address,size,_):
  if self.phase=='idle':return
  self.instructions+=1
  if self.phase=='builder' and address in [self.base+0x85ee78,self.base+0x85f108]:
   v=[u.reg_read(getattr(retained,'UC_ARM64_REG_X'+str(i))) for i in range(6)]
   assert v[0]==self.cmd
   if address==self.base+0x85ee78:
    assert v[1:4]==[0x5f58,3,self.image]
    self.observed.append(('reg',v[1],v[2],bytes(u.mem_read(v[3],12))))
   else:
    assert v[1]==0x5f08 and v[2] in [1,2,3] and v[3]==self.dmi and v[5]==1024
    self.observed.append(('dmi',v[1],v[2],v[4],v[5]))
   u.reg_write(retained.UC_ARM64_REG_X0,0);u.reg_write(retained.UC_ARM64_REG_PC,u.reg_read(retained.UC_ARM64_REG_LR));return
  lo,hi=(0xb394a0,0xb3957c) if self.phase=='packer' else (0xb38dd0,0xb38ee0)
  assert self.base+lo<=address<self.base+hi,'unmodeled source instruction'
 def write(self,u,access,address,size,value,_):
  if self.phase=='idle' or self.n.stack<=address<address+size<=self.n.stack+0x10000:return
  assert self.phase=='packer'
  assert self.image<=address<address+size<=self.image+12 or (
   address,size) in [(self.obj+48,8),(self.obj+56,8),(self.obj+64,8)]
 def vector(self,placement,bank,enabled,seed=0,offset=37):
  u=self.u;a=self.arena+placement;u.mem_write(self.arena,bytes(0xa0000))
  self.obj=a+0x1000;self.image=a+0x3000;self.req=a+0x10000
  common=a+0x40000;self.meta=a+0x42000;self.cmd=a+0x48000;self.dmi=a+0x50000
  u.mem_write(self.obj+32,struct.pack('<Q',self.image))
  u.mem_write(common,struct.pack('<2H',bank,enabled))
  pointers=[a+0x60000,a+0x61000,a+0x62000]
  for off,ptr in zip([8,24,40],pointers):u.mem_write(common+off,struct.pack('<Q',ptr))
  u.mem_write(self.image,struct.pack('<3I',seed,seed,seed))
  u.mem_write(self.image-16,b'\xa5'*16);u.mem_write(self.image+12,b'\x5a'*16)
  u.mem_write(self.req+80,struct.pack('<2Q',self.cmd,self.dmi))
  u.mem_write(self.meta,struct.pack('<I',offset))
  watched=[(common,64),(self.req,0x20000),(self.meta,16)]
  before=[bytes(u.mem_read(p,n)) for p,n in watched]
  obj=bytes(u.mem_read(self.obj,128));real_req=self.req;self.req=common
  self.invoke(0xb394a0,'packer');self.req=real_req
  image=bytes(u.mem_read(self.image,12));values=struct.unpack('<3I',image)
  assert values==((seed&~1)|(bank&1),(seed&~1)|(bank&1),(seed&~1)|(enabled&1))
  after=bytearray(u.mem_read(self.obj,128))
  for off,ptr in zip([48,56,64],pointers):
   assert struct.unpack_from('<Q',after,off)[0]==ptr;after[off:off+8]=obj[off:off+8]
  assert bytes(after)==obj
  packed_obj=bytes(u.mem_read(self.obj,128));self.observed=[];self.invoke(0xb38dd0,'builder')
  assert self.observed==[('reg',0x5f58,3,image)]+[
   ('dmi',0x5f08,i+1,offset*4+i*1024,1024) for i in range(3)]
  assert bytes(u.mem_read(self.obj,128))==packed_obj and bytes(u.mem_read(self.image,12))==image
  for (p,n),v in zip(watched,before):assert bytes(u.mem_read(p,n))==v
  assert bytes(u.mem_read(self.image-16,16))==b'\xa5'*16 and bytes(u.mem_read(self.image+12,16))==b'\x5a'*16
  return image
def main():
 O=Path(sys.argv[1]);O.mkdir();f=Fixture();cases=0
 for placement in [0,128,512]:
  for bank in [0,1]:
   for enable in [0,1]:
    for seed in [0,0xffffffff]:
     f.vector(placement,bank,enable,seed);cases+=1
 records=b''.join(f.vector(0,b,1) for b in [0,1]);cases+=2
 for b in [2,3,65535]:assert f.vector(0,b,1)==f.vector(0,b&1,1);cases+=2
 assert f.vector(0,1,2)==f.vector(0,1,0);cases+=2
 f.unchanged()
 headers={
 'sp11-front-gamma-handoff.h':Q/'sp11-front-gamma-handoff.h',
 'native-front-gamma.h':R/'src/native-rgb/native-front-gamma.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():(O/n).write_bytes(p.read_bytes())
 (O/'test-host.c').write_bytes((Q/'test-host.c').read_bytes())
 original=(Q/'sp11-front-gamma-handoff.h').read_text()
 mutations={
 'wrong_semantic_channel':original.replace('{ 1, 2, 0 }','{ 0, 1, 2 }'),
 'wrong_read_bank':original.replace('banks[1] = mapping->bank;','banks[1] = !mapping->bank;'),
 'early_publication':original.replace('\tif (!out || !policy || !mapping || !gamma)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy || !mapping || !gamma)',1),
 'skip_encoding_validation':original.replace('ret = native_front_gamma12_validate(gamma, gamma_bytes);','ret = 0;'),
 'bypass_domain':original.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;')}
 assert all(x!=original for x in mutations.values());runs=[]
 for cc in ['gcc','clang']:
  for label,source in [('actual',original),*mutations.items()]:
   (O/'sp11-front-gamma-handoff.h').write_text(source);exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-fno-omit-frame-pointer','-I'+str(O),str(O/'test-host.c'),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2500:]
   p=subprocess.run([str(exe)],input=records,capture_output=True,timeout=20)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2500:].decode()
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':json.loads(p.stdout)})
   else:assert p.returncode!=0,'unsafe compiled mutation survived '+label
 (O/'sp11-front-gamma-handoff.h').write_text(original)
 result={'schema':'sp11-front-gamma-handoff-source-v1','status':'PASS_REUSED_GAMMA_BANK_AND_DMI_HANDOFF',
 'source_cases':cases,'native_instructions':f.instructions,'placements':3,
 'original_PE_sha256':retained.retained.old.DLL_SHA,'original_PE_immutable':True,
 'SP_callee_saved_restored':True,'canaries_intact':True,'inputs_immutable':True,
 'native_entries':{'packer':'0xb394a0','builder':'0xb38dd0'},
 'intercepted_helpers':['0x85ee78 register command observer/success','0x85f108 DMI argument observer/success'],
 'arithmetic_or_branch_shims':False,'serializer_executed':False,'constructor_executed':False,
 'source_context':{'object_image_pointer':32,'common_bank_u16':0,'common_enable_u16':2,
 'common_G_B_R_pointers':[8,24,40],'request_command_pointer':80,'request_DMI_buffer_pointer':88,
 'builder_metadata_offset_unit':'u32 words; helper receives bytes'},
 'source_fixed_addresses_observed':True,'addresses_substituted':False,
 'source_bank_fields':'bit0 in both5f58 and5f5c','source_enable_field':'bit0 at5f60',
 'source_truncation_counterexamples_checked':True,'nonzero_residual_counterexample_checked':True,
 'configuration_addresses':['0x5f58','0x5f5c'],'separate_activation_address':'0x5f60',
 'prepare_bytes':52,'activation_bytes':12,'DMI_selector_register':'0x5f08',
 'semantic_RGB_DMA_channel_offsets':[1024,2048,0],
 'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),
 'header_pins':{n:sha(p) for n,p in headers.items()},
 'prior_reference_pins':{str(PRE.relative_to(R)):sha(PRE),
 'src/native-rgb/native-front-gamma-kernel.inc':sha(R/'src/native-rgb/native-front-gamma-kernel.inc')},
 'CPU_DMA_correspondence_proven':False,'physical_channel_binding_proven':False,
 'activation_after_DMI_hardware_order_proven':False,'request_bank_lifetime_integrated':False,
 'private_profile_read':False,'private_tuning_read':False,'pixels_read':False,'calibration_remeasured':False,
 'runtime_changed':False,'installed':False,'loaded':False,'hardware':False}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','source_cases','native_instructions','compiler_runs','hardware']}))
if __name__=='__main__':main()
