#!/usr/bin/env python3
"""E011BT original cold metadata routing prefixes/copy; originals remain on SP11."""
from pathlib import Path
import importlib.util,json,struct,hashlib,random,collections
import pefile,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;EX=HERE.parent
spec=importlib.util.spec_from_file_location("bt_native",EX/"e011ai-rear-neutral-scalar-full-integration/native-private.py")
N=importlib.util.module_from_spec(spec);spec.loader.exec_module(N)
DLL=HERE.parents[4]/"00-RE-archive/sp11-driverdump/surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
TAGS=(0x50000019,0x50000018,0x5000001c,0x5000001d,0x3000000f)
class Fixture:
 def __init__(self):
  self.n=N.Native();self.u=self.n.u;self.calls=[];self.stubs=collections.Counter();self.writes=[]
  self.ife=0x74000000;self.u.mem_map(self.ife,0x90000)
  self.teb=0x72000000;self.u.mem_map(self.teb,0x4000)
  self.u.hook_add(UC_HOOK_CODE,self.hook)
  self.u.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=self.n.heap,end=self.n.heap+0x2ffff)
 def hook(self,u,pc,size,user):
  r=pc-self.n.base
  if r in [0x11d0,0x11f0]:
   self.stubs[r]+=1;u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
  elif r==0x5bde08:
   # Explicit controlled trace-state interface; OS/TLS/trace construction is excluded.
   self.stubs[r]+=1;u.reg_write(UC_ARM64_REG_X0,self.n.heap+0x10000)
   u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
  elif r in [0x5c44c8,0x5c4d78,0x5c34a0,0x5c3758,0x5c2fc0,0x5c4658,0x5d2638,0x5d2e48,0x1aca8,0xce7c98]:
   self.calls.append((r,[u.reg_read(globals()["UC_ARM64_REG_X"+str(i)]) for i in range(8)]));u.emu_stop()
 def write(self,u,access,address,size,value,user):self.writes.append((address,size))
 def reset(self,bias=0):
  u=self.u;n=self.n;u.mem_write(n.heap,b"\xa5"*0x30000);u.mem_write(n.stack,bytes(0x10000));u.mem_write(self.ife,bytes(0x90000))
  self.node=n.heap+0x1000+bias;self.pipeline=n.heap+0x11000;self.pool=n.heap+0x18000+bias
  self.store=n.heap+0x1b000+bias;self.decoy=n.heap+0x1d000;self.src=n.heap+0x20000+bias
  self.keys=n.heap+0x26000+bias;self.outvec=n.heap+0x27000+bias;self.trace=n.heap+0x14000
  u.mem_write(self.node,bytes(0x5000));u.mem_write(self.pipeline,bytes(0x3000));u.mem_write(self.pool,bytes(0x1000))
  u.mem_write(self.decoy,bytes(0x1000));u.mem_write(self.outvec,bytes(40))
  # Every other pool is an explicit decoy; selection of member1200 must be genuine.
  for at in [1168,1176,1192,1208]:u.mem_write(self.node+at,struct.pack("<Q",self.decoy))
  u.mem_write(self.node+1200,struct.pack("<Q",self.pool));u.mem_write(self.node+1024,struct.pack("<Q",self.pipeline))
  u.mem_write(self.pool+632,struct.pack("<I",1));u.mem_write(self.pool+664,struct.pack("<Q",self.store))
  u.mem_write(self.decoy+632,struct.pack("<I",1));u.mem_write(self.decoy+664,struct.pack("<Q",self.decoy+0x800))
  # The original trace-state interface dereferences object+16 -> box+16 -> thread record.
  u.mem_write(n.heap+0x10000,bytes(0x100));u.mem_write(self.trace,bytes(0x100))
  u.mem_write(n.heap+0x10000+16,struct.pack("<Q",self.trace));u.mem_write(self.trace+16,struct.pack("<Q",self.trace+0x80))
  u.mem_write(self.keys,struct.pack("<5I",*TAGS))
  # Reader directly dereferences ARM64 thread-register x18+88; all TLS context is owned.
  u.mem_write(self.teb,bytes(0x4000));tlsarr=self.teb+0x1000;tlsblock=self.teb+0x2000
  u.reg_write(UC_ARM64_REG_X18,self.teb);u.mem_write(self.teb+88,struct.pack("<Q",tlsarr))
  for i in range(64):u.mem_write(tlsarr+8*i,struct.pack("<Q",tlsblock))
  u.mem_write(tlsblock+16,struct.pack("<Q",self.trace+0x80))
  self.calls=[];self.stubs.clear();self.writes=[]
 def invoke(self,rva,args,stop=None):
  u=self.u;n=self.n
  for i,v in enumerate(args):u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],v)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+rva,n.base+stop if stop else n.end,count=1000000)
 def route(self,bias,request,slots,tagindex):
  assert slots==1 and tagindex==2
  self.reset(bias);u=self.u;n=self.n;tag=TAGS[tagindex];payload=random.Random(request^bias^tag).randbytes(2072)
  u.mem_write(self.src,payload);u.mem_write(self.pool+632,struct.pack("<I",slots))
  before=bytes(u.mem_read(n.heap,0x30000))
  self.invoke(0x5d6a18,[self.node,request,tag,2072,self.src,0])
  assert len(self.calls)==1 and self.calls[0][0]==0x5c44c8
  args=self.calls[0][1];assert args[:4]==[self.store,tag,self.src,2072]
  assert bytes(u.mem_read(self.src,2072))==payload
  assert bytes(u.mem_read(self.store,128))==before[self.store-n.heap:self.store-n.heap+128]
  assert all(self.trace<=p and p+size<=self.trace+0x100 for p,size in self.writes),"writer prefix changed non-trace owned heap"
  self.reset(bias);u.mem_write(self.src,payload);u.mem_write(self.pool+632,struct.pack("<I",slots))
  # Real reader ABI: property-array pointer, output-vector pointer, index, request/offset context.
  self.invoke(0x5d4d30,[self.node,self.keys,self.outvec,tagindex,request,0,0,0])
  assert len(self.calls)==1 and self.calls[0][0]==0x5c4d78
  args=self.calls[0][1];assert args[:2]==[self.store,tag]
  assert bytes(u.mem_read(self.src,2072))==payload and bytes(u.mem_read(self.outvec,40))==bytes(40)
  assert all((self.trace<=p and p+size<=self.trace+0x100) or (self.outvec<=p and p+size<=self.outvec+40) for p,size in self.writes),"reader prefix changed non-trace/output owned heap"
  return 2
 def publisher(self,bias,request):
  self.reset(bias);n=self.n;u=self.u;stack=n.stack+0x9000
  first=random.Random(bias^request).randbytes(2072);second=bytes(x^0xff for x in first)
  u.mem_write(stack+3152,first);u.mem_write(stack+5232,second)
  u.mem_write(self.trace,struct.pack("<Q",request))
  u.reg_write(UC_ARM64_REG_X19,self.node);u.reg_write(UC_ARM64_REG_X21,self.trace);u.reg_write(UC_ARM64_REG_X20,0)
  u.reg_write(UC_ARM64_REG_X23,n.base+0x1483f38);u.reg_write(UC_ARM64_REG_SP,stack)
  u.emu_start(n.base+0x83abbc,n.base+0x83abd4,count=1000)
  got=[u.reg_read(globals()["UC_ARM64_REG_X"+str(i)]) for i in range(6)]
  assert got==[self.node,request,0x5000001c,2072,stack+3152,0]
  assert bytes(u.mem_read(got[4],2072))==first and bytes(u.mem_read(stack+5232,2072))==second
  return 1
 def cold_copy(self,bias,seed):
  self.reset(bias);u=self.u;n=self.n;node=self.ife+bias
  dst=n.heap+0x22000+bias;payload=random.Random(seed).randbytes(2072)
  u.mem_write(self.src,payload);u.mem_write(node+0x72a58,struct.pack("<Q",dst))
  stack=n.stack+0x9000;u.mem_write(stack+0x70,struct.pack("<Q",self.src));u.mem_write(stack+0x80,struct.pack("<Q",self.node))
  before=bytes(u.mem_read(n.heap,0x30000));ife_before=bytes(u.mem_read(self.ife,0x90000))
  u.reg_write(UC_ARM64_REG_SP,stack);u.reg_write(UC_ARM64_REG_X24,node+0x72000)
  u.emu_start(n.base+0x73c078,n.base+0x73c094,count=1000000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x73c094
  expected=bytearray(before);off=dst-n.heap;expected[off:off+2072]=payload
  assert bytes(u.mem_read(n.heap,0x30000))==expected and bytes(u.mem_read(self.ife,0x90000))==ife_before
  assert all(dst<=p and p+size<=dst+2072 for p,size in self.writes)
  assert not self.calls and not self.stubs,"cold copy executes original memcpy without a helper shim"
  return 1
def source():
 raw=DLL.read_bytes();assert hashlib.sha256(raw).hexdigest()==SHA;p=pefile.PE(data=raw)
 assert struct.unpack("<5I",p.get_data(0x1439208,20))==TAGS
 assert struct.unpack("<I",p.get_data(0x1483f3c,4))[0]==0x5000001c
 cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);cs.detail=True
 copy=next(cs.disasm(p.get_data(0x73c090,4),0x73c090));assert copy.mnemonic=="bl" and copy.operands[0].imm==0xf5d480
 for at,target in [(0x83aa1c,0x83df68),(0x83aad0,0x83df68),(0x83abd4,0x5d6a18),(0x83ab04,0xf5d480)]:
  ins=next(cs.disasm(p.get_data(at,4),at));assert ins.mnemonic=="bl" and ins.operands[0].imm==target
 # Input stack first/second stats destinations and publication source remain separate.
 return {"original_DLL_sha256":SHA,"reader_property_table_RVA":"0x1439208","reader_AEC_property_index":2,
  "publisher_property_table_RVA":"0x1483F38","publisher_property_member_offset":4,
  "property_ID":"0x5000001C","metadata_copy_bytes":2072,"node_UsecasePool_member_offset":1200,
  "writer_RVA":"0x5D6A18","writer_property_argument_index":2,"writer_payload_argument_index":4,
  "reader_RVA":"0x5D4D30","metadata_store_write_boundary_RVA":"0x5C44C8",
  "metadata_store_read_boundary_RVA":"0x5C4D78","publisher_call_RVA":"0x83ABD4",
  "publisher_owned_request_vector_index":0,"published_AEC_temporary_stack_offset":3152,"other_AEC_temporary_stack_offset":5232,
  "cold_copy_call_RVA":"0x73C090","cold_retained_destination_pointer_node_offset":469592,
  "cold_reader_source_pointer_vector_index":2}
