#!/usr/bin/env python3
"""Original factory/enumeration bootstrap in retained helper VM, with distinct owned nodes."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011ds-original-cached-object-nested-lock-clear/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="5efcae3a58ea8ebbf16027f936778d06dd8520badd4b08a52bbd4607f6dc9e0a"
s=importlib.util.spec_from_file_location("actual_ds_parent",P);DS=importlib.util.module_from_spec(s);s.loader.exec_module(DS)
DR=DS.DR;PE=DS.PE;M=DS.M;C=DS.C;INS=dict(DS.INS);PINS=dict(DS.PINS);NONVOL=DS.NONVOL
EXTRA_PINS={'0x5bde08': {'body_bytes': 4004, 'ranges': [['0x5bde08', '0x5bedab']], 'sha256': '6ac0077e8b76bd1301294aab6e24517b3c62e84f1046cde686e18620fbd2b84b'}, '0x5f8dc0': {'body_bytes': 1776, 'ranges': [['0x5f8dc0', '0x5f94af']], 'sha256': 'd6509a3050729b92fb3a89e93c334e04eb4316ea2ff4af082f56e02de1a6af29'}, '0x1440': {'body_bytes': 48, 'ranges': [['0x1440', '0x146f']], 'sha256': 'f63f52748e3065341e8e73a6fb2abab1f5af2e25a17f3b0d627034c7341c9b5b'}}
for entry,pin in EXTRA_PINS.items():
 body=b"".join(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in pin["ranges"])
 assert len(body)==pin["body_bytes"] and hashlib.sha256(body).hexdigest()==pin["sha256"]
 for lo,hi in pin["ranges"]:INS.update({i.address:i for i in C.disasm(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1),int(lo,16))})
 PINS[entry]=pin
ZF=R/"experiments/E004-front-ir-vd55g0/e011dh-original-factory-initialization-clear/FACTORY-INITIALIZATION-ZERO-FIELDS-SAFE.json"
assert hashlib.sha256(ZF.read_bytes()).hexdigest()=="0f62dedc35657a133d2f1e4e9b5736fde52d69c78bfc6d0800e9498df3e93389"
ZERO_FIELDS=json.loads(ZF.read_text())["fields"];assert len(ZERO_FIELDS)==190
OUT=Path(__file__).resolve().parent
class Case(DS.Case):
 def __init__(self,bias,index,epoch,bound,diag,api,poison):
  super().__init__(bias,index,epoch,bound,diag,api,poison,0x80000040);n=self.n;u=self.u
  self.dt_ready=True;self.dt_srw_ready=True;self.dt_alloc_ready=True;self.dt_nodes=[n.heap+0x9000+bias,n.heap+0xd000+bias]
  self.dt_leases=[];self.dt_phase="entry";self.dt_apis=[];self.dt_frames=[];self.dt_guards_returned=0;self.dt_probe_returned=0;self.dt_clear_returned=0
  self.dt_trace=[];self.dt_literal_reads=[];self.dt_clear_visits=0;self.dt_clear_stores=0;self.dt_stopped=False;self.dt_factory_sp=None;self.dt_enum_sp=None
  self.dt_factory_guard=n.base+0x1b302d0;self.dt_enum_guard=n.base+0x1b30320;self.dt_static=n.base+0x169fe00
  assert self.rd(self.dt_factory_guard,4)==self.rd(self.dt_enum_guard,4)==0
  self.wr(self.teb+8,n.stack+65536,8);self.wr(self.teb+16,n.stack,8)
  for node in self.dt_nodes:u.mem_write(node-32,bytes([poison])*112)
  for x in ZERO_FIELDS:
   at=n.base+int(x["field_RVA"],16);width=x["width"]
   assert not (at<self.container+64 and at+width>self.inline)
   u.mem_write(at,bytes([poison])*width)
  u.mem_write(self.dt_static,bytes([poison])*56)
  self.dt_fields={(0xce7b14,self.dt_factory_guard,4):0xffffffff,(0x5be68c,n.base+0x18a296c,4):0,
   (0x5be694,n.base+0x1b302a0,8):0,(0x5be694,n.base+0x1b302a8,8):0}
  for k,node in enumerate(self.dt_nodes):
   shift=k*0x34
   for site,off,width,value in ((0x5be6a4,26,8,0),(0x5be6a4,34,8,0),(0x5be6a8,42,4,0),(0x5be6ac,46,2,0),(0x5be6b0,0,8,node),(0x5be6b0,8,8,node),(0x5be6b8,16,8,node),(0x5be6bc,24,2,257)):
    actual=site+shift-(4 if k==1 and off in (16,24) else 0)
    self.dt_fields[actual,node+off,width]=value
  self.dt_fields.update({(0x5be6c0,n.base+0x1b302a0,8):self.dt_nodes[0],(0x5be6c8,n.base+0x1b302c0,8):0,(0x5be6c8,n.base+0x1b302c8,8):0,(0x5be6f0,n.base+0x1b302c0,8):self.dt_nodes[1]})
  for x in ZERO_FIELDS:self.dt_fields[int(x["site_RVA"],16),n.base+int(x["field_RVA"],16),x["width"]]=0
  self.dt_fields[0xce7b14,self.dt_enum_guard,4]=0xffffffff
  for off in range(0,32,8):self.dt_fields[0x5f9488,self.dt_static+off,8]=0
  for off in (32,40):self.dt_fields[0x5f9490,self.dt_static+off,8]=0
  self.dt_fields[0x5f9494,self.dt_static+48,8]=0
  assert len(self.dt_fields)==222
 def logical(self):
  return super().logical()+(getattr(self,"dt_ready",False),getattr(self,"dt_srw_ready",False),getattr(self,"dt_alloc_ready",False),tuple(getattr(self,"dt_leases",[])),len(getattr(self,"dt_apis",[])))
 def dt_layout(self):
  n=self.n;u=self.u
  assert self.dt_ready and self.dt_srw_ready and self.dt_alloc_ready and self.held and self.inner_held and not self.crt_held
  assert self.rd(self.block+16,4)==self.rd(n.base+0x1607b04,4)==self.published_epoch==0x80000041
  assert u.reg_read(UC_ARM64_REG_X18)==self.teb and self.rd(self.teb+88,8)==self.array and self.rd(self.array+self.index*8,8)==self.block
  assert self.rd(self.teb+8,8)==n.stack+65536 and self.rd(self.teb+16,8)==n.stack
  assert all(self.rd(n.base+cell,8)==self.apis[name] for name,cell in DS.BINDINGS.items())
  self.constructed()
  assert self.rd(n.base+0x17a4220,4)==self.published_epoch and self.wakes==1
  assert [self.decode(self.rd(self.exit_table+off,8)) for off in (0,8,16)]==[self.exit_storage,self.exit_storage+8,self.exit_storage+256]
  assert self.decode(self.rd(self.exit_storage,8))==n.base+0xf7b120 and all(self.decode(self.rd(self.exit_storage+k*8,8))==0 for k in range(1,32))
  assert self.rd(self.cached,8)==self.inline and bytes(u.mem_read(self.clear_at,self.clear_bytes))==bytes(self.clear_bytes)
 def dt_entry(self,site,sp,ret):
  self.dt_layout();n=self.n;u=self.u
  assert site==0x5b8268 and sp==u.reg_read(UC_ARM64_REG_SP) and ret==n.base+0x5b826c and sp%16==0
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+site and not self.srw_held and not self.dt_leases and not self.dt_apis
  assert self.rd(self.dt_factory_guard,4)==self.rd(self.dt_enum_guard,4)==0
  assert all(bytes(u.mem_read(node,48))==bytes([self.poison])*48 for node in self.dt_nodes)
 def dt_api(self,name,ret,args,ready,held):
  self.dt_layout();n=self.n;k=len(self.dt_apis)
  assert ready and k<4 and name==("AcquireSRWLockExclusive" if k%2==0 else "ReleaseSRWLockExclusive") and held==self.srw_held==(k%2==1)
  assert args==[n.base+0x16a3738] and ret==n.base+(0xce7b08 if k%2==0 else 0xce7b80)
  assert self.dt_frames and self.dt_frames[-1]["kind"]=="guard"
 def dt_allocator(self,site,ret,args,pointer,ready):
  self.dt_layout();n=self.n;k=len(self.dt_leases)
  assert ready and k<2 and site==0xcae740 and ret==n.base+(0x5be69c if k==0 else 0x5be6d0) and args==[48] and pointer==self.dt_nodes[k]
  assert not self.srw_held and len(self.dt_apis)==2 and self.dt_guards_returned==1 and self.rd(self.dt_factory_guard,4)==0xffffffff
  assert pointer%16==0 and bytes(self.u.mem_read(pointer,48))==bytes([self.poison])*48
  assert self.dt_leases==[(a,48) for a in self.dt_nodes[:k]]
  existing=self.leases+[(self.exit_storage,256)]+self.dt_leases
  assert all(pointer+48<=a or a+width<=pointer for a,width in existing)
 def dt_patch(self,a,data):
  n=self.n
  if any(node<=a and a+len(data)<=node+48 for node in self.dt_nodes):
   site=self.u.reg_read(UC_ARM64_REG_PC)-n.base;key=(site,a,len(data));assert self.dt_fields.get(key)==int.from_bytes(data,"little")
   assert any(node<=a and a+len(data)<=node+width for node,width in self.dt_leases)
   assert key not in self.field_order;self.field_order.append(key);self.field_stores+=1
   region=next(k for k in self.before if k[0]<=a and a+len(data)<=k[1]+1)
   if region not in self.models:self.models[region]=bytearray(self.before[region])
   self.models[region][a-region[0]:a-region[0]+len(data)]=data;return
  self.patch_stack(a,data)
 def dt_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending
  if self.dt_frames and pc==self.dt_frames[-1]["ret"]:
   f=self.dt_frames.pop();assert all(u.reg_read(k)==v for k,v in f["saved"].items())
   if f["kind"]=="guard":
    assert self.rd(f["guard"],4)==0xffffffff and not self.srw_held;self.dt_guards_returned+=1
   elif f["kind"]=="probe":
    assert u.reg_read(UC_ARM64_REG_X15)==370;self.dt_probe_returned+=1
   else:
    assert u.reg_read(UC_ARM64_REG_X0)==self.dt_receiver and bytes(u.mem_read(self.dt_receiver,1040))==bytes(1040);self.dt_clear_returned+=1
  if r==0x5f94a0:
   assert self.dt_guards_returned==2 and self.dt_probe_returned==self.dt_clear_returned==1 and len(self.dt_apis)==4 and not self.dt_frames
   assert u.reg_read(UC_ARM64_REG_X0)==n.base+0xf7b5e0 and not self.srw_held
   self.dt_stopped=True;u.emu_stop();return
  if r==0xcae740:
   ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0)];pointer=self.dt_nodes[len(self.dt_leases)]
   owned=(r,ret,args,pointer,self.dt_alloc_ready);self.dt_allocator(*owned)
   bad=[(r+4,ret,args,pointer,True),(r,ret+4,args,pointer,True),(r,ret,[49],pointer,True),(r,ret,args+[0],pointer,True),(r,ret,args,pointer+16,True),(r,ret,args,pointer,False)]
   self.reject(self.dt_allocator,bad);old=self.dt_alloc_ready;self.dt_alloc_ready=False
   try:self.reject(self.dt_allocator,[owned])
   finally:self.dt_alloc_ready=old
   old=bytes(u.mem_read(pointer,1));u.mem_write(pointer,bytes([self.poison^1]))
   try:self.reject(self.dt_allocator,[owned])
   finally:u.mem_write(pointer,old)
   self.reject(self.dt_allocator,[(r,ret,args,self.array_storage,True)])
   self.dt_leases.append((pointer,48));u.reg_write(UC_ARM64_REG_X0,pointer);u.reg_write(UC_ARM64_REG_PC,ret);return
  if pc in self.reverse:
   name=self.reverse[pc];ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0)];owned=(name,ret,args,self.dt_srw_ready,self.srw_held);self.dt_api(*owned)
   self.reject(self.dt_api,[(name,ret+4,args,True,self.srw_held),(name,ret,args+[0],True,self.srw_held),(name,ret,[args[0]+8],True,self.srw_held),(name,ret,args,False,self.srw_held),(name,ret,args,True,not self.srw_held)])
   old=self.dt_srw_ready;self.dt_srw_ready=False
   try:self.reject(self.dt_api,[owned])
   finally:self.dt_srw_ready=old
   self.srw_held=name=="AcquireSRWLockExclusive";self.dt_apis.append(name);u.reg_write(UC_ARM64_REG_X0,self.api_clobber);u.reg_write(UC_ARM64_REG_PC,ret);return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4),("unqualified DT source",hex(r))
  if r==0x5bde08:
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0x5b826c;self.dt_factory_sp=u.reg_read(UC_ARM64_REG_SP);self.dt_receiver=self.dt_factory_sp-1144
  if r==0x5f8dc0:
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0x5bea00 and u.reg_read(UC_ARM64_REG_X0)==self.dt_receiver
   self.dt_enum_sp=u.reg_read(UC_ARM64_REG_SP)
  if r==0xce7ad8:
   guard=u.reg_read(UC_ARM64_REG_X0);ret=u.reg_read(UC_ARM64_REG_LR)
   assert (guard,ret) in ((self.dt_factory_guard,n.base+0x5be680),(self.dt_enum_guard,n.base+0x5f9464)) and self.rd(guard,4)==0 and not self.srw_held
   self.dt_frames.append({"kind":"guard","guard":guard,"ret":ret,"saved":{k:u.reg_read(k) for k in NONVOL}})
  if r==0x1440:
   assert self.dt_enum_sp and u.reg_read(UC_ARM64_REG_SP)==self.dt_enum_sp-112 and u.reg_read(UC_ARM64_REG_X15)==370 and u.reg_read(UC_ARM64_REG_LR)==n.base+0x5f8dec
   assert u.reg_read(UC_ARM64_REG_SP)-5920>=n.stack
   self.dt_frames.append({"kind":"probe","ret":n.base+0x5f8dec,"saved":{k:u.reg_read(k) for k in NONVOL}})
  if r==0xf5e600:
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0x5be9fc and [u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2)]==[self.dt_receiver,0,1040]
   assert len(self.dt_leases)==2 and not self.srw_held
   self.dt_frames.append({"kind":"clear","ret":n.base+0x5be9fc,"saved":{k:u.reg_read(k) for k in NONVOL}})
  self.dt_trace.append(r);i=INS[r]
  if 0xf5e600<=r<=0xf5e7ab:self.dt_clear_visits+=1
  if i.mnemonic.startswith(("str","stp","stnp","st1","stur")):
   memidx=next(k for k,o in enumerate(i.operands) if o.type==capstone.arm64.ARM64_OP_MEM);memory=i.operands[memidx];assert not memory.mem.index
   at=DR.reg(u,C.reg_name(memory.mem.base))+memory.mem.disp
   ops=list(i.operands[:memidx]) if i.mnemonic=="st1" else i.operands[:2] if i.mnemonic in ("stp","stnp") else i.operands[:1]
   for k,o in enumerate(ops):
    name=C.reg_name(o.reg)
    if i.mnemonic=="st1":assert name.startswith("v") and o.vas in (capstone.arm64.ARM64_VAS_16B,capstone.arm64.ARM64_VAS_8B);name="q"+name[1:]
    width=16 if name.startswith("q") else 8 if name.startswith(("x","d")) or name in ("fp","lr") else 2 if name.startswith("h") else 1 if name.startswith("b") else 4
    if i.mnemonic=="st1":width=16 if o.vas==capstone.arm64.ARM64_VAS_16B else 8
    elif i.mnemonic.endswith("h"):width=2
    elif i.mnemonic.endswith("b"):width=1
    data=(DR.reg(u,name)&((1<<(width*8))-1)).to_bytes(width,"little")
    for off in range(0,width,8):
     addr=at+k*width+off;chunk=data[off:off+8]
     if 0xf5e600<=r<=0xf5e7ab:assert self.dt_receiver<=addr and addr+len(chunk)<=self.dt_receiver+1040 and chunk==bytes(len(chunk));self.dt_clear_stores+=1
     self.dt_patch(addr,chunk);self.pending[addr,len(chunk)]=int.from_bytes(chunk,"little")
 def dt_read(self,u,access,at,size,value,_):
  if (at,size) in ((self.dt_factory_guard,4),(self.dt_enum_guard,4),(self.teb+16,8)):return
  if (at,size)==(self.n.base+0xf5e644,1):
   assert bytes(u.mem_read(at,size))==PE.get_data(at-self.n.base,size);self.dt_literal_reads.append((hex(at-self.n.base),size));return
  self.read(u,access,at,size,value,_)
 def run(self):
  prior=super().run();n=self.n;u=self.u;self.dt_start_negatives=self.negatives;self.dt_start_stores=self.stores;self.dt_start_fields=self.field_stores
  self.fields.update(self.dt_fields);args=(0x5b8268,u.reg_read(UC_ARM64_REG_SP),n.base+0x5b826c);self.dt_entry(*args)
  self.reject(self.dt_entry,[(args[0]+4,args[1],args[2]),(args[0],args[1]+16,args[2]),(args[0],args[1],args[2]+4)])
  for flag in ("dt_ready","dt_srw_ready","dt_alloc_ready","held","inner_held"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.dt_entry,[args])
   finally:setattr(self,flag,old)
  for at,value,width in ((self.dt_factory_guard,1,4),(self.dt_enum_guard,1,4),(self.block+16,0x80000042,4),(self.teb+16,0,8),(self.dt_nodes[0],0,1),(self.dt_nodes[1],0,1),(self.cached,0,8),(self.exit_table+8,self.encode(self.exit_storage),8),(self.teb+8,n.stack+65520,8)):
   old=bytes(u.mem_read(at,width));self.wr(at,value,width)
   try:self.reject(self.dt_entry,[args])
   finally:u.mem_write(at,old)
  hooks=[u.hook_add(UC_HOOK_CODE,self.dt_code),u.hook_add(UC_HOOK_MEM_WRITE,self.write),u.hook_add(UC_HOOK_MEM_READ,self.dt_read)]
  try:u.emu_start(n.base+0x5b8268,n.end,count=4000)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.dt_stopped and not self.pending and self.held and self.inner_held and not self.srw_held and not self.crt_held
  self.dt_layout();self.constructed()
  assert self.dt_leases==[(x,48) for x in self.dt_nodes]
  for k,node in enumerate(self.dt_nodes):
   assert self.rd(n.base+(0x1b302a0 if k==0 else 0x1b302c0),8)==node
   assert all(self.rd(node+off,8)==node for off in (0,8,16)) and self.rd(node+24,2)==257 and bytes(u.mem_read(node+26,22))==bytes(22)
  assert all(self.rd(n.base+int(x["field_RVA"],16),x["width"])==0 for x in ZERO_FIELDS)
  assert self.rd(self.dt_factory_guard,4)==self.rd(self.dt_enum_guard,4)==0xffffffff
  assert self.rd(n.base+0x18a296c,4)==0 and bytes(u.mem_read(self.dt_static,56))==bytes(56)
  assert set(self.field_order)==set(self.fields) and self.field_stores==352
  after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"combined DS/DT memory mismatch"
  added={"original_instruction_visits":len(self.dt_trace),"factory_clear_instruction_visits":self.dt_clear_visits,"factory_clear_store_chunks":self.dt_clear_stores,"exact_source_store_chunks":self.stores-self.dt_start_stores,"nonstack_field_store_chunks":self.field_stores-self.dt_start_fields,"rejected_owned_requests":self.negatives-self.dt_start_negatives,"guard_returns_ABI_exact":self.dt_guards_returned,"probe_returns_ABI_exact":self.dt_probe_returned,"clear_returns_ABI_exact":self.dt_clear_returned,"owned_OS_API_calls":len(self.dt_apis),"owned_allocation_calls":len(self.dt_leases),"owned_allocation_bytes":96,"clear_literal_data_reads":self.dt_literal_reads,"stop_before_RVA":"0x5f94a0","next_callback_RVA":"0xf7b5e0","factory_and_enumeration_guards_in_progress":True,"outer_and_nested_registry_locks_held":True,"whole_entry_to_frontier_memory_and_permissions_exact":True,"ancestor_live_allocations_redzones_TLS_and_container_retained":True}
  return {"DS":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 report={"experiment":"E011DT","status":"PASS_BOUNDED_ACTUAL_FACTORY_ENUMERATION_IN_COLD_HELPER","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,"clear_literal_window_authority":DS.LITERAL_AUTHORITY,"added_clear_literal_read_RVA":"0xf5e644","added_clear_literal_read_bytes":1,"factory_zero_field_plan_sha256":"0f62dedc35657a133d2f1e4e9b5736fde52d69c78bfc6d0800e9498df3e93389","factory_nodes_are_distinct_from_ancestor_allocations":True,"actual_published_TLS_epoch_retained":True,"already_committed_stack_bounds_are_owned_model":True,"source_result_fixture_used":False,"details":rows,"next_experiment":"E011DU","native_rear_runtime_allowed":False,"full_factory_or_first_helper_return_qualified":False,"full_descriptor_registry_publication_qualified":False,"callback_registration_with_existing_encoded_table_qualified":False,"native_OS_CRT_allocator_construction_and_failure_paths_qualified":False,"stack_growth_guard_page_OS_qualified":False,"cold_global_epoch":"0x80000040","actual_published_thread_epoch":"0x80000041","new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False}
 report["added_totals"]={k:sum(r["added"][k] for r in rows) for k in ("original_instruction_visits","factory_clear_instruction_visits","factory_clear_store_chunks","exact_source_store_chunks","nonstack_field_store_chunks","rejected_owned_requests","guard_returns_ABI_exact","probe_returns_ABI_exact","clear_returns_ABI_exact","owned_OS_API_calls","owned_allocation_calls","owned_allocation_bytes")}
 report["inherited_DS_totals"]={k:sum(r["DS"][k] for r in rows) for k in ("original_instruction_visits","invalid_owned_dependency_requests_rejected","stack_store_chunks","nonstack_field_store_chunks","large_clear_store_chunks")}
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
