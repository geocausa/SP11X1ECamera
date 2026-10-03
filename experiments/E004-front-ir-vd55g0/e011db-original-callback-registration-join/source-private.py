#!/usr/bin/env python3
"""Original callback-record registration, independent whole memory and registered camera-entry join."""
from pathlib import Path
import importlib.util,inspect,textwrap,json,hashlib,struct,collections,copy
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
P=ROOT/'experiments/E004-front-ir-vd55g0/e011da-original-runtime-helper-camera-join/source-private.py'
assert hashlib.sha256(P.read_bytes()).hexdigest()=='984c6e09c3ac3a333cdead1dcb3a2969b9c546398caacafa6bc372eb71a9c420'
s=importlib.util.spec_from_file_location('db_da',P);DA=importlib.util.module_from_spec(s);s.loader.exec_module(DA)
CF=DA.CF;CP=DA.CP;CW=DA.CW;CV=DA.CZ.CV
RAW=CF.p.get_data(0x36e9c8,448)
REGISTRATION_SHA='42009cec630593ad99c7d269abf72f740a7c6297cd0effc70f927b72f58118f4'
assert hashlib.sha256(RAW).hexdigest()==REGISTRATION_SHA
TRACE=list(range(0x36e9c8,0x36ea0c,4))+list(range(0x36ea44,0x36ea78,4))+list(range(0x36eb10,0x36eb1c,4))+list(range(0x36eb58,0x36eb88,4))
assert len(TRACE)==45
CONTROL={(0x160a218,8):0,(0x1608858,4):1,(0x160a210,8):0}
class Registration:
 def __init__(self,n,table,root,stack,o=None):
  self.n=n;self.u=n.u;self.table=table;self.root=root;self.stack=stack;self.o=o
  self.instructions={i.address:i for i in CF.c.disasm(RAW,n.base+0x36e9c8)}
  self.qualified=False
 def snapshot(self):return {(a,b,p):bytes(self.u.mem_read(a,b-a+1)) for a,b,p in self.u.mem_regions()}
 def q(self,at):return int.from_bytes(self.u.mem_read(at,8),'little')
 def contract(self,entry,args):
  assert entry==0x36e9c8 and args==self.request
  assert self.u.reg_read(UC_ARM64_REG_X0)==self.table and self.q(self.n.base+0x1798458)==self.root
  assert int.from_bytes(self.u.mem_read(self.root,4),'little')==self.ref and self.ref in [0,1,41]
  assert self.table%8==0 and self.root%8==0
  assert any(a<=self.table and self.table+48<=b+1 for a,b,p in self.u.mem_regions())
  assert any(a<=self.root and self.root+4<=b+1 for a,b,p in self.u.mem_regions())
  for (r,z),v in CONTROL.items():assert int.from_bytes(self.u.mem_read(self.n.base+r,z),'little')==v
 def patch(self,at,data):
  region=next(k for k in self.before if k[0]<=at and at+len(data)<=k[1]+1)
  if region not in self.models:self.models[region]=bytearray(self.before[region])
  self.models[region][at-region[0]:at-region[0]+len(data)]=data
 def run(self):
  u=self.u;n=self.n
  self.paused={r:u.reg_read(r) for r in [*[globals()['UC_ARM64_REG_X'+str(k)] for k in range(31)],*[globals()['UC_ARM64_REG_Q'+str(k)] for k in range(32)],
   UC_ARM64_REG_SP,UC_ARM64_REG_PC,UC_ARM64_REG_NZCV,UC_ARM64_REG_FPCR,UC_ARM64_REG_FPSR]}
  u.reg_write(UC_ARM64_REG_X0,self.table);u.reg_write(UC_ARM64_REG_SP,self.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  self.ref=int.from_bytes(u.mem_read(self.root,4),'little')
  self.request=[self.table,self.root,self.ref,self.stack+0xf000,n.end]
  self.contract(0x36e9c8,self.request)
  self.before=self.snapshot();self.resources=self.o.helper_join.resources() if self.o else None
  self.incoming={r:u.reg_read(r) for r in [UC_ARM64_REG_SP,*[globals()['UC_ARM64_REG_X'+str(k)] for k in range(19,30)],*[globals()['UC_ARM64_REG_D'+str(k)] for k in range(8,16)]]}
  before_regs={r:u.reg_read(r) for r in self.paused};tests=[(0x36e9cc,self.request),(0x36e9c8,self.request+[0])]
  for k in range(5):
   bad=self.request.copy();bad[k]+=1;tests.append((0x36e9c8,bad))
  for entry,args in tests:
   try:self.contract(entry,args)
   except AssertionError:pass
   else:raise AssertionError('invalid registration request admitted')
  assert self.snapshot()==self.before and all(u.reg_read(r)==v for r,v in before_regs.items())
  self.negative_count=len(tests);self.models={};self.pending={};self.trace=[];self.writes=0;self.reads=collections.Counter()
  self.fields={(0x36ea48,self.table,4):48,(0x36ea54,self.table+16,8):n.base+0x36e870,
   (0x36ea68,self.table+32,8):n.base+0x36cba0,(0x36ea68,self.table+40,8):n.base+0x36e900,
   (0x36eb64,self.root,4):self.ref+1}
  for (site,at,z),value in self.fields.items():self.patch(at,value.to_bytes(z,'little'))
  self.hooks=[type(u).hook_add(u,UC_HOOK_CODE,self.code),type(u).hook_add(u,UC_HOOK_MEM_WRITE,self.memory),type(u).hook_add(u,UC_HOOK_MEM_READ,self.read)]
  try:u.emu_start(n.base+0x36e9c8,n.end,count=2000)
  finally:
   for hook in self.hooks:u.hook_del(hook)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end and u.reg_read(UC_ARM64_REG_X0)==self.table and not self.pending
  assert self.trace==TRACE and self.writes==13
  after=self.snapshot();assert after.keys()==self.before.keys() and all(after[k]==self.models.get(k,v) for k,v in self.before.items()),'independent entire registration memory model'
  assert all(u.reg_read(r)==v for r,v in self.incoming.items())
  if self.o:assert self.o.helper_join.resources()==self.resources
  self.table_bytes=bytes(u.mem_read(self.table,48));self.frozen_stack=bytes(u.mem_read(self.stack,65536))
  self.table_region=next(k for k in after if k[0]<=self.table and self.table+48<=k[1]+1);self.frozen_table_region=after[self.table_region]
  self.root_extent=48 if self.o else 176;self.frozen_root=bytes(u.mem_read(self.root,self.root_extent))
  self.stack_region=next(k for k in after if k[0]<=self.stack and self.stack+65536<=k[1]+1)
  self.root_entry=self.q(self.table+32)
  assert self.root_entry==n.base+0x36cba0
  for r,v in self.paused.items():u.reg_write(r,v)
  assert all(u.reg_read(r)==v for r,v in self.paused.items())
  self.qualified=True
  self.detail={'original_registration_instructions':len(self.trace),'exact_source_store_chunks':self.writes,'invalid_scope_requests_rejected':self.negative_count,
   'initial_owned_root_reference_count':self.ref,'source_produced_root_reference_count':self.ref+1,
   'complete48byte_callback_record_and_entire_other_memory_checked':True,'original_return_is_input_record_pointer':True,
   'original_SP_X19_X29_D8_D15_and_complete_paused_caller_restored':True,'permissions_and_resource_state_checked':True,
   'registered_entry_RVA':hex(self.root_entry-n.base),'registered_slot_offset':32,
   'owned_nonnull_root_and_file_image_control_globals_are_fixtures':True,'fresh_root176_constructor_and_live_Default_input_producer_qualified':False}
  self.before=None;self.models=None
  return self.detail
 def code(self,u,pc,z,user):
  assert not self.pending and pc in self.instructions and u.reg_read(UC_ARM64_REG_PC)==pc
  r=pc-self.n.base;assert bytes(u.mem_read(pc,4))==CF.p.get_data(r,4)
  assert len(self.trace)<len(TRACE) and r==TRACE[len(self.trace)];self.trace.append(r)
  i=self.instructions[pc];self.pending_pc=pc
  if i.mnemonic.startswith(('str','stp','stur','stlxr')):
   op=next(o for o in i.operands if o.type==3);assert not op.mem.index
   at=CV.reg(u,CF.c.reg_name(op.mem.base))+op.mem.disp
   first=1 if i.mnemonic=='stlxr' else 0;name=CF.c.reg_name(i.operands[first].reg)
   width=1 if i.mnemonic.endswith('b') else 2 if i.mnemonic.endswith('h') else 16 if name.startswith('q') else 8 if name.startswith(('x','d')) or name in ('fp','lr') else 4
   for k,o in enumerate(i.operands[:2] if i.mnemonic=='stp' else i.operands[first:first+1]):
    address=at+k*width;value=CV.reg(u,CF.c.reg_name(o.reg))&((1<<(8*width))-1)
    if self.stack<=address and address+width<=self.stack+65536:self.patch(address,value.to_bytes(width,'little'))
    else:assert self.fields.get((r,address,width))==value,('unowned registration store',hex(r),width)
    for j in range(0,width,8):z=min(width-j,8);self.pending[address+j,z]=(value>>(8*j))&((1<<(8*z))-1)
 def memory(self,u,access,at,z,value,user):
  assert u.reg_read(UC_ARM64_REG_PC)==self.pending_pc and (at,z) in self.pending
  assert value&((1<<(8*z))-1)==self.pending.pop((at,z));self.writes+=1
 def read(self,u,access,at,z,value,user):
  if self.stack<=at and at+z<=self.stack+65536:return
  assert (at,z) in {(self.n.base+r,s) for r,s in CONTROL}|{(self.n.base+0x1798458,8),(self.root,4)}
  self.reads[at-self.n.base if self.n.base<=at<self.n.base+CF.p.OPTIONAL_HEADER.SizeOfImage else 'root_reference']+=1
 def final(self):
  assert self.qualified and bytes(self.u.mem_read(self.table,48))==self.table_bytes and bytes(self.u.mem_read(self.stack,65536))==self.frozen_stack
  assert self.q(self.n.base+0x1798458)==self.root and int.from_bytes(self.u.mem_read(self.root,4),'little')==self.ref+1
  assert self.root_entry==self.q(self.table+32)==self.n.base+0x36cba0
  assert self.table_region in list(self.u.mem_regions()) and self.stack_region in list(self.u.mem_regions())
  a,b,p=self.table_region;assert bytes(self.u.mem_read(a,b-a+1))==self.frozen_table_region
  assert bytes(self.u.mem_read(self.root,self.root_extent))==self.frozen_root
# Replace the independently written caller's fixed entry address with the source-registered record slot.
owners=[]
for cls in DA.Startup.__mro__:
 fn=cls.__dict__.get('invoke_entry')
 if fn:
  try:text=inspect.getsource(fn)
  except OSError:continue
  if 'self.n.base+0x36cba0' in text:owners.append((cls,fn,text))
assert len(owners)==1
cls,fn,text=owners[0];assert text.count('self.n.base+0x36cba0')==1
module=fn.__globals__;code=textwrap.dedent(text).replace('self.n.base+0x36cba0','self.registration.root_entry')
scope={};exec(code,module,scope);cls.invoke_entry=scope['invoke_entry']
ROWS=[]
class Startup(DA.Startup):
 def invoke_entry(self):
  u=self.u;n=self.n;assert not self.active
  u.mem_map(0x97400000,65536);u.mem_write(0x97400000,bytes([0xa5])*65536)
  u.mem_map(0x97410000,65536);u.mem_write(0x97410000,bytes([0xa5])*65536)
  self.registration=Registration(n,0x97411000,self.f.readq(n.base+0x1798458),0x97400000,self)
  detail=self.registration.run()
  try:DA.Startup.invoke_entry(self)
  except CW.BoundedStop:pass
  self.registration.final();ROWS.append({'registration':detail,'inherited_runtime_helper_camera_join':DA.ROWS[-1],
   'camera_entry_called_through_original_registered_slot32':True,'source_created_callback_record_retained_through_outer_return':True})
  raise CW.BoundedStop()
CP.Startup=Startup
def isolated():
 rows=[]
 for bias in [0,16,128,512]:
  for ref in [0,1,41]:
   n=DA.CZ.N.Native();u=n.u;table=n.heap+0x1000+bias;root=n.heap+0x3000+bias
   u.mem_write(n.heap,bytes([0xa5])*0x30000);u.mem_write(n.stack,bytes([0xd5])*65536)
   u.mem_write(root,struct.pack('<I',ref)+bytes([0xd5])*172);u.mem_write(n.base+0x1798458,struct.pack('<Q',root))
   for k in range(31):u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0x111000+k)
   for k in range(8,16):u.reg_write(globals()['UC_ARM64_REG_D'+str(k)],0x222000+k)
   proof=Registration(n,table,root,n.stack);d=proof.run();proof.final();rows.append({'placement_bias':bias,**d})
 print(json.dumps({'isolated_registration_cases':len(rows),'original_instructions':sum(r['original_registration_instructions'] for r in rows),'exact_stores':sum(r['exact_source_store_chunks'] for r in rows),'status':'PASS_BOUNDED_ORIGINAL_REGISTRATION_RECORD'}),flush=True)
 return rows
