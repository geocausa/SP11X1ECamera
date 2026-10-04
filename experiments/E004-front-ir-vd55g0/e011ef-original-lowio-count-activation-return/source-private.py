#!/usr/bin/env python3
"""E011EF: original lowIO cold count transition, first-record activation, and initializer return."""
from pathlib import Path
import hashlib,importlib.util,itertools,json
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *

R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011ee-original-isolated-lowio-block-publication/source-private.py"
P_SHA="e5d9306154333e61fa423c4406ec328ee722ae3977256be1cc9d712e2851f671"
assert hashlib.sha256(P.read_bytes()).hexdigest()==P_SHA
s=importlib.util.spec_from_file_location("ef_actual_ee_parent",P);EE=importlib.util.module_from_spec(s);s.loader.exec_module(EE)
PE=EE.PE;M=EE.M;C=EE.C;NONVOL=EE.NONVOL;INS=dict(EE.INS);PINS=dict(EE.PINS)

EXTRA_PINS={
 "0xcc07b0":{"body_bytes":40,"ranges":[["0xcc07b0","0xcc07d7"]],"sha256":"be7159a0f0c442885d5f7a5e3789c97b5890579c91d607448b651d13f4e2d17c"},
 "0xcb7398":{"body_bytes":28,"ranges":[["0xcb7398","0xcb73b3"]],"sha256":"ba0fb2d4a1e1a1d1effa82370b5d86970cbf56048020dfd66c1702bb8237af60"}}
for entry,pin in EXTRA_PINS.items():
 body=b"".join(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in pin["ranges"])
 assert len(body)==pin["body_bytes"] and hashlib.sha256(body).hexdigest()==pin["sha256"]
 for lo,hi in pin["ranges"]:
  for at in range(int(lo,16),int(hi,16)+1,4):
   i=list(C.disasm(PE.get_data(at,4),at));assert len(i)==1;INS[at]=i[0]
 PINS[entry]=pin

COUNT_AUTH=[{"RVA":"0x16a2e90","bytes":4,"section_writable":True,"virtual_zero_fill":True,"file_backed":False,
 "accepted_owned_initial_value":0,"native_runtime_selection_qualified":False}]
for t in COUNT_AUTH:
 at=int(t["RVA"],16);sec=next(z for z in PE.sections if z.VirtualAddress<=at and at+t["bytes"]<=z.VirtualAddress+z.Misc_VirtualSize)
 assert sec.Characteristics&0x80000000 and at-sec.VirtualAddress>=sec.SizeOfRawData

PROVIDER_AUTH={"count_read_RVA":"0xcc0948","count_write_RVA":"0xcc0950","initial_count":0,"count_increment":64,"final_count":64,
 "record_lock_wrapper_RVA":"0xcc07b0","record_lock_return_RVA":"0xcc095c","record_index":0,"record_lock_resource_offset":0,
 "enter_import_cell_RVA":"0xf7e0b8","record_lock_owned_model_held_after_return":True,
 "global_unlock_wrapper_RVA":"0xcb7398","global_unlock_return_RVA":"0xcc0978","global_lock_index":7,
 "global_lock_resource_RVA":"0x16a2fd8","leave_import_cell_RVA":"0xf7e0c0","global_lock_owned_model_held_after_return":False,
 "OS_void_return_is_owned_clobber_model":True,"native_CRT_resource_initialization_qualified":False}

READS=[(0xcc0948,0x16a2e90,4,"count"),(0xcc07c0,0x16a2a90,8,"block"),(0xcc07d0,0xf7e0b8,8,"enter"),
 (0xcc0960,0x16a2a90,8,"block"),(0xcb73ac,0xf7e0c0,8,"leave")]
WRITES=[(0xcc0950,0x16a2e90,4,"image",64),(0xcc0968,56,1,"block",1)]
OUT=Path(__file__).resolve().parent

