#!/usr/bin/env python3
"""Original inner-manager attachment and configuration prefix; derived facts only."""
from pathlib import Path
import importlib.util,struct,json,hashlib,collections,inspect,textwrap
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
OUT=Path(__file__).resolve().parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
CG=load('ch_cg',ROOT/'experiments/E004-front-ir-vd55g0/e011cg-inner-descriptor-lifetime/source-private.py')
CF=CG.CF;CD=CF.CE.CD;PREFIX=0x36d3dc;STOP=0x36d63c;NEW_DIAGNOSTIC_SITES=set()
def authority():
 facts=CG.authority();CD.authority()
 for site,targets in CF.CC.CA.NUMERIC.items():CF.NUMERIC.setdefault(site,set()).update(targets)
 CF.NUMERIC[0xce7be8].add(0x3a0760)
 for site in [0x36d3f8,0x36d594]:CF.NUMERIC[site]={0x3a8730}
 for site in [0x36d5c4,0x36d5e8,0x36d60c]:CF.NUMERIC[site]={0x3a88e0}
 for site in [0x39598c,0x3959c8,0x395a04]:CF.NUMERIC[site]={0x3a8820}
 p,c=CF.p,CF.c
 def ins(r):return next(c.disasm(p.get_data(r,4),r))
 # Exact original import and pre-core frame facts; no original instruction text leaves SP11.
 assert ins(0x36cbd8).mnemonic=='str' and ins(0x36cbd8).operands[-1].mem.disp==32
 assert ins(0x36cbdc).mnemonic=='mov' and [c.reg_name(o.reg) for o in ins(0x36cbdc).operands]==['x26','x1']
 assert ins(0x36ccec).mnemonic=='add' and ins(0x36ccec).operands[-1].imm==8
 assert ins(0x36d280).mnemonic=='ldr' and ins(0x36d280).operands[-1].mem.disp==40
 i=ins(0x36d288);assert i.mnemonic in ['ldrb','ldrsb'] and c.reg_name(i.operands[-1].mem.base)=='x8' and c.reg_name(i.operands[-1].mem.index)=='w9' and i.operands[-1].mem.disp==0
 assert ins(0x36e094).operands[-1].imm==0x36d034
 assert ins(0x36d3d0).operands[0].imm==0x39f070 and ins(0x36d3d8).operands[0].imm==0x39faf8
 for site,target in [(0x36d3f8,0x3a8730),(0x36d594,0x3a8730),(0x36d5c4,0x3a88e0),(0x36d5e8,0x3a88e0),(0x36d60c,0x3a88e0),(0x39598c,0x3a8820),(0x3959c8,0x3a8820),(0x395a04,0x3a8820)]:
  assert ins(site).mnemonic==ins(site+4).mnemonic=='blr'
  assert c.reg_name(ins(site).operands[0].reg)=='x17' and c.reg_name(ins(site+4).operands[0].reg)=='x15'
 for site,field in [(0x36d3e8,312),(0x36d580,312),(0x36d5b4,8),(0x36d5d4,8),(0x36d5f8,8),(0x39597c,0),(0x3959b8,0),(0x3959f4,0)]:
  assert ins(site).mnemonic=='ldr' and ins(site).operands[-1].mem.disp==field
 assert ins(0x36d524).operands[-1].imm==96 and ins(0x36d52c).operands[0].imm==0xcae740
 assert ins(0x36d61c).operands[0].imm==0x395940
 assert ins(0x36d638).mnemonic=='str' and ins(0x36d638).operands[-1].mem.disp==1840
 p.parse_data_directories();imports={}
 for d in p.DIRECTORY_ENTRY_IMPORT:
  for imp in d.imports:
   if imp.name in [b'EnterCriticalSection',b'LeaveCriticalSection']:imports[imp.name.decode()]=imp.address-p.OPTIONAL_HEADER.ImageBase
 assert imports['EnterCriticalSection']==0xf7e0b8 and len(imports)==2
 return {'original_DLL_sha256':facts['original_DLL_sha256'],
 'entry_RVA':'0x36cba0','stop_before_RVA':hex(STOP),'outer_function_bytes':6160,
 'caller_frame_input_offset':32,'caller_frame40_is_diagnostic_TLS_not_output_cell':True,
 'saved_output_argument_register':'x26','diagnostic_TLS_initialized_byte_offset':20,
 'explicit_singlethread_lock_object_global_RVA':'0x1798458','critical_section_object_offset':8,
 'OS_mutex_import_IAT_RVAs':{k:hex(v) for k,v in imports.items()},
 'source_record_array_stride_bytes':48,'source_record_array_count':9,'attached_statistics_manager_inner_offset':40,'attached_mode_configuration_inner_offset':91952,'complete_mode_configuration_RVA':'0x395940','complete_mode_configuration_bytes':224,'mode_configuration_receiver_bytes':96,'post_statistics_numeric_callback_targets':{'interface_slot312':'0x3a8730','interface_slot8':'0x3a88e0','32byte_mode_record_slot0':'0x3a8820'},
 'source_ranges_sha256':{hex(r):hashlib.sha256(p.get_data(r,z)).hexdigest() for r,z in [(0x36cba0,STOP-0x36cba0),(0x36cba0,6160),(0x39faf8,3168),(0x3a0760,96),(0x395940,224),(0x3a88e0,768),(0x3a8820,48)]}},imports
