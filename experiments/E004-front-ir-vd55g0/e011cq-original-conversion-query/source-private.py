#!/usr/bin/env python3
"""Bounded original CRT continuation; stop before the unmodeled conversion API."""
from pathlib import Path
import importlib.util,hashlib,json,struct,collections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
OUT=Path(__file__).resolve().parent
BASE='bc0cc194aa4f3b1eb7f24ef3d00079697a37ed8c'
CP_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011cp-original-file-encoding-policy/source-private.py'
CP_PIN='19a9db934607cbbf0eb73b4a85c1f42a687fc2f3ab07852df98e824f8f02ad13'
assert hashlib.sha256(CP_PATH.read_bytes()).hexdigest()==CP_PIN
s=importlib.util.spec_from_file_location('cq_cp',CP_PATH);CP=importlib.util.module_from_spec(s);s.loader.exec_module(CP)
CF=CP.CF
RANGES={0xcfd4a4:(68,'b60d018c6986a000195665554d32639ab93677924c2dfb1fbaccb6c9af3efd1e'),
 0xcb76b0:(256,'f95cd35469685df9c6b431cf5fe41ffb6ff852c638e89c489fe334d646480f34'),
 0xcb8d88:(92,'c3e685c5f481ab8a5f599ce384c05270931e15027b15cf026e17da8f5a66fef7')}
CASES=[]
def authority():
 inherited,camera=CP.authority()
 for a,(z,pin) in RANGES.items():assert hashlib.sha256(CF.p.get_data(a,z)).hexdigest()==pin
 imp=next(i for d in CF.p.DIRECTORY_ENTRY_IMPORT for i in d.imports if i.name==b'MultiByteToWideChar')
 assert imp.address-CF.p.OPTIONAL_HEADER.ImageBase==0xf7e2e8
 for site,target in [(0xcfd4e4,0xcb76b0),(0xcb7784,0xcb8d88)]:
  i=next(CF.c.disasm(CF.p.get_data(site,4),site));assert i.mnemonic=='bl' and i.operands[0].imm==target
 i=next(CF.c.disasm(CF.p.get_data(0xcb8dd4,4),0xcb8dd4))
 assert i.mnemonic=='br' and CF.c.reg_name(i.operands[0].reg)=='x8'
 # Derive/check saved-register identities and addressing, independently of write events.
 specs=[(0xcb76b4,['x19','x20'],-48,True),(0xcb76b8,['x21','x22'],16,False),
        (0xcb76bc,['x23','x24'],32,False),(0xcb76c0,['fp','lr'],-16,True)]
 for site,names,off,writeback in specs:
  i=next(CF.c.disasm(CF.p.get_data(site,4),site))
  assert i.mnemonic=='stp' and [CF.c.reg_name(o.reg) for o in i.operands[:2]]==names
  assert CF.c.reg_name(i.operands[2].mem.base)=='sp' and i.operands[2].mem.disp==off and i.writeback==writeback
 return {'inherited_CP_verifier_sha256':CP_PIN,'original_OEM_DLL_sha256':'c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35',
  'ranges':{hex(a):{'bytes':z,'sha256':pin} for a,(z,pin) in RANGES.items()},
  'converter_entry_RVA':'0xcb76b0','converter_original_call_RVA':'0xcfd4e4',
  'query_original_call_RVA':'0xcb7784','query_tail_branch_RVA':'0xcb8dd4',
  'conversion_IAT_RVA':'0xf7e2e8','stop_before_tail_branch':True},camera
