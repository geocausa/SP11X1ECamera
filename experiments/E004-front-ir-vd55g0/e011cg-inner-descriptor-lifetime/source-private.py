#!/usr/bin/env python3
"""Original descriptor-search/inner/core binding and retired-caller lifetime, on SP11 only."""
from pathlib import Path
import importlib.util,struct,json,hashlib,collections
from unicorn import UC_HOOK_MEM_READ
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('cg_cf',ROOT/'experiments/E004-front-ir-vd55g0/e011cf-full-core-startup/source-private.py');CF=importlib.util.module_from_spec(s);s.loader.exec_module(CF)
START=0x36d03c;STOP=0x36d27c;INNER_BYTES=606264
def authority():
 facts=CF.authority();p,c=CF.p,CF.c
 # These original numeric accessors are already qualified by E011CA.
 for site in [0x3a8754,0x3af560]:CF.NUMERIC[site]=set(CF.CC.CA.NUMERIC[site])
 CF.authority()
 def ins(r):return next(c.disasm(p.get_data(r,4),r))
 for r,value in [(0x36d050,4),(0x36d05c,24)]:
  i=ins(r);assert i.mnemonic=='cmp' and i.operands[-1].imm==value
 i=ins(0x36d0f0);assert i.mnemonic=='ldr' and c.reg_name(i.operands[0].reg)=='x22' and c.reg_name(i.operands[-1].mem.base)=='x9' and i.operands[-1].mem.disp==0
 i=ins(0x36d278);assert i.mnemonic=='bl' and i.operands[0].imm==0x3a8be0
 return {'original_DLL_sha256':facts['original_DLL_sha256'],'caller_slice_start_RVA':hex(START),'caller_stop_before_RVA':hex(STOP),'caller_slice_bytes':STOP-START,
 'source_parameter_record_stride_bytes':16,'selected_descriptor_bytes':24,'selected_descriptor_kind':4,'selects_first_matching_kind_then_requires_24_bytes':True,
 'actual_inner_allocation_bytes':INNER_BYTES,'actual_inner_vtable_RVA':'0x1337fd8','interface_pointer_inner_offset':8,'core_creator_argument1_inner_offset':93032,
 'caller_parameter_list_and_outer_prior_state_remain_owned':True,'source_ranges_sha256':{hex(r):hashlib.sha256(p.get_data(r,z)).hexdigest() for r,z in [(START,STOP-START),(0x3a9f60,112),(0x3a8be0,4980),(0x3ca4a0,1776),(0x3a8730,56)]}}
class Binding(CF.Observer):
 def hook(self,u,pc,size,user):
  if self.active:
   r=pc-self.n.base
   if r==0x36d0e8:
    assert u.reg_read(UC_ARM64_REG_X9)==self.entry;self.events['exact_selected_parameter_entry']+=1
   if r==0x3a8be0:
    inner=u.reg_read(UC_ARM64_REG_X20)
    assert (inner,INNER_BYTES) in self.f.allocs and self.f.readq(inner)==self.n.base+0x1337fd8
    assert [u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(4)]==[self.descriptor,inner+93032,self.inputs,inner+8]
    self.inner=inner;self.events['exact_original_inner_creator_arguments']+=1
   if r==STOP:
    assert u.reg_read(UC_ARM64_REG_X0)==0 and self.vector is None and self.pending is None and not self.setup_active
    self.done=True;u.emu_stop();return
  return super().hook(u,pc,size,user)
 def caller(self):
  self.events=collections.Counter();self.numeric=collections.Counter();self.requested=collections.Counter();self.vector=None;self.cache_active=False;self.setup_active=False;self.setup_gettags=[];self.pending=None;self.done=False
  for k in range(29):self.u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0)
  sp=self.n.stack+0xf000;self.u.mem_write(self.n.stack,bytes(0x10000));self.u.mem_write(sp+32,struct.pack('<Q',self.inputs))
  self.u.reg_write(UC_ARM64_REG_SP,sp);self.u.reg_write(UC_ARM64_REG_X18,self.tls);self.u.reg_write(UC_ARM64_REG_X27,9);self.u.reg_write(UC_ARM64_REG_LR,self.n.end);self.active=True
  try:self.u.emu_start(self.n.base+START,self.n.end,count=1000000)
  except Exception:
   print(json.dumps({'excluded_fixture_failure_RVA':hex(self.u.reg_read(UC_ARM64_REG_PC)-self.n.base),'placement_bias':self.bias}),flush=True);raise
  self.active=False;assert self.done
  return dict(self.events)