# Reuse the independently written complete 152-byte record/attachment model,
# with names isolated from the core-cache observer's own pending lookups.
record_method=textwrap.dedent(inspect.getsource(CD.Model.hook))
record_method=record_method[:record_method.rindex('return super().hook')].rstrip()+'\n'
record_method=record_method.replace('def hook(','def record_lineage(').replace('self.pending','self.record_pending').replace('self.setter','self.record_setter').replace('self.totals','self.record_counts').replace('dict(self.allocs)','dict(self.f.allocs)')
ns={};exec(record_method,dict(CD.__dict__),ns)
class Startup(CF.Observer):
 record_lineage=ns['record_lineage']
 def __init__(self,f):
  super().__init__(f);self.target_origins={};self.new_diagnostic_sites={};self.record_pending=None;self.record_setter=None;self.record_counts=collections.Counter();self.done=False;self.decode={}
 def hook(self,u,pc,size,user):
  r=pc-self.n.base
  if self.active and 0<=r<CF.p.OPTIONAL_HEADER.SizeOfImage:
   if r not in self.decode:self.decode[r]=next(CF.c.disasm(CF.p.get_data(r,4),r),None)
   ins=self.decode[r]
   if ins is not None:
    ops=ins.operands
    if ins.mnemonic=='blr' and CF.c.reg_name(ops[0].reg)=='x17' and ((r not in CF.NUMERIC and r not in CF.LOG) or r in NEW_DIAGNOSTIC_SITES):
     nxt=next(CF.c.disasm(CF.p.get_data(r+4,4),r+4))
     assert nxt.mnemonic=='blr' and CF.c.reg_name(nxt.operands[0].reg)=='x15'
     assert self.target_origins.get('x15')==(0x16a4230,self.n.base+0x16a4230),('dispatch lacks admitted diagnostic origin',hex(r))
     assert u.reg_read(UC_ARM64_REG_X15)==self.f.readq(self.n.base+0x16a4230)==0
     CF.LOG[r]=0x36cba0;NEW_DIAGNOSTIC_SITES.add(r);self.new_diagnostic_sites[r]=0x16a4230
    if ops and ops[0].type==1:
     dst=CF.c.reg_name(ops[0].reg)
     if ins.mnemonic=='mov' and len(ops)>1 and ops[1].type==1:
      origin=self.target_origins.get(CF.c.reg_name(ops[1].reg));self.target_origins.pop(dst,None)
      if origin is not None:self.target_origins[dst]=origin
     elif ins.mnemonic.startswith(('ldr','ldur')) and ops[-1].type==3:
      mem=ops[-1].mem;reg=CF.c.reg_name(mem.base);self.target_origins.pop(dst,None)
      if not mem.index and reg.startswith('x') and reg[1:].isdigit():
       at=u.reg_read(globals()['UC_ARM64_REG_X'+reg[1:]])+mem.disp
       if at==self.n.base+0x16a4230:self.target_origins[dst]=(0x16a4230,at)
     else:
      read,written=ins.regs_access()
      for register in written:self.target_origins.pop(CF.c.reg_name(register),None)
   if r in [0x36d3f8,0x36d594,0x36d5c4,0x36d5e8,0x36d60c]:
    receiver=u.reg_read(UC_ARM64_REG_X0);slot=312 if r in [0x36d3f8,0x36d594] else 8
    assert receiver==self.f.readq(self.inner+8)
    assert self.f.readq(receiver+slot)==u.reg_read(UC_ARM64_REG_X15)==self.n.base+(0x3a8730 if slot==312 else 0x3a88e0)
    self.events['post_statistics_interface_slot'+str(slot)]+=1
   if r in [0x39598c,0x3959c8,0x395a04]:
    receiver=u.reg_read(UC_ARM64_REG_X0)
    assert (receiver,32) in self.f.allocs and receiver not in self.f.released
    assert self.f.readq(receiver)==u.reg_read(UC_ARM64_REG_X15)==self.n.base+0x3a8820
    self.events['source_created_mode_record_accessor']+=1
   if r==0x36d52c:assert u.reg_read(UC_ARM64_REG_X0)==96
   if r==0x36d530:
    self.mode_configuration=u.reg_read(UC_ARM64_REG_X0)
    assert (self.mode_configuration,96) in self.f.allocs and self.mode_configuration not in self.f.released
   if r==0x395940:
    assert u.reg_read(UC_ARM64_REG_X0)==self.mode_configuration
    self.events['complete_original_mode_configuration_entry']+=1
   if r==0x36d620:self.events['complete_original_mode_configuration_return']+=1
   if r==PREFIX:
    assert self.vector is None and self.pending is None and self.record_pending is None and not self.setup_active
    self.prefix_inner=bytes(u.mem_read(self.inner,606264));self.prefix_outer=bytes(u.mem_read(self.outer,72))
    self.events['full_following_statistics_return']+=1
   if r==0x36d03c:
    sp=u.reg_read(UC_ARM64_REG_SP)
    assert self.f.readi(sp+24)==self.events["original_entry_saved_input_output_TLS"]
    assert self.f.readq(sp+32)==self.inputs and self.f.readq(sp+40)==self.tls+0x2000
    assert u.reg_read(UC_ARM64_REG_X26)==self.output
    self.outer=u.reg_read(UC_ARM64_REG_X23);assert (self.outer,72) in self.f.allocs
    self.events['original_entry_saved_input_output_TLS']+=1
   if r==0x36d0e8:
    assert u.reg_read(UC_ARM64_REG_X9)==self.selected_entry
    self.events['exact_first_kind4_parameter_entry']+=1
   if r==0x36d288:
    assert u.reg_read(UC_ARM64_REG_X8)==self.tls+0x2000 and u.reg_read(UC_ARM64_REG_W9)==20
    self.events['original_diagnostic_initialized_byte_source']+=1
   if r==0x3a8be0:
    self.inner=u.reg_read(UC_ARM64_REG_X20)
    assert (self.inner,606264) in self.f.allocs and self.f.readq(self.inner)==self.n.base+0x1337fd8
    assert [u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(4)]==[self.descriptor,self.inner+93032,self.inputs,self.inner+8]
    self.events['actual_original_inner_creator_arguments']+=1
   if r==0x36d33c:
    self.manager=u.reg_read(UC_ARM64_REG_X0);assert (self.manager,1664) in self.f.allocs
    self.events['original_stats_manager_allocation_return']+=1
   if r in [0x39f070,0x39faf8]:
    assert u.reg_read(UC_ARM64_REG_X0)==self.manager
    self.events['actual_inner_stats_entry_'+hex(r)]+=1
   if r==0x3a8730 and u.reg_read(UC_ARM64_REG_LR)-self.n.base in [site+8 for site in [0x39f0b4,0x39f0d4,0x39fb40,0x39fb60]]:
    assert u.reg_read(UC_ARM64_REG_X0)==self.f.readq(self.inner+8)
    self.events['actual_original_interface_statistics_access']+=1
   if r in CF.CC.CA.INIT:
    assert dict(self.f.allocs)[u.reg_read(UC_ARM64_REG_X0)]=={0x3a0d70:40,0x3a14e0:40,0x39d7e0:32,0x3a2440:328}[r]
    self.events['original_primary_initializer_'+hex(r)]+=1
   if r==0x36d3d4:self.events['full_ConfigureHWStats_return']+=1
   self.record_lineage(u,pc,size,user)
   if r==0xce7b98 and u.reg_read(UC_ARM64_REG_X3)==self.n.base+0x3a0760:
    assert self.vector is None
    dest=u.reg_read(UC_ARM64_REG_X0);stride=u.reg_read(UC_ARM64_REG_X1);count=u.reg_read(UC_ARM64_REG_X2)
    assert stride==48 and count==9 and any(a<=dest and dest+stride*count<=a+z and a not in self.f.released for a,z in self.f.allocs)
    self.vector={'base':dest,'stride':stride,'count':count,'target':0x3a0760,'index':0,'return':u.reg_read(UC_ARM64_REG_LR)-self.n.base}
    self.requested[(0xce7be8,0x3a0760)]+=count;self.events['original_48byte_record_array']+=1;return
   if r==STOP:
    assert self.vector is None and self.pending is None and self.record_pending is None and self.record_setter is None and not self.setup_active
    expected=bytearray(self.prefix_inner)
    struct.pack_into('<Q',expected,40,self.manager);struct.pack_into('<Q',expected,91952,self.mode_configuration)
    assert bytes(u.mem_read(self.inner,606264))==expected,'exact entire inner manager attachment delta'
    assert bytes(u.mem_read(self.outer,72))==self.prefix_outer,'outer changed before publication'
    self.events['independent_entire_inner_statistics_and_mode_links']+=1;self.done=True;u.emu_stop();return
  return super().hook(u,pc,size,user)
 def invoke_entry(self):
  self.events=collections.Counter();self.numeric=collections.Counter();self.requested=collections.Counter();self.vector=None;self.cache_active=False;self.setup_active=False;self.setup_gettags=[];self.pending=None
  self.record_pending=None;self.record_setter=None;self.record_counts=collections.Counter();self.done=False;self.target_origins={}
  for k in range(29):self.u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],0)
  self.u.mem_write(self.n.stack,bytes(0x10000));self.u.reg_write(UC_ARM64_REG_X0,self.inputs);self.u.reg_write(UC_ARM64_REG_X1,self.output);self.u.reg_write(UC_ARM64_REG_X18,self.tls);self.u.reg_write(UC_ARM64_REG_SP,self.n.stack+0xf000);self.u.reg_write(UC_ARM64_REG_LR,self.n.end);self.active=True
  try:self.u.emu_start(self.n.base+0x36cba0,self.n.end,count=2000000)
  except Exception:
   print(json.dumps({'excluded_fixture_stop_RVA':hex(self.u.reg_read(UC_ARM64_REG_PC)-self.n.base),'placement_bias':self.bias}),flush=True);raise
  self.active=False;assert self.done