class Bootstrap(EE.Bootstrap):
 def __init__(self,*args):
  super().__init__(*args)
  self.ef_ready=self.ef_count_ready=self.ef_enter_ready=self.ef_leave_ready=True
  self.ef_record_lock_held=False;self.ef_reads=[];self.ef_writes=[];self.ef_trace=[];self.ef_entries=[];self.ef_api_calls=[];self.ef_returned=False
 def logical(self):
  return super().logical()+(getattr(self,"ef_ready",False),getattr(self,"ef_count_ready",False),getattr(self,"ef_enter_ready",False),
   getattr(self,"ef_leave_ready",False),getattr(self,"ef_record_lock_held",False),tuple(getattr(self,"ef_reads",[])),
   tuple(getattr(self,"ef_writes",[])),tuple(getattr(self,"ef_entries",[])),tuple(getattr(self,"ef_api_calls",[])),getattr(self,"ef_returned",False))
 def ef_layout(self):
  assert self.ef_ready and self.ef_count_ready and self.ef_enter_ready and self.ef_leave_ready
  self.ee_layout();n=self.n
  assert self.rd(n.base+0xf7e0b8,8)==self.apis["EnterCriticalSection"] and self.rd(n.base+0xf7e0c0,8)==self.apis["LeaveCriticalSection"]
  assert self.reverse[self.apis["EnterCriticalSection"]]=="EnterCriticalSection" and self.reverse[self.apis["LeaveCriticalSection"]]=="LeaveCriticalSection"
  assert self.rd(n.base+0x16a2a90,8)==self.ee_block and self.ee_resources==[self.ee_block+k*72 for k in range(64)]
 def ef_entry(self,site,sp,count,ready):
  self.ef_layout();assert ready and site==0xcc0948 and self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+site
  assert sp==self.u.reg_read(UC_ARM64_REG_SP)==self.ee_entry_sp-96 and count==self.rd(self.n.base+0x16a2e90,4)==0
  assert self.ee_lock_held and not self.ef_record_lock_held and not self.ef_reads and not self.ef_writes and not self.ef_entries and not self.ef_api_calls and not self.ef_trace
 def ef_read_contract(self,site,at,width,value,ready):
  self.ef_layout();assert ready and len(self.ef_reads)<len(READS)
  src,off,size,kind=READS[len(self.ef_reads)];addr=self.n.base+off
  wanted=0 if kind=="count" else self.ee_block if kind=="block" else self.apis["EnterCriticalSection"] if kind=="enter" else self.apis["LeaveCriticalSection"]
  assert (site,at,width,value)==(src,addr,size,wanted) and value==self.rd(at,width)
  if kind=="count":assert self.ee_lock_held and not self.ef_record_lock_held and not self.ef_writes
  elif kind=="enter":assert self.ee_lock_held and not self.ef_record_lock_held
  elif kind=="leave":assert self.ee_lock_held and self.ef_record_lock_held
 def ef_write_contract(self,site,at,width,value,ready):
  self.ef_layout();assert ready and len(self.ef_writes)<len(WRITES)
  src,off,size,kind,wanted=WRITES[len(self.ef_writes)];addr=self.ee_block+off if kind=="block" else self.n.base+off
  assert (site,at,width,value)==(src,addr,size,wanted)
  if kind=="image":assert self.rd(at,width)==0 and len(self.ef_reads)==1 and not self.ef_record_lock_held
  else:assert self.rd(at,width)==0 and len(self.ef_reads)==4 and self.ef_record_lock_held and self.rd(self.n.base+0x16a2e90,4)==64
 def ef_wrapper(self,site,ret,sp,arg,ready):
  self.ef_layout();assert ready;k=len(self.ef_entries)
  if k==0:
   assert (site,ret,sp,arg)==(0xcc07b0,self.n.base+0xcc095c,self.ee_entry_sp-96,0)
   assert self.rd(self.n.base+0x16a2e90,4)==64 and self.ee_lock_held and not self.ef_record_lock_held and len(self.ef_reads)==1 and len(self.ef_writes)==1
  else:
   assert k==1 and (site,ret,sp,arg)==(0xcb7398,self.n.base+0xcc0978,self.ee_entry_sp-96,7)
   assert self.ee_lock_held and self.ef_record_lock_held and self.rd(self.ee_block+56,1)==1 and len(self.ef_reads)==4 and len(self.ef_writes)==2
  assert ret==self.u.reg_read(UC_ARM64_REG_LR) and sp==self.u.reg_read(UC_ARM64_REG_SP) and arg==(self.u.reg_read(UC_ARM64_REG_X0)&0xffffffff)
 def ef_api(self,pc,ret,sp,arg,ready):
  self.ef_layout();assert ready;k=len(self.ef_api_calls)
  if k==0:
   assert pc==self.apis["EnterCriticalSection"] and ret==self.n.base+0xcc095c and sp==self.ee_entry_sp-96 and arg==self.ee_block
   assert self.ee_lock_held and not self.ef_record_lock_held and len(self.ef_entries)==1 and len(self.ef_reads)==3 and len(self.ef_writes)==1
  else:
   assert k==1 and pc==self.apis["LeaveCriticalSection"] and ret==self.n.base+0xcc0978 and sp==self.ee_entry_sp-96 and arg==self.n.base+0x16a2fd8
   assert self.ee_lock_held and self.ef_record_lock_held and len(self.ef_entries)==2 and len(self.ef_reads)==5 and len(self.ef_writes)==2
  assert pc==self.u.reg_read(UC_ARM64_REG_PC) and ret==self.u.reg_read(UC_ARM64_REG_LR) and sp==self.u.reg_read(UC_ARM64_REG_SP) and arg==self.u.reg_read(UC_ARM64_REG_X0)
 def ef_read(self,u,a,at,width,value,_):
  if self.n.stack<=at and at+width<=self.n.stack+65536:return
  site=u.reg_read(UC_ARM64_REG_PC)-self.n.base;data=self.rd(at,width);owned=(site,at,width,data,True);self.ef_read_contract(*owned)
  self.reject(self.ef_read_contract,[(site+4,at,width,data,True),(site,at+1,width,data,True),(site,at,width+1,data,True),(site,at,width,data^1,True),(site,at,width,data,False)])
  self.ef_reads.append((site,at,width))
 def ef_write(self,u,a,at,width,value,_):
  if self.n.stack<=at and at+width<=self.n.stack+65536:return
  site=u.reg_read(UC_ARM64_REG_PC)-self.n.base;value&=(1<<(width*8))-1;owned=(site,at,width,value,True);self.ef_write_contract(*owned)
  self.reject(self.ef_write_contract,[(site+4,at,width,value,True),(site,at+1,width,value,True),(site,at,width+1,value,True),(site,at,width,value^1,True),(site,at,width,value,False)])
  data=value.to_bytes(width,"little");self.ed_model(at,data)
  if self.ee_block<=at and at+width<=self.ee_block+4608:self.ee_block_expected[at-self.ee_block:at-self.ee_block+width]=data
  self.ef_writes.append((site,at,width))
 def ef_code(self,u,pc,z,_):
  n=self.n
  if pc in (self.apis["EnterCriticalSection"],self.apis["LeaveCriticalSection"]):
   arg=u.reg_read(UC_ARM64_REG_X0);owned=(pc,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),arg,True);self.ef_api(*owned)
   self.reject(self.ef_api,[(pc+0x20,*owned[1:]),(pc,owned[1]+4,*owned[2:]),(pc,owned[1],owned[2]+16,arg,True),(pc,owned[1],owned[2],arg+8,True),(*owned[:4],False)])
   saved={k:u.reg_read(k) for k in NONVOL}
   if pc==self.apis["EnterCriticalSection"]:self.ef_record_lock_held=True
   else:self.ee_lock_held=False
   self.ef_api_calls.append(self.reverse[pc]);u.reg_write(UC_ARM64_REG_X0,self.api_clobber);u.reg_write(UC_ARM64_REG_PC,owned[1])
   assert all(u.reg_read(k)==v for k,v in saved.items());return
  r=pc-n.base;assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4)
  assert (0xcc0948<=r<=0xcc0994) or (0xcc07b0<=r<=0xcc07d4) or (0xcb7398<=r<=0xcb73b0)
  if r in (0xcc07b0,0xcb7398):
   arg=u.reg_read(UC_ARM64_REG_X0)&0xffffffff;owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),arg,True);self.ef_wrapper(*owned)
   self.reject(self.ef_wrapper,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,arg,True),(r,owned[1],owned[2],arg+1,True),(*owned[:4],False)])
   self.ef_entries.append(r)
  self.ef_trace.append(r)
 def run(self):
  ee=super().run();u=self.u;n=self.n;owned=(0xcc0948,u.reg_read(UC_ARM64_REG_SP),self.rd(n.base+0x16a2e90,4),True);self.ef_entry(*owned)
  self.reject(self.ef_entry,[(owned[0]+4,*owned[1:]),(owned[0],owned[1]+16,*owned[2:]),(owned[0],owned[1],owned[2]^1,True),(*owned[:3],False)])
  for flag in ("ef_ready","ef_count_ready","ef_enter_ready","ef_leave_ready"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.ef_entry,[owned])
   finally:setattr(self,flag,old)
  for at,width in ((n.base+0x16a2e90,4),(n.base+0xf7e0b8,8),(n.base+0xf7e0c0,8)):
   old=bytes(u.mem_read(at,width));self.wr(at,self.rd(at,width)^1,width)
   try:self.reject(self.ef_entry,[owned])
   finally:u.mem_write(at,old)
  before=self.snapshot();neg=self.negatives;hooks=[u.hook_add(UC_HOOK_CODE,self.ef_code),u.hook_add(UC_HOOK_MEM_READ,self.ef_read),u.hook_add(UC_HOOK_MEM_WRITE,self.ef_write)]
  try:u.emu_start(n.base+0xcc0948,n.end,count=1000)
  finally:
   for h in hooks:u.hook_del(h)
  self.ef_returned=True
  assert u.reg_read(UC_ARM64_REG_PC)==n.end and u.reg_read(UC_ARM64_REG_SP)==self.ee_entry_sp and u.reg_read(UC_ARM64_REG_X0)==0
  assert all(u.reg_read(k)==v for k,v in self.ee_saved.items())
  assert len(self.ef_trace)==37 and len(self.ef_reads)==5 and len(self.ef_writes)==2 and self.ef_entries==[0xcc07b0,0xcb7398]
  assert self.ef_api_calls==["EnterCriticalSection","LeaveCriticalSection"] and self.ef_record_lock_held and not self.ee_lock_held
  assert self.rd(n.base+0x16a2e90,4)==64 and self.rd(n.base+0x16a2a90,8)==self.ee_block
  record=bytearray(72);record[40:48]=bytes([255])*8;record[56:60]=(0x0a0a0000).to_bytes(4,"little");record[60]=10
  expected=bytearray(bytes(record)*64);expected[56]=1;assert bytes(u.mem_read(self.ee_block,4608))==bytes(expected)
  after=self.snapshot();assert after.keys()==before.keys()
  for key,old in before.items():assert after[key]==(bytes(self.models[key]) if key in self.models else old),"E011EF continuation memory mismatch"
  return {"EE":ee,"added":{"original_instruction_visits":len(self.ef_trace),"exact_source_store_chunks":len(self.ef_writes),
   "rejected_owned_requests":self.negatives-neg,"exact_dependency_reads":len(self.ef_reads),"exact_original_wrapper_entries":len(self.ef_entries),
   "owned_OS_API_calls":len(self.ef_api_calls),"original_lowIO_initializer_ABI_return_exact":1,"count_initial":0,"count_final":64,
   "count_increment":64,"first_record_active_byte":1,"first_record_lock_owned_model_held":True,"lowIO_global_lock_owned_model_released":True,
   "isolated_lowIO_memory_and_permissions_exact":True,"redzones_exact":True,"original_lowIO_initializer_return_qualified":True,
   "all_initializer_and_camera_states_join_qualified":False,"actual_loader_CRT_startup_caller_qualified":False,
   "native_CRT_resource_initialization_qualified":False,"native_runtime_count_selection_qualified":False}}

