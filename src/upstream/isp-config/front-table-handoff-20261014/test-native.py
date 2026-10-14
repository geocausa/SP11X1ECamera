#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Reuse original source builders and actual existing own measured tables."""
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
  if address in [self.base+0x85ee78,self.base+0x85f108]:
   v=[u.reg_read(getattr(retained,'UC_ARM64_REG_X'+str(i))) for i in range(6)]
   assert v[0]==self.cmd
   if address==self.base+0x85ee78:
    regs=[(0x4358,3,0),(0x4368,13,12)] if self.kind=='LSC' else [
     (0x4968,2,12),(0x4980,4,20),(0x49a0,8,36),(0x49c8,9,68),(0x4958,3,0)]
    index=len(self.observed_regs);reg,count,off=regs[index]
    assert v[1:4]==[reg,count,self.image+off]
    self.observed_regs.append((reg,count,bytes(u.mem_read(v[3],count*4))))
   else:
    reg=0x4308 if self.kind=='LSC' else 0x4908
    count=len(self.observed);length=884 if self.kind=='LSC' else 256
    assert v[1:6]==[reg,count+1,self.dmi,self.offset*4+count*length,length]
    self.observed.append(tuple([v[1],v[2],v[4],v[5]]))
   u.reg_write(retained.UC_ARM64_REG_X0,0);u.reg_write(retained.UC_ARM64_REG_PC,u.reg_read(retained.UC_ARM64_REG_LR));return
  assert self.base+self.lo<=address<self.base+self.hi,'unmodeled source instruction'
 def write(self,u,access,address,size,value,_):
  if self.phase=='idle' or self.n.stack<=address<address+size<=self.n.stack+0x10000:return
  raise AssertionError('builder wrote outside stack')
 def vector(self,placement,kind,offset,seed):
  self.kind=kind;self.offset=offset
  u=self.u;a=self.arena+placement;u.mem_write(self.arena,bytes(0xa0000))
  self.obj=a+0x1000;self.image=a+0x3000;self.req=a+0x10000
  self.meta=a+0x40000;self.cmd=a+0x48000;self.dmi=a+0x50000;stripe=a+0x60000
  # Owned image and ordinary stripe/request contexts; no source constructor.
  u.mem_write(self.obj,struct.pack('<Q',self.image));u.mem_write(self.obj+32,struct.pack('<Q',self.image))
  u.mem_write(self.image,struct.pack('<26I',*([seed]*26)))
  u.mem_write(self.image-16,b'\xa5'*16);u.mem_write(self.image+104,b'\x5a'*16)
  u.mem_write(self.req+80,struct.pack('<2Q',self.cmd,self.dmi))
  u.mem_write(self.req+0xf20,struct.pack('<Q',stripe))
  u.mem_write(self.meta,struct.pack('<I',offset))
  watched=[(self.obj,128),(self.image,104),(self.req,0x20000),(self.meta,16),(stripe,0x10000)]
  before=[bytes(u.mem_read(p,n)) for p,n in watched]
  self.lo,self.hi=(0xb3cda0,0xb3cf70) if kind=='LSC' else (0xb404f0,0xb4070c)
  self.observed=[];self.observed_regs=[];self.invoke(self.lo,'builder')
  assert len(self.observed)==(3 if kind=='LSC' else 1)
  assert len(self.observed_regs)==(2 if kind=='LSC' else 5)
  for (p,n),v in zip(watched,before):assert bytes(u.mem_read(p,n))==v
  assert bytes(u.mem_read(self.image-16,16))==b'\xa5'*16 and bytes(u.mem_read(self.image+104,16))==b'\x5a'*16
  return self.observed