class Query:
 def __init__(self,o):
  self.o=o;self.n=o.n;self.u=o.u;self.active=False;self.entry=None;self.expected={};self.writes=collections.Counter();self.instructions=collections.Counter()
  type(self.u).hook_add(self.u,UC_HOOK_CODE,self.code)
  type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.memory)
 def regs(self,ks):return [self.u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in ks]
 def code(self,u,pc,z,user):
  if not self.active:return
  a=pc-self.n.base
  assert (0xcfd4a4<=a<0xcfd4e8 or 0xcb76b0<=a<0xcb7788 or 0xcb8d88<=a<=0xcb8dd4) and a%4==0,('unqualified query continuation',hex(a))
  if a==0xcb8dd4:
   assert self.entry and self.regs(range(6))==[int(CP.CP_MODE=='OEM'),9,self.entry[0],0xffffffff,0,0]
   assert u.reg_read(UC_ARM64_REG_LR)==self.n.base+0xcb7788
   assert u.reg_read(UC_ARM64_REG_X8)==int.from_bytes(u.mem_read(self.n.base+0xf7e2e8,8),'little')
   u.emu_stop();return
  if a==0xcb76b0:
   assert self.entry is None and u.reg_read(UC_ARM64_REG_LR)==self.n.base+0xcfd4e8
   self.entry=self.regs(range(4));sp=u.reg_read(UC_ARM64_REG_SP)
   assert self.entry[3]==int(CP.CP_MODE=='OEM')
   for ptr in self.entry[:3]:assert self.n.stack<=ptr<self.n.stack+0x10000
   data=bytes(u.mem_read(self.entry[0],min(4096,self.n.stack+0x10000-self.entry[0])))
   assert 0 in data;self.input=data[:data.index(0)+1]
   assert len(self.input)>1 and self.entry[1]+8<=self.n.stack+0x10000
   assert bytes(u.mem_read(self.entry[1],8))==bytes(8)
   self.entry_sp=sp
   for site,at,ks in [(0xcb76b4,sp-48,[19,20]),(0xcb76b8,sp-32,[21,22]),(0xcb76bc,sp-16,[23,24]),(0xcb76c0,sp-64,[29,30])]:
    for j,value in enumerate(self.regs(ks)):self.expected[(site,at+8*j,8)]=value
  if a==0xcb7784:
   assert self.regs(range(6))==[int(CP.CP_MODE=='OEM'),9,self.entry[0],0xffffffff,0,0]
  self.instructions[a]+=1
 def memory(self,u,access,at,z,value,user):
  if not self.active:return
  key=(u.reg_read(UC_ARM64_REG_PC)-self.n.base,at,z)
  assert key in self.expected and value==self.expected[key],'unqualified query write'
  self.writes[key]+=1
 def negatives(self):
  counts=self.instructions.copy();writes=self.writes.copy();pc=self.u.reg_read(UC_ARM64_REG_PC)
  k=next(iter(self.expected));site,at,z=k;value=self.expected[k]
  self.active=True
  try:
   for addr,size,v in [(at+1,z,value),(at,4,value),(at,z,value^1),(self.n.heap,z,value)]:
    self.u.reg_write(UC_ARM64_REG_PC,self.n.base+site)
    try:self.memory(self.u,0,addr,size,v,None)
    except AssertionError:pass
    else:raise AssertionError('wrong query write admitted')
   for a in [0xcb7788,0xcfe600]:
    try:self.code(self.u,self.n.base+a,4,None)
    except AssertionError:pass
    else:raise AssertionError('unqualified query continuation admitted')
  finally:self.active=False;self.u.reg_write(UC_ARM64_REG_PC,pc)
  assert self.instructions==counts and self.writes==writes
  return 6
 def run(self):
  n=self.n;u=self.u;o=self.o;b=o.crt
  start=u.reg_read(UC_ARM64_REG_PC);assert start==n.base+(0xcfd4c0 if CP.CP_MODE=='ANSI' else 0xcfd4a4)
  original_sp=u.reg_read(UC_ARM64_REG_SP);assert u.mem_read(original_sp+48,1)[0]==0
  regions=[(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage),(n.heap,0x30000),(b.own,b.extent),(o.f.arena,o.f.arena_size),(o.f.map,o.f.map_size),(0x90000000,0x80000)]
  before=[bytes(u.mem_read(at,z)) for at,z in regions];stack=bytes(u.mem_read(n.stack,0x10000))
  allocations=list(o.f.allocs);depths=b.depths.copy();self.active=True
  try:u.emu_start(start,n.end,count=1000)
  finally:self.active=False
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0xcb8dd4 and u.reg_read(UC_ARM64_REG_SP)==self.entry_sp-64
  assert len(self.expected)==8 and self.writes==collections.Counter({k:1 for k in self.expected})
  expected=bytearray(stack)
  for (site,at,z),value in self.expected.items():struct.pack_into('<Q',expected,at-n.stack,value)
  assert bytes(u.mem_read(n.stack,0x10000))==expected,'independent entire stack mismatch'
  assert [bytes(u.mem_read(at,z)) for at,z in regions]==before
  assert bytes(u.mem_read(self.entry[0],len(self.input)))==self.input
  assert bytes(u.mem_read(self.entry[1],8))==bytes(8)
  assert list(o.f.allocs)==allocations and b.depths==depths
  b.policy.check_pages();assert o.f.readq(o.output)==0 and b.depths[b.new_stream+48]==1
  negative=self.negatives()
  assert bytes(u.mem_read(n.stack,0x10000))==expected and [bytes(u.mem_read(at,z)) for at,z in regions]==before
  return {'policy_fixture':CP.CP_MODE,'source_codepage_value':int(CP.CP_MODE=='OEM'),
   'source_query_flags':9,'source_query_input_count_W3':4294967295,'source_query_output_pointer':0,'source_query_output_capacity':0,
   'source_filename_stack_offset':self.entry[0]-n.stack,'source_filename_bytes_including_NUL':len(self.input),'source_filename_sha256':hashlib.sha256(self.input).hexdigest(),
   'converter_result_record_stack_offset':self.entry[1]-n.stack,'converter_context_pointer_stack_offset':self.entry[2]-n.stack,
   'source_converter_entry_SP_offset':self.entry_sp-n.stack,'converter_stack_bytes_reserved':64,
   'exact_original_saved_qword_stores':8,'original_executed_instruction_count':sum(self.instructions.values()),
   'original_executed_RVAs':[hex(a) for a in sorted(self.instructions)],'all_executed_sites_once':all(v==1 for v in self.instructions.values()),
   'independent_entire64KB_stack_model':True,'whole_other_regions_unchanged':True,'source_filename_and_result_record_unchanged':True,
   'new_camera_or_CRT_allocations':0,'lock_depths_unchanged':True,'conversion_API_executed':False,'conversion_result_supplied':False,
   'query_tail_branch_executed':False,'source_caller_byte_SP48':0,'public_output_zero':True,'rejected_query_scope_requests':negative,
   'accepted_stop_RVA':'0xcb8dd4'}
