#!/usr/bin/env python3
"""Bounded original parser dispatch and first variadic argument acquisition."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011dy-original-cold-runtime-context-receiver/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="ffe2bff630c784a3190e34a910f83d5271f53cdeeb46b24eaca5a71f448e228d"
s=importlib.util.spec_from_file_location("dz_actual_dy_parent",P);DY=importlib.util.module_from_spec(s);s.loader.exec_module(DY)
PE=DY.PE;M=DY.M;C=DY.C;DR=DY.DR;NONVOL=DY.NONVOL;INS=dict(DY.INS);PINS=dict(DY.PINS)
EXTRA_PINS={
"0xca94e8":{"body_bytes":1028,"ranges":[["0xca94e8","0xca98eb"]],"sha256":"8e1aa3dcf0d019df157030034475dc1fe87defc61d765e4f5deecac6b56b150a"},
"0xcab178":{"body_bytes":1252,"ranges":[["0xcab178","0xcab65b"]],"sha256":"dd3ea3cf979b2411d9dabcce803e553a9f29929dcce44a6f623b0666de57835f"},
"0xcacdf8":{"body_bytes":184,"ranges":[["0xcacdf8","0xcaceaf"]],"sha256":"e4e3964e1c8eb7a8fb470069d381b057652975b02ac2450c7249b715cf068a3c"},
"0xca65a8":{"body_bytes":64,"ranges":[["0xca65a8","0xca65e7"]],"sha256":"73db5979ec481e935a61010e1c9120f40197182accea2442c026aabdba25957c"}}
for entry,pin in EXTRA_PINS.items():
 body=b"".join(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in pin["ranges"])
 assert len(body)==pin["body_bytes"] and hashlib.sha256(body).hexdigest()==pin["sha256"]
 for lo,hi in pin["ranges"]:
  for at in range(int(lo,16),int(hi,16)+1,4):
   i=list(C.disasm(PE.get_data(at,4),at));assert len(i)==1;INS[at]=i[0]
 PINS[entry]=pin
DATA_RVA=0x1370760;DATA=PE.get_data(DATA_RVA,7)
DATA_AUTH={"RVA":"0x1370760","bytes_including_NUL":7,"sha256":"3c6150311763e7162e56773dd3a25a716f251c11cd14f9a4ebc57531ecb50430","file_backed":True,"section_nonwritable":True,"terminator_at_last_byte":True,"original_literal_contents_exported":False}
CELLS=[
(0xf8b21b,1,"4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a"),
(0xf8b222,1,"4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a"),
(0xca98f0,4,"25cb28d3768e2a7055eeedc507751889495fc6131f85dab1ce0ce72ff303b324"),
(0xf8b2b7,1,"beead77994cf573341ec17b58bbf7eb34d2711c993c1d976b128b3188dc1829a"),
(0xf8b2a2,1,"ca358758f6d27e6cf45272937977a748fd88391db679ceda7dc7bf1f005ee879"),
(0xca9908,4,"447e12701a0d03cf90a4ad7f02f1a045b35d284e26fe520440edb116d76bf700"),
(0xcab724,4,"fcd04ecb4a5b36f9f092c7c47141908f25c274f1a1758e78731a16d0fd4897d7")]
AUTH=[DATA_AUTH]+[{"RVA":hex(at),"bytes":width,"sha256":pin,"file_backed":True,"section_nonwritable":True,"sparse_cell_authority_only":True} for at,width,pin in CELLS]
for at,width,pin in [(DATA_RVA,len(DATA),DATA_AUTH["sha256"])]+CELLS:
 sec=next(t for t in PE.sections if t.VirtualAddress<=at and at+width<=t.VirtualAddress+t.Misc_VirtualSize)
 assert not sec.Characteristics&0x80000000 and at-sec.VirtualAddress+width<=sec.SizeOfRawData
 assert hashlib.sha256(PE.get_data(at,width)).hexdigest()==pin
assert DATA[-1]==0 and all(DATA[:-1])
READS=[(0xca984c,DATA_RVA,1),(0xca95b8,0xf8b21b,1),(0xca95d8,0xf8b222,1),(0xca95f4,0xca98f0,4),
(0xca984c,DATA_RVA+1,1),(0xca95b8,0xf8b2b7,1),(0xca95d8,0xf8b2a2,1),(0xca95f4,0xca9908,4),(0xcab1c4,0xcab724,4)]
PLANS=[
(0xca94ec,-3184,8,"scalar",640),(0xca94ec,-3176,8,"stack",-1392),
(0xca94f0,-3168,8,"scalar",0),(0xca94f0,-3160,8,"scalar",0),(0xca94f4,-3152,8,"input",23),
(0xca94f8,-3200,8,"stack",-1952),(0xca94f8,-3192,8,"image",0xca634c),
(0xca9568,-1976,4,"scalar",1),(0xca9584,-3032,4,"scalar",0),(0xca9588,-3068,1,"scalar",0),
(0xca9850,-3088,8,"image",DATA_RVA+1),(0xca9854,-3047,1,"data",0),(0xca95dc,-3068,1,"scalar",1),
(0xca971c,-3048,1,"scalar",0),(0xca9720,-3064,8,"scalar",0),(0xca9720,-3056,8,"scalar",0xffffffff),
(0xca9724,-3028,1,"scalar",0),(0xca9850,-3088,8,"image",DATA_RVA+2),(0xca9854,-3047,1,"data",1),
(0xca95dc,-3068,1,"cell",0xf8b2a2),
(0xcab17c,-3280,8,"stack",-3200),(0xcab17c,-3272,8,"image",0xca9840),
(0xcab180,-3264,8,"stack",-3104),(0xcab180,-3256,8,"image",0xf8b210),
(0xcab184,-3248,8,"scalar",1),(0xcab184,-3240,8,"scalar",0),
(0xcab188,-3232,8,"scalar",0xffffffff),(0xcab188,-3224,8,"image",0x160a1f0),
(0xcab18c,-3216,8,"image",0x13f2000),(0x11e0,-3288,8,"cookie_frame",-3296),
(0xcab1a8,-3312,8,"scalar",0xfffffffffffffffe),
(0xcacdfc,-3344,8,"stack",-3104),(0xcacdfc,-3336,8,"image",0xf8b210),
(0xcace00,-3328,8,"scalar",1),(0xcace04,-3360,8,"stack",-3280),(0xcace04,-3352,8,"image",0xcab1f8),
(0xcace24,-3080,8,"stack",-1488),(0xcace38,-3040,8,"image",0x10f0380)]
OUT=Path(__file__).resolve().parent
class Case(DY.Case):
 def __init__(self,*args):
  super().__init__(*args)
  self.dz_ready=True;self.dz_data_ready=True;self.dz_reads=[];self.dz_order=[];self.dz_trace=[];self.dz_frames=[]
  self.dz_cookie_frame=None;self.dz_cookie_returns=0;self.dz_leaf_frame=None;self.dz_leaf_returns=0;self.dz_stopped=False;self.dz_inputs=None
 def logical(self):
  return super().logical()+(getattr(self,"dz_ready",False),getattr(self,"dz_data_ready",False),tuple(getattr(self,"dz_reads",[])),
   tuple(getattr(self,"dz_order",[])),len(getattr(self,"dz_frames",[])),getattr(self,"dz_cookie_returns",0),getattr(self,"dz_leaf_returns",0))
 def dz_layout(self):
  self.dy_layout();assert self.dz_ready and self.dz_data_ready and self.dy_stopped and len(self.dy_order)==44 and len(self.dy_reads)==4
  for at,width,pin in [(DATA_RVA,len(DATA),DATA_AUTH["sha256"])]+CELLS:
   assert hashlib.sha256(bytes(self.u.mem_read(self.n.base+at,width))).hexdigest()==pin
 def dz_entry(self,site,sp,args,ready):
  self.dz_layout();self.dy_next(site,sp,args,ready)
  assert not self.dz_order and not self.dz_reads and not self.dz_frames
 def dz_effect(self,site,at,width,value,ready):
  assert ready and self.dz_ready and self.dz_data_ready and self.held and self.inner_held and len(self.dz_order)<len(PLANS)
  src,off,size,kind,v=PLANS[len(self.dz_order)]
  expected=self.n.base+v if kind=="image" else self.dw_entry_sp+v if kind=="stack" else self.dz_inputs[v] if kind=="input" else DATA[v] if kind=="data" else PE.get_data(v,1)[0] if kind=="cell" else ((self.dw_entry_sp+v-self.cookie)&((1<<64)-1)) if kind=="cookie_frame" else v
  assert (site,at,width,value)==(src,self.dw_entry_sp+off,size,expected)
  assert self.n.stack<=at and at+width<=self.dw_stack_receiver
 def dz_read_contract(self,site,at,width,value,ready):
  assert ready and self.dz_ready and self.dz_data_ready and len(self.dz_reads)<len(READS)
  src,rva,size=READS[len(self.dz_reads)]
  assert (site,at,width)==(src,self.n.base+rva,size)
  assert value==self.rd(at,width)==int.from_bytes(PE.get_data(rva,size),"little")
 def dz_call(self,site,ret,sp,args,ready):
  self.dz_layout();k=len(self.dz_frames);n=self.n;u=self.u
  assert ready and k<3 and site==[0xca94e8,0xcab178,0xcacdf8][k]
  assert ret==u.reg_read(UC_ARM64_REG_LR)==n.base+[0xca634c,0xca9840,0xcab1f8][k]
  assert sp==u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp+[-3136,-3200,-3312][k]
  expected=[self.dw_entry_sp-3104,self.dw_stack_receiver,640,n.base+DATA_RVA,self.dw_entry_sp-1888,self.dw_entry_sp-1496] if k==0 else [self.dw_entry_sp-3104]
  assert args==expected==[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(len(args))]
  assert len(self.dz_reads)==[0,8,9][k] and len(self.dz_order)==[0,20,31][k]
 def dz_leaf(self,site,ret,sp,args,ready):
  self.dz_layout();u=self.u;n=self.n
  assert ready and site==0xca65a8 and ret==u.reg_read(UC_ARM64_REG_LR)==n.base+0xcace4c
  assert sp==u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp-3360
  assert args==[0,DATA[1],0]==[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(3)]
  assert len(self.dz_order)==38 and len(self.dz_reads)==9 and len(self.dz_frames)==3 and self.dz_leaf_frame is None
 def dz_next(self,site,sp,args,ready):
  self.dz_layout();u=self.u;n=self.n
  assert ready and site==0xcace90 and u.reg_read(UC_ARM64_REG_PC)==n.base+site
  assert sp==u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp-3360
  assert args==[n.base+0x10f0380,0x7fffffff]==[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(2)]
  assert len(self.dz_order)==38 and len(self.dz_reads)==9 and len(self.dz_frames)==3 and self.dz_cookie_returns==self.dz_leaf_returns==1
  assert self.rd(self.dw_entry_sp-3080,8)==self.dw_entry_sp-1488 and self.rd(self.dw_entry_sp-3040,8)==n.base+0x10f0380
  assert self.rd(self.dw_entry_sp-3088,8)==n.base+DATA_RVA+2 and self.rd(self.dw_entry_sp-3047,1)==DATA[1]
 def dz_read(self,u,a,at,width,value,_):
  if self.n.base+DATA_RVA<=at<self.n.base+DATA_RVA+len(DATA) or any(at==self.n.base+rva for rva,size,pin in CELLS):
   site=u.reg_read(UC_ARM64_REG_PC)-self.n.base;data=self.rd(at,width);owned=(site,at,width,data,True);self.dz_read_contract(*owned)
   self.reject(self.dz_read_contract,[(site+4,at,width,data,True),(site,at+1,width,data,True),(site,at,width+1,data,True),(site,at,width,data^1,True),(site,at,width,data,False)])
   self.dz_reads.append((hex(site),hex(at-self.n.base),width));return
  self.dy_read(u,a,at,width,value,_)
 def dz_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending
  if r==0xcace90:
   owned=(r,u.reg_read(UC_ARM64_REG_SP),[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1)],True);self.dz_next(*owned)
   wrong=owned[2].copy();wrong[0]+=8
   self.reject(self.dz_next,[(r+4,*owned[1:]),(r,owned[1]+16,*owned[2:]),(r,owned[1],wrong,True),(*owned[:3],False)])
   self.dz_stopped=True;u.emu_stop();return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4)
  if r==0xcab198:
   f=self.dz_cookie_frame;assert f and pc==f["ret"] and u.reg_read(UC_ARM64_REG_SP)==f["sp"]-16
   assert all(u.reg_read(k)==v for k,v in f["saved"].items() if k!=UC_ARM64_REG_SP)
   assert self.rd(f["sp"]-8,8)==((f["sp"]-16-self.cookie)&((1<<64)-1));self.dz_cookie_returns+=1;self.dz_cookie_frame=None
  if r==0xcace4c:
   f=self.dz_leaf_frame;assert f and pc==f["ret"] and all(u.reg_read(k)==v for k,v in f["saved"].items()) and u.reg_read(UC_ARM64_REG_X0)==0
   self.dz_leaf_returns+=1;self.dz_leaf_frame=None
  if r in (0xca94e8,0xcab178,0xcacdf8):
   k=len(self.dz_frames);args=[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(6 if k==0 else 1)]
   owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),args,True);self.dz_call(*owned)
   wrong=args.copy();wrong[0]+=8
   self.reject(self.dz_call,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,args,True),(r,owned[1],owned[2],wrong,True),(*owned[:4],False)])
   self.dz_frames.append({"entry":r,"ret":owned[1],"saved":{k:u.reg_read(k) for k in NONVOL}})
  if r==0x11d0:
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+0xcab198 and u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp-3280 and self.dz_cookie_frame is None
   self.dz_cookie_frame={"ret":u.reg_read(UC_ARM64_REG_LR),"sp":u.reg_read(UC_ARM64_REG_SP),"saved":{k:u.reg_read(k) for k in NONVOL}}
  if r==0xca65a8:
   args=[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(3)];owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),args,True);self.dz_leaf(*owned)
   wrong=args.copy();wrong[0]=1
   self.reject(self.dz_leaf,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,args,True),(r,owned[1],owned[2],wrong,True),(*owned[:4],False)])
   self.dz_leaf_frame={"ret":owned[1],"saved":{k:u.reg_read(k) for k in NONVOL}}
  self.dz_trace.append(r);i=INS[r]
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
     addr=at+k*width+off;chunk=data[off:off+8];v=int.from_bytes(chunk,"little");self.dz_effect(r,addr,len(chunk),v,True)
     self.reject(self.dz_effect,[(r+4,addr,len(chunk),v,True),(r,addr+8,len(chunk),v,True),(r,addr,len(chunk)+1,v,True),(r,addr,len(chunk),v^1,True),(r,addr,len(chunk),v,False)])
     self.patch_stack(addr,chunk);self.dz_order.append((r,addr-self.dw_entry_sp,len(chunk)));self.pending[addr,len(chunk)]=v
 def run(self):
  prior=super().run();n=self.n;u=self.u;stores=self.stores;neg=self.negatives
  self.dz_inputs={k:u.reg_read(globals()[f"UC_ARM64_REG_X{k}"]) for k in range(31)}
  owned=(0xca6348,u.reg_read(UC_ARM64_REG_SP),[u.reg_read(globals()[f"UC_ARM64_REG_X{k}"]) for k in range(6)],True);self.dz_entry(*owned)
  wrong=owned[2].copy();wrong[0]+=8
  self.reject(self.dz_entry,[(owned[0]+4,*owned[1:]),(owned[0],owned[1]+16,*owned[2:]),(owned[0],owned[1],wrong,True),(*owned[:3],False)])
  for flag in ("dz_ready","dz_data_ready","dy_ready","dy_loader_ready","held","inner_held"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.dz_entry,[owned])
   finally:setattr(self,flag,old)
  for at,width,pin in [(DATA_RVA,len(DATA),DATA_AUTH["sha256"])]+CELLS:
   loc=n.base+at;old=bytes(u.mem_read(loc,width));u.mem_write(loc,bytes([old[0]^1])+old[1:])
   try:self.reject(self.dz_entry,[owned])
   finally:u.mem_write(loc,old)
  hooks=[u.hook_add(UC_HOOK_CODE,self.dz_code),u.hook_add(UC_HOOK_MEM_WRITE,self.write),u.hook_add(UC_HOOK_MEM_READ,self.dz_read)]
  try:u.emu_start(n.base+0xca6348,n.end,count=2000)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.dz_stopped and not self.pending and u.reg_read(UC_ARM64_REG_PC)==n.base+0xcace90 and self.dz_cookie_frame is self.dz_leaf_frame is None
  self.dz_layout();after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():
   assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"cumulative retained DZ memory mismatch"
  added={"original_instruction_visits":len(self.dz_trace),"exact_source_store_chunks":self.stores-stores,"independent_parser_store_contracts":len(self.dz_order),
   "rejected_owned_requests":self.negatives-neg,"exact_immutable_data_reads":len(self.dz_reads),"cookie_frame_returns_convention_exact":self.dz_cookie_returns,
   "scalar_helper_ABI_returns_exact":self.dz_leaf_returns,"exact_nested_consumer_entries":len(self.dz_frames),"owned_allocation_calls":0,"owned_OS_API_calls":0,
   "first_variadic_argument_pointer_acquired":True,"variadic_cursor_advanced_by_8":True,"nine_live_allocations_retained":True,"stack_destination_640_bytes_still_zero":True,
   "whole_original_entry_to_frontier_memory_and_permissions_exact":True,"outer_and_nested_registry_locks_held":True,"CRT_and_SRW_released":True,
   "retained_active_consumer_frames":9,"stop_before_RVA":"0xcace90","next_callee_RVA":"0xf5e3e0","next_callee_return_RVA":"0xcace94",
   "current_SP_relative_outer_entry":-3360,"next_argument_pointer_RVA":"0x10f0380","next_string_limit":0x7fffffff,"variadic_cursor_relative_outer_entry":-1488,
   "outer_callee_return_not_reached_RVA":"0x5f8ea8"}
  return {"DY":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 rows=json.loads(json.dumps(rows));ancestor=json.loads((P.parent/"SOURCE-SAFE.json").read_text());assert [r["DY"] for r in rows]==ancestor["details"]
 report={"experiment":"E011DZ","status":"PASS_BOUNDED_ORIGINAL_PARSER_DISPATCH_AND_VARIADIC_ARGUMENT","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
  "immutable_data_authority":AUTH,"runtime_initial_value_model_authority":DY.MODEL_AUTHORITY,"details":rows,"source_result_fixture_used":False,"native_rear_runtime_allowed":False,
  "bounded_literal_and_sparse_parser_cells_qualified":True,"pointed_argument_string_contents_or_length_qualified":False,
  "full_constant_consumer_return_qualified":False,"full_outer_callee_return_qualified":False,"full_factory_or_first_helper_return_qualified":False,
  "native_runtime_scalar_and_pointer_selection_qualified":False,"alternate_nonzero_runtime_flag_paths_qualified":False,"pointed_locale_tables_qualified":False,
  "cookie_leaf_has_SP_preserving_ABI":False,"stack_growth_guard_page_OS_qualified":False,"next_string_helper_qualified":False,
  "new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False,"next_experiment":"E011EA"}
 keys=("original_instruction_visits","exact_source_store_chunks","independent_parser_store_contracts","rejected_owned_requests","exact_immutable_data_reads","cookie_frame_returns_convention_exact",
  "scalar_helper_ABI_returns_exact","exact_nested_consumer_entries","owned_allocation_calls","owned_OS_API_calls")
 report["added_totals"]={k:sum(row["added"][k] for row in rows) for k in keys};report["inherited_DY_totals"]=ancestor["added_totals"]
 for k in ("DX","DW","DV","DU","DT","DS"):report["inherited_"+k+"_totals"]=ancestor["inherited_"+k+"_totals"]
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
