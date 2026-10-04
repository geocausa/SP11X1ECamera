#!/usr/bin/env python3
"""Original enclosing caller and stream setup; stop before runtime table selection."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011eb-original-complete-constant-consumer-return/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="6633a78e568cc5001f9f328f6026daa01bb6503ccee257638e3f949475e5b8e2"
spec=importlib.util.spec_from_file_location("ec_actual_eb_parent",P);EB=importlib.util.module_from_spec(spec);spec.loader.exec_module(EB)
PE=EB.PE;M=EB.M;C=EB.C;DR=EB.DR;NONVOL=EB.NONVOL;INS=dict(EB.INS);PINS=dict(EB.PINS)
EXTRA_PINS={
"0xced2f0":{"body_bytes":104,"ranges":[["0xced2f0","0xced357"]],"sha256":"2f01c5c987420ed8a66fe9b598884e0769d591d030222e364df1936b0141db53"},
"0xced0d8":{"body_bytes":196,"ranges":[["0xced0d8","0xced19b"]],"sha256":"3e7921b298228ceba63639c8ad5143816fa88e92741b9bf36543dcaaf5f176b2"},
"0xcc6078":{"body_bytes":100,"ranges":[["0xcc6078","0xcc60db"]],"sha256":"7eca050b7b7a4284ed60cdb2a8d067cb2d4ecd964bbd9da560e5af2a15ff0fe8"},
"0xcc6108":{"body_bytes":248,"ranges":[["0xcc6108","0xcc61ff"]],"sha256":"92392516a581bfd36da290b122fe121ec3da6715a050a19cb286dd14d7c573ff"}}
for entry,pin in EXTRA_PINS.items():
 body=b"".join(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in pin["ranges"])
 assert len(body)==pin["body_bytes"] and hashlib.sha256(body).hexdigest()==pin["sha256"]
 for lo,hi in pin["ranges"]:
  for at in range(int(lo,16),int(hi,16)+1,4):
   i=list(C.disasm(PE.get_data(at,4),at));assert len(i)==1;INS[at]=i[0]
 PINS[entry]=pin
MODE_AUTH={"RVA":"0x1363d40","bytes_including_NUL":2,"sha256":"96229c0a1dcb79d7d50913f882e3144961b5616140ded9ab844bd685e08e3a30",
 "file_backed":True,"section_nonwritable":True,"terminator_at_last_byte":True,"original_literal_contents_exported":False}
MODE_RVA=int(MODE_AUTH["RVA"],16);MODE=PE.get_data(MODE_RVA,MODE_AUTH["bytes_including_NUL"])
sec=next(z for z in PE.sections if z.VirtualAddress<=MODE_RVA and MODE_RVA+len(MODE)<=z.VirtualAddress+z.Misc_VirtualSize)
assert not sec.Characteristics&0x80000000 and MODE_RVA-sec.VirtualAddress+len(MODE)<=sec.SizeOfRawData
assert MODE[-1]==0 and all(MODE[:-1]) and hashlib.sha256(MODE).hexdigest()==MODE_AUTH["sha256"]
LOCK_AUTH={"owned_resource_RVA":"0x16a3000","modeled_ready":True,"initial_logical_lock_held":False,
 "inherited_import_cell_RVA":"0xf7e0b8","OS_void_return_is_owned_clobber_model":True,"native_CRT_resource_initialization_qualified":False}
PLANS=[(0xced2f4,-1472,8,"image",0x13f1000),(0xced2f8,-1488,8,"stack",-96),(0xced2f8,-1480,8,"image",0x600454),
 (0xced0dc,-1520,8,"stack",-1448),(0xced0dc,-1512,8,"scalar",0),(0xced0e0,-1504,8,"image",0x1608000),
 (0xced0e4,-1552,8,"stack",-1488),(0xced0e4,-1544,8,"image",0xced330),
 (0xcc607c,-1568,8,"scalar",128),(0xcc6080,-1600,8,"stack",-1552),(0xcc6080,-1592,8,"image",0xced150),(0xcc608c,-1536,8,"scalar",0),
 (0xcc610c,-1632,8,"stack",-1536),(0xcc610c,-1624,8,"stack",-1392),(0xcc6110,-1616,8,"image",MODE_RVA),(0xcc6110,-1608,8,"image",0x135f000),
 (0xcc6114,-1648,8,"stack",-1600),(0xcc6114,-1640,8,"image",0xcc60a0)]
CALLS=[(0xced2f0,0x600454,-1456,[("stack",-1448),("stack",-1392),("image",MODE_RVA)],0,0),
 (0xced0d8,0xced330,-1488,[("stack",-1392),("image",MODE_RVA),("scalar",128)],3,0),
 (0xcc6078,0xced150,-1552,[("stack",-1536)],8,1),(0xcb7300,0xcc6098,-1600,[("scalar",8)],12,1),
 (0xcc6108,0xcc60a0,-1600,[("stack",-1584)],12,2)]
OUT=Path(__file__).resolve().parent
class Case(EB.Case):
 def __init__(self,*args):
  super().__init__(*args)
  self.ec_ready=True;self.ec_data_ready=True;self.ec_lock_ready=True;self.ec_lock_held=False;self.ec_order=[];self.ec_reads=[];self.ec_trace=[]
  self.ec_entries=[];self.ec_frames=[];self.ec_returns=0;self.ec_api_calls=0;self.ec_stopped=False
 def logical(self):
  return super().logical()+(getattr(self,"ec_ready",False),getattr(self,"ec_data_ready",False),getattr(self,"ec_lock_ready",False),getattr(self,"ec_lock_held",False),
   tuple(getattr(self,"ec_order",[])),tuple(getattr(self,"ec_reads",[])),tuple(getattr(self,"ec_entries",[])),getattr(self,"ec_returns",0),getattr(self,"ec_api_calls",0))
 def resolve(self,kind,value):
  return self.n.base+value if kind=="image" else self.dw_entry_sp+value if kind=="stack" else value
 def ec_layout(self):
  self.eb_layout();assert self.ec_ready and self.ec_data_ready and self.ec_lock_ready and self.eb_stopped
  assert hashlib.sha256(bytes(self.u.mem_read(self.n.base+MODE_RVA,len(MODE)))).hexdigest()==MODE_AUTH["sha256"]
  assert self.rd(self.n.base+0xf7e0b8,8)==self.apis["EnterCriticalSection"] and self.reverse[self.apis["EnterCriticalSection"]]=="EnterCriticalSection"
  assert bytes(self.u.mem_read(self.dw_stack_receiver,640))==EB.OUTPUT+bytes(640-EB.TOTAL)
  assert not self.crt_held and not self.srw_held and self.held and self.inner_held
 def ec_entry(self,site,sp,result,ready):
  self.ec_layout();assert ready
  self.eb_next(site,sp,result,ready)
  assert not self.ec_order and not self.ec_reads and not self.ec_entries and not self.ec_frames and not self.ec_lock_held and self.ec_api_calls==0
 def ec_effect(self,site,at,width,value,ready):
  self.ec_layout();assert ready and len(self.ec_order)<len(PLANS)
  src,off,size,kind,v=PLANS[len(self.ec_order)]
  assert (site,at,width,value)==(src,self.dw_entry_sp+off,size,self.resolve(kind,v))
  assert self.n.stack<=at and at+width<=self.n.stack+65536
  assert self.ec_lock_held==(len(self.ec_order)>=12)
 def ec_call(self,site,ret,sp,args,ready):
  self.ec_layout();k=len(self.ec_entries);assert ready and k<len(CALLS)
  src,return_rva,off,formal,stores,reads=CALLS[k]
  assert (site,ret,sp)==(src,self.n.base+return_rva,self.dw_entry_sp+off)
  assert ret==self.u.reg_read(UC_ARM64_REG_LR) and sp==self.u.reg_read(UC_ARM64_REG_SP)
  expected=[self.resolve(kind,v) for kind,v in formal]
  assert args==expected==[self.u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(len(formal))]
  assert len(self.ec_order)==stores and len(self.ec_reads)==reads and self.ec_lock_held==(k==4)
 def ec_read_contract(self,site,at,width,value,ready):
  self.ec_layout();assert ready and len(self.ec_reads)<2
  if not self.ec_reads:
   assert (site,at,width,value)==(0xced128,self.n.base+MODE_RVA,1,MODE[0]) and len(self.ec_order)==8
  else:
   assert (site,at,width,value)==(0xcb7314,self.n.base+0xf7e0b8,8,self.apis["EnterCriticalSection"]) and len(self.ec_order)==12
  assert value==self.rd(at,width) and not self.ec_lock_held
 def ec_api(self,pc,ret,sp,args,ready):
  self.ec_layout();assert ready and self.ec_lock_ready and not self.ec_lock_held and self.ec_api_calls==0
  assert pc==self.u.reg_read(UC_ARM64_REG_PC)==self.apis["EnterCriticalSection"]
  assert ret==self.u.reg_read(UC_ARM64_REG_LR)==self.n.base+0xcc6098 and sp==self.u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp-1600
  assert args==[self.n.base+0x16a3000]==[self.u.reg_read(UC_ARM64_REG_X0)]
  assert len(self.ec_order)==12 and len(self.ec_reads)==2 and len(self.ec_entries)==4 and self.ec_frames[-1]["entry"]==0xcb7300
 def ec_next(self,site,sp,pointer,ready):
  self.ec_layout();assert ready and site==0xcc6120 and self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+site
  assert sp==self.u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp-1648 and pointer==self.n.base+0x16a2a58
  i=INS[site];mem=next(o.mem for o in i.operands if o.type==capstone.arm64.ARM64_OP_MEM)
  assert not mem.index and DR.reg(self.u,C.reg_name(mem.base))+mem.disp==pointer and bytes(self.u.mem_read(self.n.base+site,4))==PE.get_data(site,4)
  assert len(self.ec_order)==18 and len(self.ec_reads)==2 and len(self.ec_entries)==5 and self.ec_returns==1 and self.ec_api_calls==1 and self.ec_lock_held
  assert [f["entry"] for f in self.ec_frames]==[0xced2f0,0xced0d8,0xcc6078,0xcc6108]
  assert self.rd(self.dw_entry_sp-1536,8)==0 and not self.dx_frames and not self.dy_frames and not self.dz_frames
 def ec_read(self,u,a,at,width,value,_):
  site=u.reg_read(UC_ARM64_REG_PC)-self.n.base
  if self.n.base+MODE_RVA<=at<self.n.base+MODE_RVA+len(MODE) or at==self.n.base+0xf7e0b8:
   data=self.rd(at,width);owned=(site,at,width,data,True);self.ec_read_contract(*owned)
   self.reject(self.ec_read_contract,[(site+4,at,width,data,True),(site,at+1,width,data,True),(site,at,width+1,data,True),(site,at,width,data^1,True),(site,at,width,data,False)])
   self.ec_reads.append((site,at-self.n.base,width));return
  assert self.n.stack<=at and at+width<=self.n.stack+65536,"unqualified new nonstack read"
 def ec_record(self,site,at,data):
  width=len(data);value=int.from_bytes(data,"little");self.ec_effect(site,at,width,value,True)
  self.reject(self.ec_effect,[(site+4,at,width,value,True),(site,at+8,width,value,True),(site,at,width+1,value,True),(site,at,width,value^1,True),(site,at,width,value,False)])
  self.patch_stack(at,data);self.ec_order.append((site,at-self.dw_entry_sp,width));self.pending[at,width]=value
 def ec_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending
  if self.ec_frames and pc==self.ec_frames[-1]["ret"]:
   f=self.ec_frames.pop();assert f["entry"]==0xcb7300 and all(u.reg_read(k)==v for k,v in f["saved"].items())
   assert self.ec_lock_held and self.ec_api_calls==1 and u.reg_read(UC_ARM64_REG_X0)==self.api_clobber;self.ec_returns+=1
  if r==0xcc6120:
   owned=(r,u.reg_read(UC_ARM64_REG_SP),n.base+0x16a2a58,True);self.ec_next(*owned)
   self.reject(self.ec_next,[(r+4,*owned[1:]),(r,owned[1]+16,*owned[2:]),(r,owned[1],owned[2]+8,True),(*owned[:3],False)])
   self.ec_stopped=True;u.emu_stop();return
  if pc in self.reverse:
   owned=(pc,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),[u.reg_read(UC_ARM64_REG_X0)],True);self.ec_api(*owned)
   self.reject(self.ec_api,[(pc+16,*owned[1:]),(pc,owned[1]+4,*owned[2:]),(pc,owned[1],owned[2]+16,owned[3],True),
    (pc,owned[1],owned[2],[owned[3][0]+8],True),(*owned[:4],False)])
   self.ec_lock_held=True
   try:self.reject(self.ec_api,[owned])
   finally:self.ec_lock_held=False
   self.ec_lock_held=True;self.ec_api_calls+=1
   saved={k:u.reg_read(k) for k in NONVOL};u.reg_write(UC_ARM64_REG_X0,self.api_clobber);u.reg_write(UC_ARM64_REG_PC,owned[1])
   assert all(u.reg_read(k)==v for k,v in saved.items());return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4)
  assert any(int(lo,16)<=r<=int(hi,16) for key in ("0x600368","0xcb7300",*EXTRA_PINS) for lo,hi in PINS[key]["ranges"]),"unqualified caller"
  if r in [v[0] for v in CALLS]:
   size=len(CALLS[len(self.ec_entries)][3]);args=[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(size)]
   owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),args,True);self.ec_call(*owned);wrong=args.copy();wrong[0]+=8
   self.reject(self.ec_call,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,args,True),(r,owned[1],owned[2],wrong,True),(*owned[:4],False)])
   self.ec_entries.append(r);self.ec_frames.append({"entry":r,"ret":owned[1],"saved":{k:u.reg_read(k) for k in NONVOL}})
  self.ec_trace.append(r);i=INS[r]
  if i.mnemonic.startswith(("str","stp","stnp","st1","stur")):
   mi=next(k for k,o in enumerate(i.operands) if o.type==capstone.arm64.ARM64_OP_MEM);mem=i.operands[mi]
   at=DR.reg(u,C.reg_name(mem.mem.base))+mem.mem.disp
   if mem.mem.index:
    assert mem.ext==capstone.arm64.ARM64_EXT_INVALID and mem.shift.type in (capstone.arm64.ARM64_SFT_INVALID,capstone.arm64.ARM64_SFT_LSL)
    at+=DR.reg(u,C.reg_name(mem.mem.index))<<mem.shift.value
   ops=list(i.operands[:mi]) if i.mnemonic=="st1" else i.operands[:2] if i.mnemonic in ("stp","stnp") else i.operands[:1]
   for k,o in enumerate(ops):
    name=C.reg_name(o.reg)
    if i.mnemonic=="st1":assert name.startswith("v");name="q"+name[1:]
    width=16 if name.startswith("q") else 8 if name.startswith(("x","d")) or name in ("fp","lr") else 2 if name.startswith("h") else 1 if name.startswith("b") else 4
    if i.mnemonic=="st1":width=16 if o.vas==capstone.arm64.ARM64_VAS_16B else 8
    elif i.mnemonic.endswith("h"):width=2
    elif i.mnemonic.endswith("b"):width=1
    data=(DR.reg(u,name)&((1<<(width*8))-1)).to_bytes(width,"little")
    for off in range(0,width,8):self.ec_record(r,at+k*width+off,data[off:off+8])
 def run(self):
  prior=super().run();n=self.n;u=self.u;stores=self.stores;neg=self.negatives
  owned=(0x600440,u.reg_read(UC_ARM64_REG_SP),u.reg_read(UC_ARM64_REG_X0),True);self.ec_entry(*owned)
  self.reject(self.ec_entry,[(owned[0]+4,*owned[1:]),(owned[0],owned[1]+16,*owned[2:]),(owned[0],owned[1],owned[2]+1,True),(*owned[:3],False)])
  for flag in ("ec_ready","ec_data_ready","ec_lock_ready","eb_ready","eb_data_ready","held","inner_held"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.ec_entry,[owned])
   finally:setattr(self,flag,old)
  at=n.base+MODE_RVA;old=bytes(u.mem_read(at,len(MODE)));u.mem_write(at,bytes([old[0]^1])+old[1:])
  try:self.reject(self.ec_entry,[owned])
  finally:u.mem_write(at,old)
  hooks=[u.hook_add(UC_HOOK_CODE,self.ec_code),u.hook_add(UC_HOOK_MEM_WRITE,self.eb_write),u.hook_add(UC_HOOK_MEM_READ,self.ec_read)]
  try:u.emu_start(n.base+0x600440,n.end,count=2000)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.ec_stopped and not self.pending and u.reg_read(UC_ARM64_REG_PC)==n.base+0xcc6120
  self.ec_layout();after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():
   assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"cumulative EC memory mismatch"
  added={"original_instruction_visits":len(self.ec_trace),"exact_source_store_chunks":self.stores-stores,"independent_stream_setup_store_contracts":len(self.ec_order),
   "rejected_owned_requests":self.negatives-neg,"exact_immutable_mode_reads":1,"exact_inherited_loader_binding_reads":1,"original_lock_wrapper_ABI_returns_exact":self.ec_returns,
   "exact_original_callee_entries":len(self.ec_entries),"owned_allocation_calls":0,"owned_OS_API_calls":self.ec_api_calls,
   "formatted_output_length":37,"destination_remaining_zero_bytes":603,"completed_output_retained_exact":True,"stream_lock_owned_model_held":self.ec_lock_held,
   "native_CRT_resource_initialization_qualified":False,"stream_runtime_pointer_read_qualified":False,"file_open_or_contents_qualified":False,
   "nine_live_allocations_retained":True,"whole_original_entry_to_frontier_memory_and_permissions_exact":True,
   "outer_and_nested_registry_locks_held":True,"inherited_publication_CRT_and_SRW_released":True,"active_stream_callee_frames":4,
   "stop_before_RVA":"0xcc6120","next_dependency_RVA":"0x16a2a58","next_dependency_bytes":8,"current_SP_relative_outer_entry":-1648,
   "outer_callee_return_not_reached_RVA":"0x5f8ea8"}
  return {"EB":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 rows=json.loads(json.dumps(rows));ancestor=json.loads((P.parent/"SOURCE-SAFE.json").read_text());assert [row["EB"] for row in rows]==ancestor["details"]
 report={"experiment":"E011EC","status":"PASS_BOUNDED_ORIGINAL_STREAM_SETUP_LOCK","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
  "mode_data_authority":MODE_AUTH,"stream_lock_owned_model_authority":LOCK_AUTH,"runtime_initial_value_model_authority":ancestor["runtime_initial_value_model_authority"],"details":rows,
  "source_result_fixture_used":False,"native_rear_runtime_allowed":False,"original_stream_wrapper_setup_qualified":True,"owned_stream_lock_acquisition_qualified":True,"bounded_parent_after_consumer_continuation_qualified":True,
  "full_constant_consumer_return_qualified":True,"all_three_argument_length_copy_and_termination_qualified":True,"cold_runtime_context_cleanup_qualified":True,
  "full_outer_callee_return_qualified":False,"full_factory_or_first_helper_return_qualified":False,"native_CRT_resource_initialization_qualified":False,
  "native_runtime_scalar_and_pointer_selection_qualified":False,"alternate_nonzero_runtime_flag_paths_qualified":False,"pointed_locale_tables_qualified":False,
  "cookie_leaf_has_SP_preserving_ABI":False,"stack_growth_guard_page_OS_qualified":False,"stream_runtime_pointer_read_qualified":False,"file_open_or_contents_qualified":False,
  "new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False,"next_experiment":"E011ED"}
 keys=("original_instruction_visits","exact_source_store_chunks","independent_stream_setup_store_contracts","rejected_owned_requests","exact_immutable_mode_reads",
  "exact_inherited_loader_binding_reads","original_lock_wrapper_ABI_returns_exact","exact_original_callee_entries","owned_allocation_calls","owned_OS_API_calls")
 report["added_totals"]={k:sum(row["added"][k] for row in rows) for k in keys};report["inherited_EB_totals"]=ancestor["added_totals"]
 for k in ("EA","DZ","DY","DX","DW","DV","DU","DT","DS"):report["inherited_"+k+"_totals"]=ancestor["inherited_"+k+"_totals"]
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
