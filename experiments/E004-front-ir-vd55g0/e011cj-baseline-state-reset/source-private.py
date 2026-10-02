#!/usr/bin/env python3
"""Guarded original post-attachment baseline reset; derived scalar facts only."""
from pathlib import Path
import importlib.util,struct,json,hashlib,collections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
OUT=Path(__file__).resolve().parent
CI_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ci-outer-return-publication/source-private.py'
assert hashlib.sha256(CI_PATH.read_bytes()).hexdigest()=='39334a11dead19f682bad29185aae4c32303328d278f81b8c9312d2edd7ac776'
spec=importlib.util.spec_from_file_location('cj_ci',CI_PATH);CI=importlib.util.module_from_spec(spec);spec.loader.exec_module(CI)
CF=CI.CF;CG=CI.CG;ATTACH=0x36d63c;STOP=0x36d784;POISON=False
# Independent field schema. Float values are represented by their scalar IEEE bits.
CLEARS={0x36d650:(90712,352),0x36d668:(91064,352),0x36d6bc:(4088,1608)}
WRITES={
 0x36d674:[(90368,4,0xbf800000),(90372,4,0xbf800000)],
 0x36d67c:[(90360,8,0)],0x36d680:[(90376,4,0x3f800000)],
 0x36d684:[(90380,8,0)],0x36d68c:[(90388,4,0)],
 0x36d69c:[(k,8,0) for k in range(3928,4056,8)],
 0x36d6a8:[(4056,8,0),(4064,8,0)],0x36d6cc:[(4072,8,0),(4080,8,0)],
 0x36d6d8:[(91944,4,0)],0x36d6e0:[(91748,4,0x3f800000)],
 0x36d6e8:[(91808,4,0)],0x36d6f0:[(91752,4,0x3f800000)],
 0x36d6f8:[(91756,4,0x3f800000)],0x36d700:[(91784,4,0)],
 0x36d708:[(91760,4,0x3f800000)],0x36d710:[(91764,4,1149239296)],
 0x36d718:[(91768,8,1)],0x36d728:[(91776,8,1000000000)],
 0x36d734:[(91888,8,4294967296)],0x36d740:[(91832,4,1)],
 0x36d750:[(91816,8,'inner_buffer92976')],0x36d758:[(92968,4,0)],
 0x36d760:[(557760,8,0)],0x36d774:[(k,8,0) for k in range(557768,557800,8)],
 0x36d778:[(k,8,0) for k in range(557800,557832,8)],
 0x36d77c:[(557832,8,0),(557840,8,0)]}
def schema(inner):
 return {(r,off,z):inner+92976 if isinstance(value,str) else value for r,rows in WRITES.items() for off,z,value in rows}
def authority():
 facts,imports=CI.authority();p,c=CF.p,CF.c
 for r in CLEARS:
  i=next(c.disasm(p.get_data(r,4),r));assert i.mnemonic=='bl' and i.operands[0].imm==0xf5e600
 for r in WRITES:
  i=next(c.disasm(p.get_data(r,4),r));assert i.mnemonic.startswith(('str','stp','st1','st4'))
 # The stopping instruction is the next allocator call; it must not execute.
 i=next(c.disasm(p.get_data(STOP,4),STOP));assert i.mnemonic=='bl' and i.operands[0].imm==0xcae740
 facts.update({'stop_before_RVA':hex(STOP),'attachment_prefix_RVA':hex(ATTACH),'baseline_reset_bytes':STOP-ATTACH,'independent_clear_regions':list(CLEARS.values()),'explicit_store_chunks':sum(map(len,WRITES.values())),'internal_buffer_link_inner_offset':91816,'internal_buffer_target_inner_offset':92976,'poison_fixture_has_no_live_Default_claim':True,'baseline_range_sha256':hashlib.sha256(p.get_data(ATTACH,STOP-ATTACH)).hexdigest(),'inherited_verifier_sha256':hashlib.sha256(CI_PATH.read_bytes()).hexdigest()})
 return facts,imports
