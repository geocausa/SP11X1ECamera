#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reuse complete own measured words; original builder/activation field proof."""
from pathlib import Path
import importlib.util,json,re,struct,subprocess,sys
Q=Path(__file__).resolve().parent;R=Q.parents[3]
PRE=R/'src/upstream/isp-config/front-table-handoff-20261014/test-native.py'
s=importlib.util.spec_from_file_location('retained_table_fixture',PRE)
retained=importlib.util.module_from_spec(s);s.loader.exec_module(retained)
sha=retained.sha
groups=[(0x4968,2,12),(0x4980,4,20),(0x49a0,8,36),(0x49c8,9,68)]
class Fixture(retained.Fixture):
 def code(self,u,address,size,_):
  if self.phase!='packer':return super().code(u,address,size,_)
  self.instructions+=1
  assert self.base+0xb41090<=address<self.base+0xb41af8,'unmodeled source instruction'
 def write(self,u,access,address,size,value,_):
  if self.phase=='idle' or self.n.stack<=address<address+size<=self.n.stack+0x10000:return
  assert self.phase=='packer'
  assert (address-self.obj,size)==(80,8) or self.image<=address<address+size<=self.image+104 or (
   self.table<=address<address+size<=self.table+256),'unowned source write'
 def vector(self,placement,bank,words=None):
  u=self.u;a=self.arena+placement;u.mem_write(self.arena,bytes(0xa0000))
  self.kind='ABF';self.offset=37;self.obj=a+0x1000;self.image=a+0x3000
  self.req=a+0x10000;self.meta=a+0x40000;block=a+0x50000;self.table=a+0x60000
  u.mem_write(self.obj,struct.pack('<Q',self.image));u.mem_write(self.obj+32,struct.pack('<Q',self.image))
  u.mem_write(self.image-16,b'\xa5'*16);u.mem_write(self.image+104,b'\x5a'*16)
  if words is None:
   # Explicit own selected descriptor0/0; source-packer flag fields produce101.
   u.mem_write(self.req+16,struct.pack('<Q',block))
   u.mem_write(block,struct.pack('<4H',1,1,0,0));u.mem_write(block+0x26,struct.pack('<H',bank))
   u.mem_write(self.meta+8,struct.pack('<Q',self.table))
   u.mem_write(self.table-16,b'\xa5'*16);u.mem_write(self.table,b'\xa5'*256);u.mem_write(self.table+256,b'\x5a'*16)
   watched=[(self.req,32),(block,1024),(self.meta,32)]
   before=[bytes(u.mem_read(p,n)) for p,n in watched];obj=bytes(u.mem_read(self.obj,128))
   self.invoke(0xb41090,'packer')
   for (p,n),v in zip(watched,before):assert bytes(u.mem_read(p,n))==v
   after=bytearray(u.mem_read(self.obj,128));assert struct.unpack_from('<Q',after,80)[0]==self.table
   after[80:88]=obj[80:88];assert bytes(after)==obj
   assert bytes(u.mem_read(self.table,256))==bytes(256)
   assert bytes(u.mem_read(self.table-16,16))==b'\xa5'*16 and bytes(u.mem_read(self.table+256,16))==b'\x5a'*16
   assert struct.unpack('<3I',u.mem_read(self.image,12))==(bank,bank,0x101)
  else:
   # Owned producer image from existing own full-word replacements, not a
   # modified original packer output or a private profile/tuning sample.
   u.mem_write(self.image,struct.pack('<3I',bank,bank,0))
   for reg,count,off in groups:
    u.mem_write(self.image+off,struct.pack('<'+'I'*count,*[words[reg+i*4] for i in range(count)]))
  image=bytes(u.mem_read(self.image,104));obj=bytes(u.mem_read(self.obj,128))
  self.req=a+0x20000;self.cmd=a+0x48000;self.dmi=a+0x70000;stripe=a+0x90000
  u.mem_write(self.req+80,struct.pack('<2Q',self.cmd,self.dmi))
  u.mem_write(self.req+0xf20,struct.pack('<Q',stripe));u.mem_write(self.meta,struct.pack('<I',37))
  self.lo,self.hi=0xb404f0,0xb4070c;self.observed=[];self.observed_regs=[]
  self.invoke(self.lo,'builder')
  assert len(self.observed_regs)==5 and len(self.observed)==1
  assert bytes(u.mem_read(self.image,104))==image and bytes(u.mem_read(self.obj,128))==obj
  assert bytes(u.mem_read(self.image-16,16))==b'\xa5'*16 and bytes(u.mem_read(self.image+104,16))==b'\x5a'*16
  if words is None:
   reg,count,data=self.observed_regs[4];assert (reg,count)==(0x4958,3)
   return struct.pack('<2I',0x03000001,reg+8)+data[8:12]
  return b''.join(struct.pack('<2I',0x03000000+count,reg)+data for reg,count,data in self.observed_regs[:4])
