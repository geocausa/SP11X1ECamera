#!/usr/bin/env python3
"""Original remaining arguments and complete retained formatter return."""
from pathlib import Path
import hashlib,importlib.util,itertools,json,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
P=R/"experiments/E004-front-ir-vd55g0/e011ea-original-first-argument-length-copy/source-private.py"
assert hashlib.sha256(P.read_bytes()).hexdigest()=="687b2f430bdaa46ae62697c08633e81b13dc464c1de5b5b5a50f1be4ce7e70f3"
s=importlib.util.spec_from_file_location("eb_actual_ea_parent",P);EA=importlib.util.module_from_spec(s);s.loader.exec_module(EA)
PE=EA.PE;M=EA.M;C=EA.C;DR=EA.DR;NONVOL=EA.NONVOL;INS=dict(EA.INS);PINS=dict(EA.PINS)
EXTRA_PINS={'0xca8658': {'body_bytes': 304, 'ranges': [['0xca8658', '0xca8787']], 'sha256': '81b50e4947531268083b5f3b4115ddff3323d0fc37e4f2672d694f3d6f087652'}}
for entry,pin in EXTRA_PINS.items():
 body=b"".join(PE.get_data(int(lo,16),int(hi,16)-int(lo,16)+1) for lo,hi in pin["ranges"])
 assert len(body)==pin["body_bytes"] and hashlib.sha256(body).hexdigest()==pin["sha256"]
 for lo,hi in pin["ranges"]:
  for at in range(int(lo,16),int(hi,16)+1,4):
   i=list(C.disasm(PE.get_data(at,4),at));assert len(i)==1;INS[at]=i[0]
 PINS[entry]=pin
ARG_AUTH=[{'RVA': '0x10f03b0', 'bytes': 16, 'literal_RVA': '0x10f03b0', 'literal_bytes_including_NUL': 2, 'sha256': 'dad2ac2c3a4b7d322405d01acbb713a7042ed906bb4ec81c01ccd4021e838901', 'literal_sha256': '1472d0645f552820b5472b91341c2d9a118c8a96f4a72758d6aeeb14c10a1107', 'file_backed': True, 'section_nonwritable': True, 'terminator_at_last_literal_byte': True, 'original_literal_contents_exported': False, 'literal_offset_in_window': 0}, {'RVA': '0x13f1f20', 'bytes': 48, 'literal_RVA': '0x13f1f28', 'literal_bytes_including_NUL': 25, 'sha256': '973753c7f15d0cf4a464c323cee1d3a83724994a71bdffc9813b5f1b8e2a65c3', 'literal_sha256': 'f6576fcf7a6d985d27efdd1f30e911cdfbe9d1e64a17a6e07a19d078789a2e28', 'file_backed': True, 'section_nonwritable': True, 'terminator_at_last_literal_byte': True, 'original_literal_contents_exported': False, 'literal_offset_in_window': 8}]
CELL_AUTH=[{'RVA': '0xf8b230', 'bytes': 1, 'sha256': '4bf5122f344554c53bde2ebb8cd2b7e3d1600ad631c385a5d7cce23c7785459a', 'file_backed': True, 'section_nonwritable': True, 'sparse_cell_authority_only': True}]
FORMAT=EA.DZ.DATA;FORMAT_RVA=EA.DZ.DATA_RVA
ARGS=[PE.get_data(int(t["literal_RVA"],16),t["literal_bytes_including_NUL"]) for t in ARG_AUTH]
LENGTHS=[len(t)-1 for t in ARGS];assert LENGTHS==[1,24]
for t in ARG_AUTH+CELL_AUTH:
 at=int(t["RVA"],16);width=t["bytes"];sec=next(z for z in PE.sections if z.VirtualAddress<=at and at+width<=z.VirtualAddress+z.Misc_VirtualSize)
 assert not sec.Characteristics&0x80000000 and at-sec.VirtualAddress+width<=sec.SizeOfRawData
 assert hashlib.sha256(PE.get_data(at,width)).hexdigest()==t["sha256"]
for t,blob in zip(ARG_AUTH,ARGS):
 assert blob[-1]==0 and all(blob[:-1]) and hashlib.sha256(blob).hexdigest()==t["literal_sha256"]
