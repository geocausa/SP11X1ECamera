#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reuse native mapping and both retained scaler packers; bind front geometry."""
from pathlib import Path
import hashlib,importlib.util,json,resource,struct,subprocess,sys
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
Q=Path(__file__).resolve().parent;R=Q.parents[3]
PRE=R/'src/upstream/isp-config/front-channel-gain-20261014/test-native.py'
OLD=R/'experiments/E004-front-ir-vd55g0/e006q-rear-mnds23-packer/camss-e006q-mnds23.inc'
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
s=importlib.util.spec_from_file_location('retained_native_mapping',PRE)
retained=importlib.util.module_from_spec(s);s.loader.exec_module(retained)
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
class Fixture:
 def __init__(self):
  self.n=retained.old.Native();self.u=self.n.u;self.base=self.n.base
  pe=retained.old.pefile.PE(str(retained.old.DLL))
  self.original=bytes(self.u.mem_read(self.base,pe.OPTIONAL_HEADER.SizeOfImage))
  self.arena=0x78000000;self.u.mem_map(self.arena,0xa0000)
  self.phase='idle';self.instructions=0;self.observed=[]
  self.u.hook_add(UC_HOOK_CODE,self.code);self.u.hook_add(UC_HOOK_MEM_WRITE,self.write)
 def code(self,u,address,size,_):
  if self.phase=='idle':return
  self.instructions+=1
  if self.phase=='builder' and address==self.base+0x85ee78:
   cmd,reg,count,values=[u.reg_read(x) for x in [UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3]]
   assert cmd==self.cmd and (reg,count) in [(0x9860,10),(0x9a60,10)]
   assert values==self.image+(160 if reg==0x9860 else 200)
   self.observed.append((reg,count,bytes(u.mem_read(values,count*4))))
   u.reg_write(UC_ARM64_REG_X0,0);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return
  # Actual original FRINTA helper runs; no arithmetic interception.
  if self.base+0x14d0<=address<self.base+0x14d8:return
  lo,hi=(0xb48e10,0xb4a82c) if self.phase=='packer' else (0xb48e10,0xb49024)
  assert self.base+lo<=address<self.base+hi,'unmodeled source instruction'
 def write(self,u,access,address,size,value,_):
  if self.phase=='idle':return
  if self.n.stack<=address and address+size<=self.n.stack+0x10000:return
  assert self.phase=='packer'
  assert (self.image+160<=address and address+size<=self.image+240) or (
   (address,size) in [(self.obj+40,8),(self.obj+48,4),(self.obj+56,8)]),(hex(address-self.arena),size,hex(u.reg_read(UC_ARM64_REG_PC)-self.base))
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
  assert u.reg_read(UC_ARM64_REG_SP)==sp and [u.reg_read(x) for x in regs]==values
  self.phase='idle'
 def vector(self,placement,dims,image_seed=0,request_depth=0):
  u=self.u;a=self.arena+placement
  self.obj=a+0x1000;self.image=a+0x3000;self.req=a+0x10000
  self.meta=a+0x40000;self.geom=a+0x42000;self.cmd=a+0x48000
  self.stripe=a+0x50000;self.sink=a+0x90000
  iw,ih,ow,oh=dims
  u.mem_write(self.arena,bytes(0xa0000))
  u.mem_write(self.obj+32,struct.pack('<Q',self.image))
  u.mem_write(self.meta,struct.pack('<Q',self.geom))
  # Chroma divisors are actual float32 source inputs; path1 is VIDEO FULL.
  u.mem_write(self.meta+12,struct.pack('<2fI',2.0,2.0,1))
  u.mem_write(self.geom+4,struct.pack('<4I',0,0,iw-1,ih-1))
  u.mem_write(self.geom+0x3c,struct.pack('<2I',iw,ih))
  u.mem_write(self.geom+0x64,struct.pack('<2I',ow,oh))
  for off,value in [(80,self.cmd),(0xf20,self.stripe),(0xf28,self.sink)]:
   u.mem_write(self.req+off,struct.pack('<Q',value))
  # Request output width belongs to RoundClamp, not this normal MNDS path.
  u.mem_write(self.req+0x16cd8,struct.pack('<I',request_depth))
  u.mem_write(self.image,struct.pack('<60I',*([image_seed]*60)))
  u.mem_write(self.image-16,b'\xa5'*16);u.mem_write(self.image+240,b'\x5a'*16)
  watched=[(self.req,0x20000),(self.geom,0x200),(self.meta,128),(self.stripe,0x40000)]
  snapshots=[bytes(u.mem_read(p,n)) for p,n in watched]
  obj=bytes(u.mem_read(self.obj,128))
  self.invoke(0xb4a140,'packer')
  after=bytearray(u.mem_read(self.obj,128))
  for start,n in [(40,8),(48,4),(56,8)]:after[start:start+n]=obj[start:start+n]
  assert bytes(after)==obj
  image=bytes(u.mem_read(self.image,240))
  assert image[:160]==struct.pack('<40I',*([image_seed]*40))
  packed_obj=bytes(u.mem_read(self.obj,128))
  self.observed=[];self.invoke(0xb48e10,'builder')
  assert self.observed==[(0x9860,10,image[160:200]),(0x9a60,10,image[200:240])]
  assert bytes(u.mem_read(self.image,240))==image and bytes(u.mem_read(self.obj,128))==packed_obj
  for (p,n),before in zip(watched,snapshots):assert bytes(u.mem_read(p,n))==before
  assert bytes(u.mem_read(self.image-16,16))==b'\xa5'*16 and bytes(u.mem_read(self.image+240,16))==b'\x5a'*16
  return b''.join(struct.pack('<2I',0x03000009,base+4)+data[4:] for base,_,data in self.observed)
 def unchanged(self):assert bytes(self.u.mem_read(self.base,len(self.original)))==self.original
