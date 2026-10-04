#!/usr/bin/env python3
"""Original second callback append and enumeration guard publication in the retained parent."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011dt-original-actual-factory-enumeration/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="a5af6722f3f21e316e07f6073d2051dce13c9dccd8cb452cce72203b56d60b7f"
s=importlib.util.spec_from_file_location("du_actual_dt_parent",P);DT=importlib.util.module_from_spec(s);s.loader.exec_module(DT)
DR=DT.DR;DS=DT.DS;PE=DT.PE;M=DT.M;C=DT.C;INS=DT.INS;PINS=DT.PINS;NONVOL=DT.NONVOL
OUT=Path(__file__).resolve().parent
class Case(DT.Case):
 def __init__(self,*args):
  super().__init__(*args);n=self.n
  self.du_ready=True;self.du_trace=[];self.du_apis=[];self.du_frames=[];self.du_frame_returns=0;self.du_frame_entries=[]
  self.du_order=[];self.du_stopped=False;self.du_wakes=0
  self.du_effects={(0xcb0140,self.exit_storage+8,8):self.encode(n.base+0xf7b5e0),
   (0xcb015c,self.exit_table,8):self.encode(self.exit_storage),(0xcb0178,self.exit_table+8,8):self.encode(self.exit_storage+16),
   (0xcb0194,self.exit_table+16,8):self.encode(self.exit_storage+256),(0xce7a84,n.base+0x1607b04,4):0x80000042,
   (0xce7a88,self.dt_enum_guard,4):0x80000042,(0xce7aa4,self.block+16,4):0x80000042}
 def logical(self):
  return super().logical()+(getattr(self,"du_ready",False),len(getattr(self,"du_apis",[])),len(getattr(self,"du_frames",[])),
   getattr(self,"du_frame_returns",0),tuple(getattr(self,"du_order",[])),getattr(self,"du_wakes",0))
 def du_layout(self,entries,epoch):
  n=self.n;u=self.u
  assert self.du_ready and self.ready and self.ext_ready and self.inner_ready and self.dt_ready and self.dt_alloc_ready
  assert self.held and self.inner_held and self.exit_allocated and self.exit_ready and self.exit_alloc_ready and self.crt_ready and self.srw_ready and self.dt_srw_ready and self.cv_ready
  assert u.reg_read(UC_ARM64_REG_X18)==self.teb and self.rd(n.base+0x16a3740,4)==self.index
  assert self.rd(self.teb+88,8)==self.array and self.rd(self.array+self.index*8,8)==self.block
  assert self.rd(self.block+16,4)==self.rd(n.base+0x1607b04,4)==epoch
  assert self.rd(n.base+0x17a4220,4)==self.published_epoch==0x80000041
  assert self.rd(self.dt_factory_guard,4)==0xffffffff and self.rd(self.dt_enum_guard,4)==(0xffffffff if epoch==0x80000041 else epoch)
  assert self.rd(n.base+0x1607000,8)==self.cookie and all(self.rd(n.base+cell,8)==self.apis[name] for name,cell in DS.BINDINGS.items())
  assert [self.decode(self.rd(self.exit_table+off,8)) for off in (0,8,16)]==[self.exit_storage,self.exit_storage+entries*8,self.exit_storage+256]
  assert self.decode(self.rd(self.exit_storage,8))==n.base+0xf7b120
  assert self.decode(self.rd(self.exit_storage+8,8))==(n.base+0xf7b5e0 if entries==2 else 0)
  assert all(self.decode(self.rd(self.exit_storage+k*8,8))==0 for k in range(entries,32))
  assert self.exit_storage%16==0 and self.leases==self.reservations and self.dt_leases==[(x,48) for x in self.dt_nodes]
  all_leases=self.leases+[(self.exit_storage,256)]+self.dt_leases
  assert all(a+z<=b or b+w<=a for i,(a,z) in enumerate(all_leases) for b,w in all_leases[i+1:])
  self.constructed()
  assert self.rd(self.cached,8)==self.inline and bytes(u.mem_read(self.clear_at,self.clear_bytes))==bytes(self.clear_bytes)
  assert bytes(u.mem_read(self.inline+20,4))==bytes([self.poison])*4 and bytes(u.mem_read(self.dt_static,56))==bytes(56)
  for k,node in enumerate(self.dt_nodes):
   assert self.rd(n.base+(0x1b302a0 if k==0 else 0x1b302c0),8)==node
   assert all(self.rd(node+off,8)==node for off in (0,8,16)) and self.rd(node+24,2)==257 and bytes(u.mem_read(node+26,22))==bytes(22)
  assert all(self.rd(n.base+int(x["field_RVA"],16),x["width"])==0 for x in DT.ZERO_FIELDS)
  assert self.rd(n.base+0x18a296c,4)==0 and self.wakes==1
 def du_entry(self,site,sp,ret,callback,ready):
  n=self.n;u=self.u;self.du_layout(1,0x80000041)
  assert ready and site==0x5f94a0 and u.reg_read(UC_ARM64_REG_PC)==n.base+site and sp==u.reg_read(UC_ARM64_REG_SP) and sp%16==0
  assert ret==n.base+0x5f94a4 and callback==u.reg_read(UC_ARM64_REG_X0)==n.base+0xf7b5e0
  assert not self.crt_held and not self.srw_held and not self.du_apis and not self.du_frames and not self.du_order and not self.du_wakes
  assert self.dt_stopped and self.dt_guards_returned==2 and self.dt_clear_returned==self.dt_probe_returned==1 and not self.dt_frames
 def du_api(self,name,ret,args,ready,held):
  n=self.n;k=len(self.du_apis);assert k<5 and ready
  spec=(("EnterCriticalSection",0xcaffb4,0x16a2f10),("LeaveCriticalSection",0xcaffc8,0x16a2f10),
   ("AcquireSRWLockExclusive",0xce7a74,0x16a3738),("ReleaseSRWLockExclusive",0xce7ab4,0x16a3738),
   ("WakeAllConditionVariable",0xce7ac4,0x16a3730))
  expected,rv,at=spec[k];assert name==expected and ret==n.base+rv and args==[n.base+at]
  self.du_layout(1 if k==0 else 2,0x80000041 if k<3 else 0x80000042)
  assert self.crt_held==(k==1) and self.srw_held==(k==3) and held==(self.crt_held if k<2 else self.srw_held)
  assert self.du_frames and self.du_frames[-1]["entry"]==((0xcb7300,0xcb7398,0xce7a48,0xce7a48,0xce7a48)[k])
  assert len(self.du_order)==(0 if k==0 else 4 if k<3 else 7) and self.du_wakes==0
 def du_patch(self,at,data):
  n=self.n;u=self.u
  if n.stack<=at and at+len(data)<=n.stack+65536:self.patch_stack(at,data);return
  key=(u.reg_read(UC_ARM64_REG_PC)-n.base,at,len(data));assert self.du_effects.get(key)==int.from_bytes(data,"little")
  assert key not in self.du_order and key==list(self.du_effects)[len(self.du_order)]
  if at==self.exit_storage+8:assert self.exit_allocated and self.crt_held and not self.srw_held and len(self.du_apis)==1
  else:assert self.crt_held if len(self.du_order)<4 else self.srw_held
  region=next(k for k in self.before if k[0]<=at and at+len(data)<=k[1]+1)
  if region not in self.models:self.models[region]=bytearray(self.before[region])
  self.models[region][at-region[0]:at-region[0]+len(data)]=data;self.du_order.append(key)
 def du_read(self,u,access,at,size,value,_):
  self.dt_read(u,access,at,size,value,_)
 def du_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending
  if self.du_frames and pc==self.du_frames[-1]["ret"]:
   f=self.du_frames.pop();assert all(u.reg_read(k)==v for k,v in f["saved"].items()),"DU callee ABI not restored"
   if f["result"] is not None:assert u.reg_read(UC_ARM64_REG_X0)==f["result"]
   self.du_frame_returns+=1
  if r==0x5f8e24:
   assert len(self.du_apis)==5 and len(self.du_order)==7 and not self.du_frames and self.du_wakes==1
   assert not self.crt_held and not self.srw_held;self.du_layout(2,0x80000042);self.du_stopped=True;u.emu_stop();return
  assert r not in (0xcae740,0xcc2a50,0xcb99c0),"DU append unexpectedly needs allocator/reallocation"
  if pc in self.reverse:
   name=self.reverse[pc];ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0)]
   held=self.crt_held if len(self.du_apis)<2 else self.srw_held;owned=(name,ret,args,self.du_ready,held);self.du_api(*owned)
   self.reject(self.du_api,[(name,ret+4,args,True,held),(name,ret,args+[0],True,held),(name,ret,[args[0]+8],True,held),(name,ret,args,False,held),(name,ret,args,True,not held)])
   flags=("du_ready","held","inner_held","crt_ready","cv_ready","srw_ready","exit_ready","exit_allocated","dt_srw_ready")
   for flag in flags:
    old=getattr(self,flag);setattr(self,flag,False)
    try:self.reject(self.du_api,[owned])
    finally:setattr(self,flag,old)
   flag="crt_held" if len(self.du_apis)<2 else "srw_held";old=getattr(self,flag);setattr(self,flag,not old)
   try:self.reject(self.du_api,[owned])
   finally:setattr(self,flag,old)
   if name=="EnterCriticalSection":self.crt_held=True
   elif name=="LeaveCriticalSection":self.crt_held=False
   elif name=="AcquireSRWLockExclusive":self.srw_held=True
   elif name=="ReleaseSRWLockExclusive":self.srw_held=False
   else:self.du_wakes+=1
   self.du_apis.append(name);u.reg_write(UC_ARM64_REG_X0,self.api_clobber);u.reg_write(UC_ARM64_REG_PC,ret);return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4),("unqualified DU source",hex(r))
  returns={0xca34a0:(0x5f94a4,0),0xca3450:(0xca34b0,n.base+0xf7b5e0),0xcb0388:(0xca3488,0),0xcaff90:(0xcb03c0,0),
   0xcb7300:(0xcaffb4,None),0xcb0030:(0xcaffbc,0),0xcb7398:(0xcaffc8,None),0xce7a48:(0x5f94ac,None)}
  if r in returns:
   ret,result=returns[r];assert u.reg_read(UC_ARM64_REG_LR)==n.base+ret
   if r in (0xca34a0,0xca3450):assert u.reg_read(UC_ARM64_REG_X0)==n.base+0xf7b5e0
   if r==0xce7a48:assert u.reg_read(UC_ARM64_REG_X0)==self.dt_enum_guard and self.rd(self.dt_enum_guard,4)==0xffffffff and len(self.du_order)==4
   self.du_frames.append({"entry":r,"ret":n.base+ret,"result":result,"saved":{k:u.reg_read(k) for k in NONVOL}});self.du_frame_entries.append(hex(r))
  self.du_trace.append(r);i=INS[r]
  if i.mnemonic.startswith(("str","stp","stnp","st1","stur")):
   mi=next(k for k,o in enumerate(i.operands) if o.type==capstone.arm64.ARM64_OP_MEM);mem=i.operands[mi];assert not mem.mem.index
   at=DR.reg(u,C.reg_name(mem.mem.base))+mem.mem.disp
   ops=list(i.operands[:mi]) if i.mnemonic=="st1" else i.operands[:2] if i.mnemonic in ("stp","stnp") else i.operands[:1]
   for k,o in enumerate(ops):
    name=C.reg_name(o.reg)
    if i.mnemonic=="st1":assert name.startswith("v") and o.vas in (capstone.arm64.ARM64_VAS_16B,capstone.arm64.ARM64_VAS_8B);name="q"+name[1:]
    width=16 if name.startswith("q") else 8 if name.startswith(("x","d")) or name in ("fp","lr") else 2 if name.startswith("h") else 1 if name.startswith("b") else 4
    if i.mnemonic=="st1":width=16 if o.vas==capstone.arm64.ARM64_VAS_16B else 8
    elif i.mnemonic.endswith("h"):width=2
    elif i.mnemonic.endswith("b"):width=1
    data=(DR.reg(u,name)&((1<<(width*8))-1)).to_bytes(width,"little")
    for off in range(0,width,8):
     addr=at+k*width+off;chunk=data[off:off+8];self.du_patch(addr,chunk);self.pending[addr,len(chunk)]=int.from_bytes(chunk,"little")
 def run(self):
  prior=super().run();n=self.n;u=self.u;start_stores=self.stores;start_negatives=self.negatives
  args=(0x5f94a0,u.reg_read(UC_ARM64_REG_SP),n.base+0x5f94a4,n.base+0xf7b5e0,True);self.du_entry(*args)
  bad=[]
  for k in range(4):
   row=list(args);row[k]+=4;bad.append(tuple(row))
  bad.append((*args[:4],False));self.reject(self.du_entry,bad)
  for flag in ("du_ready","held","inner_held","crt_ready","cv_ready","srw_ready","exit_ready","exit_alloc_ready","exit_allocated","dt_ready","dt_alloc_ready","dt_srw_ready"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.du_entry,[args])
   finally:setattr(self,flag,old)
  for at,value,width in ((self.exit_table,self.encode(self.exit_storage+8),8),(self.exit_table+8,self.encode(self.exit_storage+16),8),(self.exit_table+16,self.encode(self.exit_storage+264),8),
   (self.exit_storage,self.encode(n.base+0xf7b5e0),8),(self.exit_storage+8,self.encode(n.base+0xf7b5e0),8),
   (n.base+0x1607000,self.cookie^1,8),(self.block+16,0x80000042,4),(n.base+0x1607b04,0x80000042,4),(n.base+0x17a4220,0x80000042,4),
   (self.dt_enum_guard,0,4),(self.dt_factory_guard,0,4),(self.cached,0,8),(self.dt_nodes[0]+24,0,2),(self.dt_nodes[1],0,8),(self.array+self.index*8,self.block+8,8)):
   old=bytes(u.mem_read(at,width));self.wr(at,value,width)
   try:self.reject(self.du_entry,[args])
   finally:u.mem_write(at,old)
  hooks=[u.hook_add(UC_HOOK_CODE,self.du_code),u.hook_add(UC_HOOK_MEM_WRITE,self.write),u.hook_add(UC_HOOK_MEM_READ,self.du_read)]
  try:u.emu_start(n.base+0x5f94a0,n.end,count=700)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.du_stopped and not self.pending and u.reg_read(UC_ARM64_REG_PC)==n.base+0x5f8e24
  assert len(self.du_apis)==5 and len(self.du_order)==7 and self.du_frame_returns==len(self.du_frame_entries)==8 and not self.du_frames and self.du_wakes==1
  assert self.held and self.inner_held and not self.srw_held and not self.crt_held;self.du_layout(2,0x80000042)
  after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"combined DS/DT/DU memory mismatch"
  added={"original_instruction_visits":len(self.du_trace),"exact_source_store_chunks":self.stores-start_stores,"nonstack_field_store_chunks":len(self.du_order),
   "rejected_owned_requests":self.negatives-start_negatives,"original_registration_publication_returns_ABI_exact":self.du_frame_returns,"owned_OS_API_calls":len(self.du_apis),
   "owned_exit_reallocation_calls":0,"owned_wake_calls":self.du_wakes,"actual_return_RVAs":["0x5f94a4","0x5f94ac"],
   "registration_publication_frame_entries":self.du_frame_entries,"exit_table_used_entries":2,"exit_table_capacity_entries":32,
   "published_enumeration_global_TLS_epoch":"0x80000042","retained_helper_epoch":"0x80000041","factory_guard_in_progress":True,
   "outer_and_nested_registry_locks_held":True,"CRT_and_SRW_released":True,"whole_entry_to_frontier_memory_and_permissions_exact":True,
   "ancestor_live_allocations_redzones_TLS_and_container_retained":True,"stop_before_RVA":"0x5f8e24","next_dependency_RVA":"0x1731598","next_dependency_bytes":4}
  return {"DT":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 report={"experiment":"E011DU","status":"PASS_BOUNDED_ACTUAL_EXISTING_TABLE_REGISTRATION_ENUMERATION_PUBLICATION","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
  "source_result_fixture_used":False,"native_rear_runtime_allowed":False,"full_factory_or_first_helper_return_qualified":False,"full_descriptor_registry_publication_qualified":False,
  "native_OS_CRT_allocator_construction_and_failure_paths_qualified":False,"next_enumeration_dependency_qualified":False,"stack_growth_guard_page_OS_qualified":False,
  "existing_nonempty_encoded_table_is_actual_parent_result":True,"registration_used_existing_capacity_without_allocator":True,"enumeration_epoch_publication_qualified":True,
  "prior_factory_nodes_and_registry_locks_retained":True,"next_experiment":"E011DV","details":rows,"new_camera_starts":0,"new_reboots":0,
  "new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False}
 keys=("original_instruction_visits","exact_source_store_chunks","nonstack_field_store_chunks","rejected_owned_requests","original_registration_publication_returns_ABI_exact","owned_OS_API_calls","owned_exit_reallocation_calls","owned_wake_calls")
 report["added_totals"]={k:sum(r["added"][k] for r in rows) for k in keys}
 report["inherited_DT_totals"]={k:sum(r["DT"]["added"][k] for r in rows) for k in json.loads((P.parent/"SOURCE-SAFE.json").read_text())["added_totals"]}
 report["inherited_DS_totals"]={k:sum(r["DT"]["DS"][k] for r in rows) for k in json.loads((P.parent/"SOURCE-SAFE.json").read_text())["inherited_DS_totals"]}
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
