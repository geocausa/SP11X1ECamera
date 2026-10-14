#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Complete original packers/builders for the four table bank fields."""
from pathlib import Path
import importlib.util,json,struct,subprocess,sys
Q=Path(__file__).resolve().parent;R=Q.parents[3]
PRE=R/'src/upstream/isp-config/front-table-handoff-20261014/test-native.py'
s=importlib.util.spec_from_file_location('retained_table_fixture',PRE)
retained=importlib.util.module_from_spec(s);s.loader.exec_module(retained)
sha=retained.sha
class Fixture(retained.Fixture):
 def code(self,u,address,size,_):
  if self.phase!='packer':return super().code(u,address,size,_)
  self.instructions+=1
  lo,hi=(0xb3d8a0,0xb3dcf4) if self.kind=='LSC' else (0xb41090,0xb41af8)
  assert self.base+lo<=address<self.base+hi,'unmodeled original packer instruction'
 def write(self,u,access,address,size,value,_):
  if self.phase=='idle' or self.n.stack<=address<address+size<=self.n.stack+0x10000:return
  assert self.phase=='packer'
  metadata=[(40,8),(48,8),(56,8)] if self.kind=='LSC' else [(80,8)]
  spans=[(self.image,64 if self.kind=='LSC' else 104)]
  spans += [(p,884 if self.kind=='LSC' else 256) for p in self.tables]
  assert (address-self.obj,size) in metadata or any(p<=address<address+size<=p+n for p,n in spans),'unowned original write'
 def vector(self,placement,kind,bank,wide_sample=False):
  self.kind=kind;self.offset=37;u=self.u;a=self.arena+placement
  u.mem_write(self.arena,bytes(0xa0000));self.obj=a+0x1000;self.image=a+0x3000
  self.req=a+0x10000;common=self.req;self.meta=a+0x40000
  block=a+0x50000;self.tables=[a+0x60000+i*0x1000 for i in range(3 if kind=='LSC' else 1)]
  u.mem_write(self.obj,struct.pack('<Q',self.image));u.mem_write(self.obj+32,struct.pack('<Q',self.image))
  if kind=='LSC':
   u.mem_write(common+8,struct.pack('<H',bank));u.mem_write(common+0x14,struct.pack('<2I',15,11))
   u.mem_write(self.meta+16,struct.pack('<3Q',*self.tables))
   if wide_sample:
    assert bank==0;u.mem_write(common+0x1c,struct.pack('<H',0x2000))
   packer=0xb3d8a0;metadata=[40,48,56]
  else:
   # Descriptor fields4<2,8<3; own selected0/0, actual common pointer16.
   u.mem_write(common+16,struct.pack('<Q',block))
   u.mem_write(block+0x26,struct.pack('<H',bank))
   u.mem_write(self.meta+8,struct.pack('<Q',self.tables[0]))
   packer=0xb41090;metadata=[80]
  watched=[(common,0x18a0),(self.meta,64),(block,1024)]
  before=[bytes(u.mem_read(p,n)) for p,n in watched];obj=bytes(u.mem_read(self.obj,128))
  u.mem_write(self.image-16,b'\xa5'*16);u.mem_write(self.image+104,b'\x5a'*16)
  length=884 if kind=='LSC' else 256
  for p in self.tables:
   u.mem_write(p-16,b'\xa5'*16);u.mem_write(p,b'\xa5'*length);u.mem_write(p+length,b'\x5a'*16)
  self.invoke(packer,'packer')
  after=bytearray(u.mem_read(self.obj,128))
  for off,p in zip(metadata,self.tables):
   assert struct.unpack_from('<Q',after,off)[0]==p
   after[off:off+8]=obj[off:off+8]
  assert bytes(after)==obj
  image=bytes(u.mem_read(self.image,104));banks=struct.unpack('<2I',image[:8])
  assert banks==(bank&1,bank&1)
  for (p,n),v in zip(watched,before):assert bytes(u.mem_read(p,n))==v
  for index,p in enumerate(self.tables):
   expected=bytearray(length)
   if wide_sample and index==0:struct.pack_into('<I',expected,0,0x2000)
   assert bytes(u.mem_read(p,length))==expected
   assert bytes(u.mem_read(p-16,16))==b'\xa5'*16 and bytes(u.mem_read(p+length,16))==b'\x5a'*16
  assert bytes(u.mem_read(self.image-16,16))==b'\xa5'*16 and bytes(u.mem_read(self.image+104,16))==b'\x5a'*16
  # Reuse the prior exact builder argument observer.
  self.req=a+0x20000;self.cmd=a+0x48000;self.dmi=a+0x80000;stripe=a+0x90000
  u.mem_write(self.req+80,struct.pack('<2Q',self.cmd,self.dmi))
  u.mem_write(self.req+0xf20,struct.pack('<Q',stripe));u.mem_write(self.meta,struct.pack('<I',37))
  self.lo,self.hi=(0xb3cda0,0xb3cf70) if kind=='LSC' else (0xb404f0,0xb4070c)
  self.observed=[];self.observed_regs=[];self.invoke(self.lo,'builder')
  command=next(x for x in self.observed_regs if x[0]==(0x4358 if kind=='LSC' else 0x4958))
  assert command[1]==3 and command[2][:8]==image[:8]
  assert bytes(u.mem_read(self.image,104))==image
  return struct.pack('<2I',*banks)