class Startup(CP.Startup):
 def invoke_entry(self):
  super().invoke_entry();detail=Query(self).run();CASES.append(detail)
CP.Startup=Startup
def main():
 facts,camera=authority();sources=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  for mode in ['ANSI','OEM']:
   CP.CP_MODE=mode;CASES.clear();row=CP.integrated(blob,pin,camera);assert len(CASES)==1
   row['cases'][0].update(CASES[0]);sources.append(row)
   print(json.dumps({'source_sha256':pin,'query_policy':mode,'query_instructions':CASES[0]['original_executed_instruction_count'],'saved_qword_stores':8}),flush=True)
 cases=[r['cases'][0] for r in sources]
 assert len(cases)==6 and all(r['all_executed_sites_once'] for r in cases)
 result={'experiment':'E011CQ','status':'PASS_BOUNDED_ORIGINAL_CONVERSION_QUERY','base_commit':BASE,'authority':facts,'sources':sources,
  'integrated_camera_cases':6,'distinct_tuning_sources':3,'camera_placements_per_source_per_policy':1,
  'ANSI_query_codepage0_cases':3,'OEM_query_codepage1_cases':3,'exact_original_saved_qword_stores':48,
  'original_query_continuation_instructions':sum(r['original_executed_instruction_count'] for r in cases),
  'rejected_query_scope_requests':36,'independent_complete_stack_and_other_regions':True,
  'source_owned_stack_filename_NUL_terminated_and_unchanged':True,'source_converter_result_record_zero_unchanged':True,
  'conversion_API_executed':False,'conversion_result_supplied':False,'actual_codepage_locale_qualified':False,
  'live_Default_filename_qualified':False,'whole_outer_return_qualified':False,'final_output_publication_qualified':False,
  'original_numeric_TLS_policy_or_conversion_success_stub':False,'new_logger16A4228_admitted':False,
  'native_Windows_DLL_execution':False,'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,
  'runtime_or_image_test':False,'next_experiment':'E011CR'}
 assert sum(r['exact_original_saved_qword_stores'] for r in cases)==48 and sum(r['rejected_query_scope_requests'] for r in cases)==36
 (OUT/'QUERY-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