def main():
 DA.CY.authority();standalone=isolated();rows=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  for mode in ('ANSI','OEM'):
   CP.CP_MODE=mode;ROWS.clear();DA.ROWS.clear();DA.CY.ROWS.clear();DA.CX.ROWS.clear();CW.ROWS.clear();CW.CS.CASES.clear();CW.CS.CR.CASES.clear();CW.CS.CR.CQ.CASES.clear()
   try:CP.integrated(blob,pin,CW.camera)
   except CW.BoundedStop:assert len(ROWS)==1
   else:raise AssertionError('registered camera callback return not reached')
   row={'source_sha256':pin,'policy':mode,**ROWS[0]};rows.append(row)
   print(json.dumps({'policy':mode,'source_sha256':pin,**row['registration'],'registered_camera_join':'PASS'}),flush=True)
 result={'experiment':'E011DB','status':'PASS_BOUNDED_ORIGINAL_CALLBACK_REGISTRATION_AND_REGISTERED_CAMERA_ENTRY','base_commit':'71206fac8d62792f986e7b3f7ed748416a58dc7f',
  'isolated_cases':standalone,'camera_cases':rows,'isolated_registration_cases':len(standalone),'registered_camera_cases':len(rows),
  'original_registration_instructions':sum(r['original_registration_instructions'] for r in standalone)+sum(r['registration']['original_registration_instructions'] for r in rows),
  'exact_registration_store_chunks':sum(r['exact_source_store_chunks'] for r in standalone)+sum(r['registration']['exact_source_store_chunks'] for r in rows),
  'invalid_registration_scope_requests_rejected':sum(r['invalid_scope_requests_rejected'] for r in standalone)+sum(r['registration']['invalid_scope_requests_rejected'] for r in rows),
  'source_authority':{'entry_RVA':'0x36e9c8','bytes':448,'sha256':REGISTRATION_SHA,'executed_trace_RVAs':[hex(r) for r in TRACE]},
  'original_callback_record_size':48,'registered_entry_slot':32,'registered_camera_entry_RVA':'0x36cba0',
  'original_table_pointer_return_and_reference_increment_independently_checked':True,
  'complete_record_and_whole_mapped_memory_permissions_resources_and_caller_checks':True,
  'camera_entry_uses_source_registered_callback':True,'callback_record_and_root_reference_retained_through_outer_return':True,'entire_new_table_region_stack_root_record_and_actual_permissions_retained':True,
  'inherited_output_global_actual_caller_and_same_root_lock_checks_retained':True,
  'owned_nonnull_root_and_file_image_control_globals_and_component_ordering_are_fixtures':True,
  'fresh_root176_allocation_initialization_and_cleanup_qualified':False,'actual_Default_input_producer_and_full_Windows_startup_qualified':False,
  'original_Host_provider_2BC618_and_full_2128byte_caller_qualified':False,
  'hardware_WM16_IRQ_IOVA_DMA_IOMMU_retirement_optical_qualified':False,'native_rear_runtime_allowed':False,
  'new_camera_Starts':0,'new_reboots':0,'new_Linux_image_tests':0,'production_C_or_kernel_changed':False,'next_experiment':'E011DC'}
 assert len(standalone)==12 and len(rows)==6 and result['original_registration_instructions']==810 and result['exact_registration_store_chunks']==234 and result['invalid_registration_scope_requests_rejected']==126
 (OUT/'REGISTRATION-CAMERA-JOIN-V2-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
