#!/usr/bin/env python3
"""Independent original low-level I/O block construction and publication; contexts not joined."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011ed-original-isolated-stream-initializer-publication/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="208e27ff50e0f1338284e101a324b8ec3cae25c6a9db211a5f659acf3f34abf6"
s=importlib.util.spec_from_file_location("ee_actual_ed_parent",P);ED=importlib.util.module_from_spec(s);s.loader.exec_module(ED)
PE=ED.PE;M=ED.M;C=ED.C;DR=ED.DR;NONVOL=ED.NONVOL;INS=dict(ED.INS);PINS=dict(ED.PINS)
EXTRA_PINS={
 "0xcc08e8":{"body_bytes":332,"ranges":[["0xcc08e8","0xcc0a33"]],"sha256":"0fd5d934868e2d438d497d94de0922455cf909e3553a24833a1f8cf659c7893b"},
 "0xcc05b8":{"body_bytes":204,"ranges":[["0xcc05b8","0xcc0683"]],"sha256":"2e8f62889f5850eb5275da5b71bc43cf777b62913547526e8c8c2b5ab5b53b87"}}
for entry,pin in EXTRA_PINS.items():
 body=b"".join(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in pin["ranges"])
 assert len(body)==pin["body_bytes"] and hashlib.sha256(body).hexdigest()==pin["sha256"]
 for lo,hi in pin["ranges"]:
  for at in range(int(lo,16),int(hi,16)+1,4):
   i=list(C.disasm(PE.get_data(at,4),at));assert len(i)==1;INS[at]=i[0]
 PINS[entry]=pin
INITIAL_AUTH=[{"RVA":"0x16a2a90","bytes":8,"section_writable":True,"virtual_zero_fill":True,"file_backed":False,"accepted_owned_initial_value":0,"native_runtime_selection_qualified":False}]
for t in INITIAL_AUTH:
 at=int(t["RVA"],16);sec=next(z for z in PE.sections if z.VirtualAddress<=at and at+t["bytes"]<=z.VirtualAddress+z.Misc_VirtualSize)
 assert sec.Characteristics&0x80000000 and at-sec.VirtualAddress>=sec.SizeOfRawData
OWNED_AUTH={"allocator_request_RVA":"0xcb75e0","allocator_return_RVA":"0xcc05dc","count":64,"element_bytes":72,"allocation_bytes":4608,
 "zeroed_allocation_provider_is_owned_model":True,"native_allocator_implementation_qualified":False,
 "lock_wrapper_RVA":"0xcb7300","lock_index":7,"lock_resource_RVA":"0x16a2fd8","lock_model_ready":True,"lock_return_RVA":"0xcc090c",
 "lock_import_cell_RVA":"0xf7e0b8","OS_void_return_is_owned_clobber_model":True,
 "resource_initializer_wrapper_RVA":"0xcba4b0","resource_initializer_return_RVA":"0xcc061c","import_cell_RVA":"0xf7e230",
 "record_resource_offset":0,"resource_bytes":40,"spin_count":4000,"flags":0,"resource_success_return_is_owned_model":True,
 "native_CRT_resource_initialization_qualified":False,"native_handles_or_file_contents_qualified":False}
PLANS=[(0xcc08ec,-64,8,"saved",UC_ARM64_REG_X19),(0xcc08ec,-56,8,"saved",UC_ARM64_REG_X20),
 (0xcc08f0,-48,8,"saved",UC_ARM64_REG_X21),(0xcc08f0,-40,8,"saved",UC_ARM64_REG_X22),
 (0xcc08f4,-32,8,"saved",UC_ARM64_REG_X23),(0xcc08f4,-24,8,"saved",UC_ARM64_REG_X24),
 (0xcc08f8,-16,8,"saved",UC_ARM64_REG_X25),(0xcc08fc,-96,8,"saved",UC_ARM64_REG_X29),(0xcc08fc,-88,8,"saved",UC_ARM64_REG_LR),
 (0xcc0914,-80,4,"scalar",0xffffffff),(0xcc091c,-76,4,"scalar",0),
 (0xcc05bc,-144,8,"saved",UC_ARM64_REG_X19),(0xcc05bc,-136,8,"saved",UC_ARM64_REG_X20),
 (0xcc05c0,-128,8,"scalar",0),(0xcc05c0,-120,8,"image",0x16a2a90),
 (0xcc05c4,-112,8,"scalar",0),(0xcc05c4,-104,8,"scalar",0xffffffff),
 (0xcc05c8,-160,8,"stack",-96),(0xcc05c8,-152,8,"image",0xcc093c)]
for k in range(64):
 for r,off,width,v in [(0xcc061c,40,8,0xffffffffffffffff),(0xcc061c,48,8,0),(0xcc0624,56,4,0x0a0a0000),
  (0xcc062c,60,1,10),(0xcc0634,61,1,0)]+[(0xcc0648,x,1,0) for x in range(62,67)]:
  PLANS.append((r,k*72+off,width,"block",v))
PLANS += [(0xcb1654,-176,8,"block_pointer",0),(0xcb1658,-192,8,"stack",-160),(0xcb1658,-184,8,"image",0xcc0668),(0xcc093c,0x16a2a90,8,"publication",0)]
assert len(PLANS)==663
OUT=Path(__file__).resolve().parent
class Bootstrap(ED.Bootstrap):
 def __init__(self,*args):
  super().__init__(*args)
  self.ee_ready=self.ee_cell_ready=self.ee_alloc_ready=self.ee_resource_ready=self.ee_lock_ready=True
  self.ee_block=self.n.heap+0x26000+self.bias;self.ee_block_expected=bytearray([self.poison]*4608);self.u.mem_write(self.ee_block-32,bytes([self.poison])*4672)
  self.ee_pending_old={};self.ee_allocated=False;self.ee_lock_held=False;self.ee_resources=[];self.ee_order=[];self.ee_reads=[];self.ee_trace=[]
  self.ee_frames=[];self.ee_entries=[];self.ee_returns=0;self.ee_calloc_calls=0;self.ee_OS_calls=0;self.ee_stopped=False
  self.ee_entry_sp=self.u.reg_read(UC_ARM64_REG_SP);self.ee_saved={k:self.u.reg_read(k) for k in [*NONVOL,UC_ARM64_REG_LR]}
 def logical(self):
  return super().logical()+(getattr(self,"ee_ready",False),getattr(self,"ee_cell_ready",False),getattr(self,"ee_alloc_ready",False),getattr(self,"ee_resource_ready",False),getattr(self,"ee_lock_ready",False),
   getattr(self,"ee_allocated",False),getattr(self,"ee_lock_held",False),tuple(getattr(self,"ee_resources",[])),tuple(getattr(self,"ee_order",[])),tuple(getattr(self,"ee_reads",[])),
   tuple(getattr(self,"ee_entries",[])),getattr(self,"ee_returns",0),getattr(self,"ee_calloc_calls",0),getattr(self,"ee_OS_calls",0))
 def ee_layout(self):
  assert self.ee_ready and self.ee_cell_ready and self.ee_alloc_ready and self.ee_resource_ready and self.ee_lock_ready
  u=self.u;n=self.n;assert self.rd(n.base+0xf7e230,8)==self.ed_api and self.rd(n.base+0xf7e0b8,8)==self.apis["EnterCriticalSection"]
  assert bytes(u.mem_read(self.ee_block-32,32))==bytes([self.poison])*32 and bytes(u.mem_read(self.ee_block+4608,32))==bytes([self.poison])*32
  actual=bytearray(u.mem_read(self.ee_block,4608))
  for (at,width),value in self.pending.items():
   if self.ee_block<=at and at+width<=self.ee_block+4608:
    off=at-self.ee_block;assert actual[off:off+width]==self.ee_pending_old[at,width]
    actual[off:off+width]=value.to_bytes(width,"little")
  assert actual==self.ee_block_expected
  assert not self.held and not self.inner_held and not self.crt_held and not self.srw_held and not self.ec_lock_held
  assert not self.ed_allocated and not self.ed_resources and self.rd(n.base+0x16a2a58,8)==0
 def ee_entry(self,site,sp,ret,ready):
  self.ee_layout();assert ready and site==0xcc08e8 and sp==self.ee_entry_sp==self.stacktop and ret==self.n.end
  assert self.u.reg_read(UC_ARM64_REG_SP)==sp and self.u.reg_read(UC_ARM64_REG_LR)==ret
  assert self.rd(self.n.base+0x16a2a90,8)==0 and not self.ee_order and not self.ee_reads and not self.ee_entries and not self.ee_allocated and not self.ee_resources and not self.ee_lock_held
 def ee_effect(self,site,at,width,value,ready):
  self.ee_layout();assert ready and len(self.ee_order)<len(PLANS)
  src,off,size,kind,v=PLANS[len(self.ee_order)]
  if kind=="block":
   address=self.ee_block+off;expected=v;assert self.ee_allocated and len(self.ee_resources)==off//72+1
  elif kind=="publication":
   address=self.n.base+off;expected=self.ee_block;assert len(self.ee_resources)==64 and self.ee_returns==67 and not self.ee_frames
  else:
   address=self.ee_entry_sp+off;expected=self.ee_saved[v] if kind=="saved" else self.n.base+v if kind=="image" else self.ee_entry_sp+v if kind=="stack" else self.ee_block if kind=="block_pointer" else v
  assert (site,at,width,value)==(src,address,size,expected) and self.ee_lock_held==(len(self.ee_order)>=9)
 def ee_calloc(self,site,ret,sp,args,pointer,ready):
  self.ee_layout();assert ready and not self.ee_allocated and self.ee_calloc_calls==0 and self.ee_lock_held
  assert site==0xcb75e0 and ret==self.u.reg_read(UC_ARM64_REG_LR)==self.n.base+0xcc05dc and sp==self.u.reg_read(UC_ARM64_REG_SP)==self.ee_entry_sp-160
  assert args==[64,72]==[self.u.reg_read(UC_ARM64_REG_X0),self.u.reg_read(UC_ARM64_REG_X1)] and pointer==self.ee_block and pointer%16==0
  assert len(self.ee_order)==19 and len(self.ee_reads)==2 and not self.ee_resources and self.rd(self.n.base+0x16a2a90,8)==0
  leases=self.reservations+self.dw_allocations+[(self.exit_storage,256),(self.dv_buffer,18832),(self.ed_table,4096)]+[(x,48) for x in self.dt_nodes]
  assert all(not(at-32<=pointer+4608+32 and pointer-32<=at+size+32) for at,size in leases)
 def ee_call(self,site,ret,sp,args,ready):
  self.ee_layout();assert ready
  k=len(self.ee_entries)
  if k==0:expected=(0xcb7300,0xcc090c,-96,[7],9,0);assert not self.ee_lock_held
  elif k==1:expected=(0xcc05b8,0xcc093c,-96,[],11,2);assert self.ee_lock_held
  elif 2<=k<66:
   j=k-2;expected=(0xcba4b0,0xcc061c,-160,[self.ee_block+j*72,4000,0],19+j*10,2+j*2)
   assert len(self.ee_resources)==j and self.ee_allocated and self.ee_lock_held
  else:assert k==66;expected=(0xcb1650,0xcc0668,-160,[0],659,130);assert len(self.ee_resources)==64 and self.ee_lock_held
  src,return_rva,off,formal,stores,reads=expected
  assert (site,ret,sp,args)==(src,self.n.base+return_rva,self.ee_entry_sp+off,formal)
  assert ret==self.u.reg_read(UC_ARM64_REG_LR) and sp==self.u.reg_read(UC_ARM64_REG_SP)
  assert args==[self.u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(len(formal))]
  assert len(self.ee_order)==stores and len(self.ee_reads)==reads
 def ee_api(self,pc,ret,sp,args,ready):
  self.ee_layout();assert ready
  if pc==self.apis["EnterCriticalSection"]:
   assert not self.ee_lock_held and self.ee_OS_calls==0 and len(self.ee_entries)==1 and len(self.ee_order)==9 and len(self.ee_reads)==1
   assert ret==self.n.base+0xcc090c and sp==self.ee_entry_sp-96 and args==[self.n.base+0x16a2fd8]
  else:
   assert pc==self.ed_api and self.ee_lock_held and self.ee_allocated
   j=len(self.ee_resources);assert j<64 and self.ee_OS_calls==j+1 and len(self.ee_entries)==j+3
   assert len(self.ee_order)==19+j*10 and len(self.ee_reads)==3+j*2
   assert ret==self.n.base+0xcc061c and sp==self.ee_entry_sp-160 and args==[self.ee_block+j*72,4000,0]
  assert pc==self.u.reg_read(UC_ARM64_REG_PC) and ret==self.u.reg_read(UC_ARM64_REG_LR) and sp==self.u.reg_read(UC_ARM64_REG_SP)
  assert args==[self.u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(len(args))]
 def ee_read_contract(self,site,at,width,value,ready):
  self.ee_layout();assert ready
  k=len(self.ee_reads)
  if k==0:expected=(0xcb7314,self.n.base+0xf7e0b8,8,self.apis["EnterCriticalSection"],9);assert not self.ee_lock_held
  elif k==1:expected=(0xcc0930,self.n.base+0x16a2a90,8,0,11);assert self.ee_lock_held
  else:
   j=(k-2)//2;assert j<64 and self.ee_allocated and self.ee_lock_held
   if k%2==0:
    expected=(0xcba4b4,self.n.base+0xf7e230,8,self.ed_api,19+j*10);assert len(self.ee_resources)==j
   else:
    expected=(0xcc0628,self.ee_block+j*72+61,1,0,22+j*10);assert len(self.ee_resources)==j+1
  src,address,size,wanted,stores=expected
  assert (site,at,width,value)==(src,address,size,wanted) and value==self.rd(at,width) and len(self.ee_order)==stores
 def ee_next(self,site,sp,pointer,ready):
  self.ee_layout();assert ready and site==0xcc0948 and self.u.reg_read(UC_ARM64_REG_PC)==self.n.base+site
  assert sp==self.u.reg_read(UC_ARM64_REG_SP)==self.ee_entry_sp-96 and pointer==self.n.base+0x16a2e90
  i=INS[site];mem=next(o.mem for o in i.operands if o.type==capstone.arm64.ARM64_OP_MEM)
  assert not mem.index and DR.reg(self.u,C.reg_name(mem.base))+mem.disp==pointer and C.reg_name(i.operands[0].reg).startswith("w")
  assert bytes(self.u.mem_read(self.n.base+site,4))==PE.get_data(site,4)
  assert len(self.ee_order)==663 and len(self.ee_reads)==130 and self.ee_returns==67 and len(self.ee_entries)==67 and not self.ee_frames
  assert self.ee_calloc_calls==1 and self.ee_OS_calls==65 and self.ee_lock_held and self.ee_resources==[self.ee_block+k*72 for k in range(64)]
  assert self.rd(self.n.base+0x16a2a90,8)==self.ee_block
  record=bytearray(72);record[40:48]=bytes([255])*8;record[56:60]=(0x0a0a0000).to_bytes(4,"little");record[60]=10
  assert bytes(self.u.mem_read(self.ee_block,4608))==bytes(record)*64
 def ee_record(self,site,at,data):
  width=len(data);value=int.from_bytes(data,"little");self.ee_effect(site,at,width,value,True)
  self.reject(self.ee_effect,[(site+4,at,width,value,True),(site,at+8,width,value,True),(site,at,width+1,value,True),(site,at,width,value^1,True),(site,at,width,value,False)])
  if self.n.stack<=at and at+width<=self.n.stack+65536:self.patch_stack(at,data)
  else:
   self.ed_model(at,data)
   if self.ee_block<=at and at+width<=self.ee_block+4608:self.ee_block_expected[at-self.ee_block:at-self.ee_block+width]=data
  self.ee_pending_old[at,width]=bytes(self.u.mem_read(at,width));self.ee_order.append((site,at,width));self.pending[at,width]=value
 def ee_read(self,u,a,at,width,value,_):
  if self.n.stack<=at and at+width<=self.n.stack+65536:return
  site=u.reg_read(UC_ARM64_REG_PC)-self.n.base;data=self.rd(at,width);owned=(site,at,width,data,True);self.ee_read_contract(*owned)
  self.reject(self.ee_read_contract,[(site+4,at,width,data,True),(site,at+1,width,data,True),(site,at,width+1,data,True),(site,at,width,data^1,True),(site,at,width,data,False)])
  self.ee_reads.append((site,at,width))
 def ee_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending
  if self.ee_frames and pc==self.ee_frames[-1]["ret"]:
   f=self.ee_frames.pop();assert all(u.reg_read(k)==v for k,v in f["saved"].items()) and u.reg_read(UC_ARM64_REG_X0)==f["result"];self.ee_returns+=1
  if r==0xcc0948:
   owned=(r,u.reg_read(UC_ARM64_REG_SP),n.base+0x16a2e90,True);self.ee_next(*owned)
   self.reject(self.ee_next,[(r+4,*owned[1:]),(r,owned[1]+16,*owned[2:]),(r,owned[1],owned[2]+4,True),(*owned[:3],False)])
   self.ee_stopped=True;u.emu_stop();return
  if r==0xcb75e0:
   owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1)],self.ee_block,True);self.ee_calloc(*owned)
   self.reject(self.ee_calloc,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,*owned[3:]),
    (r,owned[1],owned[2],[63,72],self.ee_block,True),(r,owned[1],owned[2],[64,73],self.ee_block,True),(r,owned[1],owned[2],owned[3],self.ee_block+16,True),(*owned[:5],False)])
   old=bytes(u.mem_read(self.ee_block,1));u.mem_write(self.ee_block,bytes([self.poison^1]))
   try:self.reject(self.ee_calloc,[owned])
   finally:u.mem_write(self.ee_block,old)
   self.ee_allocated=True;self.ee_calloc_calls+=1;self.ee_block_expected[:]=bytes(4608);self.ed_model(self.ee_block,bytes(4608))
   saved={k:u.reg_read(k) for k in NONVOL};u.mem_write(self.ee_block,bytes(4608));u.reg_write(UC_ARM64_REG_X0,self.ee_block);u.reg_write(UC_ARM64_REG_PC,owned[1])
   assert all(u.reg_read(k)==v for k,v in saved.items());return
  if pc in (self.apis["EnterCriticalSection"],self.ed_api):
   lock=pc==self.apis["EnterCriticalSection"];size=1 if lock else 3;args=[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(size)]
   owned=(pc,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),args,True);self.ee_api(*owned);wrong=args.copy();wrong[0]+=8
   self.reject(self.ee_api,[(pc+16,*owned[1:]),(pc,owned[1]+4,*owned[2:]),(pc,owned[1],owned[2]+16,args,True),(pc,owned[1],owned[2],wrong,True),(*owned[:4],False)])
   if lock:self.ee_lock_held=True
   else:self.ee_resources.append(args[0])
   try:self.reject(self.ee_api,[owned])
   finally:
    if lock:self.ee_lock_held=False
    else:self.ee_resources.pop()
   if lock:self.ee_lock_held=True
   else:self.ee_resources.append(args[0])
   self.ee_OS_calls+=1;saved={k:u.reg_read(k) for k in NONVOL};u.reg_write(UC_ARM64_REG_X0,self.api_clobber if lock else 1);u.reg_write(UC_ARM64_REG_PC,owned[1])
   assert all(u.reg_read(k)==v for k,v in saved.items());return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4)
  assert any(int(lo,16)<=r<=int(hi,16) for key in ("0xcc08e8","0xcc05b8","0xcb7300","0xcba4b0","0xcb1650") for lo,hi in PINS[key]["ranges"])
  if r in (0xcb7300,0xcc05b8,0xcba4b0,0xcb1650):
   size=3 if r==0xcba4b0 else 0 if r==0xcc05b8 else 1;args=[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(size)]
   owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),args,True);self.ee_call(*owned);wrong=args.copy()
   if wrong:wrong[0]+=8
   else:wrong=[8]
   self.reject(self.ee_call,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,args,True),(r,owned[1],owned[2],wrong,True),(*owned[:4],False)])
   self.ee_entries.append(r);result=self.api_clobber if r==0xcb7300 else self.ee_block if r==0xcc05b8 else 1 if r==0xcba4b0 else 0
   self.ee_frames.append({"entry":r,"ret":owned[1],"saved":{k:u.reg_read(k) for k in NONVOL},"result":result})
  self.ee_trace.append(r);i=INS[r]
  if i.mnemonic.startswith(("str","stp","stnp","st1","stur")):
   mi=next(k for k,o in enumerate(i.operands) if o.type==capstone.arm64.ARM64_OP_MEM);mem=i.operands[mi]
   at=DR.reg(u,C.reg_name(mem.mem.base))+mem.mem.disp
   if mem.mem.index:
    assert mem.ext in (capstone.arm64.ARM64_EXT_INVALID,capstone.arm64.ARM64_EXT_SXTW) and mem.shift.type in (capstone.arm64.ARM64_SFT_INVALID,capstone.arm64.ARM64_SFT_LSL)
    index=DR.reg(u,C.reg_name(mem.mem.index))
    if mem.ext==capstone.arm64.ARM64_EXT_SXTW:
     assert r==0xcc093c and mem.shift.value==3 and index==0
     index&=0xffffffff
     if index&0x80000000:index-=1<<32
    at+=index<<mem.shift.value
   ops=list(i.operands[:mi]) if i.mnemonic=="st1" else i.operands[:2] if i.mnemonic in ("stp","stnp") else i.operands[:1]
   for k,o in enumerate(ops):
    name=C.reg_name(o.reg)
    if i.mnemonic=="st1":assert name.startswith("v");name="q"+name[1:]
    width=16 if name.startswith("q") else 8 if name.startswith(("x","d")) or name in ("fp","lr") else 2 if name.startswith("h") else 1 if name.startswith("b") else 4
    if i.mnemonic=="st1":width=16 if o.vas==capstone.arm64.ARM64_VAS_16B else 8
    elif i.mnemonic.endswith("h"):width=2
    elif i.mnemonic.endswith("b"):width=1
    data=(DR.reg(u,name)&((1<<(width*8))-1)).to_bytes(width,"little")
    for off in range(0,width,8):self.ee_record(r,at+k*width+off,data[off:off+8])
 def run(self):
  u=self.u;n=self.n;stores=self.stores;neg=self.negatives;owned=(0xcc08e8,self.ee_entry_sp,n.end,True)
  self.ee_entry(*owned);self.reject(self.ee_entry,[(owned[0]+4,*owned[1:]),(owned[0],owned[1]+16,*owned[2:]),(owned[0],owned[1],owned[2]+4,True),(*owned[:3],False)])
  for flag in ("ee_ready","ee_cell_ready","ee_alloc_ready","ee_resource_ready","ee_lock_ready"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.ee_entry,[owned])
   finally:setattr(self,flag,old)
  for at,width in ((n.base+0x16a2a90,8),(n.base+0xf7e230,8),(n.base+0xf7e0b8,8)):
   old=bytes(u.mem_read(at,width));self.wr(at,self.rd(at,width)^1,width)
   try:self.reject(self.ee_entry,[owned])
   finally:u.mem_write(at,old)
  self.before=self.snapshot();self.expected_stack=bytearray(u.mem_read(n.stack,65536))
  hooks=[u.hook_add(UC_HOOK_CODE,self.ee_code),u.hook_add(UC_HOOK_MEM_WRITE,self.eb_write),u.hook_add(UC_HOOK_MEM_READ,self.ee_read)]
  try:u.emu_start(n.base+0xcc08e8,n.end,count=10000)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.ee_stopped and not self.pending;self.ee_layout();after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():
   assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"isolated original lowIO memory mismatch"
  return {"original_instruction_visits":len(self.ee_trace),"exact_source_store_chunks":self.stores-stores,"independent_lowIO_store_contracts":len(self.ee_order),
   "rejected_owned_requests":self.negatives-neg,"exact_dependency_reads":len(self.ee_reads),"original_nested_ABI_returns_exact":self.ee_returns,
   "exact_original_nested_callee_entries":len(self.ee_entries),"owned_allocation_calls":self.ee_calloc_calls,"owned_zeroed_allocation_bytes":4608,"owned_OS_API_calls":self.ee_OS_calls,
   "published_lowIO_blocks":1,"records_per_block":64,"record_bytes":72,"owned_ready_record_resources":64,"lowIO_lock_owned_model_held":True,
   "isolated_lowIO_memory_and_permissions_exact":True,"redzones_exact":True,"original_lowIO_block_constructor_return_qualified":True,"original_lowIO_initializer_return_qualified":False,
   "all_initializer_and_camera_states_join_qualified":False,"native_CRT_resource_initialization_qualified":False,"native_handles_or_file_contents_qualified":False,
   "stop_before_RVA":"0xcc0948","next_dependency_RVA":"0x16a2e90","next_dependency_bytes":4,"current_SP_relative_lowIO_entry":-96}
class Case(ED.EC.Case):
 def __init__(self,*args):
  super().__init__(*args);self.ee_args=args
 def run(self):
  ec=super().run();camera_before=self.snapshot();camera_pc=self.u.reg_read(UC_ARM64_REG_PC)
  stream=ED.Bootstrap(*self.ee_args);ed_added=stream.run()
  assert stream.u is not self.u and self.snapshot()==camera_before and self.u.reg_read(UC_ARM64_REG_PC)==camera_pc==self.n.base+0xcc6120
  assert self.rd(self.n.base+0x16a2a58,8)==0 and self.ec_lock_held
  ed_added.update(camera_caller_memory_permissions_and_frontier_unchanged=True,initializer_isolated_from_camera_parent=True)
  prior={"EC":ec,"added":ed_added};stream_before=stream.snapshot();stream_pc=stream.u.reg_read(UC_ARM64_REG_PC);stream_logical=stream.logical()
  lowio=Bootstrap(*self.ee_args);assert lowio.u is not stream.u and lowio.u is not self.u;added=lowio.run()
  assert self.snapshot()==camera_before and self.u.reg_read(UC_ARM64_REG_PC)==camera_pc
  assert stream.snapshot()==stream_before and stream.u.reg_read(UC_ARM64_REG_PC)==stream_pc==stream.n.base+0xcb3338 and stream.logical()==stream_logical
  added.update(camera_caller_memory_permissions_and_frontier_unchanged=True,stream_initializer_memory_permissions_and_frontier_unchanged=True,lowIO_initializer_isolated_from_other_contexts=True)
  return {"ED":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 rows=json.loads(json.dumps(rows));ancestor=json.loads((P.parent/"SOURCE-SAFE.json").read_text());assert [row["ED"] for row in rows]==ancestor["details"]
 report={"experiment":"E011EE","status":"PASS_BOUNDED_ORIGINAL_ISOLATED_LOWIO_BLOCK_PUBLICATION","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
  "lowIO_owned_cold_initial_value_authority":INITIAL_AUTH,"lowIO_owned_provider_authority":OWNED_AUTH,
  "initializer_owned_cold_initial_value_authority":ancestor["initializer_owned_cold_initial_value_authority"],"initializer_owned_provider_authority":ancestor["initializer_owned_provider_authority"],
  "runtime_initial_value_model_authority":ancestor["runtime_initial_value_model_authority"],"details":rows,
  "original_lowIO_block_construction_and_publication_qualified":True,"original_lowIO_block_constructor_return_qualified":True,"lowIO_initializer_isolated_from_other_contexts":True,
  "camera_caller_memory_permissions_and_frontier_unchanged":True,"stream_initializer_memory_permissions_and_frontier_unchanged":True,
  "original_lowIO_initializer_return_qualified":False,"original_stream_initializer_return_qualified":False,"all_initializer_and_camera_states_join_qualified":False,
  "stream_initializer_and_camera_state_join_qualified":False,"actual_loader_CRT_startup_caller_qualified":False,"native_allocator_implementation_qualified":False,
  "source_result_fixture_used":False,"native_rear_runtime_allowed":False,"native_CRT_resource_initialization_qualified":False,"native_runtime_scalar_and_pointer_selection_qualified":False,
  "pointed_standard_stream_contents_qualified":False,"stream_runtime_pointer_read_qualified":False,"native_handles_or_file_contents_qualified":False,"file_open_or_contents_qualified":False,
  "full_outer_callee_return_qualified":False,"full_factory_or_first_helper_return_qualified":False,"new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,
  "production_code_changed":False,"private_raw_material_exported":False,"next_experiment":"E011EF"}
 keys=("original_instruction_visits","exact_source_store_chunks","independent_lowIO_store_contracts","rejected_owned_requests","exact_dependency_reads",
 "original_nested_ABI_returns_exact","exact_original_nested_callee_entries","owned_allocation_calls","owned_zeroed_allocation_bytes","owned_OS_API_calls")
 report["added_totals"]={k:sum(row["added"][k] for row in rows) for k in keys};report["inherited_ED_totals"]=ancestor["added_totals"]
 for k in ("EC","EB","EA","DZ","DY","DX","DW","DV","DU","DT","DS"):report["inherited_"+k+"_totals"]=ancestor["inherited_"+k+"_totals"]
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n");print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
