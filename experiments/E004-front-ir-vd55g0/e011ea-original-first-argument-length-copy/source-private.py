#!/usr/bin/env python3
"""Original first argument length and copy with retained parser ownership."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011dz-original-parser-dispatch-variadic-argument/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="eb8571dc568be812ddb4a41ff9f3aec6fc798fd28272dbcb8a3454ab375e2d5b"
s=importlib.util.spec_from_file_location("ea_actual_dz_parent",P);DZ=importlib.util.module_from_spec(s);s.loader.exec_module(DZ)
PE=DZ.PE;M=DZ.M;C=DZ.C;DR=DZ.DR;NONVOL=DZ.NONVOL;INS=dict(DZ.INS);PINS=dict(DZ.PINS)
EXTRA_PINS={'0xf5e3e0': {'body_bytes': 184, 'ranges': [['0xf5e3e0', '0xf5e497']], 'sha256': 'ce5ad5d84ac2a5ff6ef3bf2de15ffb746b4d31ef4a73c941101e906506a749cf'}, '0xcad1f0': {'body_bytes': 200, 'ranges': [['0xcad1f0', '0xcad2b7']], 'sha256': '7c090b8f136c3934fd4da97aa8de33dcd52259357c6bb6f81d34892bd4705d05'}, '0xf5d480': {'body_bytes': 664, 'ranges': [['0xf5d480', '0xf5d4c7'], ['0xf5d4e0', '0xf5d5c3'], ['0xf5d5e0', '0xf5d62b'], ['0xf5d640', '0xf5d75f']], 'sha256': 'b7d952b2014e55260ce44226d14da79db6ec60e9d7d6756fafcb106340871dc3'}}
for entry,pin in EXTRA_PINS.items():
 body=b"".join(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in pin["ranges"])
 assert len(body)==pin["body_bytes"] and hashlib.sha256(body).hexdigest()==pin["sha256"]
 for lo,hi in pin["ranges"]:
  for at in range(int(lo,16),int(hi,16)+1,4):
   i=list(C.disasm(PE.get_data(at,4),at));assert len(i)==1;INS[at]=i[0]
 PINS[entry]=pin
AUTH={'RVA': '0x10f0380', 'bytes': 16, 'file_backed': True, 'section_nonwritable': True, 'sha256': 'c1092551461cd5ac0ad08f8fae02ab47447e1fd1c0b5d3bc068c969e57053a95', 'literal_bytes_including_NUL': 13, 'literal_sha256': '3072831f71eeaba699423425c497fac7b56a1657abae573e8ac18b073018fb77', 'terminator_at_last_literal_byte': True, 'original_literal_contents_exported': False}
ARG_RVA=0x10f0380;ARG_WINDOW=PE.get_data(ARG_RVA,16);ARG=ARG_WINDOW[:13];LENGTH=12
assert hashlib.sha256(ARG_WINDOW).hexdigest()==AUTH["sha256"] and hashlib.sha256(ARG).hexdigest()==AUTH["literal_sha256"]
assert ARG[-1]==0 and all(ARG[:-1]) and ARG.index(0)==LENGTH
sec=next(t for t in PE.sections if t.VirtualAddress<=ARG_RVA and ARG_RVA+16<=t.VirtualAddress+t.Misc_VirtualSize)
assert not sec.Characteristics&0x80000000 and ARG_RVA-sec.VirtualAddress+16<=sec.SizeOfRawData
READS=[(0xf5e3e8,ARG_RVA,8),(0xf5e3e8,ARG_RVA+8,8),(0xf5d594,ARG_RVA,8)]+[(0xf5d5a0,ARG_RVA+k,1) for k in range(8,12)]
PLANS=[(0xcace94,-3032,4,"length",0),(0xcab288,-3304,2,"scalar",0),(0xcab28c,-3302,1,"scalar",0)]
for ret in (0xcab3f0,0xcab590):
 PLANS.extend([(0xcad1f4,-3360,8,"stack",-3104),(0xcad1f4,-3352,8,"scalar",0xffffffff),(0xcad1f8,-3344,8,"scalar",48),(0xcad1f8,-3336,8,"stack",-3312),(0xcad1fc,-3328,8,"scalar",32),(0xcad200,-3376,8,"stack",-3280),(0xcad200,-3368,8,"image",ret)])
PLANS.extend([(0xf5d598,-1392,8,"argument",0)]+[(0xf5d5a4,-1392+k,1,"argument",k) for k in range(8,12)]+[(0xcad26c,-3136,8,"stack",-1380),(0xcad27c,-3120,8,"length",0),(0xcad29c,-3072,4,"length",0)])
OUT=Path(__file__).resolve().parent
class Case(DZ.Case):
 def __init__(self,*args):
  super().__init__(*args);self.ea_ready=True;self.ea_data_ready=True;self.ea_trace=[];self.ea_reads=[];self.ea_order=[]
  self.ea_entries=[];self.ea_calls=[];self.ea_returns=0;self.ea_consumer_returns=0;self.ea_cookie_pop=None;self.ea_cookie_returns=0;self.ea_stopped=False
  self.ea_destination_expected=bytearray(640)
 def logical(self):
  return super().logical()+(getattr(self,"ea_ready",False),getattr(self,"ea_data_ready",False),tuple(getattr(self,"ea_reads",[])),
   tuple(getattr(self,"ea_order",[])),tuple(getattr(self,"ea_entries",[])),getattr(self,"ea_returns",0),getattr(self,"ea_consumer_returns",0),getattr(self,"ea_cookie_returns",0))
 def dx_layout(self):
  # Advance only the earlier zero-destination invariant, through exact original copy effects.
  self.dw_layout();self.dw_constructed()
  assert self.dx_ready and len(self.dw_leases)==3 and not self.dw_frames
  assert self.dw_nested_returns==self.dw_heap_clear_returns==self.dw_stack_clear_returns==1
  assert self.rd(self.dw_allocations[0][0]+8,8)==self.dw_allocations[1][0]
  assert bytes(self.u.mem_read(self.dw_stack_receiver,640))==bytes(self.ea_destination_expected)
  assert bytes(self.u.mem_read(self.n.base+DZ.DY.DX.DATA_RVA,DZ.DY.DX.DATA_BYTES))==DZ.DY.DX.DATA
 def ea_layout(self):
  self.dz_layout();assert self.ea_ready and self.ea_data_ready and self.dz_stopped and len(self.dz_reads)==9 and len(self.dz_order)==38
  assert bytes(self.u.mem_read(self.n.base+ARG_RVA,16))==ARG_WINDOW
 def ea_entry(self,site,sp,args,ready):
  self.ea_layout();self.dz_next(site,sp,args,ready)
  assert not self.ea_reads and not self.ea_order and not self.ea_entries
 def ea_read_contract(self,site,at,width,value,ready):
  assert ready and self.ea_ready and self.ea_data_ready and len(self.ea_reads)<7
  src,rva,size=READS[len(self.ea_reads)]
  assert (site,at,width)==(src,self.n.base+rva,size)
  assert value==self.rd(at,width)==int.from_bytes(PE.get_data(rva,size),"little")
 def ea_effect(self,site,at,width,value,ready):
  assert ready and self.ea_ready and self.ea_data_ready and self.held and self.inner_held and len(self.ea_order)<25
  src,off,size,kind,v=PLANS[len(self.ea_order)]
  expected=self.n.base+v if kind=="image" else self.dw_entry_sp+v if kind=="stack" else LENGTH if kind=="length" else int.from_bytes(ARG[v:v+size],"little") if kind=="argument" else v
  assert (site,at,width,value)==(src,self.dw_entry_sp+off,size,expected)
  assert self.n.stack<=at and at+width<=self.n.stack+65536
  if kind=="argument":
   assert self.dw_stack_receiver<=at and at+width<=self.dw_stack_receiver+LENGTH and at-self.dw_stack_receiver==v
 def ea_call(self,site,ret,sp,args,ready):
  self.ea_layout();u=self.u;n=self.n;k=len(self.ea_entries)
  assert ready and k<4 and site==[0xf5e3e0,0xcad1f0,0xcad1f0,0xf5d480][k]
  assert ret==u.reg_read(UC_ARM64_REG_LR)==n.base+[0xcace94,0xcab3f0,0xcab590,0xcad260][k]
  assert sp==u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp+[-3360,-3312,-3312,-3376][k]
  expected=[[n.base+ARG_RVA,0x7fffffff],[self.dw_entry_sp-1984,self.dw_entry_sp-3304,0,self.dw_entry_sp-3072],
   [self.dw_entry_sp-1984,n.base+ARG_RVA,LENGTH,self.dw_entry_sp-3072],[self.dw_stack_receiver,n.base+ARG_RVA,LENGTH]][k]
  assert args==expected==[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(len(args))]
  assert len(self.ea_order)==[0,3,10,17][k] and len(self.ea_reads)==[0,2,2,2][k]
 def ea_next(self,site,sp,pointer,ready):
  self.ea_layout();u=self.u;n=self.n
  assert ready and site==0xca984c and u.reg_read(UC_ARM64_REG_PC)==n.base+site and sp==u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp-3200
  assert pointer==self.rd(self.dw_entry_sp-3088,8)==n.base+DZ.DATA_RVA+2
  assert len(self.ea_order)==25 and len(self.ea_reads)==7 and self.ea_returns==4 and self.ea_consumer_returns==2 and self.ea_cookie_returns==1
  assert len(self.dz_frames)==1 and self.dz_frames[0]["entry"]==0xca94e8 and not self.ea_calls and self.ea_cookie_pop is None
  assert bytes(u.mem_read(self.dw_stack_receiver,640))==ARG[:LENGTH]+bytes(640-LENGTH)
  assert self.rd(self.dw_entry_sp-3136,8)==self.dw_stack_receiver+LENGTH and self.rd(self.dw_entry_sp-3120,8)==LENGTH and self.rd(self.dw_entry_sp-3072,4)==LENGTH
  assert self.rd(self.dw_entry_sp-3080,8)==self.dw_entry_sp-1488
 def ea_read(self,u,a,at,width,value,_):
  if self.n.base+ARG_RVA<=at<self.n.base+ARG_RVA+16:
   site=u.reg_read(UC_ARM64_REG_PC)-self.n.base;data=self.rd(at,width);owned=(site,at,width,data,True);self.ea_read_contract(*owned)
   self.reject(self.ea_read_contract,[(site+4,at,width,data,True),(site,at+1,width,data,True),(site,at,width+1,data,True),(site,at,width,data^1,True),(site,at,width,data,False)])
   self.ea_reads.append((hex(site),hex(at-self.n.base),width));return
  self.dz_read(u,a,at,width,value,_)
 def ea_record(self,site,at,data):
  v=int.from_bytes(data,"little");width=len(data);self.ea_effect(site,at,width,v,True)
  self.reject(self.ea_effect,[(site+4,at,width,v,True),(site,at+8,width,v,True),(site,at,width+1,v,True),(site,at,width,v^1,True),(site,at,width,v,False)])
  if self.dw_stack_receiver<=at<self.dw_stack_receiver+LENGTH:
   offset=at-self.dw_stack_receiver;self.ea_destination_expected[offset:offset+width]=ARG[offset:offset+width]
  self.patch_stack(at,data);self.ea_order.append((site,at-self.dw_entry_sp,width));self.pending[at,width]=v
 def ea_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending
  if r==0xca984c:
   owned=(r,u.reg_read(UC_ARM64_REG_SP),self.rd(self.dw_entry_sp-3088,8),True);self.ea_next(*owned)
   self.reject(self.ea_next,[(r+4,*owned[1:]),(r,owned[1]+16,*owned[2:]),(r,owned[1],owned[2]+1,True),(*owned[:3],False)])
   self.ea_stopped=True;u.emu_stop();return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4)
  if self.ea_calls and pc==self.ea_calls[-1]["ret"]:
   f=self.ea_calls.pop();assert all(u.reg_read(k)==v for k,v in f["saved"].items()),"EA original callee ABI"
   expected=LENGTH if f["entry"]==0xf5e3e0 else self.dw_stack_receiver if f["entry"]==0xf5d480 or f["ret"]==n.base+0xcab590 else self.dw_entry_sp-1984
   assert u.reg_read(UC_ARM64_REG_X0)==expected;self.ea_returns+=1
  if r in (0xcab1f8,0xca9840):
   f=self.dz_frames.pop();assert pc==f["ret"] and all(u.reg_read(k)==v for k,v in f["saved"].items()) and u.reg_read(UC_ARM64_REG_X0)==1
   self.ea_consumer_returns+=1
  if r==0xcab640:
   f=self.ea_cookie_pop;assert f and pc==f["ret"] and u.reg_read(UC_ARM64_REG_SP)==f["sp"]+16
   assert all(u.reg_read(k)==v for k,v in f["saved"].items() if k!=UC_ARM64_REG_SP)
   self.ea_cookie_returns+=1;self.ea_cookie_pop=None
  if r==0x11f0:
   assert self.ea_cookie_pop is None and u.reg_read(UC_ARM64_REG_LR)==n.base+0xcab640 and u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp-3296
   self.ea_cookie_pop={"ret":u.reg_read(UC_ARM64_REG_LR),"sp":u.reg_read(UC_ARM64_REG_SP),"saved":{k:u.reg_read(k) for k in NONVOL}}
  if r in (0xf5e3e0,0xcad1f0,0xf5d480):
   k=len(self.ea_entries);args=[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range([2,4,4,3][k])]
   owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),args,True);self.ea_call(*owned)
   wrong=args.copy();wrong[0]+=8
   self.reject(self.ea_call,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,args,True),(r,owned[1],owned[2],wrong,True),(*owned[:4],False)])
   self.ea_entries.append(r);self.ea_calls.append({"entry":r,"ret":owned[1],"saved":{k:u.reg_read(k) for k in NONVOL}})
  self.ea_trace.append(r);i=INS[r]
  if r==0xf5d5a4:
   assert i.mnemonic=="st4" and len(i.operands)==5
   mem=i.operands[4];assert mem.type==capstone.arm64.ARM64_OP_MEM and not mem.mem.index
   at=DR.reg(u,C.reg_name(mem.mem.base))+mem.mem.disp
   for k,o in enumerate(i.operands[:4]):
    assert o.vector_index in (-1,0);name=C.reg_name(o.reg);assert name.startswith("v")
    data=(DR.reg(u,"q"+name[1:])&0xff).to_bytes(1,"little");self.ea_record(r,at+k,data)
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
     addr=at+k*width+off;chunk=data[off:off+8];self.ea_record(r,addr,chunk)
 def run(self):
  prior=super().run();n=self.n;u=self.u;stores=self.stores;neg=self.negatives
  owned=(0xcace90,u.reg_read(UC_ARM64_REG_SP),[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1)],True);self.ea_entry(*owned)
  wrong=owned[2].copy();wrong[0]+=8
  self.reject(self.ea_entry,[(owned[0]+4,*owned[1:]),(owned[0],owned[1]+16,*owned[2:]),(owned[0],owned[1],wrong,True),(*owned[:3],False)])
  for flag in ("ea_ready","ea_data_ready","dz_ready","dz_data_ready","held","inner_held"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.ea_entry,[owned])
   finally:setattr(self,flag,old)
  loc=n.base+ARG_RVA;old=bytes(u.mem_read(loc,16));u.mem_write(loc,bytes([old[0]^1])+old[1:])
  try:self.reject(self.ea_entry,[owned])
  finally:u.mem_write(loc,old)
  hooks=[u.hook_add(UC_HOOK_CODE,self.ea_code),u.hook_add(UC_HOOK_MEM_WRITE,self.write),u.hook_add(UC_HOOK_MEM_READ,self.ea_read)]
  try:u.emu_start(n.base+0xcace90,n.end,count=2000)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.ea_stopped and not self.pending and u.reg_read(UC_ARM64_REG_PC)==n.base+0xca984c
  self.ea_layout();after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():
   assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"cumulative retained EA memory mismatch"
  added={"original_instruction_visits":len(self.ea_trace),"exact_source_store_chunks":self.stores-stores,"independent_argument_store_contracts":len(self.ea_order),
   "rejected_owned_requests":self.negatives-neg,"exact_immutable_argument_reads":len(self.ea_reads),"original_callee_ABI_returns_exact":self.ea_returns,
   "original_argument_consumer_ABI_returns_exact":self.ea_consumer_returns,"cookie_pop_convention_returns_exact":self.ea_cookie_returns,
   "exact_original_callee_entries":len(self.ea_entries),"owned_allocation_calls":0,"owned_OS_API_calls":0,
   "first_argument_length":LENGTH,"exact_private_argument_bytes_copied":LENGTH,"destination_remaining_zero_bytes":640-LENGTH,
   "first_argument_complete_source_length_and_copy_qualified":True,"nine_live_allocations_retained":True,
   "whole_original_entry_to_frontier_memory_and_permissions_exact":True,"outer_and_nested_registry_locks_held":True,"CRT_and_SRW_released":True,
   "retained_active_consumer_frames":7,"stop_before_RVA":"0xca984c","next_dependency_RVA":"0x1370762","next_dependency_bytes":1,
   "current_SP_relative_outer_entry":-3200,"variadic_cursor_relative_outer_entry":-1488,"output_cursor_relative_outer_entry":-1380,
   "outer_callee_return_not_reached_RVA":"0x5f8ea8"}
  return {"DZ":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 rows=json.loads(json.dumps(rows));ancestor=json.loads((P.parent/"SOURCE-SAFE.json").read_text());assert [r["DZ"] for r in rows]==ancestor["details"]
 report={"experiment":"E011EA","status":"PASS_BOUNDED_ORIGINAL_FIRST_ARGUMENT_LENGTH_AND_COPY","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
  "argument_data_authority":AUTH,"runtime_initial_value_model_authority":ancestor["runtime_initial_value_model_authority"],"details":rows,
  "source_result_fixture_used":False,"native_rear_runtime_allowed":False,"first_argument_length_and_copy_qualified":True,
  "full_constant_consumer_return_qualified":False,"full_outer_callee_return_qualified":False,"full_factory_or_first_helper_return_qualified":False,
  "native_runtime_scalar_and_pointer_selection_qualified":False,"alternate_nonzero_runtime_flag_paths_qualified":False,"pointed_locale_tables_qualified":False,
  "cookie_leaf_has_SP_preserving_ABI":False,"stack_growth_guard_page_OS_qualified":False,"remaining_format_or_argument_continuation_qualified":False,
  "new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False,"next_experiment":"E011EB"}
 keys=("original_instruction_visits","exact_source_store_chunks","independent_argument_store_contracts","rejected_owned_requests","exact_immutable_argument_reads",
 "original_callee_ABI_returns_exact","original_argument_consumer_ABI_returns_exact","cookie_pop_convention_returns_exact","exact_original_callee_entries","owned_allocation_calls","owned_OS_API_calls")
 report["added_totals"]={k:sum(row["added"][k] for row in rows) for k in keys};report["inherited_DZ_totals"]=ancestor["added_totals"]
 for k in ("DY","DX","DW","DV","DU","DT","DS"):report["inherited_"+k+"_totals"]=ancestor["inherited_"+k+"_totals"]
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
