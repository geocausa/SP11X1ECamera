#!/usr/bin/env python3
"""Original post-cleanup output publication; strict independently declared memory and callback scope verifier."""
from pathlib import Path
import importlib.util,inspect,textwrap,hashlib,json,collections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
OUT=Path(__file__).resolve().parent
P=ROOT/'experiments/E004-front-ir-vd55g0/e011cw-original-file-thread-cleanup/source-private.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='6ebc560a810af826732050f3a2d4fa59d83f4ca67b51b46f65ea84f0a90f5094'
spec=importlib.util.spec_from_file_location('cx_cw',P);CW=importlib.util.module_from_spec(spec);spec.loader.exec_module(CW)
CF=CW.CF;CP=CW.CP
source=textwrap.dedent(inspect.getsource(CW.Startup.invoke_entry))
assert source.count(' cleanup=Cleanup(self,join,adapters).run()')==1
source=source.replace(' cleanup=Cleanup(self,join,adapters).run()',' cleanup_owner=Cleanup(self,join,adapters);cleanup=cleanup_owner.run()')
assert source.count('super().invoke_entry()')==1 and source.count(' ROWS.append')==1
source=source.replace('super().invoke_entry()','CS.Startup.invoke_entry(self)').replace(' ROWS.append',' self.cw_join=join;self.cw_cleanup=cleanup_owner\n ROWS.append')
scope={};exec(source,CW.__dict__,scope);invoke=scope['invoke_entry']
CI=CW.CP.CO.CN.CI
owners=[cls for cls in CW.Startup.__mro__ if cls.__module__==CI.__name__ and cls.__name__=='Startup'];assert len(owners)==1
observer=textwrap.dedent(inspect.getsource(owners[0].hook))
assert observer.count('if r==0x36d03c:')==1 and observer.count('super().hook(u,pc,size,user)')==1
observer=observer.replace('if r==0x36d03c:','if r==0x36d03c and self.events["original_entry_saved_input_output_TLS"]==0:').replace('super().hook(u,pc,size,user)','CF.Observer.hook(self,u,pc,size,user)')
patched={};exec(observer,CI.__dict__,patched);owners[0].hook=patched['hook']

