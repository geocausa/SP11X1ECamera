#!/usr/bin/env python3
"""Guarded original core startup and actual-core statistics bridge; scalar output only."""
from pathlib import Path
import importlib.util,struct,json,hashlib,collections,bisect
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
sp=importlib.util.spec_from_file_location('cf_ce',ROOT/'experiments/E004-front-ir-vd55g0/e011ce-full-source-cache-and-request-search/source-private.py');CE=importlib.util.module_from_spec(sp);sp.loader.exec_module(CE);CC=CE.CC
CORE_BYTES=5152;CORE_VTABLE=0x1338428;SECONDARY_VTABLE=0x13383b8
NUMERIC={0xce7be8:{0x3d4380,0x3a7c50,0x3c0de0},0x3c8534:{0x3aebb0},0x3c8564:{0x3ae980},0x3cb160:{0x3aebb0}}
LOG={3966188: 3965824, 4016096: 4015160, 3935668: 3934968, 3936332: 3935856, 3977784: 3977504, 3797636: 3797104, 3798088: 3797104, 3798380: 3797104, 3798920: 3797104, 3799520: 3797104, 3799696: 3797104}
MODE_FIELDS=list(zip([0,12,20,28,36,44,52],[3016,3024,3032,3040,3048,3056,3064],[1,1,1,1,1,1,1]))
bootstrap_rows=[]
def authority():
 global p,c
 CE.authority();p,c=CE.p,CE.c
 for site in set(NUMERIC)|set(LOG):
  a,b=list(c.disasm(p.get_data(site,8),site));assert a.mnemonic==b.mnemonic=='blr' and c.reg_name(a.operands[0].reg)=='x17' and c.reg_name(b.operands[0].reg)=='x15'
 for site,start in LOG.items():
  vals={};origins={}
  for i in c.disasm(p.get_data(start,site-start),start):
   o=i.operands
   if not o:continue
   dest=c.reg_name(o[0].reg) if o[0].type==1 else None
   if i.mnemonic=='adrp':vals[dest]=o[1].imm
   elif i.mnemonic=='add' and o[1].type==1 and o[2].type==2 and c.reg_name(o[1].reg) in vals:vals[dest]=vals[c.reg_name(o[1].reg)]+(o[2].imm<<o[2].shift.value)
   elif i.mnemonic=='mov' and o[1].type==1:
    src=c.reg_name(o[1].reg);sv=vals.get(src);vals.pop(dest,None)
    if sv is not None:vals[dest]=sv
    if src in origins:origins[dest]=origins[src]
   elif i.mnemonic.startswith(('ldr','ldur')) and o[-1].type==3:
    mem=o[-1].mem;base=vals.get(c.reg_name(mem.base));origins[dest]=None if base is None else base+mem.disp;vals.pop(dest,None)
   elif i.mnemonic in ['bl','blr']:
    for k in range(18):vals.pop('x'+str(k),None)
   elif dest and i.mnemonic not in ['cmp','cmn','tst','str','stp','cbz','cbnz','tbz','tbnz','br','ret'] and not i.mnemonic.startswith('b.'):vals.pop(dest,None)
  assert origins.get('x15')==0x16a4230
 for slot,target in [(16,0x3ae980),(104,0x3aebb0)]:assert struct.unpack('<Q',p.get_data(SECONDARY_VTABLE+slot,8))[0]==p.OPTIONAL_HEADER.ImageBase+target
 return {'original_DLL_sha256':CC.CA.BW.N.DLL_SHA,'core_creator_RVA':'0x3a8be0','core_creator_bytes':4980,'full_core_setup_RVA':'0x3c8380','full_core_setup_bytes':516,'full_following_bank_update_RVA':'0x3d4bd0','full_following_bank_update_bytes':3376,'primary_core_allocation_bytes':CORE_BYTES,'secondary_receiver_primary_offset':8,'source_owned_descriptor_copy_primary_offset':168,'mode_field_pairs':MODE_FIELDS,'checked_numeric_sites':{hex(k):[hex(t) for t in sorted(v)] for k,v in NUMERIC.items()},'diagnostic_sites_from_global16A4230':[hex(k) for k in LOG],'source_ranges_sha256':{hex(r):hashlib.sha256(p.get_data(r,z)).hexdigest() for r,z in [(0x3a8be0,4980),(0x3c8380,516),(0x3d4bd0,3376),(0x3d4438,1112),(0x3d4020,248)]}}
