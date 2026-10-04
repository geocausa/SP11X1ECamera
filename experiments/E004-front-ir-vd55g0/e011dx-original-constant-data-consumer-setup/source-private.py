#!/usr/bin/env python3
"""Exact opaque constant-data read and variadic consumer setup in the retained parent."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011dw-original-nested-enumeration-container/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="94aaaec408d9d4ab3ccd147339f15362920724c3bc1f583a57e1961025663e84"
s=importlib.util.spec_from_file_location("dx_actual_dw_parent",P);DW=importlib.util.module_from_spec(s);s.loader.exec_module(DW)
PE=DW.PE;M=DW.M;C=DW.C;DR=DW.DR;NONVOL=DW.NONVOL;INS=dict(DW.INS);PINS=dict(DW.PINS)
EXTRA_PINS={
"0x7ac38":{"body_bytes":104,"ranges":[["0x7ac38","0x7ac9f"]],"sha256":"e116b84a78df86ea5e6e25179a5cd2acca434f07365cf00d0c249b97f28ea611"},
"0x7aca0":{"body_bytes":84,"ranges":[["0x7aca0","0x7acf3"]],"sha256":"6b302c4ecbc82135952ef5bb6e58184338b7fda2b1fdd9ef14a7d535cfbec4e4"},
"0x6bdd0":{"body_bytes":80,"ranges":[["0x6bdd0","0x6be1f"]],"sha256":"455b961625e30f926b1cee4e3979994807df131706393611c18e23617bb1ef06"},
"0x6bd48":{"body_bytes":132,"ranges":[["0x6bd48","0x6bdcb"]],"sha256":"3f73ed17e48df056ce5d481e0f27b003137b1ef73e5ad750d3a7d6bd95dd33ca"},
"0xedd0":{"body_bytes":12,"ranges":[["0xedd0","0xeddb"]],"sha256":"fccd30fe0400a87e1bee6601eac29919f8c78e65be18e9fabd5afa7982d92d44"}}
for entry,pin in EXTRA_PINS.items():
 body=b"".join(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in pin["ranges"])
 assert len(body)==pin["body_bytes"] and hashlib.sha256(body).hexdigest()==pin["sha256"]
 for lo,hi in pin["ranges"]:
  for at in range(int(lo,16),int(hi,16)+1,4):
   i=list(C.disasm(PE.get_data(at,4),at));assert len(i)==1;INS[at]=i[0]
 PINS[entry]=pin
DATA_RVA=0x10f03a0;DATA_BYTES=8;DATA_SHA="a2fb00d4cf5a726758f3b5d24abbf631cccc4da72abd78c7e7556755fce7d726"
DATA=PE.get_data(DATA_RVA,DATA_BYTES)
assert len(DATA)==DATA_BYTES and hashlib.sha256(DATA).hexdigest()==DATA_SHA
SEC=next(t for t in PE.sections if t.VirtualAddress<=DATA_RVA and DATA_RVA+DATA_BYTES<=t.VirtualAddress+t.Misc_VirtualSize)
assert DATA_RVA-SEC.VirtualAddress+DATA_BYTES<=SEC.SizeOfRawData and not(SEC.Characteristics&0x80000000)
# Independently authored exact setup effects. Tags bind values to image/stack coordinates or preserved inputs.
PLANS=[
(0x7ac40,-1496,8,"image",0x10f0380),(0x7ac40,-1488,8,"image",0x10f03b0),
(0x7ac44,-1480,8,"image",0x13f1f28),(0x7ac44,-1472,8,"input",6),(0x7ac48,-1464,8,"input",7),
(0x7ac4c,-1568,8,"stack",-96),(0x7ac4c,-1560,8,"image",0x600440),
(0x7ac54,-1520,8,"stack",-1392),(0x7ac58,-1528,8,"scalar",640),(0x7ac5c,-1536,8,"image",0x1370760),
(0x7ac64,-1544,8,"stack",-1496),(0x7aca4,-1632,8,"stack",-1568),(0x7aca4,-1624,8,"image",0x7ac7c),
(0x7acac,-1584,8,"stack",-1392),(0x7acb0,-1592,8,"scalar",640),(0x7acb4,-1600,8,"image",0x1370760),
(0x7acb8,-1608,8,"stack",-1496),(0x7acc0,-1616,4,"scalar",0),
(0x6bdd4,-1696,8,"stack",-1632),(0x6bdd4,-1688,8,"image",0x7acdc),
(0x6bddc,-1648,8,"stack",-1392),(0x6bde0,-1656,8,"scalar",640),(0x6bde4,-1664,8,"scalar",0xffffffffffffffff),
(0x6bde8,-1672,8,"image",0x1370760),(0x6bdec,-1680,8,"stack",-1496),
(0x6bd4c,-1776,8,"stack",-1696),(0x6bd4c,-1768,8,"image",0x6be0c),
(0x6bd54,-1712,8,"stack",-1392),(0x6bd58,-1720,8,"scalar",640),(0x6bd5c,-1728,8,"scalar",0xffffffffffffffff),
(0x6bd60,-1736,8,"image",0x1370760),(0x6bd64,-1744,8,"scalar",0),(0x6bd68,-1752,8,"stack",-1496)]
CALLS={0x7ac38:(0x600440,-1456),0x7aca0:(0x7ac7c,-1568),0x6bdd0:(0x7acdc,-1632),0x6bd48:(0x6be0c,-1696),0xedd0:(0x6bd70,-1776)}
OUT=Path(__file__).resolve().parent
class Case(DW.Case):
 def __init__(self,*args):
  super().__init__(*args)
  self.dx_ready=True;self.dx_order=[];self.dx_trace=[];self.dx_reads=0;self.dx_entries=[];self.dx_frames=[];self.dx_leaf_returns=0;self.dx_stopped=False;self.dx_inputs=None
 def logical(self):
  return super().logical()+(getattr(self,"dx_ready",False),tuple(getattr(self,"dx_order",[])),getattr(self,"dx_reads",0),
   tuple(getattr(self,"dx_entries",[])),len(getattr(self,"dx_frames",[])),getattr(self,"dx_leaf_returns",0))
 def dx_layout(self):
  self.dw_layout();self.dw_constructed()
  assert self.dx_ready and len(self.dw_leases)==3 and not self.dw_frames
  assert self.dw_nested_returns==self.dw_heap_clear_returns==self.dw_stack_clear_returns==1
  assert self.rd(self.dw_allocations[0][0]+8,8)==self.dw_allocations[1][0]
  assert bytes(self.u.mem_read(self.dw_stack_receiver,640))==bytes(640)
  assert bytes(self.u.mem_read(self.n.base+DATA_RVA,DATA_BYTES))==DATA
 def dx_entry(self,site,sp,dest,ready):
  self.dx_layout();u=self.u;n=self.n
  assert ready and site==0x600420 and u.reg_read(UC_ARM64_REG_PC)==n.base+site
  assert self.dw_stopped and sp==self.dw_entry_sp-1456==u.reg_read(UC_ARM64_REG_SP)
  assert dest==self.dw_stack_receiver==u.reg_read(UC_ARM64_REG_X0) and not self.dx_order and not self.dx_entries and self.dx_reads==0
 def dx_constant(self,site,at,width,data,ready):
  assert ready and self.dx_ready and self.held and self.inner_held
  assert site==0x600420 and at==self.n.base+DATA_RVA and width==DATA_BYTES and data==DATA
  assert self.dx_reads==0 and not self.dx_entries and not self.dx_order
  assert bytes(self.u.mem_read(at,width))==DATA
 def dx_call(self,entry,ret,sp,args,ready):
  self.dx_layout();n=self.n;u=self.u;expected=list(CALLS)[len(self.dx_entries)]
  assert ready and entry==expected and (ret-n.base,sp-self.dw_entry_sp)==CALLS[entry]
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+entry and ret==u.reg_read(UC_ARM64_REG_LR) and sp==u.reg_read(UC_ARM64_REG_SP)
  assert args==[u.reg_read(globals()[f"UC_ARM64_REG_X{k}"]) for k in range(len(args))]
  dest=self.dw_stack_receiver;fmt=n.base+0x1370760;va=self.dw_entry_sp-1496
  if entry==0x7ac38:
   assert args==[dest,640,fmt,n.base+0x10f0380,n.base+0x10f03b0,n.base+0x13f1f28,self.dx_inputs[6],self.dx_inputs[7]]
  elif entry==0x7aca0:assert args==[dest,640,fmt,va]
  elif entry==0x6bdd0:assert args==[dest,640,0xffffffffffffffff,fmt,va]
  elif entry==0x6bd48:assert args==[dest,640,0xffffffffffffffff,fmt,0,va]
  else:assert args==[]
  assert self.dx_reads==1
 def dx_store(self,site,at,width,value,ready):
  assert ready and self.dx_ready and self.held and self.inner_held
  assert len(self.dx_order)<len(PLANS)
  src,off,size,kind,v=PLANS[len(self.dx_order)]
  assert (site,at,width)==(src,self.dw_entry_sp+off,size)
  expected=self.n.base+v if kind=="image" else self.dw_entry_sp+v if kind=="stack" else self.dx_inputs[v] if kind=="input" else v
  assert value==expected and self.n.stack<=at and at+width<=self.n.stack+65536
  assert at+width<=self.dw_stack_receiver or at>=self.dw_stack_receiver+640
 def dx_read(self,u,a,at,width,value,_):
  if self.n.base+DATA_RVA<=at<self.n.base+DATA_RVA+DATA_BYTES:
   data=bytes(u.mem_read(at,width));site=u.reg_read(UC_ARM64_REG_PC)-self.n.base
   self.dx_constant(site,at,width,data,True)
   self.reject(self.dx_constant,[(site+4,at,width,data,True),(site,at+4,width,data,True),(site,at,width+1,data,True),
    (site,at,width,bytes([data[0]^1])+data[1:],True),(site,at,width,data,False)])
   self.dx_reads+=1;return
  self.dw_read(u,a,at,width,value,_)
 def dx_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending
  if r==0x6bd8c:
   assert u.reg_read(UC_ARM64_REG_X0)==n.base+0x17a1150 and len(self.dx_order)==33 and self.dx_leaf_returns==1
   self.dx_stopped=True;u.emu_stop();return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4)
  if self.dx_frames and pc==self.dx_frames[-1]["ret"]:
   frame=self.dx_frames.pop();assert r==0x6bd70 and frame["entry"]==0xedd0
   assert all(u.reg_read(k)==v for k,v in frame["saved"].items()) and u.reg_read(UC_ARM64_REG_X0)==n.base+0x17a1150
   self.dx_leaf_returns+=1
  if r in CALLS:
   size={0x7ac38:8,0x7aca0:4,0x6bdd0:5,0x6bd48:6,0xedd0:0}[r]
   args=[u.reg_read(globals()[f"UC_ARM64_REG_X{k}"]) for k in range(size)]
   owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),args,True);self.dx_call(*owned)
   wrong=args.copy()
   if wrong:wrong[0]+=8
   else:wrong=[0]
   self.reject(self.dx_call,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,args,True),
    (r,owned[1],owned[2],wrong,True),(r,*owned[1:4],False)])
   self.dx_entries.append(r)
   self.dx_frames.append({"entry":r,"ret":owned[1],"saved":{k:u.reg_read(k) for k in NONVOL}})
  self.dx_trace.append(r);i=INS[r]
  if i.mnemonic.startswith(("str","stp","stnp","st1","stur")):
   mi=next(k for k,o in enumerate(i.operands) if o.type==capstone.arm64.ARM64_OP_MEM);mem=i.operands[mi];assert not mem.mem.index
   at=DR.reg(u,C.reg_name(mem.mem.base))+mem.mem.disp
   ops=list(i.operands[:mi]) if i.mnemonic=="st1" else i.operands[:2] if i.mnemonic in ("stp","stnp") else i.operands[:1]
   for k,o in enumerate(ops):
    name=C.reg_name(o.reg)
    if i.mnemonic=="st1":assert name.startswith("v");name="q"+name[1:]
    width=16 if name.startswith("q") else 8 if name.startswith(("x","d")) or name in ("fp","lr") else 2 if name.startswith("h") else 1 if name.startswith("b") else 4
    if i.mnemonic=="st1":width=16 if o.vas==capstone.arm64.ARM64_VAS_16B else 8
    elif i.mnemonic.endswith("h"):width=2
    elif i.mnemonic.endswith("b"):width=1
    data=(DR.reg(u,name)&((1<<(width*8))-1)).to_bytes(width,"little")
    for off in range(0,width,8):
     addr=at+k*width+off;chunk=data[off:off+8];v=int.from_bytes(chunk,"little")
     self.dx_store(r,addr,len(chunk),v,True)
     self.reject(self.dx_store,[(r+4,addr,len(chunk),v,True),(r,addr+8,len(chunk),v,True),
      (r,addr,len(chunk)-1,v,True),(r,addr,len(chunk),v^1,True),(r,addr,len(chunk),v,False)])
     self.patch_stack(addr,chunk);self.dx_order.append((r,addr-self.dw_entry_sp,len(chunk)))
     self.pending[addr,len(chunk)]=v
 def run(self):
  prior=super().run();u=self.u;n=self.n;stores=self.stores;neg=self.negatives
  self.dx_inputs={k:u.reg_read(globals()[f"UC_ARM64_REG_X{k}"]) for k in range(31)}
  args=(0x600420,u.reg_read(UC_ARM64_REG_SP),self.dw_stack_receiver,True);self.dx_entry(*args)
  self.reject(self.dx_entry,[(args[0]+4,*args[1:]),(args[0],args[1]+16,*args[2:]),(args[0],args[1],args[2]+8,True),(*args[:3],False)])
  for flag in ("dx_ready","dw_ready","dw_alloc_ready","held","inner_held"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.dx_entry,[args])
   finally:setattr(self,flag,old)
  hooks=[u.hook_add(UC_HOOK_CODE,self.dx_code),u.hook_add(UC_HOOK_MEM_WRITE,self.write),u.hook_add(UC_HOOK_MEM_READ,self.dx_read)]
  try:u.emu_start(n.base+0x600420,n.end,count=1000)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.dx_stopped and not self.pending and u.reg_read(UC_ARM64_REG_PC)==n.base+0x6bd8c
  assert self.dx_reads==1 and self.dx_entries==list(CALLS) and [f["entry"] for f in self.dx_frames]==list(CALLS)[:-1]
  self.dx_layout()
  after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():
   assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"cumulative retained DX memory mismatch"
  added={"original_instruction_visits":len(self.dx_trace),"exact_source_store_chunks":self.stores-stores,"rejected_owned_requests":self.negatives-neg,
   "exact_opaque_constant_reads":self.dx_reads,"original_leaf_returns_ABI_exact":self.dx_leaf_returns,"exact_active_consumer_entries":len(self.dx_entries),
   "independent_setup_store_contracts":len(self.dx_order),"owned_allocation_calls":0,"owned_OS_API_calls":0,"nine_live_allocations_retained":True,
   "whole_original_entry_to_frontier_memory_and_permissions_exact":True,"stack_receiver_640_bytes_still_zero":True,
   "outer_and_nested_registry_locks_held":True,"CRT_and_SRW_released":True,"stop_before_RVA":"0x6bd8c","next_dependency_RVA":"0x17a1150","next_dependency_bytes":8,
   "active_consumer_RVAs":[hex(x) for x in CALLS if x!=0xedd0],"outer_callee_return_not_reached_RVA":"0x5f8ea8"}
  return {"DW":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 rows=json.loads(json.dumps(rows))
 ancestor=json.loads((P.parent/"SOURCE-SAFE.json").read_text())
 assert [row["DW"] for row in rows]==ancestor["details"]
 report={"experiment":"E011DX","status":"PASS_BOUNDED_ORIGINAL_CONSTANT_DATA_CONSUMER_SETUP","scenarios":len(rows),"source_pins":PINS,
  "constant_data_authority":{"RVA":hex(DATA_RVA),"bytes":DATA_BYTES,"sha256":DATA_SHA,"file_backed":True,"section_nonwritable":True,"opaque":True},
  "image_sha256":M.DLL_SHA,"details":rows,"source_result_fixture_used":False,"native_rear_runtime_allowed":False,
  "full_constant_consumer_return_qualified":False,"full_outer_callee_return_qualified":False,"full_factory_or_first_helper_return_qualified":False,
  "next_runtime_dependency_qualified":False,"constant_pointed_strings_or_format_contents_qualified":False,"native_CRT_runtime_scalar_selection_qualified":False,
  "stack_growth_guard_page_OS_qualified":False,"new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,
  "private_raw_material_exported":False,"next_experiment":"E011DY"}
 keys=("original_instruction_visits","exact_source_store_chunks","rejected_owned_requests","exact_opaque_constant_reads",
  "original_leaf_returns_ABI_exact","exact_active_consumer_entries","independent_setup_store_contracts","owned_allocation_calls","owned_OS_API_calls")
 report["added_totals"]={k:sum(row["added"][k] for row in rows) for k in keys}
 report["inherited_DW_totals"]=ancestor["added_totals"]
 for k in ("DV","DU","DT","DS"):report["inherited_"+k+"_totals"]=ancestor["inherited_"+k+"_totals"]
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
