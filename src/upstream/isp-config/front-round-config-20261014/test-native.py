#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Bind existing video configuration to original source; no new field math."""
from pathlib import Path
import hashlib,importlib.util,json,resource,struct,subprocess,sys
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
Q=Path(__file__).resolve().parent;R=Q.parents[3]
PRE=R/'src/upstream/isp-config/front-channel-gain-20261014/test-native.py'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('retained_channel_fixture',PRE)
retained=importlib.util.module_from_spec(s);s.loader.exec_module(retained)
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
class Fixture:
 def __init__(self):
  self.n=retained.old.Native();self.u=self.n.u;self.base=self.n.base
  pe=retained.old.pefile.PE(str(retained.old.DLL))
  self.original=bytes(self.u.mem_read(self.base,pe.OPTIONAL_HEADER.SizeOfImage))
  self.arena=0x78000000;self.u.mem_map(self.arena,0x50000)
  self.phase='idle';self.instructions=0;self.observed=[]
  self.u.hook_add(UC_HOOK_CODE,self.code);self.u.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def code(self,u,address,size,_):
  if self.phase=='idle':return
  self.instructions+=1
  if self.phase=='builder' and address==self.base+0x85ee78:
   cmd,reg,count,values=[u.reg_read(x) for x in [UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3]]
   assert cmd==self.cmd
   assert (reg,count) in [(self.lbase,1),(self.lbase+16,10)]+(
    [(self.cbase,1),(self.cbase+16,10)] if self.cbase else [])
   offset=(0 if reg==self.lbase else 4) if reg<self.lbase+0x20 else (44 if reg==self.cbase else 48)
   assert values==self.image+self.slot+offset
   self.observed.append((reg,count,bytes(u.mem_read(values,count*4))))
   u.reg_write(UC_ARM64_REG_X0,0);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return
  lo,hi=(0xb54b50,0xb55540) if self.phase=='packer' else (0xb54810,0xb54b50)
  assert self.base+lo<=address<self.base+hi,'unmodeled source instruction'
 def write(self,u,access,address,size,value,_):
  if self.phase=='idle':return
  if self.n.stack<=address and address+size<=self.n.stack+0x10000:return
  if address==self.obj+40 and size==4:return
  assert self.phase=='packer',(self.phase,hex(address-self.arena),size,hex(u.reg_read(UC_ARM64_REG_PC)-self.base))
  assert (self.image+self.slot<=address and address+size<=self.image+self.slot+(88 if self.cbase else 44)) or (
   address in [self.obj+40,self.obj+44] and size==4),'unowned source write'
 def invoke(self,rva,phase):
  u=self.u;self.phase=phase
  regs=[globals()['UC_ARM64_REG_X'+str(i)] for i in range(19,30)]
  regs += [globals()['UC_ARM64_REG_D'+str(i)] for i in range(8,16)]
  values=[0x12300000+i*0x101 for i in range(11)]+[0x3ff0000000000000+i for i in range(8)]
  for reg,value in zip(regs,values):u.reg_write(reg,value)
  sp=self.n.stack+0xf000
  for reg,value in [(UC_ARM64_REG_X0,self.obj),(UC_ARM64_REG_X1,self.req),(UC_ARM64_REG_X2,self.meta),
   (UC_ARM64_REG_SP,sp),(UC_ARM64_REG_LR,self.n.end)]:u.reg_write(reg,value)
  u.emu_start(self.base+rva,self.n.end,count=100000)
  assert u.reg_read(UC_ARM64_REG_PC)==self.n.end and u.reg_read(UC_ARM64_REG_X0)==0
  assert u.reg_read(UC_ARM64_REG_SP)==sp
  assert [u.reg_read(x) for x in regs]==values
  self.phase='idle'
 def vector(self,placement,path,bits,metadata_seed=0,image_seed=0):
  u=self.u;a=self.arena+placement
  self.obj=a+0x1000;self.image=a+0x3000;self.req=a+0x10000
  self.sink=a+0x40000;self.meta=a+0x44000;self.cmd=a+0x48000
  self.lbase,self.cbase,self.slot={0:(0x9c60,0x9e60,0),2:(0xa460,0xa660,0xb0),
   3:(0xac60,0xae60,0x108),8:(0x7660,0,0x268)}[path]
  u.mem_write(self.arena,bytes(0x50000))
  u.mem_write(self.obj+32,struct.pack('<Q',self.image));u.mem_write(self.obj+40,struct.pack('<2I',metadata_seed,metadata_seed))
  u.mem_write(self.req+80,struct.pack('<Q',self.cmd));u.mem_write(self.req+0xf28,struct.pack('<Q',self.sink))
  u.mem_write(self.req+0xf80,struct.pack('<I',path));u.mem_write(self.req+0x16cd8,struct.pack('<I',bits))
  u.mem_write(self.image,struct.pack('<256I',*([image_seed]*256)))
  u.mem_write(self.image-16,b'\xa5'*16);u.mem_write(self.image+1024,b'\x5a'*16)
  before_obj=bytes(u.mem_read(self.obj,128));before_req=bytes(u.mem_read(self.req,0x20000))
  before_sink=bytes(u.mem_read(self.sink,0x2000));before_meta=bytes(u.mem_read(self.meta,128))
  self.invoke(0xb54b50,'packer');image=bytes(u.mem_read(self.image,1024))
  after_obj=bytearray(u.mem_read(self.obj,128));after_obj[40:48]=before_obj[40:48]
  assert bytes(after_obj)==before_obj and bytes(u.mem_read(self.req,0x20000))==before_req
  assert bytes(u.mem_read(self.sink,0x2000))==before_sink and bytes(u.mem_read(self.meta,128))==before_meta
  packed_obj=bytes(u.mem_read(self.obj,128))
  self.observed=[];self.invoke(0xb54810,'builder')
  assert bytes(u.mem_read(self.obj,128))==packed_obj
  assert bytes(u.mem_read(self.req,0x20000))==before_req
  expected=[(self.lbase,1,image[self.slot:self.slot+4]),(self.lbase+16,10,image[self.slot+4:self.slot+44])]
  if self.cbase:expected += [(self.cbase,1,image[self.slot+44:self.slot+48]),(self.cbase+16,10,image[self.slot+48:self.slot+88])]
  assert self.observed==expected and bytes(u.mem_read(self.image,1024))==image
  assert bytes(u.mem_read(self.image-16,16))==b'\xa5'*16 and bytes(u.mem_read(self.image+1024,16))==b'\x5a'*16
  return self.observed
 def unchanged(self):
  assert bytes(self.u.mem_read(self.base,len(self.original)))==self.original