def source(blob,pin,imports):
 f=CG.load_source(blob);u=f.n.u;n=f.n;o=Startup(f);own=0x90000000
 u.mem_map(own,0x80000);u.mem_write(own,b'\xa5'*0x80000)
 lock=own+0x6c000;u.mem_write(lock,bytes(48));u.mem_write(n.base+0x1798458,struct.pack('<Q',lock))
 sentinels={own+0x70000:'EnterCriticalSection',own+0x70020:'LeaveCriticalSection'}
 for at,name in sentinels.items():u.mem_write(n.base+imports[name],struct.pack('<Q',at))
 lock_depth=0;lock_events=collections.Counter()
 def mutex(u,pc,z,user):
  nonlocal lock_depth
  if pc not in sentinels:return
  name=sentinels[pc];assert u.reg_read(UC_ARM64_REG_X0)==lock+8
  if name=='EnterCriticalSection':lock_depth+=1
  else:assert lock_depth>0;lock_depth-=1
  lock_events[name]+=1;u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
 type(u).hook_add(u,UC_HOOK_CODE,mutex)
 native=bytes(u.mem_read(n.heap,0x30000));serialized=bytes(u.mem_read(f.map,f.map_size));image=bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage));cases=[]
 for idx,(bias,index) in enumerate(zip([0,1,40,1230],[1,2,5,8])):
  o.bias=bias;base=own+idx*0x10000+bias;o.descriptor=base+0x1000;o.inputs=base+0x2000;entries=base+0x3000;context=base+0x4000;o.tls=base+0x5000;o.output=base+0x9000;o.mode=base+0xa000;diag=base+0xc000;o.selected_entry=entries+16*index
  u.mem_write(o.descriptor,struct.pack('<QQII',f.manager,o.mode,0,0));u.mem_write(o.mode,bytes(320));u.mem_write(o.output,bytes(8))
  u.mem_write(o.inputs,struct.pack('<QI',entries,9)+bytes(4));u.mem_write(entries,bytes(144));u.mem_write(diag,bytes(24))
  u.mem_write(entries,struct.pack('<QII',diag,24,3));u.mem_write(entries+48,struct.pack('<QII',context,8,1));u.mem_write(context,bytes(8));u.mem_write(entries+16*index,struct.pack('<QII',o.descriptor,24,4))
  u.mem_write(o.tls,bytes(0x4000));u.mem_write(o.tls+88,struct.pack('<Q',o.tls+0x1000));u.mem_write(o.tls+0x1000,struct.pack('<64Q',*([o.tls+0x2000]*64)));u.mem_write(o.tls+0x2000+20,struct.pack('<I',1))
  owner_before=bytes(u.mem_read(own,0x80000));before=bytes(u.mem_read(f.arena,f.arena_size));old_count=len(f.allocs);depth_before=lock_depth;lock_before=lock_events.copy();f.next=((f.next+4095)&~4095)+bias
  o.invoke_entry();assert lock_depth==depth_before+1 and lock_events['EnterCriticalSection']==lock_before['EnterCriticalSection']+1
  assert lock_events['LeaveCriticalSection']==lock_before['LeaveCriticalSection']
  outer=o.outer;assert f.readq(o.output)==0;inner=o.inner;interface=f.readq(inner+8);core=f.readq(interface);manager=o.manager;sizes=dict(f.allocs)
  assert sizes[outer]==72 and sizes[inner]==606264 and sizes[interface]==320 and sizes[core]==5152 and sizes[manager]==1664
  assert core==o.core
  # Original code attaches distinct statistics and mode objects; output remains unpublished.
  assert f.readq(inner+40)==manager and f.readq(inner+91952)==o.mode_configuration
  assert o.events["post_statistics_interface_slot312"]==2 and o.events["post_statistics_interface_slot8"]==3
  assert o.events["source_created_mode_record_accessor"]==3
  assert all(o.events[k]==1 for k in ["complete_original_mode_configuration_entry","complete_original_mode_configuration_return","independent_entire_inner_statistics_and_mode_links"])
  assert f.readq(interface+312)==n.base+0x3a8730 and f.readq(core+0xff0)==f.actual_module+288
  shape=CF.CC.verify_configuration(f,f.readq(core+0xf20)-288)
  counts=[f.readi(f.actual_module+288+off) for off in [44,64,80]];total=sum(counts)
  assert counts[0]==4 and total in [12,14]
  assert f.readi(manager+0x614)==f.readi(manager+0x62c)==total
  primary=f.readq(manager+0x608);secondary=f.readq(manager+0x620)
  assert sizes[primary]==sizes[secondary]==160 and (f.readi(manager+0x610),f.readi(manager+0x618),f.readi(manager+0x628),f.readi(manager+0x630))==(0,20,0,20)
  prim=list(struct.unpack('<'+str(total)+'Q',u.mem_read(primary,8*total)));sec=list(struct.unpack('<'+str(total)+'Q',u.mem_read(secondary,8*total)))
  assert len(set(prim))==len(set(sec))==total and all(a in sizes and a not in f.released for a in prim+sec)
  assert [sizes[a] for a in prim[:counts[0]]]==[40]*counts[0]
  assert all(sizes[a] in [40,32] for a in prim[counts[0]:counts[0]+counts[1]])
  assert [sizes[a] for a in prim[counts[0]+counts[1]:]]==[328]*counts[2]
  assert o.events['original_primary_initializer_0x3a0d70']==counts[0]
  assert o.events['original_primary_initializer_0x3a14e0']+o.events['original_primary_initializer_0x39d7e0']==counts[1]
  assert o.events['original_primary_initializer_0x3a2440']==counts[2]
  assert o.events['actual_original_interface_statistics_access']==4
  assert [sizes[a] for a in sec]==[648]*counts[0]+[504]*counts[1]+[488]*counts[2]
  records=[]
  for obj in sec:
   rp=f.readq(obj+8);head,used,cap=[f.readi(obj+k) for k in [16,20,24]]
   assert sizes[rp]==160 and head==0 and cap==20 and used<=20
   records+=list(struct.unpack('<'+str(used)+'Q',u.mem_read(rp,used*8))) if used else []
   assert bytes(u.mem_read(rp+used*8,160-used*8))==bytes(160-used*8)
  assert len(set(records))==len(records)==15 and all(sizes[a]==152 for a in records)
  assert dict(o.record_counts)=={k:15 for k in ['exact_pre_attachment_records','original_attachment_setter_entries','exact_attachment_setter_returns','exact_final_152_byte_records']}
  assert o.events['original_48byte_record_array']==total
  assert o.numeric[(0xce7be8,0x3a0760)]==9*total
  assert o.events['original_entry_saved_input_output_TLS']==index+1
  assert all(o.events[k]==1 for k in ['exact_first_kind4_parameter_entry','actual_original_inner_creator_arguments','setup_entry','independent_complete_setup_delta','full_cache_entry','full_cache_return','full_bank_update_entry','full_bank_update_return','actual_inner_stats_entry_0x39f070','actual_inner_stats_entry_0x39faf8','full_ConfigureHWStats_return','full_following_statistics_return']),dict(o.events)
  expected_numeric=dict(o.requested)
  for key in [(0x3c8534,0x3aebb0),(0x3c8564,0x3ae980),(0x3cb160,0x3aebb0)]:expected_numeric[key]=1
  for key,value in expected_numeric.items():assert o.numeric[key]==value
  assert len(o.setup_gettags)==43
  new=CG.exact_new_payloads(f,before,old_count)
  expected_owned=bytearray(owner_before)
  expected_owned[o.tls+0x2000-own:o.tls+0x2000+4-own]=bytes(4)
  expected_owned[o.tls+0x2000+304-own:o.tls+0x2000+308-own]=bytes(4)
  assert bytes(u.mem_read(own,0x80000))==expected_owned,'unexpected complete caller/diagnostic delta'
  assert bytes(u.mem_read(n.heap,0x30000))==native and bytes(u.mem_read(f.map,f.map_size))==serialized
  assert bytes(u.mem_read(n.base,CF.p.OPTIONAL_HEADER.SizeOfImage))==image,'unexpected mapped-image/OS-fixture delta'
  f.bounds()
  cases.append({'placement_bias':bias,'first_kind4_parameter_index':index,'exact_parameter_search_visits':index+1,'full_original_entry_to_statistics_prefix':True,'original_inner_manager_attachment':True,'original_mode_configuration_attachment':True,'independent_entire606264byte_inner_attachment_delta':True,'complete_original_mode_configuration_returns':1,'post_statistics_interface_accessors':2,'source_created_mode_record_factory_calls':3,'source_created_mode_record_accessor_calls':3,'source_primary_secondary_counts':counts,'primary_secondary_objects_each':total,'independent_152byte_records':15,'original_48byte_stride_array_initializers':9*total,'original_core_vector_initializers':sum(v for (site,target),v in o.numeric.items() if site==0xce7be8 and target!=0x3a0760),'source_cache_lookups':43,'caller_TLS_frame40_source_verified':True,'new_diagnostic_sites_only_admitted_global16A4230':{hex(k):hex(v) for k,v in o.new_diagnostic_sites.items()},'preexisting_arena_image_native_serialized_immutable':True,'guarded_new_allocations':len(new),'singlethread_lock_held_at_bounded_stop':True,'whole_outer_return_or_concurrency_proven':False})
  print(json.dumps({'source_sha256':pin,'completed_original_entry_statistics_bias':bias,'independent_records':15}),flush=True)
 return {'source_sha256':pin,'cases':cases}