OUTPUT=EA.ARG[:EA.LENGTH]+b"".join(t[:-1] for t in ARGS);TOTAL=len(OUTPUT);assert TOTAL==37 and all(OUTPUT)
READS=[]
for pos,t in zip((2,4),ARG_AUTH):
 READS.extend([(0xca984c,FORMAT_RVA+pos,1),(0xca95b8,0xf8b21b,1),(0xca95d8,0xf8b230,1),(0xca95f4,0xca98f0,4),(0xca984c,FORMAT_RVA+pos+1,1),(0xca95b8,0xf8b2b7,1),(0xca95d8,0xf8b2a2,1),(0xca95f4,0xca9908,4),(0xcab1c4,0xcab724,4)])
 lo=int(t["RVA"],16);ptr=int(t["literal_RVA"],16)
 READS.extend([(0xf5e3e8,lo,8),(0xf5e3e8,lo+8,8)])
 if pos==2:READS.append((0xf5d4bc,ptr,1))
 else:READS.extend([(0xf5e440,lo+16,8),(0xf5e440,lo+24,8),(0xf5e454,lo+32,8),(0xf5e454,lo+40,8),(0xf5d588,ptr,8),(0xf5d588,ptr+8,8),(0xf5d594,ptr+16,8)])
READS.append((0xca984c,FORMAT_RVA+6,1));assert len(READS)==31
PLANS=[];produced=EA.LENGTH
for k,(pos,t,length) in enumerate(zip((2,4),ARG_AUTH,LENGTHS)):
 ptr=int(t["literal_RVA"],16)
 PLANS.extend([(0xca9850,-3088,8,"image",FORMAT_RVA+pos+1),(0xca9854,-3047,1,"format",pos),(0xca95dc,-3068,1,"scalar",1),(0xca971c,-3048,1,"scalar",0),(0xca9720,-3064,8,"scalar",0),(0xca9720,-3056,8,"scalar",0xffffffff),(0xca9724,-3028,1,"scalar",0),(0xca9850,-3088,8,"image",FORMAT_RVA+pos+2),(0xca9854,-3047,1,"format",pos+1),(0xca95dc,-3068,1,"scalar",7)])
 PLANS.extend([(0xcab17c,-3280,8,"stack",-3200),(0xcab17c,-3272,8,"image",0xca9840),(0xcab180,-3264,8,"stack",-3104),(0xcab180,-3256,8,"image",0xf8b210),(0xcab184,-3248,8,"scalar",1),(0xcab184,-3240,8,"scalar",0),(0xcab188,-3232,8,"scalar",0xffffffff),(0xcab188,-3224,8,"image",0x160a1f0),(0xcab18c,-3216,8,"image",0x13f2000),(0x11e0,-3288,8,"cookie_frame",-3296),(0xcab1a8,-3312,8,"scalar",0xfffffffffffffffe)])
 PLANS.extend([(0xcacdfc,-3344,8,"stack",-3104),(0xcacdfc,-3336,8,"image",0xf8b210),(0xcace00,-3328,8,"scalar",1),(0xcace04,-3360,8,"stack",-3280),(0xcace04,-3352,8,"image",0xcab1f8),(0xcace24,-3080,8,"stack",-1496+8*(k+2)),(0xcace38,-3040,8,"image",ptr),(0xcace94,-3032,4,"scalar",length),(0xcab288,-3304,2,"scalar",0),(0xcab28c,-3302,1,"scalar",0)])
 for ret in (0xcab3f0,0xcab590):
  PLANS.extend([(0xcad1f4,-3360,8,"stack",-3104),(0xcad1f4,-3352,8,"scalar",0xffffffff),(0xcad1f8,-3344,8,"scalar",48),(0xcad1f8,-3336,8,"stack",-3312),(0xcad1fc,-3328,8,"scalar",32),(0xcad200,-3376,8,"stack",-3280),(0xcad200,-3368,8,"image",ret)])
 if k==0:PLANS.append((0xf5d4c0,-1392+produced,1,"output",produced))
 else:PLANS.extend([(0xf5d58c,-1392+produced,8,"output",produced),(0xf5d58c,-1392+produced+8,8,"output",produced+8),(0xf5d598,-1392+produced+16,8,"output",produced+16)])
 produced+=length
 PLANS.extend([(0xcad26c,-3136,8,"stack",-1392+produced),(0xcad27c,-3120,8,"scalar",produced),(0xcad29c,-3072,4,"scalar",produced)])