CV=CW.CV
AUTH_PATH=OUT/'PUBLICATION-CODE-AUTHORITY-SAFE.json'
assert hashlib.sha256(AUTH_PATH.read_bytes()).hexdigest()=='d4a90cbcb7d2c04128412cad7552d90a5c7149d313bfd83d2f31a3668d74d316'
AUTH=json.loads(AUTH_PATH.read_text())
class Publication:
 def __init__(self,o):
  self.o=o;self.u=o.u;self.n=o.n;self.b=o.crt;self.j=o.cw_join;self.f=o.f
  self.regions=o.cw_cleanup.regions.copy()+[('caller',0x90000000,0x80000)]
  self.before=self.snapshot();self.models={k:bytearray(v) for k,v in self.before.items() if k in ('stack','camera','caller','image')}
  inner=o.inner;outer=o.outer;interface=self.f.readq(inner+8);core=self.f.readq(interface)
  assert (inner,606264) in self.f.allocs and (outer,72) in self.f.allocs and (interface,320) in self.f.allocs and (core,5152) in self.f.allocs
  self.interface=interface;self.core=core;self.fields={}
  rows=[(0x36df6c,inner+91432,16,0),(0x36df70,inner+91448,4,0),(0x36df88,inner+91436,4,0x7fffffff),
        (0x3afb88,core+128,4,0),(0x3afc54,core+128,4,0),(0x3afc58,core+136,8,inner+91432),
        (0x36e034,inner+604736,8,0),(0x36e04c,inner+604744,8,0),(0x36e04c,inner+604752,8,0)]
  rows += [(0x36e060,inner+605168+k*16,16,(1<<128)-1) for k in range(2)]
  rows += [(0x36e064,inner+605200,16,(1<<128)-1),(0x36e068,inner+605216,1,255),(0x36e070,inner+605224,8,0),
           (0x36e0c4,outer+40,8,inner),(0x36e130,o.output,8,outer),(0x36e164,self.n.base+0x1798460,8,outer)]
  for r,at,size,value in rows:
   self.fields[r,at,size]=value
   name,base,extent=next((name,base,extent) for name,base,extent in self.regions if name in self.models and name!='stack' and base<=at and at+size<=base+extent)
   self.models[name][at-base:at-base+size]=value.to_bytes(size,'little')
  assert self.f.readq(o.output)==0 and self.f.readq(self.n.base+0x1798460)==0
  self.pending={};self.visits=0;self.executed=0;self.os_count=0;self.writes=0;self.stopped=False;self.native=False
  self.adapters=collections.Counter();self.contracts=collections.Counter();self.negatives_count=0;self.loop_indices=[]
  self.allocs=self.f.allocs.copy();self.released=self.f.released.copy();self.next=self.f.next
  self.crt_state=(self.b.allocs.copy(),self.b.next_alloc,self.b.depths.copy(),self.b.api_events.copy())
  self.pages=self.j.pages();self.instructions={}
  for row in AUTH['source_authority']:
   r=int(row['RVA'],16);size=row['bytes'];raw=CF.p.get_data(r,size);assert hashlib.sha256(raw).hexdigest()==row['sha256']
   for i in CF.c.disasm(raw,self.n.base+r):self.instructions[i.address]=(i,CF.p,self.n.base,'OEM')
  for at,row in self.j.instructions.items():
   if row[3]=='FlsGetValue2':self.instructions[at]=row
  i=next(CF.c.disasm(CF.p.get_data(0x3a9d5c,4),0x3a9d5c));assert i.mnemonic=='stp' and i.operands[-1].mem.disp==96
  assert CF.p.get_qword_at_rva(0x1338438)==CF.p.OPTIONAL_HEADER.ImageBase+0x3afb60
  self.diagnostics_before=o.new_diagnostic_sites.copy()
  self.hooks=[type(self.u).hook_add(self.u,UC_HOOK_CODE,self.code),type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.memory),type(self.u).hook_add(self.u,UC_HOOK_MEM_READ,self.read)]
 def snapshot(self):return {name:bytes(self.u.mem_read(at,size)) for name,at,size in self.regions}
 def contract(self,site,args):
  o=self.o;u=self.u;n=self.n
  assert site in (0x36dfb4,0x3a7fc0,0x36df4c,0x36e028,self.j.getter)
  assert len(args)==3 and self.contracts[site]==0
  if site==0x36dfb4:
   assert args==[self.interface,n.base+0x3a7f90,96] and self.f.readq(o.inner+8)==self.interface and self.f.readq(self.interface+96)==args[1]
  elif site==0x3a7fc0:
   assert args==[self.core,n.base+0x3afb60,16] and self.f.readq(self.interface)==self.core and self.f.readq(self.core)==n.base+0x1338428 and self.f.readq(n.base+0x1338438)==args[1]
  elif site in (0x36df4c,0x36e028):
   assert args==[0,n.base+0x16a4230,0] and o.target_origins.get('x15')==(0x16a4230,n.base+0x16a4230) and self.f.readq(n.base+0x16a4230)==0
  else:
   assert args==[self.j.slot,self.j.teb,0xcb4210] and u.reg_read(UC_ARM64_REG_X18)==self.j.teb and self.j.registry[self.j.slot]==self.j.thread
   assert int.from_bytes(u.mem_read(n.base+0x1607168,4),'little')==self.j.slot and int.from_bytes(u.mem_read(self.j.teb+0x68,4),'little')==3
 def negatives(self,site,args):
  requests=[(site+4,args),(site,args+[0])]
  for k in range(3):
   bad=args.copy();bad[k]+=1;requests.append((site,bad))
  before=self.snapshot();state=(self.contracts.copy(),self.j.pages(),self.f.allocs.copy(),self.b.depths.copy())
  for req in requests:
   try:self.contract(*req)
   except AssertionError:pass
   else:raise AssertionError('invalid publication scope request admitted')
  assert before==self.snapshot() and state==(self.contracts.copy(),self.j.pages(),self.f.allocs.copy(),self.b.depths.copy())
  self.negatives_count+=len(requests)
 def before_hook(self,pc):
  u=self.u;n=self.n;o=self.o;r=pc-n.base
  if pc==self.j.getter:site=pc;args=[u.reg_read(UC_ARM64_REG_W0),u.reg_read(UC_ARM64_REG_X18),u.reg_read(UC_ARM64_REG_LR)-n.base]
  elif r in (0x36dfb4,0x3a7fc0):site=r;args=[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X15),96 if r==0x36dfb4 else 16]
  elif r in (0x36df4c,0x36e028):site=r;args=[u.reg_read(UC_ARM64_REG_X15),n.base+0x16a4230,0]
  else:return
  self.contract(site,args);self.negatives(site,args);self.contracts[site]+=1
  if site==self.j.getter:self.native=True
  elif site in (0x36dfb4,0x3a7fc0):CF.NUMERIC[site]={args[1]-n.base}
 def code(self,u,pc,size,user):
  assert not self.pending
  n=self.n;o=self.o;r=pc-n.base
  if self.native and pc==n.base+0xcb4210:
   assert u.reg_read(UC_ARM64_REG_X0)==self.j.thread and int.from_bytes(u.mem_read(self.j.teb+0x68,4),'little')==3;self.native=False
  if r==0x36e178:
   assert u.reg_read(UC_ARM64_REG_X0)==o.outer and u.reg_read(UC_ARM64_REG_X15)==self.f.readq(o.outer+16)==n.base+0x36e670
   self.stopped=True;u.emu_stop();return
  assert pc in self.instructions,('unqualified publication instruction',hex(r))
  i,pe,base,component=self.instructions[pc];assert bytes(u.mem_read(pc,4))==pe.get_data(pc-base,4)
  if component=='OEM':
   self.visits+=1
   if u.reg_read(UC_ARM64_REG_PC)!=pc:
    assert r in (0xce7c98,0x1a8c0,0x36df4c,0x36dfb4,0x3a7fc0,0x36e028)
    self.adapters[r]+=1;return
   self.executed+=1
  else:assert component=='FlsGetValue2' and self.native;self.os_count+=1
  if r==0x36d03c:
   sp=u.reg_read(UC_ARM64_REG_SP);index=self.f.readi(sp+24)
   assert 0<index<9 and self.f.readq(sp+32)==o.inputs and self.f.readq(sp+40)==o.tls+0x2000 and self.f.readq(sp+96)==o.output
   self.loop_indices.append(index)
  self.pending_pc=pc
  if i.mnemonic.startswith(('stp','str','stur','stlxr')):
   operand=next(op for op in i.operands if op.type==3);mem=operand.mem
   index=0
   if mem.index:
    assert r==0x36e164 and CF.c.reg_name(mem.base)=='x22' and CF.c.reg_name(mem.index)=='w21' and operand.shift.value==3 and operand.ext==3
    index=CV.reg(u,'w21');assert index==0
   at=CV.reg(u,CF.c.reg_name(mem.base))+mem.disp+(index<<operand.shift.value);first=1 if i.mnemonic=='stlxr' else 0;name=CF.c.reg_name(i.operands[first].reg)
   width=2 if i.mnemonic.endswith('h') or name.startswith('h') else 1 if i.mnemonic.endswith('b') or name.startswith('b') else 16 if name.startswith('q') else 8 if name in ('fp','lr') or name.startswith(('x','d')) else 4
   ops=i.operands[:2] if i.mnemonic=='stp' else i.operands[first:first+1]
   for k,op in enumerate(ops):
    address=at+k*width;value=CV.reg(u,CF.c.reg_name(op.reg))&((1<<(8*width))-1)
    if n.stack<=address and address+width<=n.stack+65536:
     off=address-n.stack;self.models['stack'][off:off+width]=value.to_bytes(width,'little')
    else:assert (r,address,width) in self.fields and self.fields[r,address,width]==value,('unowned publication store',hex(r),width,address-self.o.inner,value)
    for j in range(0,width,8):z=min(width-j,8);self.pending[address+j,z]=(value>>(8*j))&((1<<(8*z))-1)
 def memory(self,u,access,at,size,value,user):
  assert u.reg_read(UC_ARM64_REG_PC)==self.pending_pc and (at,size) in self.pending
  assert value&((1<<(8*size))-1)==self.pending.pop((at,size));self.writes+=1
 def read(self,u,access,at,size,value,user):
  assert at+size<=self.b.utf_output or at>=self.b.utf_output+74,'read of retired Unicode owner'
  if self.native:assert (at,size) in {(self.j.teb+0x17c8,8),(self.j.data+8*self.j.chunk,8),(self.j.slab+8*self.j.index,8)}
 def run(self):
  o=self.o;u=self.u;n=self.n;o.active=True;o.cx_active=True
  try:u.emu_start(n.base+0xced194,n.end,count=200000)
  finally:
   o.active=False;o.cx_active=False
   for hook in self.hooks:u.hook_del(hook)
  assert self.stopped and u.reg_read(UC_ARM64_REG_PC)==n.base+0x36e178 and not self.pending and not self.native
  assert self.visits==394 and self.executed==386 and self.os_count==19 and self.writes==64
  assert self.loop_indices==list(range(2,9)) and self.negatives_count==25
  assert dict(self.adapters)=={0xce7c98:2,0x1a8c0:2,0x36df4c:1,0x36dfb4:1,0x3a7fc0:1,0x36e028:1}
  assert all(v==1 for v in self.contracts.values()) and len(self.contracts)==5
  after=self.snapshot();assert all(after[k]==self.models.get(k,v) for k,v in self.before.items()),'independent whole publication memory delta'
  assert self.f.allocs==self.allocs and self.f.released==self.released and self.f.next==self.next
  assert (self.b.allocs,self.b.next_alloc,self.b.depths,self.b.api_events)==self.crt_state and self.j.pages()==self.pages
  assert self.o.cw_cleanup.released==[self.b.utf_output] and self.f.readq(o.output)==o.outer and self.f.readq(o.outer+40)==o.inner and self.f.readq(n.base+0x1798460)==o.outer
  fresh={r:value for r,value in o.new_diagnostic_sites.items() if r not in self.diagnostics_before}
  assert fresh=={0x36df4c:0x16a4230,0x36e028:0x16a4230}
  self.b.policy.check_pages()
  return {'source_guarded_OEM_visits':self.visits,'unchanged_executed_OEM_instructions':self.executed,'inherited_typed_adapter_entries':sum(self.adapters.values()),'original_OS_getter_instructions':self.os_count,'exact_source_store_chunks':self.writes,'invalid_callback_getter_requests_rejected':self.negatives_count,'remaining_parameter_indices':self.loop_indices,'independent_whole_stack_camera_caller_image_models':True,'all_other_entire_regions_immutable':True,'actual_permissions_and_allocation_lock_state_unchanged':True,'original_interface96_and_core_vtable16_callbacks_executed_unchanged':True,'original_inner_link_and_output_and_global_publication_exact':True,'retired_UTF16_no_reads':True,'stop_before_publication_callback_RVA':'0x36e178','unexecuted_original_callback_RVA':'0x36e670','full_original_outer_return_qualified':False,'camera_root_mutex_still_held':True}
