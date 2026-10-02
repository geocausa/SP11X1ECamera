#!/usr/bin/env python3
"""Private full source cache population and internal ordinary request search model."""
from pathlib import Path
import importlib.util,struct,json,hashlib,collections
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
s=importlib.util.spec_from_file_location('ce_cd',ROOT/'experiments/E004-front-ir-vd55g0/e011cd-statistics-record-field-lineage/source-private.py');CD=importlib.util.module_from_spec(s);s.loader.exec_module(CD);CC=CD.CC
CACHE_RVA=0x3ca4a0;CACHE_BYTES=1776;CACHE_START=0xf00;CACHE_SIZE=43*8
cache_rows=[]
def prepare_full(blob,pin):
 f=CC.BP.Production(blob,0);needed=((len(f.sy)*320+len(f.records)*224+2*len(blob)+0x800000+4095)//4096)*4096;assert needed<0x8000000
 if needed>f.arena_size:
  extra=needed-f.arena_size;f.n.u.mem_map(f.arena+f.arena_size,extra);f.n.u.mem_write(f.arena+f.arena_size,b'\xa5'*extra);f.arena_size=needed
 f.run_full();u=f.n.u;n=f.n;memory=0x90000000;u.mem_map(memory,0x10000);u.mem_write(memory,b'\xa5'*0x10000)
 calls=[];pending=None;active=False;core=memory
 def watch(u,pc,size,user):
  nonlocal pending
  if not active:return
  r=pc-n.base
  if r==0x6f39f8:
   assert pending is None and u.reg_read(UC_ARM64_REG_X0)==f.manager and u.reg_read(UC_ARM64_REG_X2)==core+256 and u.reg_read(UC_ARM64_REG_W3)==0
   keyptr=u.reg_read(UC_ARM64_REG_X1);key=bytes(u.mem_read(keyptr,128)).split(b'\0',1)[0]
   assert key and p.get_data(keyptr-n.base,len(key)+1)==key+b'\0'
   pending={'return_RVA':u.reg_read(UC_ARM64_REG_LR)-n.base,'key':key,'alloc_count':len(f.allocs)}
  elif pending and r==pending['return_RVA']:
   module=u.reg_read(UC_ARM64_REG_X0);assert module in dict(f.allocs) and module not in f.released and dict(f.allocs)[module]>=288
   assert f.name_bytes(module+16,32)==pending['key'];new=f.allocs[pending['alloc_count']:]
   assert len(new)==(1 if len(pending['key'])>15 else 0)
   for ptr,z in new:
    assert z==32 and ptr in f.released and bytes(u.mem_read(ptr,len(pending['key'])+1))==pending['key']+b'\0'
   calls.append(module);pending=None
 type(u).hook_add(u,UC_HOOK_CODE,watch,begin=n.base+0x6f39f8,end=n.base+0x6f39f8)
 type(u).hook_add(u,UC_HOOK_CODE,watch,begin=n.base+CACHE_RVA,end=n.base+CACHE_RVA+CACHE_BYTES-1)
 cases=[]
 for bias in [0,1,40,1230]:
  core=memory+bias;calls=[];pending=None;u.mem_write(memory,b'\xa5'*0x10000);u.mem_write(core,bytes(5152));u.mem_write(core+168,struct.pack('<QQII',f.manager,core+256,0,0))
  core_before=bytes(u.mem_read(memory,0x10000));arena_before=bytes(u.mem_read(f.arena,f.arena_size));old_count=len(f.allocs)
  file_before=bytes(u.mem_read(f.map,f.map_size));heap_before=bytes(u.mem_read(n.heap,0x30000))
  for k in range(8):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0)
  u.reg_write(UC_ARM64_REG_X0,core+8);u.reg_write(UC_ARM64_REG_X1,core+168);u.reg_write(UC_ARM64_REG_SP,n.stack+0xd000);u.reg_write(UC_ARM64_REG_LR,n.end);f.phase='cache_fragment';active=True
  u.emu_start(n.base+CACHE_RVA,n.end,count=5000000);active=False;assert u.reg_read(UC_ARM64_REG_PC)==n.end and pending is None and len(calls)==43
  expected=bytearray(core_before);expected[bias+CACHE_START:bias+CACHE_START+CACHE_SIZE]=struct.pack('<43Q',*[m+288 for m in calls]);assert bytes(u.mem_read(memory,0x10000))==expected
  arena_after=bytes(u.mem_read(f.arena,f.arena_size));expected_arena=bytearray(arena_before)
  new=f.allocs[old_count:];assert len(new)==27 and all(z==32 and ptr in f.released for ptr,z in new)
  for ptr,z in new:off=ptr-f.arena;expected_arena[off:off+z]=arena_after[off:off+z]
  assert arena_after==expected_arena and bytes(u.mem_read(f.map,f.map_size))==file_before and bytes(u.mem_read(n.heap,0x30000))==heap_before
  assert f.readq(core+0xff0)==f.actual_module+288;configuration=f.readq(core+0xf20)-288;shape=CC.verify_configuration(f,configuration);f.bounds()
  cases.append({'placement_bias':bias,'full_cache_returns':1,'original_GetTag_returns':43,'exact_cache_slots':43,'null_modules':0,'temporary_name_allocations_and_releases':27,'complete_core_delta_and_preexisting_input_immutability':True})
 Search.cache=bytes(u.mem_read(core+CACHE_START,CACHE_SIZE));cache_rows.append({'source_sha256':pin,'cases':cases})
 return f,core,shape
