#!/usr/bin/env python3
"""Original cold runtime context and nested receiver setup under explicit initial-value models."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011dx-original-constant-data-consumer-setup/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="58cc53732bbf8575c0c2f58ca156daecba3098386e17b599b06602ab4a92cc10"
s=importlib.util.spec_from_file_location("dy_actual_dx_parent",P);DX=importlib.util.module_from_spec(s);s.loader.exec_module(DX)
PE=DX.PE;M=DX.M;C=DX.C;DR=DX.DR;NONVOL=DX.NONVOL;INS=dict(DX.INS);PINS=dict(DX.PINS)
EXTRA_PINS={
"0xcad868":{"body_bytes":352,"ranges":[["0xcad868","0xcad9c7"]],"sha256":"3bd3cec587501af57ce2c37f82c3834b4737d5f346181f65571a801b3dcde393"},
"0xca6280":{"body_bytes":384,"ranges":[["0xca6280","0xca63ff"]],"sha256":"80573b1c868f55f5acbd0a1a62ecd1fc390fff39aee2275e161a64ab85cc8a1e"}}
for entry,pin in EXTRA_PINS.items():
 body=b"".join(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in pin["ranges"])
 assert len(body)==pin["body_bytes"] and hashlib.sha256(body).hexdigest()==pin["sha256"]
 for lo,hi in pin["ranges"]:
  for at in range(int(lo,16),int(hi,16)+1,4):
   i=list(C.disasm(PE.get_data(at,4),at));assert len(i)==1;INS[at]=i[0]
 PINS[entry]=pin
MODEL_AUTHORITY=[]
for at,width in ((0x17a1150,8),(0x16a2a84,4)):
 sec=next(t for t in PE.sections if t.VirtualAddress<=at and at+width<=t.VirtualAddress+t.Misc_VirtualSize)
 assert sec.Characteristics&0x80000000 and at-sec.VirtualAddress>=sec.SizeOfRawData
 MODEL_AUTHORITY.append({"RVA":hex(at),"bytes":width,"section_writable":True,"virtual_zero_fill":True,"file_backed":False,
  "accepted_owned_initial_value":0,"native_runtime_selection_qualified":False})
PAIR_RVA=0x16072d8;PAIR=PE.get_data(PAIR_RVA,16)
assert len(PAIR)==16 and hashlib.sha256(PAIR).hexdigest()=="507987659945beb7bcd11ae53dece55517a2979fc4e3ea4c9683bdceb5fd0f3f"
sec=next(t for t in PE.sections if t.VirtualAddress<=PAIR_RVA and PAIR_RVA+16<=t.VirtualAddress+t.Misc_VirtualSize)
assert sec.Characteristics&0x80000000 and PAIR_RVA-sec.VirtualAddress+16<=sec.SizeOfRawData
assert [int.from_bytes(PAIR[k:k+8],"little")-PE.OPTIONAL_HEADER.ImageBase for k in (0,8)]==[0x1607180,0x1607650]
MODEL_AUTHORITY.append({"RVA":hex(PAIR_RVA),"bytes":16,"section_writable":True,"virtual_zero_fill":False,"file_backed":True,
 "file_initial_sha256":"507987659945beb7bcd11ae53dece55517a2979fc4e3ea4c9683bdceb5fd0f3f","initial_pointer_targets_RVA":["0x1607180","0x1607650"],"native_runtime_selection_qualified":False})
READS=[(0x6bd8c,0x17a1150,8,"scalar",0),(0xcad8b8,0x16a2a84,4,"scalar",0),
 (0xcad8c8,0x16072d8,8,"image",0x1607180),(0xcad8c8,0x16072e0,8,"image",0x1607650)]
PLANS=[
(0xcad86c,-1824,8,"input",19),(0xcad86c,-1816,8,"input",20),
(0xcad870,-1808,8,"input",21),(0xcad870,-1800,8,"input",22),(0xcad874,-1792,8,"input",23),
(0xcad878,-1904,8,"stack",-1776),(0xcad878,-1896,8,"image",0x6bd94),
(0xcad884,-1888,8,"scalar",0),(0xcad88c,-1872,1,"scalar",0),(0xcad894,-1848,1,"scalar",0),
(0xcad89c,-1840,1,"scalar",0),(0xcad8a0,-1832,1,"scalar",0),(0xcad8cc,-1848,1,"scalar",1),
(0xcad8d0,-1864,8,"image",0x1607180),(0xcad8d0,-1856,8,"image",0x1607650),
(0xca6284,-1952,8,"stack",-1904),(0xca6284,-1944,8,"image",0xcad940),
(0xca6288,-1936,8,"scalar",0xffffffffffffffff),(0xca6288,-1928,8,"stack",-1392),
(0xca628c,-1920,8,"scalar",1),(0xca628c,-1912,8,"scalar",640),
(0x11e0,-1960,8,"cookie_frame",0),
(0xca62ec,-3111,4,"scalar",0),(0xca62f4,-3107,2,"scalar",0),(0xca62fc,-3105,1,"scalar",0),(0xca6300,-3112,1,"scalar",0),
(0xca630c,-1984,8,"stack",-3136),(0xca6310,-3136,8,"stack",-1392),(0xca6310,-3128,8,"scalar",640),
(0xca6314,-3120,8,"scalar",0),(0xca6318,-3072,4,"scalar",0),(0xca631c,-3068,1,"scalar",0),
(0xca6320,-3064,8,"scalar",0),(0xca6324,-3056,4,"scalar",0),(0xca6328,-3048,2,"scalar",0),
(0xca632c,-3032,4,"scalar",0),(0xca6330,-3028,1,"scalar",0),
(0xca6338,-2000,8,"scalar",0),(0xca6338,-1992,8,"scalar",0),(0xca633c,-3104,8,"scalar",0),
(0xca633c,-3096,8,"stack",-1888),(0xca6340,-3088,8,"image",0x1370760),(0xca6340,-3080,8,"stack",-1496),
(0xca6344,-1976,4,"scalar",0)]
OUT=Path(__file__).resolve().parent
class Case(DX.Case):
 def __init__(self,*args):
  super().__init__(*args)
  self.dy_ready=True;self.dy_loader_ready=True;self.dy_reads=[];self.dy_order=[];self.dy_trace=[];self.dy_entries=[];self.dy_frames=[]
  self.dy_cookie_frame=None;self.dy_cookie_returns=0;self.dy_stopped=False;self.dy_inputs=None
 def logical(self):
  return super().logical()+(getattr(self,"dy_ready",False),getattr(self,"dy_loader_ready",False),tuple(getattr(self,"dy_reads",[])),
   tuple(getattr(self,"dy_order",[])),tuple(getattr(self,"dy_entries",[])),len(getattr(self,"dy_frames",[])),getattr(self,"dy_cookie_returns",0))
 def dy_layout(self):
  self.dx_layout();n=self.n;u=self.u
  assert self.dy_ready and self.dy_loader_ready and n.base==PE.OPTIONAL_HEADER.ImageBase
  assert self.rd(n.base+0x17a1150,8)==0 and self.rd(n.base+0x16a2a84,4)==0
  assert bytes(u.mem_read(n.base+PAIR_RVA,16))==PAIR and self.rd(n.base+0x1607000,8)==self.cookie
  assert [f["entry"] for f in self.dx_frames]==[0x7ac38,0x7aca0,0x6bdd0,0x6bd48]
  assert self.dx_reads==1 and len(self.dx_order)==33 and self.dx_leaf_returns==1
 def dy_entry(self,site,sp,arg,ready):
  self.dy_layout();u=self.u;n=self.n
  assert ready and site==0x6bd8c and u.reg_read(UC_ARM64_REG_PC)==n.base+site and self.dx_stopped
  assert sp==u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp-1776 and arg==u.reg_read(UC_ARM64_REG_X0)==n.base+0x17a1150
  assert not self.dy_reads and not self.dy_order and not self.dy_entries and not self.dy_frames
 def dy_read_contract(self,site,at,width,value,ready):
  self.dy_layout();n=self.n
  assert ready and len(self.dy_reads)<4
  src,rva,size,kind,want=READS[len(self.dy_reads)]
  expected=n.base+want if kind=="image" else want
  assert (site,at,width,value)==(src,n.base+rva,size,expected) and self.rd(at,width)==expected
 def dy_call(self,site,ret,sp,args,ready):
  self.dy_layout();n=self.n;u=self.u;k=len(self.dy_entries)
  assert ready and k<2 and site==[0xcad868,0xca6280][k]
  assert ret==u.reg_read(UC_ARM64_REG_LR)==n.base+[0x6bd94,0xcad940][k]
  assert sp==u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp+[-1776,-1904][k]
  assert args==[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(len(args))]
  expected=[0,self.dw_stack_receiver,640,0xffffffffffffffff,n.base+0x1370760,0,self.dw_entry_sp-1496] if k==0 else [0,self.dw_stack_receiver,640,n.base+0x1370760,self.dw_entry_sp-1888,self.dw_entry_sp-1496]
  assert args==expected and len(self.dy_reads)==[1,4][k]
 def dy_effect(self,site,at,width,value,ready):
  assert ready and self.dy_ready and self.dy_loader_ready and self.held and self.inner_held and len(self.dy_order)<44
  src,off,size,kind,v=PLANS[len(self.dy_order)]
  expected=self.n.base+v if kind=="image" else self.dw_entry_sp+v if kind=="stack" else self.dy_inputs[v] if kind=="input" else ((self.dw_entry_sp-1968-self.cookie)&((1<<64)-1)) if kind=="cookie_frame" else v
  assert (site,at,width,value)==(src,self.dw_entry_sp+off,size,expected)
  assert self.n.stack<=at and at+width<=self.n.stack+65536 and at+width<=self.dw_stack_receiver
 def dy_next(self,site,sp,args,ready):
  self.dy_layout();n=self.n;u=self.u
  assert ready and site==0xca6348 and u.reg_read(UC_ARM64_REG_PC)==n.base+site
  assert sp==u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp-3136
  assert args==[u.reg_read(globals()[f"UC_ARM64_REG_X{k}"]) for k in range(6)]==[self.dw_entry_sp-3104,self.dw_stack_receiver,640,n.base+0x1370760,self.dw_entry_sp-1888,self.dw_entry_sp-1496]
  assert len(self.dy_order)==44 and len(self.dy_reads)==4 and self.dy_cookie_returns==1 and len(self.dy_frames)==2
  assert self.rd(self.dw_entry_sp-3136,8)==self.dw_stack_receiver and self.rd(self.dw_entry_sp-3128,8)==640
  assert self.rd(self.dw_entry_sp-3096,8)==self.dw_entry_sp-1888 and self.rd(self.dw_entry_sp-3088,8)==n.base+0x1370760
  assert self.rd(self.dw_entry_sp-3080,8)==self.dw_entry_sp-1496
  assert self.rd(self.dw_entry_sp-1864,8)==n.base+0x1607180 and self.rd(self.dw_entry_sp-1856,8)==n.base+0x1607650 and self.rd(self.dw_entry_sp-1848,1)==1
 def dy_read(self,u,a,at,width,value,_):
  if any(self.n.base+rva<=at<self.n.base+rva+size for src,rva,size,kind,want in READS):
   site=u.reg_read(UC_ARM64_REG_PC)-self.n.base;data=self.rd(at,width);owned=(site,at,width,data,True);self.dy_read_contract(*owned)
   self.reject(self.dy_read_contract,[(site+4,at,width,data,True),(site,at+4,width,data,True),(site,at,width+1,data,True),(site,at,width,data^1,True),(site,at,width,data,False)])
   self.dy_reads.append((hex(site),hex(at-self.n.base),width));return
  self.dx_read(u,a,at,width,value,_)
 def dy_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending
  if r==0xca6348:
   owned=(r,u.reg_read(UC_ARM64_REG_SP),[u.reg_read(globals()[f"UC_ARM64_REG_X{k}"]) for k in range(6)],True);self.dy_next(*owned)
   wrong=owned[2].copy();wrong[0]+=8
   self.reject(self.dy_next,[(r+4,*owned[1:]),(r,owned[1]+16,*owned[2:]),(r,owned[1],wrong,True),(*owned[:3],False)])
   self.dy_stopped=True;u.emu_stop();return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4)
  if r==0xca6298:
   f=self.dy_cookie_frame;assert f and pc==f["ret"] and u.reg_read(UC_ARM64_REG_SP)==f["sp"]-16
   assert all(u.reg_read(k)==v for k,v in f["saved"].items() if k!=UC_ARM64_REG_SP)
   assert self.rd(f["sp"]-8,8)==((f["sp"]-16-self.cookie)&((1<<64)-1));self.dy_cookie_returns+=1;self.dy_cookie_frame=None
  if r in (0xcad868,0xca6280):
   k=len(self.dy_entries);size=[7,6][k];args=[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(size)]
   owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),args,True);self.dy_call(*owned)
   wrong=args.copy();wrong[1]+=8
   self.reject(self.dy_call,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,args,True),(r,owned[1],owned[2],wrong,True),(*owned[:4],False)])
   self.dy_entries.append(r);self.dy_frames.append({"entry":r,"ret":owned[1],"saved":{k:u.reg_read(k) for k in NONVOL}})
  if r==0x11d0:
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0xca6298 and u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp-1952 and self.dy_cookie_frame is None
   self.dy_cookie_frame={"ret":u.reg_read(UC_ARM64_REG_LR),"sp":u.reg_read(UC_ARM64_REG_SP),"saved":{k:u.reg_read(k) for k in NONVOL}}
  self.dy_trace.append(r);i=INS[r]
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
     addr=at+k*width+off;chunk=data[off:off+8];v=int.from_bytes(chunk,"little");self.dy_effect(r,addr,len(chunk),v,True)
     self.reject(self.dy_effect,[(r+4,addr,len(chunk),v,True),(r,addr+8,len(chunk),v,True),(r,addr,len(chunk)+1,v,True),(r,addr,len(chunk),v^1,True),(r,addr,len(chunk),v,False)])
     self.patch_stack(addr,chunk);self.dy_order.append((r,addr-self.dw_entry_sp,len(chunk)));self.pending[addr,len(chunk)]=v
 def run(self):
  prior=super().run();n=self.n;u=self.u;stores=self.stores;neg=self.negatives
  self.dy_inputs={k:u.reg_read(globals()[f"UC_ARM64_REG_X{k}"]) for k in range(31)}
  owned=(0x6bd8c,u.reg_read(UC_ARM64_REG_SP),u.reg_read(UC_ARM64_REG_X0),True);self.dy_entry(*owned)
  self.reject(self.dy_entry,[(owned[0]+4,*owned[1:]),(owned[0],owned[1]+16,*owned[2:]),(owned[0],owned[1],owned[2]+8,True),(*owned[:3],False)])
  for flag in ("dy_ready","dy_loader_ready","dx_ready","dw_ready","held","inner_held"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.dy_entry,[owned])
   finally:setattr(self,flag,old)
  for rva,width,value in ((0x17a1150,8,1),(0x16a2a84,4,1),(0x16072d8,8,n.base+0x1607188),(0x16072e0,8,n.base+0x1607658)):
   at=n.base+rva;old=bytes(u.mem_read(at,width));self.wr(at,value,width)
   try:self.reject(self.dy_entry,[owned])
   finally:u.mem_write(at,old)
  hooks=[u.hook_add(UC_HOOK_CODE,self.dy_code),u.hook_add(UC_HOOK_MEM_WRITE,self.write),u.hook_add(UC_HOOK_MEM_READ,self.dy_read)]
  try:u.emu_start(n.base+0x6bd8c,n.end,count=1000)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.dy_stopped and not self.pending and u.reg_read(UC_ARM64_REG_PC)==n.base+0xca6348 and self.dy_cookie_frame is None
  self.dy_layout()
  after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():
   assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"cumulative retained DY memory mismatch"
  added={"original_instruction_visits":len(self.dy_trace),"exact_source_store_chunks":self.stores-stores,"independent_setup_store_contracts":len(self.dy_order),
   "rejected_owned_requests":self.negatives-neg,"exact_runtime_dependency_reads":len(self.dy_reads),"cookie_frame_returns_convention_exact":self.dy_cookie_returns,
   "exact_nested_consumer_entries":len(self.dy_entries),"owned_allocation_calls":0,"owned_OS_API_calls":0,
   "runtime_context_and_nested_receiver_fields_constructed":True,"nine_live_allocations_retained":True,"stack_destination_640_bytes_still_zero":True,
   "whole_original_entry_to_frontier_memory_and_permissions_exact":True,"outer_and_nested_registry_locks_held":True,"CRT_and_SRW_released":True,
   "retained_active_consumer_frames":6,"stop_before_RVA":"0xca6348","next_callee_RVA":"0xca94e8","next_callee_return_RVA":"0xca634c",
   "next_receiver_relative_outer_entry_SP":-3104,"next_runtime_context_relative_outer_entry_SP":-1888,"current_SP_relative_outer_entry":-3136,
   "outer_callee_return_not_reached_RVA":"0x5f8ea8"}
  return {"DX":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 rows=json.loads(json.dumps(rows));ancestor=json.loads((P.parent/"SOURCE-SAFE.json").read_text());assert [r["DX"] for r in rows]==ancestor["details"]
 report={"experiment":"E011DY","status":"PASS_BOUNDED_ORIGINAL_COLD_RUNTIME_CONTEXT_AND_RECEIVER_SETUP","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
  "runtime_initial_value_model_authority":MODEL_AUTHORITY,"details":rows,"source_result_fixture_used":False,"native_rear_runtime_allowed":False,
  "full_constant_consumer_return_qualified":False,"full_outer_callee_return_qualified":False,"full_factory_or_first_helper_return_qualified":False,
  "native_runtime_scalar_and_pointer_selection_qualified":False,"alternate_nonzero_runtime_flag_paths_qualified":False,"pointed_locale_tables_or_format_strings_qualified":False,
  "cookie_leaf_has_SP_preserving_ABI":False,"stack_growth_guard_page_OS_qualified":False,"next_original_consumer_qualified":False,
  "new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False,"next_experiment":"E011DZ"}
 keys=("original_instruction_visits","exact_source_store_chunks","independent_setup_store_contracts","rejected_owned_requests","exact_runtime_dependency_reads","cookie_frame_returns_convention_exact",
  "exact_nested_consumer_entries","owned_allocation_calls","owned_OS_API_calls")
 report["added_totals"]={k:sum(row["added"][k] for row in rows) for k in keys};report["inherited_DX_totals"]=ancestor["added_totals"]
 for k in ("DW","DV","DU","DT","DS"):report["inherited_"+k+"_totals"]=ancestor["inherited_"+k+"_totals"]
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