def main():
 O=Path(sys.argv[1]);O.mkdir();f=Fixture()
 measured=R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h'
 rows=re.findall(r'\{ (0x[0-9a-f]+)U, (0x[0-9a-f]+)U \}',measured.read_text())
 words={int(r,16):int(v,16) for r,v in rows};assert len(rows)==len(words)==24
 needed={reg+i*4 for reg,count,_ in groups for i in range(count)}
 assert len(needed)==23 and needed==set(words)-{0x4b6c}
 records=[];source_calls=0
 for placement in [0,128,512]:
  for bank in [0,1]:
   config=f.vector(placement,bank,words);source_calls+=1
   activation=f.vector(placement,bank);source_calls+=2
   assert len(config)==124 and len(activation)==12
   records.append(config+activation)
 f.unchanged()
 headers={
 'sp11-front-abf-config.h':Q/'sp11-front-abf-config.h',
 'sp11-front-abf-measured.h':Q/'sp11-front-abf-measured.h',
 'native-front-gamma.h':R/'src/native-rgb/native-front-gamma.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':measured,'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():(O/n).write_bytes(p.read_bytes())
 (O/'test-host.c').write_bytes((Q/'test-host.c').read_bytes())
 original=(Q/'sp11-front-abf-config.h').read_text()
 mutations={
 'wrong_block':original.replace('{ 0x4968, 0x4980','{ 0x4980, 0x4980'),
 'alter_calibration':original.replace('values[j] = nf_gamma_get32(word + 8);','values[j] = nf_gamma_get32(word + 8) ^ 1U;'),
 'activation_loses_ABF_bit':original.replace('const u32 module = SP11_FRONT_ABF_MEASURED_MODULE;','const u32 module = SP11_FRONT_ABF_MEASURED_MODULE & ~0x100U;'),
 'early_publication':original.replace('\tif (!out || !policy)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy)'),
 'bypass_domain':original.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;')}
 # measured_config independently retains domain admission in config; activation
 # catches bypass mutation as well, so no standalone synthetic domain oracle.
 assert all(x!=original for x in mutations.values());runs=[]
 for cc in ['gcc','clang']:
  for label,text in [('actual',original),*mutations.items()]:
   (O/'sp11-front-abf-config.h').write_text(text);exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-fno-omit-frame-pointer','-I'+str(O),str(O/'test-host.c'),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2000:]
   p=subprocess.run([str(exe)],input=b''.join(records),capture_output=True,timeout=20)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2000:].decode()
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':json.loads(p.stdout)})
   else:assert p.returncode!=0,'unsafe compiled mutation survived '+label
 (O/'sp11-front-abf-config.h').write_text(original)
 result={'schema':'sp11-front-abf-complete-source-v1','status':'PASS_REUSED_COMPLETE_OWN_ABF_CONFIGURATION',
 'original_source_calls':source_calls,'comparison_records':len(records),'native_instructions':f.instructions,'placements':3,
 'source_entries':{'builder':'0xb404f0','activation_field_packer':'0xb41090'},
 'source_configuration_input':'Owned existing23 measured full-word values, builder only; no source arithmetic equivalence claimed',
 'source_activation_input':'Owned common halfwords0=1,2=1,4=0,6=0; descriptor4/8=0/0, pointer16, bank halfword38',
 'fixed_source_registers_observed':True,'addresses_substituted':False,'original_PE_immutable':True,
 'SP_callee_saved_restored':True,'inputs_and_object_metadata_checked':True,'canaries_intact':True,
 'intercepted_helpers':['0x85ee78 register observer/success','0x85f108 DMI argument observer/success'],
 'arithmetic_or_branch_shims':False,'constructors_or_serializer_executed':False,
 'configuration_arithmetic_packer_executed':False,'activation_field_packer_executed':True,
 'own_complete_configuration_words':23,'configuration_bytes':124,'separate_activation_bytes':12,
 'own_module_word':257,'bank_words_emitted':False,'DMI_commands_emitted':False,
 'existing_calibration_and_measured_compiler_reused_unchanged':True,
 'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),'header_pins':{n:sha(p) for n,p in headers.items()},
 'prior_reference_pins':{str(p.relative_to(R)):sha(p) for p in [PRE,measured,R/'src/native-rgb/front-ae/tuning/imx681-front-open-regs.txt']},
 'new_calibration':False,'LSC_core_configuration_complete':False,'physical_precision_or_ordering_qualified':False,
 'native_lifetime_integrated':False,'private_profile_or_tuning_read':False,'own_optical_arrays_or_pixels_read':False,
 'runtime_changed':False,'installed':False,'loaded':False,'hardware':False}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','original_source_calls','comparison_records','compiler_runs','hardware']}))
if __name__=='__main__':main()