class Case(EE.ED.EC.Case):
 def __init__(self,*args):super().__init__(*args);self.ef_args=args
 def run(self):
  ec=super().run();camera_before=self.snapshot();camera_pc=self.u.reg_read(UC_ARM64_REG_PC)
  stream=EE.ED.Bootstrap(*self.ef_args);ed_added=stream.run()
  assert stream.u is not self.u and self.snapshot()==camera_before and self.u.reg_read(UC_ARM64_REG_PC)==camera_pc==self.n.base+0xcc6120
  assert self.rd(self.n.base+0x16a2a58,8)==0 and self.ec_lock_held
  ed_added.update(camera_caller_memory_permissions_and_frontier_unchanged=True,initializer_isolated_from_camera_parent=True)
  prior={"EC":ec,"added":ed_added};stream_before=stream.snapshot();stream_pc=stream.u.reg_read(UC_ARM64_REG_PC);stream_logical=stream.logical()
  lowio=Bootstrap(*self.ef_args);continued=lowio.run();ee_added=continued["EE"];added=continued["added"]
  assert self.snapshot()==camera_before and self.u.reg_read(UC_ARM64_REG_PC)==camera_pc
  assert stream.snapshot()==stream_before and stream.u.reg_read(UC_ARM64_REG_PC)==stream_pc==stream.n.base+0xcb3338 and stream.logical()==stream_logical
  ee_added.update(camera_caller_memory_permissions_and_frontier_unchanged=True,stream_initializer_memory_permissions_and_frontier_unchanged=True,lowIO_initializer_isolated_from_other_contexts=True)
  return {"EE":{"ED":prior,"added":ee_added},"added":added}

