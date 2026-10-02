#!/usr/bin/env python3
"""Private original full AEC query and invariant source-weight differential."""
from pathlib import Path
import collections,hashlib,importlib.util,json,random,struct,subprocess,tempfile
import capstone,pefile
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;EX=HERE.parent;ROOT=HERE.parents[2];PRIVATE=ROOT.parent/"private"
BASE_COMMIT="bd9589fd85593f74496caaf76850e4ea5105c6b4"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BB=load("bw_four",EX/"e011bb-rear-aec-four-grid-deserialization/source-private.py")
N=load("bw_native",EX/"e011ai-rear-neutral-scalar-full-integration/native-private.py")
NUMERIC_CFI={0x39eacc,0x39eb10,0x39eb94,0x39ec18,0x39ec68,0x39ecdc}
LOG_CFI={0x3a0fe4,0x3a1080,0x3a1108,0x373fb0,0x372efc}
ALLOWED_TARGETS={0x2dbc0,0x39d7c0,0x3a0db0}
class Flow:
 def __init__(self):
  self.n=N.Native();self.u=self.n.u;self.events=[];self.stubs=collections.Counter();self.writes=[]
  self.u.hook_add(UC_HOOK_CODE,self.hook)
  self.u.hook_add(UC_HOOK_MEM_WRITE,self.write,begin=self.n.heap,end=self.n.heap+0x2ffff)
 def write(self,u,access,address,size,value,user):self.writes.append((address,size))
 def hook(self,u,pc,size,user):
  n=self.n;r=pc-n.base
  if r in NUMERIC_CFI:
   target=u.reg_read(UC_ARM64_REG_X8);assert target-n.base in ALLOWED_TARGETS
   self.events.append(("numeric_dispatch",r,target-n.base))
   self.stubs["checked_dispatch"]+=1
   u.reg_write(UC_ARM64_REG_X15,target);u.reg_write(UC_ARM64_REG_PC,pc+4)
  elif r in LOG_CFI:
   self.stubs["logging_interface"]+=1
   # Explicit inert owned logging interface; its implementation is excluded.
   # Original 0x1A8C0 is a single RET. All numeric callbacks execute unchanged.
   u.reg_write(UC_ARM64_REG_X15,n.base+0x1a8c0);u.reg_write(UC_ARM64_REG_PC,pc+4)
  elif r==0xce7c98:
   self.stubs["diagnostic_context"]+=1;u.reg_write(UC_ARM64_REG_X0,self.tls+0x3000)
   u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
  elif r==0xcfe600:raise AssertionError("uninitialized owned TLS outside fixture scope")
  elif r==0xcae740:
   count=u.reg_read(UC_ARM64_REG_X0);assert count==24 and not self.allocated
   self.allocated=True;self.stubs["allocate"]+=1
   u.reg_write(UC_ARM64_REG_X0,self.alloc);u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
  elif r==0xcae730:
   assert self.allocated and u.reg_read(UC_ARM64_REG_X0)==self.alloc
   self.allocated=False;self.stubs["free"]+=1;u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
  elif r==0x85276c:
   target=u.reg_read(UC_ARM64_REG_X15);assert target==n.base+0x372e40
   self.events.append(("wrapper_dispatch",r,0x372e40));self.stubs["checked_dispatch"]+=1
   u.reg_write(UC_ARM64_REG_PC,pc+4)
  elif r==0x1aca8:
   self.stubs["diagnostic_print"]+=1;u.reg_write(UC_ARM64_REG_PC,u.reg_read(UC_ARM64_REG_LR))
  elif r in [0x372e40,0x39ea40,0x3a0db0]:
   self.events.append(("original_entry",r,0))
  elif r in [0x373fe8,0x39ec94,0x3a1130]:
   self.events.append(("original_return",r,u.reg_read(UC_ARM64_REG_X0)))
 def reset(self,cache,bias,selector,allocated=92,kind=None):
  assert len(cache)==120 and selector in [12,20]
  n=self.n;u=self.u;h=n.heap
  u.mem_write(h,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
  self.manager=h+0x1000+bias;self.grid=h+0x5000+bias;self.src=h+0x8000+bias
  self.out=h+0xc000+bias;self.arr=h+0xa000+bias;self.wrapper=h+0x14000+bias
  self.desc=h+0x16000+bias;self.empty_inputs=h+0x19000+bias;self.engine=h+0x1c000+bias
  self.alloc=h+0x24000;self.tls=h+0x28000;self.stats=h+0x10000+bias
  u.mem_write(self.arr,struct.pack("<Q",self.grid))
  # Explicit owned one-primary-grid manager; whole manager construction excluded.
  u.mem_write(self.manager+0x608,struct.pack("<Q",self.arr))
  u.mem_write(self.manager+0x610,struct.pack("<II",0,1))
  u.mem_write(self.manager+0x618,struct.pack("<Q",self.arr))
  u.mem_write(self.grid,struct.pack("<Q",n.base+0x13381a0));u.mem_write(self.grid+0x18,struct.pack("<Q",self.src))
  u.mem_write(self.src,cache);u.mem_write(self.out,b"\xa5"*160);u.mem_write(self.stats,b"\xa5"*128)
  u.mem_write(self.tls+88,struct.pack("<Q",self.tls+0x1000))
  u.mem_write(self.tls+0x1000,struct.pack("<64Q",*([self.tls+0x2000]*64)))
  u.mem_write(self.tls+0x2000+0x14,struct.pack("<I",1));u.reg_write(UC_ARM64_REG_X18,self.tls)
  u.mem_write(self.wrapper+8,struct.pack("<Q",n.base+0x372e40))
  u.mem_write(self.wrapper+0x28,struct.pack("<Q",self.manager))
  u.mem_write(self.engine+0x1088,struct.pack("<Q",self.wrapper))
  u.mem_write(self.desc,struct.pack("<3Q",self.out,allocated,(10 if selector==12 else 21) if kind is None else kind))
  u.mem_write(self.alloc-32,b"\xa5"*32);u.mem_write(self.alloc+24,b"\xa5"*32)
  self.events=[];self.stubs.clear();self.writes=[];self.allocated=False
 def call(self,rva,args):
  n=self.n;u=self.u
  for i,value in enumerate(args):u.reg_write(globals()["UC_ARM64_REG_X"+str(i)],value)
  u.reg_write(UC_ARM64_REG_SP,n.stack+0xf000);u.reg_write(UC_ARM64_REG_LR,n.end)
  u.emu_start(n.base+rva,n.end,count=100000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end
  return u.reg_read(UC_ARM64_REG_X0)
 def run(self,cache,bias,selector,allocated=92,kind=None):
  self.reset(cache,bias,selector,allocated,kind);u=self.u;n=self.n
  before=bytes(u.mem_read(n.heap,0x30000))
  result=self.call(0x852668,[self.engine,selector,self.empty_inputs,self.desc,1])
  assert not self.allocated and self.stubs["allocate"]==self.stubs["free"]==1
  assert bytes(u.mem_read(self.src,120))==cache
  assert bytes(u.mem_read(self.out+92,68))==b"\xa5"*68
  assert bytes(u.mem_read(self.alloc-32,32))==bytes(u.mem_read(self.alloc+24,32))==b"\xa5"*32
  after=bytes(u.mem_read(n.heap,0x30000))
  allowed=[(self.out,92),(self.desc+12,4),(self.alloc,24),(self.tls+0x2000,0x2000)]
  for offset,(a,b) in enumerate(zip(before,after)):
   if a!=b:assert any(start<=n.heap+offset<start+length for start,length in allowed),{"unexpected_owned_heap_offset":hex(offset),"selector":selector,"allocated":allocated}
  if allocated<92 or kind not in [None,10 if selector==12 else 21]:
   assert result==0 and bytes(u.mem_read(self.out,160))==b"\xa5"*160
   assert struct.unpack("<I",u.mem_read(self.desc+12,4))[0]==0
   assert not any(x[0]=="original_entry" and x[1]==0x3a0db0 for x in self.events)
   return None
  assert result==0
  assert struct.unpack("<I",u.mem_read(self.desc+12,4))[0]==92
  for r,status in [(0x373fe8,0),(0x39ec94,1),(0x3a1130,1)]:
   assert sum(x[0]=="original_return" and x[1]==r and x[2]==status for x in self.events)==1
  produced=bytes(u.mem_read(self.out,92));assert produced[68:80]==cache[20:32]
  # Exact original primary conversion fragment, not a whole SetStats return.
  frame=self.out-0x1a8;u.reg_write(UC_ARM64_REG_X21,frame);u.reg_write(UC_ARM64_REG_X19,self.stats)
  u.emu_start(n.base+0x83e01c,n.base+0x83e034,count=6)
  expected=bytearray(b"\xa5"*128);expected[48:60]=cache[20:32]
  assert bytes(u.mem_read(self.stats,128))==bytes(expected)
  return produced
def source_roots():
 result=[];audit=[]
 for name,sha in BB.AZ.AV.FILES:
  blob=(BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  h,sy,wire,info=BB.source(blob)
  weights=[wire[i*101+20:i*101+32] for i in range(4)]
  assert len(set(weights))==1
  assert all(v==0x80000000 or v<=0x3f800000 for v in struct.unpack("<3I",weights[0]))
  fixture=BB.FourGrid(blob);fixture.run(wire,0)
  array=fixture.allocs[1][0];cache=bytes(fixture.n.u.mem_read(array,120))
  assert cache[20:32]==weights[0]
  result.append((wire,cache))
  audit.append({"path":name,"sha256":sha,"qualified_Default":True,"all_four_weight_blocks_equal":True})
 assert len(set(w[20:32] for w,c in result))==1
 return result,audit
def anchors():
 raw=N.DLL.read_bytes();assert hashlib.sha256(raw).hexdigest()==N.DLL_SHA
 p=pefile.PE(data=raw);c=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);c.detail=True
 i=next(c.disasm(p.get_data(0x1a8c0,4),0x1a8c0));assert i.mnemonic=="ret"
 for r in NUMERIC_CFI|LOG_CFI|{0x85276c}:
  i=next(c.disasm(p.get_data(r,4),r));assert i.mnemonic=="blr" and c.reg_name(i.operands[0].reg)=="x17"
  i=next(c.disasm(p.get_data(r+4,4),r+4));assert i.mnemonic=="blr" and c.reg_name(i.operands[0].reg)=="x15"
 for r in [0x373fe8,0x39ec94,0x3a1130]:
  i=next(c.disasm(p.get_data(r,4),r));assert i.mnemonic=="ret"
 # Wrapper uses five arguments: engine, selector, input-list, output-array, count.
 for r,alias,origin in [(0x852688,"x21","x2"),(0x852698,"x25","x3"),(0x85269c,"w24","w4")]:
  i=next(c.disasm(p.get_data(r,4),r))
  # Layout assertion below is complemented by executable wrapper entry checks.
  assert i.mnemonic=="mov" and [c.reg_name(x.reg) for x in i.operands]==[alias,origin]
 for r,argument,owner,offset in [(0x83a9a4,"x2","sp",3152),(0x83a9ac,"x1","sp",1264)]:
  i=next(c.disasm(p.get_data(r,4),r))
  assert i.mnemonic=="add" and [c.reg_name(x.reg) for x in i.operands[:2]]==[argument,owner]
  assert i.operands[2].imm==offset
 i=next(c.disasm(p.get_data(0x83aa1c,4),0x83aa1c))
 assert i.mnemonic=="bl" and i.operands[0].imm==0x83df68
 return {"original_DLL_sha256":N.DLL_SHA,"original_GetParam_wrapper_RVA":"0x852668",
  "wrapper_argument_count":5,"wrapper_input_list_argument":2,"wrapper_output_array_argument":3,
  "wrapper_output_count_argument":4,"descriptor_allocated_bytes_u32_offset":8,"descriptor_written_bytes_u32_offset":12,"descriptor_type_u32_offset":16,"callback_RVA":"0x372E40","manager_RVA":"0x39EA40",
  "getter_RVA":"0x3A0DB0","GetParam_success_status":0,"manager_and_getter_success_boolean":1,"typed_output_bytes":92,"source_weight_offset":20,
  "getter_output_weight_offset":68,"primary_conversion_range":["0x83E01C","0x83E034"],
  "first_prepublication_frame_stack_offset":1264,"first_published_statistics_stack_offset":3152}
def main():
 facts=anchors();roots,audit=source_roots();cases=list(roots);rng=random.Random(0xe011b0)
 for bits in [0,1,0x3d000000,0x3f800000,0x80000000,0x7fc00000,0xffffffff]:
  wire,cache=roots[-1];w=bytearray(wire);cc=bytearray(cache)
  block=struct.pack("<3I",bits,bits,bits)
  for grid in range(4):w[101*grid+20:101*grid+32]=block
  cc[20:32]=block;cases.append((bytes(w),bytes(cc)))
 for _ in range(64):
  wire,cache=roots[-1];w=bytearray(wire);cc=bytearray(cache)
  block=struct.pack("<3I",*[rng.randrange(0x3f800001) for _ in range(3)])
  for grid in range(4):w[101*grid+20:101*grid+32]=block
  cc[20:32]=block;cases.append((bytes(w),bytes(cc)))
 flow=Flow();calls=rejections=0
 for bias in [0,1,0x40,0x1230]:
  for wire,cache in cases:
   a=flow.run(cache,bias,12);b=flow.run(cache,bias,20);assert a==b;calls+=2
  for selector in [12,20]:
   for size,kind in [(91,None),(0,None),(92,0xffffffff)]:
    assert flow.run(roots[-1][1],bias,selector,size,kind) is None;rejections+=1
 capture=PRIVATE/"E011BV-20261001-2310A-captured/capture/FIRST_OUT.bin"
 first=capture.read_bytes();assert len(first)==2072
 assert first[48:60]==roots[-1][0][20:32]
 # Compile the independent decoder/quantizer with two sanitizer compilers.
 reports=[]
 with tempfile.TemporaryDirectory(prefix="e011bw-source-",dir=PRIVATE) as temp:
  for compiler in ["gcc","clang"]:
   binary=Path(temp)/compiler
   cmd=[compiler,"-std=c11","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-g",str(HERE/"weights-check.c"),"-o",str(binary)]
   build=subprocess.run(cmd,capture_output=True);assert build.returncode==0,"private decoder build failed"
   run=subprocess.run([str(binary)],input=b"".join(w for w,c in cases),capture_output=True)
   assert run.returncode==0,"private decoder test failed"
   pos=valid=rejected=0
   for wire,cache in cases:
    result=struct.unpack_from("<i",run.stdout,pos)[0];pos+=4
    bits=struct.unpack("<3I",wire[20:32]);accept=all(x==0x80000000 or x<=0x3f800000 for x in bits)
    assert (result==0)==accept
    if accept:
     assert run.stdout[pos:pos+12]==wire[20:32];pos+=15;valid+=1
    else:assert result==-34;rejected+=1
   assert pos==len(run.stdout)
   reports.append({"compiler":compiler,"valid_source_cases":valid,"invalid_numeric_cases":rejected,
       "checks":int(run.stderr.decode().strip().split("=")[1])})
 safe={"experiment":"E011BW","status":"PASS_BOUNDED_SOURCE_WEIGHTS_AND_FULL_ORIGINAL_PRIMARY_QUERY",
  "base_commit":BASE_COMMIT,**facts,"source_files":audit,"source_shapes":3,"all12_Default_grid_weight_blocks_equal":True,
  "original_full_query_wrapper_returns":calls,"original_full_GetParam_manager_getter_returns_each":calls,
  "owned_source_cases":len(cases),"owned_memory_placements":4,"original_query_scope_rejections":rejections,"original_zero_status_without_payload_negative_cases":rejections,"scope_rejection_checks_written_bytes_not_status_only":True,
  "compiler_runs":reports,"first_live_published_weight_comparison_bytes":12,
  "source_weights_used_as_inputs":True,"captured_weights_used_as_inputs":False,
  "original_executable_modified":False,"numeric_callbacks_stubbed":False,
  "checked_dispatch_allocation_free_diagnostic_context_logging_interfaces_stubbed":True,
  "original_memset_and_status_helper_executed":True,"whole_manager_or_ConfigureHWStats_construction_claimed":False,
  "whole_GetHWConfigOutput_or_SetStatsConfig_return_claimed":False,
  "full_original_query_returns_are_owned_fixture_not_live_callback_return_proof":True,
  "first_live_source_cache_to_first_prepublication_frame_pointer_join_closed":False,
  "cold_weight_numeric_policy_closed":False,"source_weight_decoder_invariant_Default_scope_only":True,
  "exact_opened_tuning_filename_profile_closed":False,"complete_deterministic_bootstrap_closed":False,
  "native_rear_runtime_allowed":False,"new_camera_starts":0,"new_reboots":0,"private_bytes_exported":False}
 (HERE/"SOURCE-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in safe.items() if k!="source_files"}),flush=True)
if __name__=="__main__":main()