def main():
 facts=source();f=Fixture();routes=publishers=copies=0
 requests=[0,1,17,0xffffffff,0x100000007]
 for bias in [0,1,0x40,0x1230]:
  for request in requests:
   for slots in [1]:
    for idx in [2]:routes+=f.route(bias,request,slots,idx)
   publishers+=f.publisher(bias,request)
  for seed in range(32):copies+=f.cold_copy(bias,seed)
 rejected=0
 for slots,index in [(0,2),(2,2),(1,-1),(1,4)]:
  try:f.route(0,0,slots,index)
  except AssertionError:rejected+=1
  else:raise AssertionError("invalid owned route shape accepted")
 out={"experiment":"E011BT","status":"PASS_BOUNDED_ORIGINAL_COLD_METADATA_ROUTE_AND_COPY",
  "base_commit":"1b5efb5833edbaa28d14ab643e5bf08b62be9bc9",**facts,
  "original_writer_and_reader_routing_prefixes":routes,"original_publisher_argument_slices":publishers,
  "original_cold_copy_slices":copies,"preexecution_owned_route_rejections":rejected,
  "route_base_placements":4,"route_request_ID_cases":5,"route_pool_slot_count_cases":1,"route_Usecase_tag_cases":1,
  "trace_state_interface_fixture_RVA":"0x5BDE08","owned_x18_TEB_TLS_context":True,"security_cookie_shims":["0x11D0","0x11F0"],
  "metadata_store_write_read_implementations_executed":False,"numeric_source_initialization_closed":False,
  "whole_PrePublishMetadata_or_ReadDefaultStatsConfig_return_claimed":False,
  "live_metadata_pool_store_payload_identity_closed":False,"cold_metadata_bridge_closed":False,
  "copy_memcpy_helper_executed_original_unmodified":True,"captured_scalars_as_producer_inputs":False,
  "originals_exported":False,"new_camera_starts":0,"new_reboots":0,"production_C_changed":False,
  "kernel_build_performed":False,"native_rear_runtime_allowed":False}
 (HERE/"METADATA-SAFE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out),flush=True)
if __name__=="__main__":main()