class Production(CC.BP.Production):
 def __init__(self,blob):self.bootstrap=False;super().__init__(blob,0)
 def hook(self,u,pc,size,user):
  if self.bootstrap and pc==self.n.base+0xf5e600:
   out=u.reg_read(UC_ARM64_REG_X0);z=u.reg_read(UC_ARM64_REG_X2);ix=bisect.bisect_right(self.allocs,out,key=lambda a:a[0])-1;assert ix>=0
   a,extent=self.allocs[ix];assert a<=out and out+z<=a+extent and a not in self.released
   u.mem_write(out,bytes([u.reg_read(UC_ARM64_REG_X1)&255])*z);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR));return
  return super().hook(u,pc,size,user)
class Observer:
 def __init__(self,f):
  self.f=f;self.n=f.n;self.u=f.n.u;self.active=False;self.instructions={};self.core=None
  type(self.u).hook_add(self.u,UC_HOOK_CODE,self.hook)
 def ret(self,value=None):
  if value is not None:self.u.reg_write(UC_ARM64_REG_X0,value)
  self.u.reg_write(UC_ARM64_REG_PC,self.u.reg_read(UC_ARM64_REG_LR))
 def hook(self,u,pc,size,user):
  if not self.active:return
  r=pc-self.n.base;f=self.f
  if r==0xce7c98:self.events['owned_diagnostic_context']+=1;self.ret(self.tls+0x3000);return
  if r==0xcfe600:raise AssertionError('diagnostic TLS must already exist')
  if r in [0x1aca8,0x1a8c0]:self.events['inert_diagnostic_return']+=1;self.ret();return
  if r==0xce7b98:
   assert self.vector is None
   a=u.reg_read(UC_ARM64_REG_X0);stride=u.reg_read(UC_ARM64_REG_X1);count=u.reg_read(UC_ARM64_REG_X2);target=u.reg_read(UC_ARM64_REG_X3)-self.n.base
   assert target in NUMERIC[0xce7be8] and stride in [96,136,456] and 0<count<=18
   ix=bisect.bisect_right(f.allocs,a,key=lambda row:row[0])-1;start,extent=f.allocs[ix];assert start<=a and a+stride*count<=start+extent and start not in f.released
   self.vector={'base':a,'stride':stride,'count':count,'target':target,'index':0,'return':u.reg_read(UC_ARM64_REG_LR)-self.n.base};self.requested[(0xce7be8,target)]+=count
  elif self.vector and r==self.vector['return']:
   assert self.vector['index']==self.vector['count'];self.events['source_vector_element_returns']+=self.vector['count'];self.events['source_vector_array_returns']+=1;self.vector=None
  if r==0xce7be8:
   assert self.vector is not None and u.reg_read(UC_ARM64_REG_X0)==self.vector['base']+self.vector['stride']*self.vector['index'] and u.reg_read(UC_ARM64_REG_X15)==self.n.base+self.vector['target']
   self.vector['index']+=1
  if r==0x3c8380:
   self.events['setup_entry']+=1;self.core=u.reg_read(UC_ARM64_REG_X0)-8
   assert (self.core,CORE_BYTES) in f.allocs and u.reg_read(UC_ARM64_REG_X1)==self.descriptor
   self.core_before=bytes(u.mem_read(self.core,CORE_BYTES));self.setup_gettags=[];self.setup_active=True
  if r==0x3ca4a0:self.events['full_cache_entry']+=1;self.cache_active=True
  if r==0x3c8510:self.events['full_cache_return']+=1;self.cache_active=False;assert len(self.setup_gettags)==43
  if r==0x3d4bd0:
   assert u.reg_read(UC_ARM64_REG_X0)==f.readq(self.core+24) and u.reg_read(UC_ARM64_REG_X1)==self.core+168
   self.events['full_bank_update_entry']+=1
  if r==0x3c851c:self.events['full_bank_update_return']+=1
  if r==0x3c8538:assert u.reg_read(UC_ARM64_REG_X0)==self.core+8
  if r==0x3c853c:assert u.reg_read(UC_ARM64_REG_X0)==self.core+0xf00
  if r==0x3c8564:
   assert u.reg_read(UC_ARM64_REG_X0)==self.core+8 and u.reg_read(UC_ARM64_REG_W1)==39
   assert u.reg_read(UC_ARM64_REG_W2)==f.readi(f.readq(self.core+0xfe8)+48)
   self.events['source_selector39_entry']+=1
  if r in [0x3a9774,self.n.end-self.n.base] and self.setup_active:self.verify_setup()
  if self.cache_active and r==0x6f39f8:
   assert self.pending is None and u.reg_read(UC_ARM64_REG_X0)==f.manager and u.reg_read(UC_ARM64_REG_X2)==self.mode and u.reg_read(UC_ARM64_REG_W3)==0
   kp=u.reg_read(UC_ARM64_REG_X1);key=bytes(u.mem_read(kp,128)).split(b'\0',1)[0];assert key and p.get_data(kp-self.n.base,len(key)+1)==key+b'\0'
   self.pending=(u.reg_read(UC_ARM64_REG_LR)-self.n.base,key)
  elif self.pending and r==self.pending[0]:
   module=u.reg_read(UC_ARM64_REG_X0);assert module in dict(f.allocs) and module not in f.released and dict(f.allocs)[module]>=288
   assert f.name_bytes(module+16,32)==self.pending[1];self.setup_gettags.append(module);self.pending=None
  if r not in self.instructions:self.instructions[r]=next(c.disasm(p.get_data(r,4),r),None) if 0<=r<p.OPTIONAL_HEADER.SizeOfImage else None
  i=self.instructions[r]
  if i and i.mnemonic=='blr' and c.reg_name(i.operands[0].reg)=='x17':
   assert r in NUMERIC or r in LOG,'unclassified checked dispatch '+hex(r);target=u.reg_read(UC_ARM64_REG_X15)
   if r in LOG:
    assert target==f.readq(self.n.base+0x16a4230)==0;u.reg_write(UC_ARM64_REG_X15,self.n.base+0x1a8c0);self.events['classified_diagnostic_dispatch']+=1
   else:
    assert target-self.n.base in NUMERIC[r];self.numeric[(r,target-self.n.base)]+=1
   u.reg_write(UC_ARM64_REG_PC,pc+4)
 def verify_setup(self):
  f=self.f;u=self.u;core=self.core;expected=bytearray(self.core_before)
  expected[168:192]=u.mem_read(self.descriptor,24)
  for source,target,width in MODE_FIELDS:
   # A nonnull mode record supplies all seven fields, even at count0.
   expected[target:target+width]=u.mem_read(self.mode+source,width)
  if self.setup_gettags:
   expected[0xf00:0xf00+344]=struct.pack('<43Q',*[m+288 for m in self.setup_gettags])
   struct.pack_into('<I',expected,144,f.readi(f.readq(core+0xfe8)+48))
  assert bytes(u.mem_read(core,CORE_BYTES))==expected,'independent complete core setup delta'
  assert bytes(u.mem_read(core+168,24))==bytes(u.mem_read(self.descriptor,24))
  self.events['independent_complete_setup_delta']+=1;self.setup_active=False
 def invoke(self,rva,args):
  self.events=collections.Counter();self.numeric=collections.Counter();self.requested=collections.Counter();self.vector=None;self.cache_active=False;self.setup_active=False;self.setup_gettags=[];self.pending=None
  for k in range(8):self.u.reg_write(globals()['UC_ARM64_REG_X'+str(k)],args[k] if k<len(args) else 0)
  self.u.reg_write(UC_ARM64_REG_X18,self.tls);self.u.reg_write(UC_ARM64_REG_SP,self.n.stack+0xf000);self.u.reg_write(UC_ARM64_REG_LR,self.n.end);self.active=True
  self.u.emu_start(self.n.base+rva,self.n.end,count=1000000);self.active=False
  assert self.u.reg_read(UC_ARM64_REG_PC)==self.n.end and self.pending is None and self.vector is None
  if self.setup_active:self.verify_setup()
  return dict(self.events)
