#!/usr/bin/env python3
"""E011BE owned parent fixture, derived from E011AZ; revision executes originally."""
from pathlib import Path
import importlib.util,hashlib,json,random,struct
import pefile,capstone
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
import unicorn.arm64_const as arm
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
AY=load("az_schema",EX/"e011ay-rear-aec-cache-construction/scalar-private.py")
DEC=AY.DEC;AV=AY.AV
DLL=ROOT.parents[1]/"00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
def source(blob):
 wire,info=AY.source(blob)
 h=DEC.parse_header(blob);sy,_=DEC.parse_symbol_table(blob,h["sections"][0],h["sections"][1])
 return h,sy,wire,info
class ParentPrefix:
 def __init__(self,blob):
  self.h,self.sy,self.wire,self.info=source(blob)
  self.n=load("az_image",EX/"e011ai-rear-neutral-scalar-full-integration/native-private.py").Native()
  self.table_map=0x72000000;self.data_map=0x74000000
  self.table_size=((max(self.sy)+1)*224+0x2000+4095)&~4095
  self.n.u.mem_map(self.table_map,self.table_size)
  obj=self.h["sections"][1]
  self.data_size=(obj["size"]+0x2000+4095)&~4095
  self.n.u.mem_map(self.data_map,self.data_size)
  self.data=blob[obj["offset"]:obj["end"]]
  self.allocs=[];self.symbols=[];self.calls=[];self.copies=[]
  self.parent_context=None;self.stub_counts={};self.redzones=[]
  def returned(value=None):
   u=self.n.u
   if value is not None:u.reg_write(UC_ARM64_REG_X0,value)
   u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
  def hook(uc,pc,size,_):
   n=self.n;u=n.u;r=pc-n.base
   if r in [0x11d0,0x11f0,0x6f4ac0,0x6f45d8,0xf5df00,0xcae740,0xf5e600]:
    self.stub_counts[hex(r)]=self.stub_counts.get(hex(r),0)+1
   if r in [0x11d0,0x11f0,0x6f4ac0,0x6f45d8]:returned();return
   if r==0xf5df00:returned(0);return
   # E011BE removes only the revision stub; original DB3A0 executes.
   if r==0xcae740:
    count=u.reg_read(UC_ARM64_REG_X0);assert 0<count<0x10000
    out=self.next_alloc+32;self.next_alloc=out+((count+31)&~31)+32
    assert self.next_alloc<n.heap+0x30000
    for at in [out-32,out+count]:
     u.mem_write(at,bytes([0xa5])*32);self.redzones.append(at)
    self.allocs.append((out,count));returned(out);return
   if r==0xf5e600:
    out=u.reg_read(UC_ARM64_REG_X0);count=u.reg_read(UC_ARM64_REG_X2)
    assert any(start<=out and out+count<=start+length for start,length in self.allocs)
    u.mem_write(out,bytes([u.reg_read(UC_ARM64_REG_X1)&255])*count);returned(out);return
   if r==0x6f4f88:
    rr=u.reg_read(UC_ARM64_REG_X1)
    cursor=struct.unpack("<Q",u.mem_read(rr+0xd8,8))[0]
    src=struct.unpack("<Q",u.mem_read(rr+0xd0,8))[0]
    sid=struct.unpack("<I",u.mem_read(src+cursor,4))[0]
    self.symbols.append((u.reg_read(UC_ARM64_REG_LR)-n.base-4,(rr-self.table)//224,cursor,sid))
   if r==0x124034:
    self.parent_context={getattr(arm,"UC_ARM64_REG_X"+str(i)):u.reg_read(getattr(arm,"UC_ARM64_REG_X"+str(i))) for i in range(29)}
    rr=u.reg_read(UC_ARM64_REG_X0);out=u.reg_read(UC_ARM64_REG_X1)
    self.calls.append((rr,out,u.reg_read(UC_ARM64_REG_W22)))
   if r==0xf5d480:
    self.copies.append((u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2)))
  self.n.u.hook_add(UC_HOOK_CODE,hook)