class Startup(CI.Startup):
 def __init__(self,f):
  super().__init__(f);self.tail_active=False
  type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.write_hook)
 def write_hook(self,u,access,at,z,value,user):
  if not self.active or not self.tail_active:return
  r=u.reg_read(UC_ARM64_REG_PC)-self.n.base
  # No other object or stack is written in this straight-line original prefix.
  assert self.inner<=at and at+z<=self.inner+606264,('unowned reset write',hex(r))
  key=(r,at-self.inner,z);assert key in self.expected_writes,('unmodelled reset write',hex(r),at-self.inner,z)
  assert value==self.expected_writes[key],('reset scalar mismatch',hex(r),at-self.inner)
  self.seen_writes[key]+=1
 def hook(self,u,pc,z,user):
  r=pc-self.n.base
  if self.active and self.tail_active:
   if r in CLEARS:
    off,size=CLEARS[r]
    assert [u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2)]==[self.inner+off,0,size]
    self.clear_calls[r]+=1
   if r==STOP:
    assert bytes(u.mem_read(self.inner,606264))==self.expected_inner,'independent entire baseline reset model'
    assert self.seen_writes==collections.Counter({k:1 for k in self.expected_writes}),dict(self.seen_writes)
    assert self.clear_calls==collections.Counter({k:1 for k in CLEARS})
    assert len(self.f.allocs)==self.boundary_alloc_count
    expected_arena=bytearray(self.boundary_arena)
    off=self.inner-self.f.arena;expected_arena[off:off+606264]=self.expected_inner
    assert bytes(u.mem_read(self.f.arena,self.f.arena_size))==expected_arena,'unexpected entire post-attachment arena delta'
    assert bytes(u.mem_read(self.outer,72))==self.prefix_outer
    assert self.f.readq(self.inner+40)==self.manager and self.f.readq(self.inner+91952)==self.mode_configuration
    self.events['independent_entire_baseline_reset']+=1;self.done=True;u.emu_stop();return
   if r==ATTACH:return CF.Observer.hook(self,u,pc,z,user)
  return super().hook(u,pc,z,user)
 def invoke_entry(self):
  self.tail_active=False;super().invoke_entry()
  assert self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+ATTACH
  before=bytes(self.u.mem_read(self.inner,606264));expected=bytearray(before)
  self.expected_writes=schema(self.inner);self.seen_writes=collections.Counter();self.clear_calls=collections.Counter()
  regions=list(CLEARS.values())+[(off,z) for r,off,z in self.expected_writes]
  if POISON:
   poisoned=bytearray(before)
   for off,z in regions:poisoned[off:off+z]=b'\xa5'*z
   self.u.mem_write(self.inner,bytes(poisoned))
  for off,z in CLEARS.values():expected[off:off+z]=bytes(z)
  for (r,off,z),value in self.expected_writes.items():expected[off:off+z]=value.to_bytes(z,'little')
  self.expected_inner=bytes(expected);self.boundary_arena=bytes(self.u.mem_read(self.f.arena,self.f.arena_size));self.boundary_alloc_count=len(self.f.allocs)
  self.done=False;self.tail_active=True;self.active=True
  try:self.u.emu_start(self.n.base+ATTACH,self.n.end,count=10000)
  finally:self.active=False;self.tail_active=False
  assert self.done and self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+STOP
  self.boundary_arena=None
CI.Startup=Startup
def main():
 global POISON
 facts,imports=authority();rows=[]
 for poison in [False,True]:
  POISON=poison
  for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
   blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
   row=CI.source(blob,pin,imports);row['reset_field_poison_fixture']=poison
   for case in row['cases']:case.update({'whole_baseline_reset_model':True,'reset_field_poison_fixture':poison,'original_clear_calls':3,'exact_scalar_store_chunks':len(schema(0)),'internal_buffer_link_qualified':True,'post_attachment_other_arena_bytes_immutable':True,'no_post_attachment_allocation':True})
   rows.append(row)
 cases=[case for row in rows for case in row['cases']]
 result={'status':'PASS_BOUNDED_ORIGINAL_BASELINE_STATE_RESET','experiment':'E011CJ','base_commit':'64bf7bd01c70b2219189fece5648efc7db096cf9','authority':facts,'sources':rows,'cases':len(cases),'unmodified_original_cases':sum(not v['reset_field_poison_fixture'] for v in cases),'owned_poison_reset_cases':sum(v['reset_field_poison_fixture'] for v in cases),'independent_whole606264byte_baseline_models':len(cases),'exact_original_clear_calls':3*len(cases),'exact_original_scalar_store_chunks':len(schema(0))*len(cases),'independent_152byte_records':sum(v['independent_152byte_records'] for v in cases),'statistics_record_initializers':sum(v['original_48byte_stride_array_initializers'] for v in cases),'core_vector_initializers':sum(v['original_core_vector_initializers'] for v in cases),'cache_lookups':sum(v['source_cache_lookups'] for v in cases),'statistics_and_mode_links_retained_to_stop':True,'whole_outer_return_qualified':False,'final_output_publication_qualified':False,'CRT_locale_environment_qualified':False,'actual_live_Default_producers_qualified':False,'new_numeric_or_TLS_success_stub':False,'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,'runtime_or_image_test':False,'next_experiment':'E011CK'}
 assert result['cases']==24 and result['owned_poison_reset_cases']==result['unmodified_original_cases']==12
 assert result['independent_152byte_records']==360 and result['statistics_record_initializers']==2880 and result['core_vector_initializers']==584 and result['cache_lookups']==1032
 (OUT/'BASELINE-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