def prepare_bootstrap(blob,pin):
 f=Production(blob);needed=((len(f.sy)*320+len(f.records)*224+2*len(blob)+0x1000000+4095)//4096)*4096;assert needed<0x8000000
 if needed>f.arena_size:
  extra=needed-f.arena_size;f.n.u.mem_map(f.arena+f.arena_size,extra);f.n.u.mem_write(f.arena+f.arena_size,b'\xa5'*extra);f.arena_size=needed
 f.run_full();f.bootstrap=True;f.phase='bootstrap';o=Observer(f);u=f.n.u;n=f.n
 own=0x90000000;u.mem_map(own,0x80000);u.mem_write(own,b'\xa5'*0x80000);cases=[];cores={};interfaces={}
 original_count=len(f.allocs);source_old={a:bytes(u.mem_read(a,z)) for a,z in f.allocs if a not in f.released}
 native_before=bytes(u.mem_read(n.heap,0x30000));file_before=bytes(u.mem_read(f.map,f.map_size))
 for idx,bias in enumerate([0,1,40,1230]):
  base=own+idx*0x10000+bias;o.descriptor=base+0x1000;inputs=base+0x2000;entry=base+0x3000;context=base+0x4000;o.tls=base+0x5000;output=base+0x9000;o.mode=base+0xa000
  u.mem_write(o.descriptor,struct.pack('<QQII',f.manager,o.mode,0,0));u.mem_write(o.mode,bytes(320));u.mem_write(output,bytes(8))
  u.mem_write(inputs,struct.pack('<QQ',entry,1));u.mem_write(entry,bytes(64));u.mem_write(entry+12,struct.pack('<I',1));u.mem_write(entry+48,struct.pack('<Q',context));u.mem_write(context,bytes(8))
  u.mem_write(o.tls,bytes(0x4000));u.mem_write(o.tls+88,struct.pack('<Q',o.tls+0x1000));u.mem_write(o.tls+0x1000,struct.pack('<64Q',*([o.tls+0x2000]*64)));u.mem_write(o.tls+0x2000+20,struct.pack('<I',1))
  own_before=bytes(u.mem_read(own,0x80000));arena_before=bytes(u.mem_read(f.arena,f.arena_size));alloc_before=len(f.allocs)
  f.next=((f.next+4095)&~4095)+bias
  events=o.invoke(0x3a8be0,[o.descriptor,0,inputs,output]);assert u.reg_read(UC_ARM64_REG_X0)==0
  core=o.core;interface=f.readq(output);assert (core,5152) in f.allocs and core%32==bias%32
  assert (interface,320) in f.allocs and f.readq(interface)==core and f.readq(interface+312)==n.base+0x3a8730
  assert f.readq(core)==n.base+CORE_VTABLE and f.readq(core+8)==n.base+SECONDARY_VTABLE
  assert events['setup_entry']==events['independent_complete_setup_delta']==events['full_cache_entry']==events['full_cache_return']==events['full_bank_update_entry']==events['full_bank_update_return']==events['source_selector39_entry']==1
  expected_numeric=dict(o.requested);expected_numeric.update({(0x3c8534,0x3aebb0):1,(0x3c8564,0x3ae980):1,(0x3cb160,0x3aebb0):1});assert dict(o.numeric)==expected_numeric and events['source_vector_array_returns']==3
  vector_count=events['source_vector_element_returns'];assert vector_count==sum(o.requested.values());requested_rows=[{'callback_RVA':hex(target),'elements':count} for (site,target),count in o.requested.items()]
  new=f.allocs[alloc_before:];after=bytes(u.mem_read(f.arena,f.arena_size));expected_arena=bytearray(arena_before)
  for a,z in new:off=a-f.arena;expected_arena[off:off+z]=after[off:off+z]
  assert after==expected_arena
  expected_own=bytearray(own_before);struct.pack_into('<Q',expected_own,output-own,interface);expected_own[o.tls+0x2000+304-own:o.tls+0x2000+308-own]=bytes(4)
  assert bytes(u.mem_read(own,0x80000))==expected_own,'caller-owned inputs and output delta'
  assert f.readq(core+0xff0)==f.actual_module+288
  shape=CC.verify_configuration(f,f.readq(core+0xf20)-288)
  # Re-enter the COMPLETE setup with unchanged modes and extra0: no reload.
  warm_before=bytes(u.mem_read(f.arena,f.arena_size));warm_alloc=len(f.allocs)
  warm=o.invoke(0x3c8380,[core+8,o.descriptor])
  assert warm.get('full_cache_entry',0)==warm.get('full_bank_update_entry',0)==0 and warm['independent_complete_setup_delta']==1
  assert len(f.allocs)==warm_alloc and bytes(u.mem_read(f.arena,f.arena_size))==warm_before
  # Force a source refresh using only the declared descriptor extra field.
  u.mem_write(o.descriptor+20,struct.pack('<I',1));force_before=bytes(u.mem_read(f.arena,f.arena_size));force_alloc=len(f.allocs)
  forced=o.invoke(0x3c8380,[core+8,o.descriptor]);assert forced['full_cache_entry']==forced['full_cache_return']==forced['full_bank_update_entry']==forced['full_bank_update_return']==forced['independent_complete_setup_delta']==1
  after=bytes(u.mem_read(f.arena,f.arena_size));expect=bytearray(force_before);expect[core+188-f.arena:core+192-f.arena]=struct.pack('<I',1)
  temporary=f.allocs[force_alloc:];assert len(temporary)==39 and all(z==32 and a in f.released for a,z in temporary)
  for a,z in temporary:off=a-f.arena;expect[off:off+z]=after[off:off+z]
  assert after==expect,'forced refresh changed existing owner storage unexpectedly'
  # Restore extra0 through the original unchanged-mode path.
  u.mem_write(o.descriptor+20,bytes(4));restore=o.invoke(0x3c8380,[core+8,o.descriptor]);assert restore.get('full_cache_entry',0)==0
  for a,data in source_old.items():assert bytes(u.mem_read(a,len(data)))==data
  assert bytes(u.mem_read(n.heap,0x30000))==native_before and bytes(u.mem_read(f.map,f.map_size))==file_before
  f.bounds();cores[bias]=core;interfaces[bias]=interface
  cases.append({'placement_bias':bias,'complete_creator_returns':1,'full_setup_returns':4,'full_cache_returns':2,'exact_cache_GetTag_returns':86,'full_bank_update_returns':2,'unchanged_mode_skips':2,'source_created_primary_core_bytes':5152,'numeric_initializer_returns':vector_count,'source_requested_initializer_arrays':requested_rows,'source_constructed_interface_bytes':320,'full_core_setup_delta_exact':True,'forced_refresh_entire_existing_owner_delta_exact':True,'caller_and_preexisting_source_immutable':True,'allocation_count_full_creator':len(new),'temporary_names_forced_refresh':39})
 OriginalCore.cores=cores;OriginalCore.interfaces=interfaces;OriginalCore.owned=bytes(u.mem_read(own,0x80000));OriginalCore.source_core_used=collections.Counter()
 CE.Search.cache=bytes(u.mem_read(core+0xf00,344));bootstrap_rows.append({'source_sha256':pin,'cases':cases})
 return f,core,shape
class OriginalCore(CE.Search):
 cores={};interfaces={};owned=None;source_core_used=collections.Counter()
 def __init__(self,p,c):
  super().__init__(p,c);self.u.mem_map(0x90000000,0x80000);self.u.mem_write(0x90000000,self.owned)
 def hook(self,u,pc,size,user):
  if pc==self.n.base+0x36d338 and self.building:
   self.core=self.cores[self.bias];self.interface=self.interfaces[self.bias];u.mem_write(self.inner+8,struct.pack('<Q',self.interface));self.source_core_used[self.bias]+=1
   assert struct.unpack('<Q',u.mem_read(self.interface,8))[0]==self.core and struct.unpack('<Q',u.mem_read(self.interface+312,8))[0]==self.n.base+0x3a8730
   assert struct.unpack('<QQ',u.mem_read(self.core,16))==(self.n.base+CORE_VTABLE,self.n.base+SECONDARY_VTABLE)
  return super().hook(u,pc,size,user)
def main():
 facts=authority();CC.CA.LOG.update(site for site,start in LOG.items() if start in [0x39f070,0x39faf8]);CC.Setup=OriginalCore;CC.prepare=prepare_bootstrap;rows=[]
 for name,pin in CC.CA.BB.AZ.AV.FILES:
  blob=(CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  rows.append(CC.run(blob,pin,p,c));assert dict(OriginalCore.source_core_used)=={0:1,1:1,40:1,1230:1}
  print(json.dumps({'source_sha256':pin,'complete_core_creator_returns':4,'actual_core_full_stats_setup_returns':4}),flush=True)
 queries={k:OriginalCore.totals[k] for k in ['normal_full_query_returns','successful_original_manager_queries','exhausted_full_query_returns','failed_original_manager_queries']}
 assert queries=={'normal_full_query_returns':72,'successful_original_manager_queries':72,'exhausted_full_query_returns':72,'failed_original_manager_queries':504}
 assert all(OriginalCore.totals[k]==180 for k in ['exact_pre_attachment_records','original_attachment_setter_entries','exact_attachment_setter_returns','exact_final_152_byte_records'])
 result={'status':'PASS_BOUNDED_FULL_ORIGINAL_CORE_STARTUP_AND_ACTUAL_CORE_STATS_BRIDGE','authority':facts,'bootstrap':bootstrap_rows,'statistics_setup':rows,'complete_original_creator_returns':12,'complete_setup_returns':48,'full_cache_returns':24,'exact_cache_GetTag_returns':1032,'full_bank_update_returns':24,'unchanged_mode_skip_returns':24,'source_numeric_initializer_returns':sum(v['numeric_initializer_returns'] for r in bootstrap_rows for v in r['cases']),'actual_constructed_core_stats_setups':12,'independent_final_records':180,'queries':queries,'numeric_callbacks_unmodified':True,'actual_original_primary_core_used_by_statistics':True,'actual_original_returned_interface_used_by_statistics':True,'whole_outer_constructor_qualified':False,'actual_live_Default_descriptor_qualified':False,'complete_destruction_or_allocator_reuse_qualified':False,'all_optional_bank_fields_semantically_qualified':False,'runtime_or_image_test':False}
 (OUT/'STARTUP-SAFE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:result[k] for k in ['status','complete_original_creator_returns','actual_constructed_core_stats_setups','queries']}),flush=True)
if __name__=='__main__':main()