def load_source(blob):
 f=CF.Production(blob);needed=((len(f.sy)*320+len(f.records)*224+2*len(blob)+0x1000000+4095)//4096)*4096;assert needed<0x8000000
 if needed>f.arena_size:
  extra=needed-f.arena_size;f.n.u.mem_map(f.arena+f.arena_size,extra);f.n.u.mem_write(f.arena+f.arena_size,b'\xa5'*extra);f.arena_size=needed
 f.run_full();f.bootstrap=True;f.phase='bootstrap';return f
def exact_new_payloads(f,before,count):
 u=f.n.u;after=bytes(u.mem_read(f.arena,f.arena_size));expected=bytearray(before);new=f.allocs[count:]
 for at,z in new:off=at-f.arena;expected[off:off+z]=after[off:off+z]
 assert after==expected,'preexisting arena or allocation gaps changed'
 f.bounds();return new
def source(blob,pin):
 f=load_source(blob);u=f.n.u;n=f.n;o=Binding(f);own=0x90000000;u.mem_map(own,0x80000);u.mem_write(own,b'\xa5'*0x80000)
 retired=[];protect=False
 def no_retired_read(u,access,address,z,value,user):
  if protect:assert all(address>=at+size or address+z<=at for at,size in retired),'read of retired caller input'
 type(u).hook_add(u,UC_HOOK_MEM_READ,no_retired_read,begin=own,end=own+0x7ffff)
 native=bytes(u.mem_read(n.heap,0x30000));serialized=bytes(u.mem_read(f.map,f.map_size));cases=[]
 for idx,(bias,index) in enumerate(zip([0,1,40,1230],[1,2,5,8])):
  o.bias=bias;base=own+idx*0x10000+bias;o.descriptor=base+0x1000;o.inputs=base+0x2000;entries=base+0x3000;context=base+0x4000;o.tls=base+0x5000;o.mode=base+0xa000;o.entry=entries+16*index
  u.mem_write(o.descriptor,struct.pack('<QQII',f.manager,o.mode,0,0));u.mem_write(o.mode,bytes(320));u.mem_write(o.inputs,struct.pack('<QI',entries,9)+bytes(4));u.mem_write(entries,bytes(144))
  # The first record suppresses logger registration. Record3 supplies the original core context.
  u.mem_write(entries,struct.pack('<QII',0,24,3));u.mem_write(entries+48,struct.pack('<QII',context,8,1));u.mem_write(context,bytes(8))
  u.mem_write(entries+64,struct.pack('<QII',0,24,3));u.mem_write(o.entry,struct.pack('<QII',o.descriptor,24,4))
  u.mem_write(o.tls,bytes(0x4000));u.mem_write(o.tls+88,struct.pack('<Q',o.tls+0x1000));u.mem_write(o.tls+0x1000,struct.pack('<64Q',*([o.tls+0x2000]*64)));u.mem_write(o.tls+0x2000+20,struct.pack('<I',1))
  own_before=bytes(u.mem_read(own,0x80000));before=bytes(u.mem_read(f.arena,f.arena_size));old_count=len(f.allocs);f.next=((f.next+4095)&~4095)+bias
  events=o.caller();core=o.core;inner=o.inner;interface=f.readq(inner+8)
  assert (interface,320) in f.allocs and (core,5152) in f.allocs and inner%32==bias%32
  assert f.readq(interface)==core and f.readq(interface+312)==n.base+0x3a8730 and f.readq(core)==n.base+0x1338428 and f.readq(core+8)==n.base+0x13383b8
  assert bytes(u.mem_read(own,0x80000))==own_before
  assert all(events[k]==1 for k in ['exact_selected_parameter_entry','exact_original_inner_creator_arguments','setup_entry','independent_complete_setup_delta','full_cache_entry','full_cache_return','full_bank_update_entry','full_bank_update_return'])
  expected=dict(o.requested);expected.update({(0x3c8534,0x3aebb0):1,(0x3c8564,0x3ae980):1,(0x3cb160,0x3aebb0):1});assert dict(o.numeric)==expected and events['source_vector_array_returns']==3
  numeric_count=events['source_vector_element_returns'];exact_new_payloads(f,before,old_count)
  original_descriptor=bytes(u.mem_read(o.descriptor,24));assert bytes(u.mem_read(core+168,24))==original_descriptor
  current_retired=[(o.descriptor,24),(o.inputs,16),(entries,144),(context,8)];retired.extend(current_retired)
  for at,z in current_retired:u.mem_write(at,b'\xd3'*z)
  u.mem_write(n.stack,b'\xd5'*0x10000);protect=True;o.descriptor=core+168
  before=bytes(u.mem_read(f.arena,f.arena_size));old_count=len(f.allocs)
  warm=o.invoke(0x3c8380,[core+8,core+168]);assert warm['independent_complete_setup_delta']==1 and warm.get('full_cache_entry',0)==0 and len(f.allocs)==old_count and bytes(u.mem_read(f.arena,f.arena_size))==before
  cache=o.invoke(0x3ca4a0,[core+8,core+168]);assert cache['full_cache_entry']==1 and len(o.setup_gettags)==43
  assert bytes(u.mem_read(core+168,24))==original_descriptor
  temporary=exact_new_payloads(f,before,old_count);assert len(temporary)==27 and all(z==32 and at in f.released for at,z in temporary)
  getter_before=bytes(u.mem_read(f.arena,f.arena_size));getter_allocs=len(f.allocs)
  o.invoke(0x3a8730,[interface]);assert u.reg_read(UC_ARM64_REG_X0)==core+0xf00
  assert bytes(u.mem_read(f.arena,f.arena_size))==getter_before and len(f.allocs)==getter_allocs
  assert all(bytes(u.mem_read(at,z))==b'\xd3'*z for at,z in retired)
  assert bytes(u.mem_read(n.heap,0x30000))==native and bytes(u.mem_read(f.map,f.map_size))==serialized
  print(json.dumps({'completed_binding_bias':bias,'source_sha256':pin}),flush=True)
  f.bounds();cases.append({'placement_bias':bias,'selected_parameter_index':index,'original_inner_core_bindings':1,'full_core_setup_returns':2,'exact_cache_lookups':86,'original_numeric_initializers':numeric_count,'retired_caller_input_regions':4,'postretirement_unchanged_setup_returns':1,'postretirement_full_cache_returns':1,'postretirement_original_interface_accessor_returns':1,'postretirement_no_old_caller_reads':True,'caller_inputs_and_preexisting_arena_immutable':True,'whole_arena_guards_pass':True})
 return {'source_sha256':pin,'cases':cases}
def main():
 facts=authority();rows=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin;rows.append(source(blob,pin));print(json.dumps({'source_sha256':pin,'original_inner_core_bindings':4,'retired_caller_lifetime_cases':4}),flush=True)
 cases=[v for r in rows for v in r['cases']];assert len(cases)==12 and sum(v['original_numeric_initializers'] for v in cases)==292
 result={'status':'PASS_BOUNDED_ORIGINAL_INNER_BINDING_AND_RETIRED_CALLER_LIFETIME','authority':facts,'sources':rows,'original_inner_core_bindings':12,'postretirement_no_old_caller_read_cases':12,'retired_input_regions':48,'exact_cache_lookups':1032,'original_numeric_initializers':292,'numeric_callbacks_unmodified':True,'whole_outer_constructor_qualified':False,'actual_live_Default_descriptor_qualified':False,'actual_inner_full_statistics_setup_qualified':False,'opened_filename_lifetime_or_destruction_reuse_qualified':False,'all_optional_inner_bank_fields_semantically_qualified':False,'runtime_or_image_test':False}
 (OUT/'BINDING-SAFE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','original_inner_core_bindings','postretirement_no_old_caller_read_cases','original_numeric_initializers']}),flush=True)
if __name__=='__main__':main()