def main():
 O=Path(sys.argv[1]);O.mkdir();f=Fixture();cases=0
 for placement in [0,128,512]:
  for offset in [0,37,128]:
   for kind in ['LSC','ABF']:
    for seed in [0,0xffffffff]:f.vector(placement,kind,offset,seed);cases+=1
 records=f.vector(0,'LSC',37,0)+f.vector(0,'ABF',37,0);cases+=2;f.unchanged()
 headers={
 'sp11-front-table-handoff.h':Q/'sp11-front-table-handoff.h',
 'native-front-gamma.h':R/'src/native-rgb/native-front-gamma.h',
 'sp11-front-cold-fields.h':R/'src/upstream/isp-config/cold-front-fields-20261014/sp11-front-cold-fields.h',
 'sp11-front-measured-config.h':R/'src/upstream/isp-config/measured-front-reuse-20261014/sp11-front-measured-config.h',
 'sp11-cdm.h':R/'src/upstream/isp-config/sp11-cdm.h'}
 for n,p in headers.items():(O/n).write_bytes(p.read_bytes())
 (O/'test-host.c').write_bytes((Q/'test-host.c').read_bytes())
 K=R.parents[1]/'02-kernel'
 lsc=K/'front-lsc-v1/imx681-front-lsc-v1.bin';abf=K/'front-open-01/imx681-front-abf-v1.bin'
 # Own prepared data is used locally only, not written to reports or exported.
 data=b''.join(struct.pack('<4I',*x) for x in records)+lsc.read_bytes()+abf.read_bytes()
 assert len(data)==64+2652+256
 original=(Q/'sp11-front-table-handoff.h').read_text()
 mutations={
 'wrong_LSC_selector':original.replace('0x4308, i + 1','0x4308, 3 - i'),
 'wrong_ABF_register':original.replace('36, 0x4908, 1','36, 0x4308, 1'),
 'early_publication':original.replace('\tif (!out || !policy || !mapping || !lsc || !abf ||','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !policy || !mapping || !lsc || !abf ||',1),
 'skip_prepared_validation':original.replace('ret = sp11_front_tables_validate(lsc, lsc_bytes, abf, abf_bytes);','ret = 0;'),
 'accept_stale_request':original.replace('if (mapping->request_id != expected_request_id)','if (0)'),
 'bypass_domain':original.replace('ret = sp11_front_cold_fields(checked, sizeof(checked), policy);','ret = 0;\n\t(void)checked;')}
 assert all(x!=original for x in mutations.values());runs=[]
 for cc in ['gcc','clang']:
  for label,source in [('actual',original),*mutations.items()]:
   (O/'sp11-front-table-handoff.h').write_text(source);exe=O/(cc+'-'+label)
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined',
    '-fno-omit-frame-pointer','-I'+str(O),str(O/'test-host.c'),'-o',str(exe)],capture_output=True,text=True)
   assert p.returncode==0,p.stderr[-2500:]
   p=subprocess.run([str(exe)],input=data,capture_output=True,timeout=20)
   (O/(cc+'-'+label+'.log')).write_bytes(p.stdout+p.stderr)
   if label=='actual':
    assert p.returncode==0,p.stderr[-2500:].decode()
    runs.append({'compiler':cc,'ASan_UBSan':True,'result':json.loads(p.stdout)})
   else:assert p.returncode!=0,'unsafe compiled mutation survived '+label
 (O/'sp11-front-table-handoff.h').write_text(original)
 prior=[PRE,R/'src/native-rgb/open-profile/fit-lsc.py',R/'src/native-rgb/open-profile/gen-abf-lut.py',
 R/'experiments/E004-front-ir-vd55g0/e007i-rear-lsc-dmi-handoff/camss-e007i-rear-lsc-handoff.inc']
 result={'schema':'sp11-front-table-handoff-source-v1','status':'PASS_REUSED_FRONT_MEASURED_TABLE_HANDOFF',
 'source_cases':cases,'native_instructions':f.instructions,'placements':3,
 'original_PE_sha256':retained.retained.old.DLL_SHA,'original_PE_immutable':True,
 'SP_callee_saved_restored':True,'canaries_intact':True,'inputs_immutable':True,
 'native_entries':{'LSC_builder':'0xb3cda0','ABF_builder':'0xb404f0'},
 'intercepted_helpers':['0x85ee78 register command observer/success','0x85f108 DMI argument observer/success'],
 'arithmetic_or_branch_shims':False,'serializer_executed':False,'constructor_executed':False,
 'arithmetic_packers_executed':False,'source_fixed_DMI_addresses_observed':True,'addresses_substituted':False,
 'source_word_to_byte_offsets_observed':True,'ordinary_stripe_context':True,'ABF_request_flag_17130':0,
 'optional_ABF_flag1_context_qualified':False,'command_bytes':48,
 'source_DMI_arguments':[{'register':hex(x[0]),'selector':x[1],'offset':x[2],'bytes':x[3]} for x in records],
 'existing_own_measured_table_pairs_validated_each_compiler':1,'own_data_values_or_hashes_exported':False,
 'new_calibration':False,'module_or_bank_commands_emitted':0,
 'compiler_runs':runs,'compiled_mutations_rejected_each':list(mutations),
 'header_pins':{n:sha(p) for n,p in headers.items()},
 'prior_reference_pins':{str(p.relative_to(R)):sha(p) for p in prior},
 'CPU_DMA_correspondence_proven':False,'bank_config_integrated':False,'completion_lifetime_integrated':False,
 'physical_channel_or_mesh_binding_proven':False,'private_profile_read':False,'private_tuning_read':False,
 'pixels_read':False,'runtime_changed':False,'installed':False,'loaded':False,'hardware':False}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:result[k] for k in ['status','source_cases','native_instructions','compiler_runs','hardware']}))
if __name__=='__main__':main()