def main():
 O=Path(sys.argv[1]);O.mkdir();f=Fixture();records=[];calls=0
 for placement in [0,128,512]:
  for lsc in [0,1]:
   for abf in [0,1]:
    records.append(f.vector(placement,'LSC',lsc)+f.vector(placement,'ABF',abf));calls+=4
 f.vector(0,'LSC',0,wide_sample=True);calls+=2;f.unchanged()
 headers={
 'sp11-front-table-bank.h':Q/'sp11-front-table-bank.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():(O/n).write_bytes(p.read_bytes())
 (O/'test-host.c').write_bytes((Q/'test-host.c').read_bytes());original=(Q/'sp11-front-table-bank.h').read_text()
 mutations={
 'wrong_LSC_register':original.replace('0x4358, pair, 2','0x4958, pair, 2'),
 'wrong_ABF_bank':original.replace('pair[1] = state->abf;','pair[1] = !state->abf;'),
 'early_publication':original.replace('\tif (!out || !policy || !state)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy || !state)',1),
 'accept_masked_banks':original.replace('if (state->lsc > 1 || state->abf > 1)','if (0)'),
 'bypass_domain':original.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;')}
 assert all(x!=original for x in mutations.values());runs=[]
 for cc in ['gcc','clang']:
  for label,text in [('actual',original),*mutations.items()]:
   (O/'sp11-front-table-bank.h').write_text(text);exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-fno-omit-frame-pointer','-I'+str(O),str(O/'test-host.c'),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2000:]
   p=subprocess.run([str(exe)],input=b''.join(records),capture_output=True,timeout=20)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2000:].decode()
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':json.loads(p.stdout)})
   else:assert p.returncode!=0,'unsafe compiled mutation survived '+label
 (O/'sp11-front-table-bank.h').write_text(original)
 old=R/'experiments/E004-front-ir-vd55g0/e006z-rear-clean-scalar-bank-providers/camss-e006z-clean-scalar-bank.inc'
 result={'schema':'sp11-front-table-bank-source-v1','status':'PASS_SOURCE_TABLE_BANK_FIELDS',
 'original_source_calls':calls,'comparison_records':len(records),'native_instructions':f.instructions,
 'placements':3,'complete_packers_and_builders_executed':True,
 'native_entries':{'LSC_packer':'0xb3d8a0','LSC_builder':'0xb3cda0','ABF_packer':'0xb41090','ABF_builder':'0xb404f0'},
 'original_PE_immutable':True,'SP_callee_saved_restored':True,'input_and_object_metadata_checks':True,'canaries_intact':True,
 'intercepted_helpers':['0x85ee78 register command observer/success','0x85f108 DMI argument observer/success'],
 'arithmetic_or_branch_shims':False,'constructors_or_serializer_executed':False,
 'source_bank_field_bits':1,'bank_registers':['0x4358','0x435c','0x4958','0x495c'],
 'LSC_hardware_gain_lane_bits':14,'own_LSC_prepared_policy_bits':13,
 'LSC_bit13_source_counterexample_checked':True,'existing_table_policy_or_data_changed':False,
 'ABF_descriptor_fields':{'4':0,'8':0,'16':'owned common pointer'},
 'ABF_common_bank_halfword':38,'ABF_object_table_pointer_metadata':80,
 'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),
 'header_pins':{n:sha(p) for n,p in headers.items()},
 'prior_reference_pins':{str(p.relative_to(R)):sha(p) for p in [PRE,old]},
 'bank_scheduling_reimplemented':False,'source_startup_schedule':'all families startup_phase&1',
 'source_steady_schedule':'LSC/Gamma request_id&1; ABF(request_id+1)&1',
 'full_LSC_ABF_configuration_or_geometry_qualified':False,'native_request_lifetime_integrated':False,
 'hardware_reset_or_reserved_bits_proven':False,'private_profile_read':False,'private_tuning_read':False,
 'own_optical_arrays_or_pixels_read':False,'runtime_changed':False,'installed':False,'loaded':False,'hardware':False}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','original_source_calls','comparison_records','compiler_runs','hardware']}))
if __name__=='__main__':main()