def main():
 facts,imports=authority();rows=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  rows.append(source(blob,pin,imports))
 cases=[v for row in rows for v in row['cases']]
 result={'status':'PASS_BOUNDED_ORIGINAL_INNER_MANAGER_ATTACHMENT_AND_CONFIGURATION','authority':facts,'sources':rows,'original_entry_actual_inner_statistics_cases':len(cases),'original_inner_manager_attachments':len(cases),'original_mode_configuration_attachments':len(cases),'independent_entire_inner_attachment_delta_cases':len(cases),'complete_original_mode_configuration_returns':len(cases),'post_statistics_interface_accessor_calls':2*len(cases),'source_created_mode_record_factory_calls':3*len(cases),'source_created_mode_record_accessor_calls':3*len(cases),'independent_152byte_records':sum(v['independent_152byte_records'] for v in cases),'original_statistics_record_initializers':sum(v['original_48byte_stride_array_initializers'] for v in cases),'original_core_vector_initializers':sum(v['original_core_vector_initializers'] for v in cases),'source_cache_lookups':sum(v['source_cache_lookups'] for v in cases),'whole_outer_return_qualified':False,'final_output_publication_qualified':False,'original_inner_manager_attachment_qualified':True,'attachment_retained_through_complete_outer_return_qualified':False,'actual_live_Default_descriptor_context_qualified':False,'filename_destruction_reuse_qualified':False,'singlethread_OS_lock_fixture_not_concurrency_proof':True,'new_logger16A4228_classification_admitted':False,'numeric_callbacks_unmodified':True,'new_TLS_success_stub':False,'native_rear_runtime_allowed':False,'runtime_or_image_test':False}
 assert len(cases)==12 and result['independent_152byte_records']==180 and result['original_statistics_record_initializers']==1440 and result['original_core_vector_initializers']==292
 (OUT/'ATTACHMENT-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(dict,list))}),flush=True)
if __name__=='__main__':main()