PLANS.extend([(0xca9850,-3088,8,"image",FORMAT_RVA+7),(0xca9854,-3047,1,"format",6),(0xca9874,-1976,4,"scalar",2),(0xca63d0,-1392+TOTAL,1,"scalar",0),(0xcb1654,-3152,8,"scalar",640),(0xcb1658,-3168,8,"stack",-1952),(0xcb1658,-3160,8,"image",0xca63e0),(0xcad944,-753,1,"scalar",0),(0xca865c,-1936,8,"scalar",TOTAL),(0xca865c,-1928,8,"stack",-1392),(0xca8660,-1920,8,"scalar",1),(0xca8660,-1912,8,"scalar",640),(0xca8664,-1968,8,"stack",-1904),(0xca8664,-1960,8,"image",0xcad9ac),(0x6bd98,-1760,4,"scalar",TOTAL),(0x6bdb8,-1756,4,"scalar",TOTAL),(0x7ace0,-1616,4,"scalar",TOTAL),(0x7ac80,-1552,4,"scalar",TOTAL),(0x7ac88,-1544,8,"scalar",0)]);assert len(PLANS)==119
DX=EA.DZ.DY.DX;DY=EA.DZ.DY;OUT=Path(__file__).resolve().parent
class Case(EA.Case):
 def __init__(self,*args):
  super().__init__(*args)
  self.eb_ready=True;self.eb_data_ready=True;self.eb_trace=[];self.eb_reads=[];self.eb_order=[];self.eb_entries=[];self.eb_calls=[];self.eb_returns=0
  self.eb_cookie_entries=[];self.eb_cookie_frame=None;self.eb_cookie_returns=[];self.eb_dx_returns=0;self.eb_dy_returns=0;self.eb_dz_returns=0;self.eb_stopped=False
 def logical(self):
  return super().logical()+(getattr(self,"eb_ready",False),getattr(self,"eb_data_ready",False),tuple(getattr(self,"eb_reads",[])),tuple(getattr(self,"eb_order",[])),
   tuple(getattr(self,"eb_entries",[])),tuple(getattr(self,"eb_cookie_entries",[])),tuple(getattr(self,"eb_cookie_returns",[])),
   getattr(self,"eb_returns",0),getattr(self,"eb_dx_returns",0),getattr(self,"eb_dy_returns",0),getattr(self,"eb_dz_returns",0))
 def dy_layout(self):
  # Retire only caller frames whose original return and saved ABI were verified below.
  self.dx_layout();n=self.n;u=self.u
  assert self.dy_ready and self.dy_loader_ready and n.base==PE.OPTIONAL_HEADER.ImageBase
  assert self.rd(n.base+0x17a1150,8)==0 and self.rd(n.base+0x16a2a84,4)==0
  assert bytes(u.mem_read(n.base+DY.PAIR_RVA,16))==DY.PAIR and self.rd(n.base+0x1607000,8)==self.cookie
  assert [f["entry"] for f in self.dx_frames]==[0x7ac38,0x7aca0,0x6bdd0,0x6bd48][:4-self.eb_dx_returns]
  assert self.dx_reads==1 and len(self.dx_order)==33 and self.dx_leaf_returns==1
 def eb_layout(self):
  self.ea_layout();assert self.eb_ready and self.eb_data_ready and self.ea_stopped and len(self.ea_order)==25 and len(self.ea_reads)==7
  assert [f["entry"] for f in self.dy_frames]==[0xcad868,0xca6280][:2-self.eb_dy_returns]
  assert [f["entry"] for f in self.dz_frames]==[0xca94e8][:1-self.eb_dz_returns]
  for t in ARG_AUTH+CELL_AUTH:
   assert hashlib.sha256(bytes(self.u.mem_read(self.n.base+int(t["RVA"],16),t["bytes"]))).hexdigest()==t["sha256"]
 def eb_entry(self,site,sp,pointer,ready):
  self.eb_layout();self.ea_next(site,sp,pointer,ready)
  assert not self.eb_reads and not self.eb_order and not self.eb_entries and not self.eb_cookie_entries
 def eb_read_contract(self,site,at,width,value,ready):
  assert ready and self.eb_ready and self.eb_data_ready and len(self.eb_reads)<len(READS)
  src,rva,size=READS[len(self.eb_reads)]
  assert (site,at,width)==(src,self.n.base+rva,size)
  assert value==self.rd(at,width)==int.from_bytes(PE.get_data(rva,size),"little")
 def eb_effect(self,site,at,width,value,ready):
  assert ready and self.eb_ready and self.eb_data_ready and self.held and self.inner_held and len(self.eb_order)<len(PLANS)
  src,off,size,kind,v=PLANS[len(self.eb_order)]
  expected=self.n.base+v if kind=="image" else self.dw_entry_sp+v if kind=="stack" else FORMAT[v] if kind=="format" else int.from_bytes(OUTPUT[v:v+size],"little") if kind=="output" else ((self.dw_entry_sp+v-self.cookie)&((1<<64)-1)) if kind=="cookie_frame" else v
  assert (site,at,width,value)==(src,self.dw_entry_sp+off,size,expected)
  assert self.n.stack<=at and at+width<=self.n.stack+65536
  if kind=="output":assert at-self.dw_stack_receiver==v and EA.LENGTH<=v and v+width<=TOTAL
 def eb_call_contract(self,site,ret,sp,args,ready):
  self.eb_layout();u=self.u;n=self.n;k=len(self.eb_entries);assert ready and k<16
  if k<14:
   iteration,j=divmod(k,7);ptr=int(ARG_AUTH[iteration]["literal_RVA"],16);length=LENGTHS[iteration];start=EA.LENGTH+sum(LENGTHS[:iteration])
   src=[0xcab178,0xcacdf8,0xca65a8,0xf5e3e0,0xcad1f0,0xcad1f0,0xf5d480][j]
   return_rva=[0xca9840,0xcab1f8,0xcace4c,0xcace94,0xcab3f0,0xcab590,0xcad260][j]
   relsp=[-3200,-3312,-3360,-3360,-3312,-3312,-3376][j]
   expected=[[self.dw_entry_sp-3104],[self.dw_entry_sp-3104],[0,FORMAT[3+iteration*2],0],[n.base+ptr,0x7fffffff],
    [self.dw_entry_sp-1984,self.dw_entry_sp-3304,0,self.dw_entry_sp-3072],
    [self.dw_entry_sp-1984,n.base+ptr,length,self.dw_entry_sp-3072],[self.dw_stack_receiver+start,n.base+ptr,length]][j]
   stores=[10,21,28,28,31,38,45][j]+(49 if iteration else 0)
   reads=[8,9,9,9,11,11,11][j] if not iteration else [20,21,21,21,27,27,27][j]
  else:
   src=[0xcb1650,0xca8658][k-14];return_rva=[0xca63e0,0xcad9ac][k-14];relsp=[-3136,-1904][k-14]
   expected=[[0],[self.dw_entry_sp-1888]][k-14];stores=[104,108][k-14];reads=31
  assert site==src and ret==u.reg_read(UC_ARM64_REG_LR)==n.base+return_rva and sp==u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp+relsp
  assert args==expected==[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(len(args))]
  assert len(self.eb_order)==stores and len(self.eb_reads)==reads
 def eb_cookie_contract(self,site,ret,sp,ready):
  self.eb_layout();k=len(self.eb_cookie_entries);n=self.n;u=self.u
  assert ready and k<5 and self.eb_cookie_frame is None
  assert site==[0x11d0,0x11f0,0x11d0,0x11f0,0x11f0][k]
  assert ret==u.reg_read(UC_ARM64_REG_LR)==n.base+[0xcab198,0xcab640,0xcab198,0xcab640,0xca63ec][k]
  assert sp==u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp+[-3280,-3296,-3280,-3296,-1968][k]
  if site==0x11f0:assert self.rd(sp+8,8)==((sp-self.cookie)&((1<<64)-1))
 def eb_next(self,site,sp,result,ready):
  self.eb_layout();u=self.u;n=self.n
  assert ready and site==0x600440 and u.reg_read(UC_ARM64_REG_PC)==n.base+site and sp==u.reg_read(UC_ARM64_REG_SP)==self.dw_entry_sp-1456
  assert result==u.reg_read(UC_ARM64_REG_X0)==TOTAL and len(self.eb_order)==119 and len(self.eb_reads)==31
  assert self.eb_returns==16 and (self.eb_dx_returns,self.eb_dy_returns,self.eb_dz_returns)==(4,2,1)
  assert len(self.eb_cookie_entries)==len(self.eb_cookie_returns)==5 and not self.eb_calls and self.eb_cookie_frame is None
  assert not self.dx_frames and not self.dy_frames and not self.dz_frames
  assert bytes(u.mem_read(self.dw_stack_receiver,640))==OUTPUT+bytes(640-TOTAL)
  assert self.rd(self.dw_entry_sp-3136,8)==self.dw_stack_receiver+TOTAL and self.rd(self.dw_entry_sp-3120,8)==TOTAL and self.rd(self.dw_entry_sp-3072,4)==TOTAL
  assert self.rd(self.dw_entry_sp-3080,8)==self.dw_entry_sp-1472 and self.rd(self.dw_entry_sp-3088,8)==n.base+FORMAT_RVA+7
 def eb_read(self,u,a,at,width,value,_):
  authority=[{"RVA":hex(FORMAT_RVA),"bytes":len(FORMAT)}]+EA.DZ.AUTH[1:]+ARG_AUTH+CELL_AUTH
  if any(self.n.base+int(t["RVA"],16)<=at<self.n.base+int(t["RVA"],16)+t["bytes"] for t in authority):
   site=u.reg_read(UC_ARM64_REG_PC)-self.n.base;data=self.rd(at,width);owned=(site,at,width,data,True);self.eb_read_contract(*owned)
   self.reject(self.eb_read_contract,[(site+4,at,width,data,True),(site,at+1,width,data,True),(site,at,width+1,data,True),(site,at,width,data^1,True),(site,at,width,data,False)])
   self.eb_reads.append((hex(site),hex(at-self.n.base),width));return
  self.ea_read(u,a,at,width,value,_)
 def eb_record(self,site,at,data):
  v=int.from_bytes(data,"little");width=len(data);self.eb_effect(site,at,width,v,True)
  self.reject(self.eb_effect,[(site+4,at,width,v,True),(site,at+8,width,v,True),(site,at,width+1,v,True),(site,at,width,v^1,True),(site,at,width,v,False)])
  if self.dw_stack_receiver<=at and at+width<=self.dw_stack_receiver+640:
   offset=at-self.dw_stack_receiver
   expected=(OUTPUT+bytes(640-TOTAL))[offset:offset+width]
   assert data==expected;self.ea_destination_expected[offset:offset+width]=expected
  self.patch_stack(at,data);self.eb_order.append((site,at-self.dw_entry_sp,width));self.pending[at,width]=v
 def eb_write(self,u,a,at,width,value,_):
  # Unicorn exposes some 64-bit writes as signed Python values; compare the exact unsigned word.
  self.write(u,a,at,width,value&((1<<(width*8))-1),_)
 def eb_code(self,u,pc,z,_):
  n=self.n;r=pc-n.base;assert not self.pending
  if self.eb_calls and pc==self.eb_calls[-1]["ret"]:
   f=self.eb_calls.pop();assert all(u.reg_read(k)==v for k,v in f["saved"].items()),"EB original callee ABI"
   assert u.reg_read(UC_ARM64_REG_X0)==f["result"];self.eb_returns+=1
  if self.eb_cookie_frame and pc==self.eb_cookie_frame["ret"]:
   f=self.eb_cookie_frame;assert u.reg_read(UC_ARM64_REG_SP)==f["sp"]+f["delta"]
   assert all(u.reg_read(k)==v for k,v in f["saved"].items() if k!=UC_ARM64_REG_SP)
   if f["delta"]<0:assert self.rd(f["sp"]-8,8)==((f["sp"]-16-self.cookie)&((1<<64)-1))
   self.eb_cookie_returns.append(f["delta"]);self.eb_cookie_frame=None
  if r==0xca634c:
   f=self.dz_frames.pop();assert pc==f["ret"] and all(u.reg_read(k)==v for k,v in f["saved"].items()) and u.reg_read(UC_ARM64_REG_X0)==TOTAL
   self.eb_dz_returns+=1
  if r in (0xcad940,0x6bd94):
   f=self.dy_frames.pop();assert pc==f["ret"] and all(u.reg_read(k)==v for k,v in f["saved"].items()) and u.reg_read(UC_ARM64_REG_X0)==TOTAL
   self.eb_dy_returns+=1
  if r in (0x6be0c,0x7acdc,0x7ac7c,0x600440):
   f=self.dx_frames.pop();assert pc==f["ret"] and all(u.reg_read(k)==v for k,v in f["saved"].items()) and u.reg_read(UC_ARM64_REG_X0)==TOTAL
   self.eb_dx_returns+=1
  if r==0x600440:
   owned=(r,u.reg_read(UC_ARM64_REG_SP),u.reg_read(UC_ARM64_REG_X0),True);self.eb_next(*owned)
   self.reject(self.eb_next,[(r+4,*owned[1:]),(r,owned[1]+16,*owned[2:]),(r,owned[1],owned[2]+1,True),(*owned[:3],False)])
   self.eb_stopped=True;u.emu_stop();return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4)
  if r in (0x11d0,0x11f0):
   owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),True);self.eb_cookie_contract(*owned)
   self.reject(self.eb_cookie_contract,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,True),(*owned[:3],False)])
   self.eb_cookie_entries.append(r);self.eb_cookie_frame={"ret":owned[1],"sp":owned[2],"delta":-16 if r==0x11d0 else 16,"saved":{k:u.reg_read(k) for k in NONVOL}}
  if r in (0xcab178,0xcacdf8,0xca65a8,0xf5e3e0,0xcad1f0,0xf5d480,0xcb1650,0xca8658):
   k=len(self.eb_entries);j=k%7 if k<14 else -1;size=[1,1,3,2,4,4,3][j] if k<14 else 1
   args=[u.reg_read(globals()[f"UC_ARM64_REG_X{i}"]) for i in range(size)]
   owned=(r,u.reg_read(UC_ARM64_REG_LR),u.reg_read(UC_ARM64_REG_SP),args,True);self.eb_call_contract(*owned)
   wrong=args.copy();wrong[0]+=8
   self.reject(self.eb_call_contract,[(r+4,*owned[1:]),(r,owned[1]+4,*owned[2:]),(r,owned[1],owned[2]+16,args,True),(r,owned[1],owned[2],wrong,True),(*owned[:4],False)])
   if k<14:
    iteration,j=divmod(k,7);start=self.dw_stack_receiver+EA.LENGTH+sum(LENGTHS[:iteration])
    result=[1,1,0,LENGTHS[iteration],self.dw_entry_sp-1984,start,start][j]
   else:result=0 if k==14 else self.dw_entry_sp-1888
   self.eb_entries.append(r);self.eb_calls.append({"ret":owned[1],"saved":{k:u.reg_read(k) for k in NONVOL},"result":result})
  self.eb_trace.append(r);i=INS[r]
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
    for off in range(0,width,8):
     addr=at+k*width+off;chunk=data[off:off+8];self.eb_record(r,addr,chunk)
 def run(self):
  prior=super().run();n=self.n;u=self.u;stores=self.stores;neg=self.negatives
  owned=(0xca984c,u.reg_read(UC_ARM64_REG_SP),self.rd(self.dw_entry_sp-3088,8),True);self.eb_entry(*owned)
  self.reject(self.eb_entry,[(owned[0]+4,*owned[1:]),(owned[0],owned[1]+16,*owned[2:]),(owned[0],owned[1],owned[2]+1,True),(*owned[:3],False)])
  for flag in ("eb_ready","eb_data_ready","ea_ready","ea_data_ready","held","inner_held"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.eb_entry,[owned])
   finally:setattr(self,flag,old)
  for t in ARG_AUTH+CELL_AUTH:
   at=n.base+int(t["RVA"],16);old=bytes(u.mem_read(at,t["bytes"]));u.mem_write(at,bytes([old[0]^1])+old[1:])
   try:self.reject(self.eb_entry,[owned])
   finally:u.mem_write(at,old)
  hooks=[u.hook_add(UC_HOOK_CODE,self.eb_code),u.hook_add(UC_HOOK_MEM_WRITE,self.eb_write),u.hook_add(UC_HOOK_MEM_READ,self.eb_read)]
  try:u.emu_start(n.base+0xca984c,n.end,count=3000)
  finally:
   for h in hooks:u.hook_del(h)
  assert self.eb_stopped and not self.pending and u.reg_read(UC_ARM64_REG_PC)==n.base+0x600440
  self.eb_layout();after=self.snapshot();assert after.keys()==self.before.keys()
  for key,before in self.before.items():
   assert after[key]==(bytes(self.expected_stack) if key[0]==n.stack else bytes(self.models[key]) if key in self.models else before),"cumulative retained EB memory mismatch"
  added={"original_instruction_visits":len(self.eb_trace),"exact_source_store_chunks":self.stores-stores,"independent_formatter_store_contracts":len(self.eb_order),
   "rejected_owned_requests":self.negatives-neg,"exact_immutable_data_reads":len(self.eb_reads),"original_callee_ABI_returns_exact":self.eb_returns,
   "inherited_consumer_ABI_returns_exact":self.eb_dx_returns+self.eb_dy_returns+self.eb_dz_returns,
   "cookie_push_convention_returns_exact":self.eb_cookie_returns.count(-16),"cookie_pop_convention_returns_exact":self.eb_cookie_returns.count(16),
   "exact_original_callee_entries":len(self.eb_entries),"owned_allocation_calls":0,"owned_OS_API_calls":0,
   "remaining_argument_lengths":LENGTHS,"formatted_output_length":TOTAL,"destination_remaining_zero_bytes":640-TOTAL,
   "all_three_argument_bytes_and_terminators_exact":True,"seven_inherited_consumer_frames_returned":True,"cold_runtime_context_cleanup_qualified":True,
   "unsigned_write_observer_preserves_exact_words":True,"nine_live_allocations_retained":True,
   "whole_original_entry_to_frontier_memory_and_permissions_exact":True,"outer_and_nested_registry_locks_held":True,"CRT_and_SRW_released":True,
   "retained_active_consumer_frames":0,"stop_before_RVA":"0x600440","current_SP_relative_outer_entry":-1456,
   "variadic_cursor_relative_outer_entry":-1472,"output_cursor_relative_outer_entry":-1355,"completed_consumer_result":TOTAL,
   "outer_callee_return_not_reached_RVA":"0x5f8ea8"}
  return {"EA":prior,"added":added}