def main():
 O=Path(sys.argv[1]);O.mkdir()
 f=Fixture();records=[];source_cases=0
 dimensions=[(3840,2160,2560,1440),(3840,2160,3840,2160),(1920,1080,1280,720),
  (1280,720,640,360),(2560,1440,1280,720),(3840,2160,1280,720),(4,4,2,2),(16384,16384,8192,8192)]
 for placement in [0,128,512]:
  for dims in dimensions:
   oracle=f.vector(placement,dims);source_cases+=1
   records.append(struct.pack('<4I',*dims)+oracle)
 # Changing unrelated request output-depth declaration changes no MNDS byte.
 chosen=dimensions[0];reference=f.vector(0,chosen);source_cases+=1
 for bits in [8,10,12,14]:
  assert f.vector(0,chosen,request_depth=bits)==reference;source_cases+=1
 residual=f.vector(0,chosen,image_seed=0xffffffff);source_cases+=1
 assert residual!=reference # Whole software zero image is own policy.
 f.unchanged()
 headers={
 'sp11-front-scaler-config.h':Q/'sp11-front-scaler-config.h',
 'sp11-geometry-stats.h':R/'src/upstream/isp-config/sp11-geometry-stats.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():(O/n).write_bytes(p.read_bytes())
 (O/OLD.name).write_bytes(OLD.read_bytes());(O/'test-host.c').write_bytes((Q/'test-host.c').read_bytes())
 original=(Q/'sp11-front-scaler-config.h').read_text()
 mutations={
 'wrong_slice':original.replace('48 * plane + 12','48 * plane + 8'),
 'wrong_video_target':original.replace('0x9864U','0x7864U'),
 'early_publication':original.replace('\tif (!out || !policy)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy)',1),
 'bypass_domain':original.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;')}
 assert all(x!=original for x in mutations.values())
 runs=[];data=b''.join(records)
 for cc in ['gcc','clang']:
  for label,source in [('actual',original),*mutations.items()]:
   (O/'sp11-front-scaler-config.h').write_text(source);exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-fno-omit-frame-pointer','-I'+str(O),str(O/'test-host.c'),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2500:]
   p=subprocess.run([str(exe)],input=data,capture_output=True,timeout=20)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2500:].decode()
    res=json.loads(p.stdout);assert res['native_vectors']==len(records)
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':res})
   else:assert p.returncode!=0,'unsafe compiled mutation survived '+label
 (O/'sp11-front-scaler-config.h').write_text(original)
 result={'schema':'sp11-front-scaler-source-v1','status':'PASS_REUSED_FRONT_VIDEO_SCALER_CONFIGURATION',
  'original_PE_sha256':retained.old.DLL_SHA,'original_PE_immutable':True,'original_PE_exported':False,
  'native_source_cases':source_cases,'native_comparison_records':len(records),'native_instructions':f.instructions,
  'placements':3,'SP_callee_saved_restored':True,'canaries_intact':True,
  'native_entries':{'packer':'0xb4a140','builder':'0xb48e10','video_luma':'0xb49438','round_float':'0x14d0'},
  'intercepted_helpers':['0x85ee78 command observer/success only'],'arithmetic_or_branch_shims':False,
  'constructor_executed':False,'partial_owned_contexts':True,
  'normal_path_source_inputs':{'metadata_geometry_pointer':0,'metadata_chroma_divisors_float32':[12,16],
   'metadata_path':20,'video_full_path':1,'geometry_input_dimensions':['0x3c','0x40'],
   'geometry_output_dimensions':['0x64','0x68'],'geometry_origin_and_end_coordinates':[4,8,12,16],
   'request_stripe_pointer':'0xf20','stripe_override_flag':'0xd920'},
  'original_builder_fixed_addresses_observed':True,'addresses_substituted':False,
  'unrelated_request_output_depths_unchanged':[8,10,12,14],
  'normal_MNDS_sample_depth_conversion_proven':False,
  'initial_image':'own zero','nonzero_residual_counterexample_checked':True,
  'source_video_image_offset':160,'configuration_words':18,'configuration_bytes':88,'module_control_commands_emitted':0,'Crop12_commands_emitted':0,
  'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),
  'header_pins':{n:sha(p) for n,p in headers.items()},
  'prior_reference_pins':{str(PRE.relative_to(R)):sha(PRE),str(OLD.relative_to(R)):sha(OLD)},
  'private_profile_read':False,'private_tuning_read':False,'pixels_read':False,'calibration_remeasured':False,
  'runtime_changed':False,'installed':False,'loaded':False,'hardware':False,
  'limits':['Only calibrated front3840x2160 to2560x1440 wrapper admitted; other synthetic dimensions test existing packers',
   'Owned partial contexts and source normal stripe-disabled path; no independent source constructor or runtime mode negotiation',
   'Gamma table precision, CST12 output policy and video10 rounding are not a bound physical precision chain',
   'Configuration word0x600 is source normal-path encoding, not proof of a named sample-depth conversion',
   'Source image can preserve reserved residue; own zero image is not physical reset or inherited-profile equality',
   'No separate Crop12/module/bus/DMI/activation/startup ownership integration']}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','native_source_cases','native_comparison_records','native_instructions','hardware']}))
if __name__=='__main__':main()
