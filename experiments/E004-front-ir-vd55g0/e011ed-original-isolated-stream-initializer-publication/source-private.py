#!/usr/bin/env python3
"""Isolated original stream-table initializer publication prefix; camera caller unchanged."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011ec-original-stream-setup-lock/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="36fc853cb283ba0d5e168594b453ae9538b458fc90118ccda57553297e8c4ebb"
s=importlib.util.spec_from_file_location("ed_actual_ec_parent",P);EC=importlib.util.module_from_spec(s);s.loader.exec_module(EC)
PE=EC.PE;M=EC.M;C=EC.C;DR=EC.DR;NONVOL=EC.NONVOL;INS=dict(EC.INS);PINS=dict(EC.PINS)
EXTRA_PINS={
 "0xcb3260":{"body_bytes":296,"ranges":[["0xcb3260","0xcb3387"]],"sha256":"7aa827ad2e4914dd30c14c91bb6e27fce3eb3c9863194934ebf524b164c6ab19"},
 "0xcba4b0":{"body_bytes":12,"ranges":[["0xcba4b0","0xcba4bb"]],"sha256":"737b4eb9b5e218a973a49f6712fbd440755a2cfd690d39721d3cdc2def43018d"}}
for entry,pin in EXTRA_PINS.items():
 body=b"".join(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in pin["ranges"])
 assert len(body)==pin["body_bytes"] and hashlib.sha256(body).hexdigest()==pin["sha256"]
 for lo,hi in pin["ranges"]:
  for at in range(int(lo,16),int(hi,16)+1,4):
   i=list(C.disasm(PE.get_data(at,4),at));assert len(i)==1;INS[at]=i[0]
 PINS[entry]=pin
INITIAL_AUTH=[{"RVA":"0x16a2a50","bytes":4,"section_writable":True,"virtual_zero_fill":True,"file_backed":False,"accepted_owned_initial_value":0,"native_runtime_selection_qualified":False},
 {"RVA":"0x16a2a58","bytes":8,"section_writable":True,"virtual_zero_fill":True,"file_backed":False,"accepted_owned_initial_value":0,"native_runtime_selection_qualified":False}]
for t in INITIAL_AUTH:
 at=int(t["RVA"],16);sec=next(z for z in PE.sections if z.VirtualAddress<=at and at+t["bytes"]<=z.VirtualAddress+z.Misc_VirtualSize)
 assert sec.Characteristics&0x80000000 and at-sec.VirtualAddress>=sec.SizeOfRawData
PUBLIC_BINDING={"InitializeCriticalSectionEx":0xf7e230}
actual={ (x.name or b"").decode():x.address-PE.OPTIONAL_HEADER.ImageBase for e in PE.DIRECTORY_ENTRY_IMPORT for x in e.imports if (x.name or b"")==b"InitializeCriticalSectionEx"}
assert actual==PUBLIC_BINDING
OWNED_AUTH={"allocator_request_RVA":"0xcb75e0","allocator_return_RVA":"0xcb32ac","count":512,"element_bytes":8,"allocation_bytes":4096,
 "zeroed_allocation_provider_is_owned_model":True,"native_allocator_implementation_qualified":False,
 "resource_initializer_wrapper_RVA":"0xcba4b0","resource_initializer_return_RVA":"0xcb3328","import_cell_RVA":"0xf7e230",
 "first_standard_stream_pointer_RVA":"0x1607060","first_resource_RVA":"0x1607090","spin_count":4000,"flags":0,
 "resource_success_return_is_owned_model":True,"native_CRT_resource_initialization_qualified":False,"pointed_standard_stream_contents_qualified":False}
PLANS=[(0xcb3264,-64,8,"saved",UC_ARM64_REG_X19),(0xcb3264,-56,8,"saved",UC_ARM64_REG_X20),
 (0xcb3268,-48,8,"saved",UC_ARM64_REG_X21),(0xcb3268,-40,8,"saved",UC_ARM64_REG_X22),
 (0xcb326c,-32,8,"saved",UC_ARM64_REG_X23),(0xcb326c,-24,8,"saved",UC_ARM64_REG_X24),
 (0xcb3270,-16,8,"saved",UC_ARM64_REG_X25),(0xcb3270,-8,8,"saved",UC_ARM64_REG_X26),
 (0xcb3274,-80,8,"saved",UC_ARM64_REG_X29),(0xcb3274,-72,8,"saved",UC_ARM64_REG_LR),
 (0xcb329c,0x16a2a50,4,"count",512),(0xcb32b0,0x16a2a58,8,"table",0),
 (0xcb1654,-96,8,"image",0x16a2000),(0xcb1658,-112,8,"stack",-80),(0xcb1658,-104,8,"image",0xcb32bc),
 (0xcb3330,0,8,"slot",0x1607060)]
OUT=Path(__file__).resolve().parent
class Bootstrap(EC.Case):
 def __init__(self,*args):
  super().__init__(*args)
  self.ed_ready=self.ed_cells_ready=self.ed_alloc_ready=self.ed_resource_ready=True
  self.ed_table=self.n.heap+0x24000+self.bias;self.ed_allocated=False;self.ed_resources=[];self.ed_order=[];self.ed_reads=[];self.ed_trace=[]
  self.ed_frames=[];self.ed_entries=[];self.ed_returns=0;self.ed_calloc_calls=0;self.ed_OS_calls=0;self.ed_stopped=False
  self.ed_api=self.api_page+0x200;self.wr(self.n.base+0xf7e230,self.ed_api,8)
  self.u.mem_write(self.ed_table-32,bytes([self.poison])*4160);self.ed_table_expected=bytearray([self.poison]*4096)
  self.ed_entry_sp=self.u.reg_read(UC_ARM64_REG_SP);self.ed_saved={k:self.u.reg_read(k) for k in [*NONVOL,UC_ARM64_REG_LR]}
 def logical(self):
  return super().logical()+(getattr(self,"ed_ready",False),getattr(self,"ed_cells_ready",False),getattr(self,"ed_alloc_ready",False),getattr(self,"ed_resource_ready",False),
   getattr(self,"ed_allocated",False),tuple(getattr(self,"ed_resources",[])),tuple(getattr(self,"ed_order",[])),tuple(getattr(self,"ed_reads",[])),
   tuple(getattr(self,"ed_entries",[])),getattr(self,"ed_returns",0),getattr(self,"ed_calloc_calls",0),getattr(self,"ed_OS_calls",0))
 def ed_layout(self):
  assert self.ed_ready and self.ed_cells_ready and self.ed_alloc_ready and self.ed_resource_ready
  n=self.n;u=self.u
  assert self.rd(n.base+0xf7e230,8)==self.ed_api
  assert bytes(u.mem_read(self.ed_table-32,32))==bytes([self.poison])*32 and bytes(u.mem_read(self.ed_table+4096,32))==bytes([self.poison])*32
  assert bytes(u.mem_read(self.ed_table,4096))==bytes(self.ed_table_expected)
  assert not self.held and not self.inner_held and not self.crt_held and not self.srw_held and not self.ec_lock_held
 def ed_entry(self,site,sp,ret,ready):
  self.ed_layout();assert ready and site==0xcb3260 and sp==self.ed_entry_sp==self.stacktop and ret==self.n.end
  assert self.u.reg_read(UC_ARM64_REG_SP)==sp and self.u.reg_read(UC_ARM64_REG_LR)==ret
  assert self.rd(self.n.base+0x16a2a50,4)==0 and self.rd(self.n.base+0x16a2a58,8)==0
  assert not self.ed_order and not self.ed_reads and not self.ed_entries and not self.ed_allocated and not self.ed_resources
 def ed_effect(self,site,at,width,value,ready):
  self.ed_layout();assert ready and len(self.ed_order)<len(PLANS)
  src,off,size,kind,v=PLANS[len(self.ed_order)]
  if kind in ("count","table"):address=self.n.base+off;expected=v if kind=="count" else self.ed_table
  elif kind=="slot":
   address=self.ed_table+off;expected=self.n.base+v;assert self.ed_allocated and self.ed_resources==[self.n.base+0x1607090]
  else:
   address=self.ed_entry_sp+off;expected=self.ed_saved[v] if kind=="saved" else self.n.base+v if kind=="image" else self.ed_entry_sp+v
  assert (site,at,width,value)==(src,address,size,expected)
  if kind=="table":assert self.ed_allocated and self.ed_calloc_calls==1
 def ed_calloc(self,site,ret,sp,args,pointer,ready):
  self.ed_layout();assert ready and not self.ed_allocated and self.ed_calloc_calls==0
  assert site==0xcb75e0 and ret==self.u.reg_read(UC_ARM64_REG_LR)==self.n.base+0xcb32ac and sp==self.u.reg_read(UC_ARM64_REG_SP)==self.ed_entry_sp-80
  assert args==[512,8]==[self.u.reg_read(UC_ARM64_REG_X0),self.u.reg_read(UC_ARM64_REG_X1)] and pointer==self.ed_table and pointer%16==0
  assert len(self.ed_order)==11 and len(self.ed_reads)==1 and self.rd(self.n.base+0x16a2a50,4)==512 and self.rd(self.n.base+0x16a2a58,8)==0
  assert all(not (at-32<=pointer+4096+32 and pointer-32<=at+size+32) for at,size in self.reservations+self.dw_allocations+[(self.exit_storage,256),(self.dv_buffer,18832)]+[(x,48) for x in self.dt_nodes])
 def ed_call(self,site,ret,sp,args,ready):
  self.ed_layout();k=len(self.ed_entries);assert ready and k<2
  assert site==[0xcb1650,0xcba4b0][k] and ret==self.u.reg_read(UC_ARM64_REG_LR)==self.n.base+[0xcb32bc,0xcb3328][k]
  assert sp==self.u.reg_read(UC_ARM64_REG_SP)==self.ed_entry_sp-80
  expected=[[0],[self.n.base+0x1607090,4000,0]][k]
  assert args==expected==[self.u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(len(expected))]
  assert self.ed_allocated and len(self.ed_order)==[12,15][k] and len(self.ed_reads)==[1,2][k]
 def ed_api_contract(self,pc,ret,sp,args,ready):
  self.ed_layout();assert ready and not self.ed_resources and self.ed_OS_calls==0 and self.ed_allocated
  assert pc==self.u.reg_read(UC_ARM64_REG_PC)==self.ed_api and ret==self.u.reg_read(UC_ARM64_REG_LR)==self.n.base+0xcb3328
  assert sp==self.u.reg_read(UC_ARM64_REG_SP)==self.ed_entry_sp-80 and args==[self.n.base+0x1607090,4000,0]
  assert args==[self.u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(3)] and len(self.ed_order)==15 and len(self.ed_reads)==3 and self.ed_entries==[0xcb1650,0xcba4b0]
 def ed_read_contract(self,site,at,width,value,ready):
  self.ed_layout();assert ready and len(self.ed_reads)<4
  k=len(self.ed_reads);wanted=[(0xcb3280,self.n.base+0x16a2a50,4,0),(0xcb32bc,self.n.base+0x16a2a58,8,self.ed_table),
   (0xcba4b4,self.n.base+0xf7e230,8,self.ed_api),(0xcb3328,self.n.base+0x16a2a58,8,self.ed_table)][k]
  assert (site,at,width,value)==wanted and value==self.rd(at,width)
  assert len(self.ed_order)==[10,15,15,15][k]
  if k:assert self.ed_allocated
  if k==3:assert self.ed_resources==[self.n.base+0x1607090]
 def ed_next(self,site,sp,pointer,ready):
  self.ed_layout();assert ready and site==0xcb3338 and self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+site
  assert sp==self.u.reg_read(UC_ARM64_REG_SP)==self.ed_entry_sp-80 and pointer==self.n.base+0x16a2a90
  i=INS[site];op=next(o for o in i.operands if o.type==capstone.arm64.ARM64_OP_MEM);mem=op.mem
  address=DR.reg(self.u,C.reg_name(mem.base))+mem.disp
  if mem.index:
   assert op.ext==capstone.arm64.ARM64_EXT_INVALID and op.shift.type in (capstone.arm64.ARM64_SFT_INVALID,capstone.arm64.ARM64_SFT_LSL)
   assert DR.reg(self.u,C.reg_name(mem.index))==0
   address+=DR.reg(self.u,C.reg_name(mem.index))<<op.shift.value
  assert address==pointer and bytes(self.u.mem_read(self.n.base+site,4))==PE.get_data(site,4)
  assert len(self.ed_order)==16 and len(self.ed_reads)==4 and self.ed_returns==2 and not self.ed_frames
  assert self.ed_calloc_calls==1 and self.ed_OS_calls==1 and self.ed_resources==[self.n.base+0x1607090]
  assert self.rd(self.n.base+0x16a2a50,4)==512 and self.rd(self.n.base+0x16a2a58,8)==self.ed_table
  assert self.rd(self.ed_table,8)==self.n.base+0x1607060 and bytes(self.u.mem_read(self.ed_table+8,4088))==bytes(4088)
 def ed_model(self,at,data):
  key=next(k for k in self.before if k[0]<=at and at+len(data)<=k[1]+1)
  if key not in self.models:self.models[key]=bytearray(self.before[key])
  self.models[key][at-key[0]:at-key[0]+len(data)]=data
 def ed_record(self,site,at,data):
  width=len(data);value=int.from_bytes(data,"little");self.ed_effect(site,at,width,value,True)
  self.reject(self.ed_effect,[(site+4,at,width,value,True),(site,at+8,width,value,True),(site,at,width+1,value,True),(site,at,width,value^1,True),(site,at,width,value,False)])
  if self.n.stack<=at and at+width<=self.n.stack+65536:self.patch_stack(at,data)
  else:
   self.ed_model(at,data)
   if self.ed_table<=at and at+width<=self.ed_table+4096:self.ed_table_expected[at-self.ed_table:at-self.ed_table+width]=data
  self.ed_order.append((site,at,width));self.pending[at,width]=value
 def ed_read(self,u,a,at,width,value,_):
  if self.n.stack<=at and at+width<=self.n.stack+65536:return
  site=u.reg_read(UC_ARM64_REG_PC)-self.n.base;data=self.rd(at,width);owned=(site,at,width,data,True);self.ed_read_contract(*owned)
  self.reject(self.ed_read_contract,[(site+4,at,width,data,True),(site,at+1,width,data,True),(site,at,width+1,data,True),(site,at,width,data^1,True),(site,at,width,data,False)])
  self.ed_reads.append((site,at-self.n.base,width))
 def ed_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending
  if self.ed_frames and pc==self.ed_frames[-1]["ret"]:
   f=self.ed_frames.pop();assert all(u.reg_read(k)==v for k,v in f["saved"].items()) and u.reg_read(UC_ARM64_REG_X0)==f["result"]
   self.ed_returns+=1
  if r==0xcb3338:
   owned=(r,u.reg_read(UC_ARM64_REG_SP),n.base+0x16a2a90,True);self.ed_next(*owned)
   self.reject(self.ed_next,[(r+4,*owned[1:]),(r,owned[1]+16,*owned[2:]),(r,owned[1],owned[2]+8,True),(*owned[:3],False)])
   self.ed_stopped=True;u.emu_stop();return
  if r==0xcb75e0:
   owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1)],self.ed_table,True);self.ed_calloc(*owned)
   self.reject(self.ed_calloc,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,*owned[3:]),
    (r,owned[1],owned[2],[511,8],self.ed_table,True),(r,owned[1],owned[2],[512,9],self.ed_table,True),(r,owned[1],owned[2],owned[3],self.ed_table+16,True),(*owned[:5],False)])
   old=bytes(u.mem_read(self.ed_table,1));u.mem_write(self.ed_table,bytes([self.poison^1]))
   try:self.reject(self.ed_calloc,[owned])
   finally:u.mem_write(self.ed_table,old)
   self.ed_allocated=True;self.ed_calloc_calls+=1;self.ed_table_expected[:]=bytes(4096);self.ed_model(self.ed_table,bytes(4096))
   saved={k:u.reg_read(k) for k in NONVOL};u.mem_write(self.ed_table,bytes(4096));u.reg_write(UC_ARM64_REG_X0,self.ed_table);u.reg_write(UC_ARM64_REG_PC,owned[1])
   assert all(u.reg_read(k)==v for k,v in saved.items());return
  if pc==self.ed_api:
   args=[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(3)]
   owned=(pc,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),args,True);self.ed_api_contract(*owned)
   self.reject(self.ed_api_contract,[(pc+16,*owned[1:]),(pc,owned[1]+4,*owned[2:]),(pc,owned[1],owned[2]+16,args,True),
    (pc,owned[1],owned[2],[args[0]+8,4000,0],True),(pc,owned[1],owned[2],[args[0],3999,0],True),(pc,owned[1],owned[2],[args[0],4000,1],True),(*owned[:4],False)])
   self.ed_resources.append(args[0])
   try:self.reject(self.ed_api_contract,[owned])
   finally:self.ed_resources.pop()
   self.ed_resources.append(args[0]);self.ed_OS_calls+=1;saved={k:u.reg_read(k) for k in NONVOL};u.reg_write(UC_ARM64_REG_X0,1);u.reg_write(UC_ARM64_REG_PC,owned[1])
   assert all(u.reg_read(k)==v for k,v in saved.items());return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4)
  assert any(int(lo,16)<=r<=int(hi,16) for key in ("0xcb3260","0xcba4b0","0xcb1650") for lo,hi in PINS[key]["ranges"])
  if r in (0xcb1650,0xcba4b0):
   size=1 if r==0xcb1650 else 3;args=[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(size)]
   owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),args,True);self.ed_call(*owned);wrong=args.copy();wrong[0]+=8
   self.reject(self.ed_call,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,args,True),(r,owned[1],owned[2],wrong,True),(*owned[:4],False)])
   self.ed_entries.append(r);self.ed_frames.append({"ret":owned[1],"saved":{k:u.reg_read(k) for k in NONVOL},"result":0 if r==0xcb1650 else 1})
  self.ed_trace.append(r);i=INS[r]
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
    for off in range(0,width,8):self.ed_record(r,at+k*width+off,data[off:off+8])
 def run(self):
  u=self.u;n=self.n;stores=self.stores;neg=self.negatives;owned=(0xcb3260,self.ed_entry_sp,n.end,True)
  self.ed_entry(*owned);self.reject(self.ed_entry,[(owned[0]+4,*owned[1:]),(owned[0],owned[1]+16,*owned[2:]),(owned[0],owned[1],owned[2]+4,True),(*owned[:3],False)])
  for flag in ("ed_ready","ed_cells_ready","ed_alloc_ready","ed_resource_ready"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.ed_entry,[owned])
   finally:setattr(self,flag,old)
  for at,width in ((n.base+0x16a2a50,4),(n.base+0x16a2a58,8),(n.base+0xf7e230,8)):
   old=bytes(u.mem_read(at,width));self.wr(at,self.rd(at,width)^1,width)
   try:self.reject(self.ed_entry,[owned])
   finally:u.mem_write(at,old)
  self.before=self.snapshot();self.expected_stack=bytearray(u.mem_read(n.stack,65536))
  hooks=[u.hook_add(UC_HOOK_CODE,self.ed_code),u.hook_add(UC_HOOK_MEM_WRITE,self.eb_write),u.hook_add(UC_HOOK_MEM_READ,self.ed_read)]
  try:u.emu_start(n.base+0xcb3260,n.end,count=2000)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.ed_stopped and not self.pending;self.ed_layout();after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():
   assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"isolated original initializer memory mismatch"
  return {"original_instruction_visits":len(self.ed_trace),"exact_source_store_chunks":self.stores-stores,"independent_initializer_store_contracts":len(self.ed_order),
   "rejected_owned_requests":self.negatives-neg,"exact_dependency_reads":len(self.ed_reads),"original_nested_ABI_returns_exact":self.ed_returns,
   "exact_original_nested_callee_entries":len(self.ed_entries),"owned_allocation_calls":self.ed_calloc_calls,"owned_zeroed_allocation_bytes":4096,"owned_OS_API_calls":self.ed_OS_calls,
   "published_table_slots":512,"published_first_standard_stream_slots":1,"remaining_table_zero_bytes":4088,"first_resource_owned_model_ready":True,
   "isolated_initializer_memory_and_permissions_exact":True,"redzones_exact":True,"original_initializer_return_qualified":False,"stream_initializer_and_camera_state_join_qualified":False,
   "native_CRT_resource_initialization_qualified":False,"pointed_standard_stream_contents_qualified":False,
   "stop_before_RVA":"0xcb3338","next_dependency_RVA":"0x16a2a90","next_dependency_bytes":8,"current_SP_relative_initializer_entry":-80}
class Case(EC.Case):
 def __init__(self,*args):
  super().__init__(*args);self.ed_args=args
 def run(self):
  prior=super().run();before=self.snapshot();pc=self.u.reg_read(UC_ARM64_REG_PC)
  bootstrap=Bootstrap(*self.ed_args);assert bootstrap.u is not self.u;added=bootstrap.run()
  assert self.snapshot()==before and self.u.reg_read(UC_ARM64_REG_PC)==pc==self.n.base+0xcc6120
  assert self.rd(self.n.base+0x16a2a58,8)==0 and self.ec_lock_held
  added.update(camera_caller_memory_permissions_and_frontier_unchanged=True,initializer_isolated_from_camera_parent=True)
  return {"EC":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 rows=json.loads(json.dumps(rows));ancestor=json.loads((P.parent/"SOURCE-SAFE.json").read_text());assert [row["EC"] for row in rows]==ancestor["details"]
 report={"experiment":"E011ED","status":"PASS_BOUNDED_ORIGINAL_ISOLATED_STREAM_INITIALIZER_PUBLICATION","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
  "initializer_owned_cold_initial_value_authority":INITIAL_AUTH,"initializer_owned_provider_authority":OWNED_AUTH,
  "runtime_initial_value_model_authority":ancestor["runtime_initial_value_model_authority"],"details":rows,
  "original_stream_initializer_publication_prefix_qualified":True,"initializer_isolated_from_camera_parent":True,"camera_caller_memory_permissions_and_frontier_unchanged":True,
  "original_stream_initializer_return_qualified":False,"stream_initializer_and_camera_state_join_qualified":False,"native_allocator_implementation_qualified":False,
  "source_result_fixture_used":False,"native_rear_runtime_allowed":False,"native_CRT_resource_initialization_qualified":False,"native_runtime_scalar_and_pointer_selection_qualified":False,
  "pointed_standard_stream_contents_qualified":False,"stream_runtime_pointer_read_qualified":False,"file_open_or_contents_qualified":False,
  "full_outer_callee_return_qualified":False,"full_factory_or_first_helper_return_qualified":False,"new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,
  "production_code_changed":False,"private_raw_material_exported":False,"next_experiment":"E011EE"}
 keys=("original_instruction_visits","exact_source_store_chunks","independent_initializer_store_contracts","rejected_owned_requests","exact_dependency_reads",
 "original_nested_ABI_returns_exact","exact_original_nested_callee_entries","owned_allocation_calls","owned_zeroed_allocation_bytes","owned_OS_API_calls")
 report["added_totals"]={k:sum(row["added"][k] for row in rows) for k in keys};report["inherited_EC_totals"]=ancestor["added_totals"]
 for k in ("EB","EA","DZ","DY","DX","DW","DV","DU","DT","DS"):report["inherited_"+k+"_totals"]=ancestor["inherited_"+k+"_totals"]
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