ROWS=[]
class Startup(CW.Startup):
 def hook(self,u,pc,size,user):
  if getattr(self,'cx_active',False) and pc==self.n.base+0x36e178:
   assert u.reg_read(UC_ARM64_REG_X0)==self.outer and u.reg_read(UC_ARM64_REG_X15)==self.f.readq(self.outer+16)==self.n.base+0x36e670
   self.publication.stopped=True;u.emu_stop();return
  if getattr(self,'cx_active',False):self.publication.before_hook(pc)
  return super().hook(u,pc,size,user)
 def invoke_entry(self):
  try:invoke(self)
  except CW.BoundedStop:pass
  assert self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+0xced194
  self.publication=Publication(self);detail=self.publication.run()
  ROWS.append({'inherited_slot_thread_cleanup':CW.ROWS[-1],'publication':detail})
  raise CW.BoundedStop()
CP.Startup=Startup
def main():
 sources=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  for mode in ('ANSI','OEM'):
   CP.CP_MODE=mode;ROWS.clear();CW.ROWS.clear();CW.CS.CASES.clear();CW.CS.CR.CASES.clear();CW.CS.CR.CQ.CASES.clear()
   try:CP.integrated(blob,pin,CW.camera)
   except CW.BoundedStop:assert len(ROWS)==1
   else:raise AssertionError('publication boundary not reached')
   row={'source_sha256':pin,'policy':mode,**ROWS[0]};sources.append(row);print(json.dumps({'policy':mode,'source_sha256':pin,**row['publication']}),flush=True)
 result={'experiment':'E011CX','status':'PASS_BOUNDED_ORIGINAL_OUTPUT_AND_GLOBAL_PUBLICATION','base_commit':'ff015b131999c58576724dccab82860f995e3897','sources':sources,'source_authority':AUTH['source_authority'],'integrated_camera_cases':len(sources),'distinct_tuning_sources':3,'source_guarded_OEM_visits':sum(r['publication']['source_guarded_OEM_visits'] for r in sources),'unchanged_executed_OEM_instructions':sum(r['publication']['unchanged_executed_OEM_instructions'] for r in sources),'inherited_typed_adapter_entries':sum(r['publication']['inherited_typed_adapter_entries'] for r in sources),'original_OS_getter_instructions':sum(r['publication']['original_OS_getter_instructions'] for r in sources),'exact_source_store_chunks':sum(r['publication']['exact_source_store_chunks'] for r in sources),'invalid_callback_getter_requests_rejected':sum(r['publication']['invalid_callback_getter_requests_rejected'] for r in sources),'full_whole_memory_permissions_and_resource_state_checks':True,'original_output_and_global_published_outer':True,'original_outer40_links_actual_inner':True,'initial_entry_X26_observer_assertion_scoped_to_first_visit':True,'whole_windows_loader_Default_CRT_TLS_locale_concurrency_qualified':False,'original_CFE600_qualified':False,'publication_callback36E670_executed':False,'full_original_outer_return_qualified':False,'camera_root_mutex_still_held':True,'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,'new_Linux_image_tests':0,'next_experiment':'E011CY'}
 assert len(sources)==6
 (OUT/'OUTPUT-PUBLICATION-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(list,dict))}),flush=True)
if __name__=='__main__':main()