class Search(CD.Model):
 cache=None;totals=collections.Counter()
 def __init__(self,p,c):super().__init__(p,c);self.requests=[];self.query_active=False
 def build(self,source,bias):super().build(source,bias);self.u.mem_write(self.core+CACHE_START,self.cache)
 def hook(self,u,pc,size,user):
  r=pc-self.n.base
  if self.query_active and r==0x39ea40:self.requests.append((u.reg_read(UC_ARM64_REG_W1),u.reg_read(UC_ARM64_REG_W2),u.reg_read(UC_ARM64_REG_W4)))
  if self.query_active and r in [0x372fb8,0x373048]:self.requests[-1]+= (u.reg_read(UC_ARM64_REG_W0),)
  return super().hook(u,pc,size,user)
 def query(self,selector,context,allocated=92,kind=None):
  assert allocated==92 and kind is None;self.requests=[];self.query_active=True;output=super().query(selector,context,allocated,kind);self.query_active=False
  assert self.requests==[(0,0,92,1)];self.totals['normal_full_query_returns']+=1;self.totals['successful_original_manager_queries']+=1
  self.exhaust(selector,context);return output
 def exhaust(self,selector,context):
  u=self.u;n=self.n;self.following=False;self.query_active=True;self.requests=[];self.selected=[];self.events=collections.Counter()
  prior=bytes(u.mem_read(self.manager+0x614,4));u.mem_write(self.manager+0x614,bytes(4));u.mem_write(self.output,b'\xa5'*160)
  u.mem_write(self.desc,struct.pack('<3Q',self.output,92,10 if selector==12 else 21));u.mem_write(self.outer+68,struct.pack('<I',context));before=bytes(u.mem_read(n.heap,0x100000));cursor_before=self.cursor
  for k,v in enumerate([self.engine,selector,self.inputs,self.desc,1]):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],v)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end);u.emu_start(n.base+0x852668,n.end,count=200000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end and u.reg_read(UC_ARM64_REG_X0)==0 and self.requests==[(0,t,92,0) for t in range(7)]
  assert struct.unpack('<I',u.mem_read(self.desc+12,4))[0]==0 and bytes(u.mem_read(self.output,160))==b'\xa5'*160 and not self.selected
  assert struct.unpack('<I',u.mem_read(self.tls+0x2000+304,4))[0]==context;self.guards();assert all(self.freed[a] for a,z in self.allocs if z==24)
  after=bytes(u.mem_read(n.heap,0x100000));allowed=[(self.desc+12,4),(cursor_before,self.cursor-cursor_before),(self.tls+0x2000+304,4)]
  for i,(a,b) in enumerate(zip(before,after)):
   if a!=b:assert any(lo<=n.heap+i<lo+z for lo,z in allowed)
  assert bytes(u.mem_read(n.heap,0x30000))==self.source_before;u.mem_write(self.manager+0x614,prior);self.query_active=False
  self.totals['exhausted_full_query_returns']+=1;self.totals['failed_original_manager_queries']+=7
def authority():
 global p,c
 p,c,facts=CD.authority();ins={i.address:i for i in c.disasm(p.get_data(0x372e40,4616),0x372e40)}
 for init,call,increment,bound,loop,back in [(0x372f98,0x372fb4,0x372fc0,0x372fc4,0x372fc8,0x372f9c),(0x373028,0x373044,0x373050,0x373054,0x373058,0x37302c)]:
  i=ins[init];assert i.mnemonic=='mov' and c.reg_name(i.operands[0].reg)=='w26' and i.operands[1].imm==0
  i=ins[call];assert i.mnemonic=='bl' and i.operands[0].imm==0x39ea40
  i=ins[increment];assert i.mnemonic=='add' and c.reg_name(i.operands[0].reg)==c.reg_name(i.operands[1].reg)=='w26' and i.operands[2].imm==1
  i=ins[bound];assert i.mnemonic=='cmp' and i.operands[1].imm==7
  i=ins[loop];assert i.mnemonic=='b.lo' and i.operands[0].imm==back
  i=ins[call+4];assert i.mnemonic=='cmp' and c.reg_name(i.operands[0].reg)=='w0' and i.operands[1].imm==1
 source_calls=[i for i in c.disasm(p.get_data(CACHE_RVA,CACHE_BYTES),CACHE_RVA) if i.mnemonic=='bl'];assert len(source_calls)==43 and all(i.operands[0].imm==0x6f39f8 for i in source_calls)
 facts={'original_DLL_sha256':facts['original_DLL_sha256'],'full_cache_producer_RVA':hex(CACHE_RVA),'full_cache_bytes':CACHE_BYTES,'cache_slots':43,'cache_primary_start':CACHE_START,'cache_primary_end_exclusive':CACHE_START+CACHE_SIZE,'owned_source_input_descriptor_bytes':24,'source_input_descriptor_fields':['manager_qword0','mode_pointer_qword8','mode_count_u32_16','extra_u32_20'],'ordinary_query_role':0,'ordinary_query_type_search':[0,1,2,3,4,5,6],'ordinary_query_output_bytes':92,'ordinary_query_calls_RVA':['0x372fb4','0x373044'],'source_ranges_sha256':{'cache_producer':hashlib.sha256(p.get_data(CACHE_RVA,CACHE_BYTES)).hexdigest(),'inner_GetParam':hashlib.sha256(p.get_data(0x372e40,4616)).hexdigest()}}
 return facts
def main():
 facts=authority();CC.Setup=Search;CC.prepare=prepare_full;rows=[]
 for name,pin in CC.CA.BB.AZ.AV.FILES:
  blob=(CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin;rows.append(CC.run(blob,pin,p,c));print(json.dumps({'source_sha256':pin,'full_cache_and_setup_placements':4}),flush=True)
 expected_queries={'normal_full_query_returns':72,'successful_original_manager_queries':72,'exhausted_full_query_returns':72,'failed_original_manager_queries':504};query_counts={k:Search.totals[k] for k in expected_queries};assert query_counts==expected_queries
 assert all(Search.totals[k]==180 for k in ['exact_pre_attachment_records','original_attachment_setter_entries','exact_attachment_setter_returns','exact_final_152_byte_records'])
 result={'status':'PASS_BOUNDED_FULL_SOURCE_CACHE_AND_INTERNAL_ORDINARY_TYPE_SEARCH','authority':facts,'source_cache':cache_rows,'source_setup':rows,'query_counts':query_counts,'full_cache_returns':12,'original_GetTag_returns':516,'exact_cache_slot_stores':516,'temporary_name_allocations_and_releases':324,'independent_final_record_checks':180,'whole_core_outer_constructor_qualified':False,'actual_live_Default_descriptor_qualified':False,'actual_live_inner_receiver_context_qualified':False,'runtime_or_image_test':False,'numeric_callbacks_unmodified':True}
 (OUT/'CACHE-REQUEST-SAFE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','full_cache_returns','original_GetTag_returns','query_counts']}),flush=True)
if __name__=='__main__':main()