def main():
 O=Path(sys.argv[1]);O.mkdir()
 f=Fixture();records=[];source_cases=0
 # Old FULL encoder is admitted at8/10 only; other source paths are counterexamples.
 for placement in [0,128,512]:
  for path in [0,2,3,8]:
   for bits in [8,10,14]:
    for seed in [0,1,0xffffffff]:
     commands=f.vector(placement,path,bits,seed);source_cases+=1
     maximum=(1<<bits)-1;rounding=max(0,(14 if path==8 else 10)-bits)
     for plane in range(1,len(commands),2):
      words=struct.unpack('<10I',commands[plane][2]);chroma=plane==3
      expected=[0,(7 if chroma else 6)|(rounding<<3),0,0,0,0,maximum,0,0,0]
      if chroma:expected[3]=7|(rounding<<3);expected[7]=maximum
      assert list(words)==expected
     if path==0 and bits in [8,10]:
      data=b''.join(struct.pack('<2I',0x0300000a,commands[i][0])+commands[i][2] for i in [1,3])
      records.append(struct.pack('<I',bits)+data)
 # Unsupported source declarations enter logging helpers and are outside this fixture.
 eight=f.vector(0,0,8);source_cases+=1
 # Zero software image is own policy; original source preserves residual bits.
 residual=f.vector(0,0,8,image_seed=0xffffffff);source_cases+=1
 assert residual[1][2]!=eight[1][2] and residual[3][2]!=eight[3][2]
 # Module control differs from the historical helper; it is explicitly excluded.
 assert struct.unpack('<I',eight[0][2])[0]==0xc01
 assert struct.unpack('<I',eight[2][2])[0]==0x3c01
 f.unchanged()
 headers={
 'sp11-front-round-config.h':Q/'sp11-front-round-config.h',
 'sp11-front-fields.h':R/'src/upstream/isp-config/sp11-front-fields.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for name,p in headers.items():(O/name).write_bytes(p.read_bytes())
 (O/'test-host.c').write_bytes((Q/'test-host.c').read_bytes())
 original=(Q/'sp11-front-round-config.h').read_text()
 mutations={
 'wrong_slice':original.replace('tmp + 72, 48','tmp + 60, 48'),
 'early_publication':original.replace('\tif (!out || !policy)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy)',1),
 'foreign_input_precision':original.replace('input_bits != 10 ||','input_bits > 32 ||'),
 'bypass_policy':original.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;')}
 assert all(x!=original for x in mutations.values())
 runs=[];data=b''.join(records)
 for cc in ['gcc','clang']:
  for label,source in [('actual',original),*mutations.items()]:
   (O/'sp11-front-round-config.h').write_text(source);exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-fno-omit-frame-pointer','-I'+str(O),str(O/'test-host.c'),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2500:]
   p=subprocess.run([str(exe)],input=data,capture_output=True,timeout=20)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2500:].decode()
    result=json.loads(p.stdout);assert result['native_full_vectors']==len(records)
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':result})
   else:assert p.returncode!=0,'unsafe compiled mutation survived '+label
 (O/'sp11-front-round-config.h').write_text(original)
 result={'schema':'sp11-front-round-config-v1','status':'PASS_REUSED_FULL_VIDEO_CONFIGURATION',
  'original_PE_sha256':retained.old.DLL_SHA,'original_PE_immutable':True,'original_PE_exported':False,
  'source_cases':source_cases,'admitted_full_config_cases':len(records),'native_instructions':f.instructions,
  'placements':3,'SP_callee_saved_restored':True,'canaries_intact':True,
  'native_entries':{'packer':'0xb54b50','builder':'0xb54810'},
  'partial_source_context':{'object_image_pointer':32,'object_path_and_control_writes':[40,44],
   'request_command_pointer':80,'request_output_context_pointer':'0xf28',
   'request_path':'0xf80','request_output_bits':'0x16cd8'},
  'native_source_register_binding':True,'builder_addresses_substituted':False,
  'constructor_executed':False,'intercepted_helpers':['0x85ee78 command observer/success only'],
  'arithmetic_or_branch_shims':False,'initial_software_image':'own zero',
  'nonzero_residual_counterexample_checked':True,'unsupported_source_output_widths_executed':False,
  'video_source_paths':[0,2,3],'raw_source_counterexample_path':8,
  'source_rounding_formula':{'video':'max(0,10-output_bits)','pixel_raw':'14-output_bits'},
  'historical_module_control_not_equivalent':True,'compiler_excludes_all_module_control':True,
  'configuration_bytes':96,'configuration_register_words':20,'compiler_runs':runs,
  'compiled_mutations_rejected_each':list(mutations),'header_pins':{n:sha(p) for n,p in headers.items()},
  'prior_reference_pins':{str(PRE.relative_to(R)):sha(PRE),
   'experiments/E004-front-ir-vd55g0/e006p-rear-crop-roundclamp-packers/camss-e006p-crop-roundclamp.inc':sha(R/'experiments/E004-front-ir-vd55g0/e006p-rear-crop-roundclamp-packers/camss-e006p-crop-roundclamp.inc')},
  'private_profile_read':False,'private_tuning_read':False,'pixels_read':False,'calibration_changed':False,
  'installed':False,'loaded':False,'runtime_changed':False,'hardware':False,
  'limits':['Source-only semantic output declaration and partial owned contexts; no physical video input-depth proof',
   'Gamma12 lookup representation does not prove a12-bit input to RoundClamp',
   'CST12-to-video10 conversion remains unbound; caller precision tag is a gate, not evidence',
   'Source zero-image policy is not hardware reset proof or inherited startup equivalence',
   'Source module controls differ from old helper and are excluded, not silently reconciled',
   'No crop/scaler/bus/DMI/activation/private-loader integration']}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','source_cases','admitted_full_config_cases','native_instructions','hardware']}))
if __name__=='__main__':main()