def main():
 rows=[]
 for args in itertools.product((0,16,128,512),(0,37),(0x80000000,0x80000020),(0,0xffffffff),(0,0x8877665544332211),(0,0xffeeddccbbaa9988),(0xa5,0x5a)):
  rows.append(Case(*args).run())
  if len(rows)%32==0:print(json.dumps({"progress_cases":len(rows)}),flush=True)
 rows=json.loads(json.dumps(rows));ancestor=json.loads((P.parent/"SOURCE-SAFE.json").read_text());assert [r["EA"] for r in rows]==ancestor["details"]
 report={"experiment":"E011EB","status":"PASS_BOUNDED_ORIGINAL_COMPLETE_CONSTANT_CONSUMER_RETURN","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
  "remaining_argument_data_authority":ARG_AUTH,"new_sparse_cell_authority":CELL_AUTH,"runtime_initial_value_model_authority":ancestor["runtime_initial_value_model_authority"],"details":rows,
  "source_result_fixture_used":False,"native_rear_runtime_allowed":False,"full_constant_consumer_return_qualified":True,
  "all_three_argument_length_copy_and_termination_qualified":True,"cold_runtime_context_cleanup_qualified":True,
  "full_outer_callee_return_qualified":False,"full_factory_or_first_helper_return_qualified":False,
  "native_runtime_scalar_and_pointer_selection_qualified":False,"alternate_nonzero_runtime_flag_paths_qualified":False,"pointed_locale_tables_qualified":False,
  "cookie_leaf_has_SP_preserving_ABI":False,"stack_growth_guard_page_OS_qualified":False,"parent_after_consumer_continuation_qualified":False,
  "new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False,"next_experiment":"E011EC"}
 keys=("original_instruction_visits","exact_source_store_chunks","independent_formatter_store_contracts","rejected_owned_requests","exact_immutable_data_reads",
 "original_callee_ABI_returns_exact","inherited_consumer_ABI_returns_exact","cookie_push_convention_returns_exact","cookie_pop_convention_returns_exact",
 "exact_original_callee_entries","owned_allocation_calls","owned_OS_API_calls")
 report["added_totals"]={k:sum(row["added"][k] for row in rows) for k in keys};report["inherited_EA_totals"]=ancestor["added_totals"]
 for k in ("DZ","DY","DX","DW","DV","DU","DT","DS"):report["inherited_"+k+"_totals"]=ancestor["inherited_"+k+"_totals"]
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({"status":report["status"],"scenarios":len(rows),"added_totals":report["added_totals"]}),flush=True)
if __name__=="__main__":main()