def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 rows=json.loads(json.dumps(rows));ancestor=json.loads((P.parent/"SOURCE-SAFE.json").read_text());assert [row["EE"] for row in rows]==ancestor["details"]
 report={"experiment":"E011EF","status":"PASS_BOUNDED_ORIGINAL_LOWIO_COUNT_ACTIVATION_RETURN","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
  "lowIO_count_owned_cold_initial_value_authority":COUNT_AUTH,"lowIO_continuation_owned_provider_authority":PROVIDER_AUTH,
  "lowIO_owned_cold_initial_value_authority":ancestor["lowIO_owned_cold_initial_value_authority"],"lowIO_owned_provider_authority":ancestor["lowIO_owned_provider_authority"],
  "initializer_owned_cold_initial_value_authority":ancestor["initializer_owned_cold_initial_value_authority"],"initializer_owned_provider_authority":ancestor["initializer_owned_provider_authority"],
  "runtime_initial_value_model_authority":ancestor["runtime_initial_value_model_authority"],"details":rows,
  "original_lowIO_block_construction_and_publication_qualified":True,"original_lowIO_block_constructor_return_qualified":True,
  "original_lowIO_count_transition_qualified":True,"original_first_lowIO_record_lock_and_activation_qualified":True,"original_lowIO_initializer_return_qualified":True,
  "lowIO_initializer_isolated_from_other_contexts":True,"camera_caller_memory_permissions_and_frontier_unchanged":True,
  "stream_initializer_memory_permissions_and_frontier_unchanged":True,"original_stream_initializer_return_qualified":False,
  "all_initializer_and_camera_states_join_qualified":False,"stream_initializer_and_camera_state_join_qualified":False,
  "actual_loader_CRT_startup_caller_qualified":False,"native_allocator_implementation_qualified":False,"source_result_fixture_used":False,
  "native_rear_runtime_allowed":False,"native_CRT_resource_initialization_qualified":False,"native_runtime_scalar_and_pointer_selection_qualified":False,
  "native_runtime_count_selection_qualified":False,"pointed_standard_stream_contents_qualified":False,"stream_runtime_pointer_read_qualified":False,
  "native_handles_or_file_contents_qualified":False,"file_open_or_contents_qualified":False,"full_outer_callee_return_qualified":False,
  "full_factory_or_first_helper_return_qualified":False,"new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,
  "production_code_changed":False,"private_raw_material_exported":False,"next_experiment":"E011EG"}
 keys=("original_instruction_visits","exact_source_store_chunks","rejected_owned_requests","exact_dependency_reads","exact_original_wrapper_entries","owned_OS_API_calls","original_lowIO_initializer_ABI_return_exact")
 report["added_totals"]={k:sum(row["added"][k] for row in rows) for k in keys};report["inherited_EE_totals"]=ancestor["added_totals"];report["inherited_ED_totals"]=ancestor["inherited_ED_totals"]
 for k in ("EC","EB","EA","DZ","DY","DX","DW","DV","DU","DT","DS"):report["inherited_"+k+"_totals"]=ancestor["inherited_"+k+"_totals"]
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
