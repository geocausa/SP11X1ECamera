#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reuse prior bounded native mapper/caller checks and both Crop12 compilers."""
from pathlib import Path
import importlib.util,json,struct,subprocess,sys
Q=Path(__file__).resolve().parent;R=Q.parents[3]
PRE=R/'src/upstream/isp-config/front-scaler-config-20261014/test-native.py'
OLD=R/'experiments/E004-front-ir-vd55g0/e006p-rear-crop-roundclamp-packers/camss-e006p-crop-roundclamp.inc'
s=importlib.util.spec_from_file_location('retained_scaler_fixture',PRE)
retained=importlib.util.module_from_spec(s);s.loader.exec_module(retained)
sha=retained.sha
class Fixture(retained.Fixture):
 def code(self,u,address,size,_):
  if self.phase=='idle':return
  self.instructions+=1
  if self.phase=='builder' and address==self.base+0x85ee78:
   cmd,reg,count,ptr=[u.reg_read(x) for x in [retained.UC_ARM64_REG_X0,retained.UC_ARM64_REG_X1,retained.UC_ARM64_REG_X2,retained.UC_ARM64_REG_X3]]
   assert cmd==self.cmd and (reg,count) in [(self.lbase,2),(self.cbase,2)]
   assert ptr==self.image+self.slot+(0 if reg==self.lbase else 8)
   self.observed.append((reg,count,bytes(u.mem_read(ptr,count*4))))
   u.reg_write(retained.UC_ARM64_REG_X0,0);u.reg_write(retained.UC_ARM64_REG_PC,u.reg_read(retained.UC_ARM64_REG_LR));return
  lo,hi=(0xb57980,0xb580cc) if self.phase=='packer' else (0xb57740,0xb57974)
  assert self.base+lo<=address<self.base+hi,'unmodeled source instruction'
 def write(self,u,access,address,size,value,_):
  if self.phase=='idle':return
  if self.n.stack<=address and address+size<=self.n.stack+0x10000:return
  assert self.phase=='packer'
  assert (self.image+self.slot<=address and address+size<=self.image+self.slot+16) or (
   address==self.obj+40 and size==8),'unowned source write'
 def vector(self,placement,dims,video=1,seed=0,depth=0):
  u=self.u;a=self.arena+placement;u.mem_write(self.arena,bytes(0xa0000))
  self.obj=a+0x1000;self.image=a+0x3000;self.req=a+0x10000
  self.meta=a+0x40000;self.luma=a+0x42000;self.chroma=a+0x43000;self.cmd=a+0x48000
  self.slot=0 if video else 16;self.lbase=0x9c68 if video else 0x7c68;self.cbase=self.lbase+0x200
  ow,oh=dims
  u.mem_write(self.obj+32,struct.pack('<Q',self.image));u.mem_write(self.obj+48,struct.pack('<I',video))
  u.mem_write(self.req+80,struct.pack('<Q',self.cmd));u.mem_write(self.req+0x16cd8,struct.pack('<I',depth))
  u.mem_write(self.meta+16,struct.pack('<2Q',self.luma,self.chroma))
  u.mem_write(self.luma,struct.pack('<4I',0,0,ow-1,oh-1))
  u.mem_write(self.chroma,struct.pack('<4I',0,0,ow//2-1,oh//2-1))
  initial=struct.pack('<8I',*([seed]*8));u.mem_write(self.image,initial)
  u.mem_write(self.image-16,b'\xa5'*16);u.mem_write(self.image+32,b'\x5a'*16)
  watched=[(self.req,0x20000),(self.meta,128),(self.luma,16),(self.chroma,16)]
  before=[bytes(u.mem_read(p,n)) for p,n in watched];obj=bytes(u.mem_read(self.obj,128))
  self.invoke(0xb57980,'packer')
  after=bytearray(u.mem_read(self.obj,128));after[40:48]=obj[40:48];assert bytes(after)==obj
  image=bytes(u.mem_read(self.image,32));other=16 if video else 0
  assert image[other:other+16]==initial[other:other+16]
  packed_obj=bytes(u.mem_read(self.obj,128));self.observed=[];self.invoke(0xb57740,'builder')
  assert self.observed==[(self.lbase,2,image[self.slot:self.slot+8]),(self.cbase,2,image[self.slot+8:self.slot+16])]
  assert bytes(u.mem_read(self.obj,128))==packed_obj and bytes(u.mem_read(self.image,32))==image
  for (p,n),v in zip(watched,before):assert bytes(u.mem_read(p,n))==v
  assert bytes(u.mem_read(self.image-16,16))==b'\xa5'*16 and bytes(u.mem_read(self.image+32,16))==b'\x5a'*16
  return b''.join(struct.pack('<2I',0x03000002,reg)+data for reg,_,data in self.observed)
def main():
 O=Path(sys.argv[1]);O.mkdir();f=Fixture();records=[];cases=0
 dims=[(2560,1440),(3840,2160),(1920,1080),(1280,720),(2,2),(4,4),(8192,8192),(16384,16384)]
 for placement in [0,128,512]:
  for d in dims:records.append(struct.pack('<2I',*d)+f.vector(placement,d));cases+=1
 reference=f.vector(0,dims[0]);cases+=1
 for b in [8,10,12,14]:assert f.vector(0,dims[0],depth=b)==reference;cases+=1
 display=f.vector(0,dims[0],video=0);cases+=1;assert display!=reference
 residual=f.vector(0,dims[0],seed=0xffffffff);cases+=1;assert residual!=reference
 f.unchanged()
 headers={
 'sp11-front-crop-config.h':Q/'sp11-front-crop-config.h',
 'sp11-geometry-stats.h':R/'src/upstream/isp-config/sp11-geometry-stats.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():(O/n).write_bytes(p.read_bytes())
 (O/OLD.name).write_bytes(OLD.read_bytes());(O/'test-host.c').write_bytes((Q/'test-host.c').read_bytes())
 original=(Q/'sp11-front-crop-config.h').read_text()
 mutations={
 'wrong_slice':original.replace('full + 96','full + 80'),
 'early_publication':original.replace('\tif (!out || !policy)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy)',1),
 'bypass_domain':original.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;')}
 assert all(x!=original for x in mutations.values());runs=[];data=b''.join(records)
 for cc in ['gcc','clang']:
  for label,source in [('actual',original),*mutations.items()]:
   (O/'sp11-front-crop-config.h').write_text(source);exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-fno-omit-frame-pointer','-I'+str(O),str(O/'test-host.c'),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2500:]
   p=subprocess.run([str(exe)],input=data,capture_output=True,timeout=20)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':assert p.returncode==0,p.stderr[-2500:].decode();runs.append({'compiler':cc,'ASan_UBSan':True,'result':json.loads(p.stdout)})
   else:assert p.returncode!=0,'unsafe compiled mutation survived '+label
 (O/'sp11-front-crop-config.h').write_text(original)
 result={'schema':'sp11-front-crop-source-v1','status':'PASS_REUSED_FRONT_VIDEO_CROP',
 'source_cases':cases,'comparison_records':len(records),'native_instructions':f.instructions,
 'original_PE_sha256':retained.retained.old.DLL_SHA,'original_PE_immutable':True,'original_PE_exported':False,
 'SP_callee_saved_restored':True,'canaries_intact':True,'placements':3,
 'native_entries':{'packer':'0xb57980','builder':'0xb57740'},
 'intercepted_helpers':['0x85ee78 command observer/success only'],'arithmetic_or_branch_shims':False,
 'partial_context':{'object_image_pointer':32,'object_video_selector':48,'video_selector_value':1,
 'metadata_luma_pointer':16,'metadata_chroma_pointer':24,'rectangle_order':'first_pixel,first_line,last_pixel,last_line',
 'source_video_image_offset':0,'source_display_image_offset':16},
 'source_builder_fixed_addresses_observed':True,'addresses_substituted':False,
 'constructor_executed':False,'display_counterexample_checked':True,'nonzero_residual_counterexample_checked':True,
 'configuration_words':4,'configuration_bytes':32,'module_or_extra_CFG_commands_emitted':0,
 'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),
 'header_pins':{n:sha(p) for n,p in headers.items()},'prior_reference_pins':{str(PRE.relative_to(R)):sha(PRE),str(OLD.relative_to(R)):sha(OLD)},
 'private_profile_read':False,'private_tuning_read':False,'pixels_read':False,'calibration_remeasured':False,
 'runtime_changed':False,'installed':False,'loaded':False,'hardware':False,
 'limits':['Own video selector1 and partial contexts are source field binding, not a constructor/live routing proof',
 'Own origin-zero2560x1440 luma/1280x720 chroma policy only; runtime sensor/format negotiation remains unqualified',
 'No pixel-depth inference from dimension packing; full colour/module/Gamma/DMI/startup ownership remains open',
 'Zero software image does not establish hardware reset or inherited startup equivalence']}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','source_cases','comparison_records','native_instructions','hardware']}))
if __name__=='__main__':main()
