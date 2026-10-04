#!/usr/bin/env python3
"""Original cold CRT registration and helper guard publication under explicit runtime models."""
from pathlib import Path
import collections,hashlib,importlib.util,json,struct
import capstone,pefile
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_READ,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
R=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
OUT=Path(__file__).resolve().parent
PRIVATE=R.parent/"private"
P=R/"experiments/E004-front-ir-vd55g0/e011ai-rear-neutral-scalar-full-integration/native-private.py"
s=importlib.util.spec_from_file_location("do_original_image",P);M=importlib.util.module_from_spec(s);s.loader.exec_module(M)
blob=M.DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==M.DLL_SHA
PE=pefile.PE(data=blob)
RANGES={
 0x2ee1a0:[(0x2ee1a0,0x2ee2a3)],0xca34a0:[(0xca34a0,0xca34c3)],
 0x5b80a8:[(0x5b80a8,0x5b90af)],0xce7ad8:[(0xce7ad8,0xce7b93)],
 0x5de700:[(0x5de700,0x5df75b)],0x1df30:[(0x1df30,0x1df8b)],0x1df90:[(0x1df90,0x1dfeb)],
 0x1a8c0:[(0x1a8c0,0x1a8c3)],0x11d0:[(0x11d0,0x11e7)],
 0x11f0:[(0x11f0,0x120f),(0x1214,0x121b),(0x1220,0x1233)]}
RANGES.update({13333248: [(13333248, 13333275)], 13343168: [(13343168, 13343335)], 16115200: [(16115200, 16115251), (16115328, 16115451), (16115468, 16115507), (16115536, 16115627)], 13304712: [(13304712, 13304779)], 13531720: [(13531720, 13531859)], 13251664: [(13251664, 13251743)], 13303696: [(13303696, 13303771)], 13303856: [(13303856, 13304247)], 13333400: [(13333400, 13333427)]})
RANGES.update({0xcb1650:[(0xcb1650,0xcb16af)]})
PINS={hex(entry):{"body_bytes":sum(hi-lo+1 for lo,hi in ranges),"ranges":[[hex(lo),hex(hi)] for lo,hi in ranges],
"sha256":hashlib.sha256(b"".join(PE.get_data(lo,hi-lo+1) for lo,hi in ranges)).hexdigest()} for entry,ranges in RANGES.items()}
assert PINS["0x5de700"]["sha256"]=="776092eab939986d2258713b25723c3ad4c1ddcdc8231881da140e25a9960533"
assert PINS["0x5b80a8"]["sha256"]=="26c3514bda9b9c1e8e91c5988c51fd336d0b77465699675d4935ab2219a0ca9b"
assert PINS["0xce7ad8"]["sha256"]=="d310e3f40e9666c9e47bb67e2bef87de0f68142b0413af59613ad85d362f6efc"
assert PINS["0x2ee1a0"]["sha256"]=="5540e74845b5dcd51626470a4315ad8b36c94eea910a4ac0c47e408965fd748b"
EXTRA_PINS={'0xcb7300': 'e1f73058a5d75230088e8935971d1150dff0eb2a2335a632e38dda91ba8c7d18', '0xcb99c0': 'fd618aea90fe77c003d9c147f84bd1fe81d6bb7d27208f3cda07eb58cb7d9834', '0xf5e600': '21fadd27bc73e835f042764cb723485997912b08c24a2875478282404cd7602e', '0xcb0388': 'bff698be3287759eac54712fb2c528995d703d76e67f55f6ec27ec02a2c5af80', '0xce7a48': '6f84e7a29bab93d10f7570516c2e5be4717e748b87314a6c75857f05ce4455d2', '0xca3450': '717580a7ffc8be6182551d6786c5be03612c46a4d15c5f6fb737b6dfdacd2b20', '0xcaff90': '42a74d7a75333d2ecb174ba5db0c58029be541a07ee1e572e923f8119ad990ab', '0xcb0030': '186196a5d4a09c5c096ac0dbd01b74d0d18a023012dd52d76b9fe01c27d9c7ce', '0xcb7398': 'ba0fb2d4a1e1a1d1effa82370b5d86970cbf56048020dfd66c1702bb8237af60'}
assert all(PINS[r]["sha256"]==pin for r,pin in EXTRA_PINS.items())
C=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);C.detail=True
INS={i.address:i for ranges in RANGES.values() for lo,hi in ranges for i in C.disasm(PE.get_data(lo,hi-lo+1),lo)}
BINDINGS={}
for e in PE.DIRECTORY_ENTRY_IMPORT:
 for x in e.imports:
  name=(x.name or b"").decode()
  if name in ("EnterCriticalSection","LeaveCriticalSection","AcquireSRWLockExclusive","ReleaseSRWLockExclusive","WakeAllConditionVariable"):BINDINGS[name]=x.address-PE.OPTIONAL_HEADER.ImageBase
assert BINDINGS=={"EnterCriticalSection":0xf7e0b8,"LeaveCriticalSection":0xf7e0c0,"AcquireSRWLockExclusive":0xf7e520,"ReleaseSRWLockExclusive":0xf7e518,"WakeAllConditionVariable":0xf7e410}
LITERALS=[(0x5de82c,239),(0x5de834,282),(0xce7b10,-1)]
for site,value in LITERALS:
 i=INS[site];assert i.mnemonic in ("mov","movz") and i.operands[1].type==capstone.arm64.ARM64_OP_IMM and i.operands[1].imm==value
FIELDS={(0x5de830,0x17350ec,4):239,(0x5de838,0x17350e4,4):282,(0xce7b14,0x17a4220,4):0xffffffff}

NONVOL=[UC_ARM64_REG_SP,*[globals()["UC_ARM64_REG_X"+str(k)] for k in range(19,30)],*[globals()["UC_ARM64_REG_D"+str(k)] for k in range(8,16)]]
ALLREG=[UC_ARM64_REG_PC,UC_ARM64_REG_LR,*[globals()["UC_ARM64_REG_X"+str(k)] for k in range(29)],UC_ARM64_REG_SP]
def reg(u,name):
 if name in ("xzr","wzr"):return 0
 name={"fp":"x29","lr":"x30"}.get(name,name)
 if name.startswith("w"):return u.reg_read(globals()["UC_ARM64_REG_X"+name[1:]])&0xffffffff
 return u.reg_read(globals()["UC_ARM64_REG_"+name.upper()])
class Case:
 def __init__(self,bias,index,epoch,sentinel,diag_clobber,api_clobber,poison,global_epoch):
  bound=0
  self.n=M.Native();self.u=self.n.u;u=self.u;n=self.n
  self.bias=bias;self.bound=bound;self.diag_clobber=diag_clobber;self.api_clobber=api_clobber
  self.obj=n.base+0x1626898;self.resource=self.obj+8;self.stacktop=n.stack+0xf000-bias
  self.api_page=0x76000000;u.mem_map(self.api_page,4096);u.mem_write(self.api_page,bytes([0xa5])*4096)
  self.apis={name:self.api_page+0x100+16*i for i,name in enumerate(BINDINGS)}
  self.reverse={v:k for k,v in self.apis.items()}
  for name,cell in BINDINGS.items():self.wr(n.base+cell,self.apis[name],8)
  u.mem_write(n.stack,bytes([0xd5])*65536)
  # Pre-existing scalar bound is an explicit owned fixture; no descriptor contents are supplied.
  self.wr(n.base+0x17350e0,bound,4)
  for k in range(31):u.reg_write(globals()["UC_ARM64_REG_X"+str(k)],0x123000+k*32+bias)
  for k in range(8,16):u.reg_write(globals()["UC_ARM64_REG_D"+str(k)],0x456000+k*32+bias)
  u.reg_write(UC_ARM64_REG_SP,self.stacktop);u.reg_write(UC_ARM64_REG_LR,n.end)
  self.ready=True;self.held=False;self.next_dep=0;self.callback=None
  self.pending={};self.stores=0;self.negatives=0;self.trace=[];self.callbacks=0;self.cfg_visits=0;self.dep_names=[];self.stopped=False
  self.expected_deps=["diagnostic_enter","EnterCriticalSection","AcquireSRWLockExclusive","ReleaseSRWLockExclusive","CRT_enter","CRT_leave","AcquireSRWLockExclusive","ReleaseSRWLockExclusive","WakeAllConditionVariable"]
  self.index=index;self.epoch=epoch;self.sentinel=sentinel
  self.teb=0x97700000;self.array=0x97710000;self.block=0x97720000+bias
  for a in (self.teb,self.array,0x97720000):u.mem_map(a,65536);u.mem_write(a,bytes([0xa5])*65536)
  self.wr(n.base+0x16a3740,index,4);self.wr(self.teb+88,self.array,8);self.wr(self.array+index*8,self.block,8);self.wr(self.block+16,epoch,4)
  self.wr(n.base+0x17a4220,0,4)
  for field in (0x17350ec,0x17350e4):self.wr(n.base+field,sentinel,4)
  u.reg_write(UC_ARM64_REG_X18,self.teb)
  self.srw_ready=True;self.srw_held=False;self.guard_callback=None;self.guard_returns=0;self.field_stores=0;self.field_order=[]
  self.models={}
  self.poison=poison;self.alloc_count=0;self.leases=[];self.constructor=None;self.constructor_returns=0
  self.container=n.base+0x17a7088;self.head=n.heap+0x8000+bias;self.array_storage=n.heap+0xa000+bias
  self.reservations=[(self.head,24),(self.array_storage,128)]
  for at,size in self.reservations:u.mem_write(at-32,bytes([poison])*(size+64))
  self.fields={(site,n.base+field,size):value for (site,field,size),value in FIELDS.items()}
  obj=self.container;head=self.head;array=self.array_storage
  plans=[(0x2ee1c4,obj,4,0),(0x2ee1c8,obj+8,8,0),(0x2ee1c8,obj+16,8,0),
   (0x2ee1d4,head+16,8,0),(0x2ee1d8,head,8,head),(0x2ee1d8,head+8,8,head),(0x2ee1dc,obj+8,8,head),
   (0x2ee1e0,obj+24,8,0),(0x2ee1e0,obj+32,8,0),(0x2ee1ec,obj+40,8,0),(0x2ee1ec,obj+48,8,7),
   (0x2ee1f8,obj+56,8,8),(0x2ee1fc,obj,4,0x3f800000)]
  plans.extend((site,array+offset+k*8,8,0) for site,offset in ((0x2ee224,0),(0x2ee228,32),(0x2ee22c,64),(0x2ee230,96)) for k in range(4))
  plans.extend([(0x2ee254,obj+24,8,array),(0x2ee254,obj+32,8,array+128),(0x2ee25c,obj+40,8,array+128)])
  plans.extend((0x2ee268,array+k*8,8,head) for k in range(16))
  for site,at,size,value in plans:self.fields[site,at,size]=value
  assert len(self.fields)==51
  self.global_epoch=global_epoch;self.published_epoch=global_epoch+1;assert global_epoch in (0x80000040,41)
  self.wr(n.base+0x1607b04,global_epoch,4)
  self.cookie=self.rd(n.base+0x1607000,8)
  self.exit_table=n.base+0x16a2760;self.exit_storage=n.heap+0xc000+bias
  for offset in (0,8,16):self.wr(self.exit_table+offset,self.encode(0),8)
  u.mem_write(self.exit_storage-32,bytes([poison])*320)
  self.exit_ready=self.exit_alloc_ready=self.crt_ready=self.cv_ready=True;self.crt_held=False;self.exit_allocated=False;self.wakes=0
  self.frames=[];self.frame_returns=0
  for k in range(32):
   self.fields[0xf5e720,self.exit_storage+k*8,8]=0
  for k in range(32):
   self.fields[0xcb0114,self.exit_storage+k*8,8]=self.encode(0)
  self.fields[0xcb0140,self.exit_storage,8]=self.encode(n.base+0xf7b120)
  for site,offset,pointer in ((0xcb015c,0,self.exit_storage),(0xcb0178,8,self.exit_storage+8),(0xcb0194,16,self.exit_storage+256)):
   self.fields[site,self.exit_table+offset,8]=self.encode(pointer)
  self.fields[0xce7a84,n.base+0x1607b04,4]=self.published_epoch
  self.fields[0xce7a88,n.base+0x17a4220,4]=self.published_epoch
  self.fields[0xce7aa4,self.block+16,4]=self.published_epoch
  assert len(self.fields)==122


 def wr(self,a,v,z):self.u.mem_write(a,(v&((1<<(z*8))-1)).to_bytes(z,"little"))
 def rd(self,a,z):return int.from_bytes(self.u.mem_read(a,z),"little")
 def regs(self):return {r:self.u.reg_read(r) for r in ALLREG}
 def snapshot(self):return {(lo,hi,p):bytes(self.u.mem_read(lo,hi-lo+1)) for lo,hi,p in self.u.mem_regions()}
 def logical(self):return self.crt_ready,self.crt_held,self.cv_ready,self.exit_ready,self.exit_alloc_ready,self.exit_allocated,self.wakes,len(self.frames),self.frame_returns,self.ready,self.held,self.srw_ready,self.srw_held,self.next_dep,self.callbacks,self.stores,self.field_stores,self.guard_returns,self.alloc_count,tuple(self.leases),self.constructor_returns
 def reject(self,fn,tests):
  regs=self.regs();state=self.logical()
  for args in tests:
   try:fn(*args)
   except AssertionError:pass
   else:raise AssertionError("invalid owned dependency contract admitted")
  assert self.regs()==regs and self.logical()==state
  self.negatives+=len(tests)
 def entry(self,rva,sp,ret,obj,ready,held):
  n=self.n;assert rva==0x5de700 and sp==self.stacktop and sp%16==0 and ret==n.end
  assert obj==self.obj and ready and not held
  assert self.rd(self.obj,8)==n.base+0x1330a68
  assert self.rd(n.base+0x1330a70,8)==n.base+0x1df30 and self.rd(n.base+0x1330a78,8)==n.base+0x1df90
  assert self.rd(n.base+0xf7e7b8,8)==n.base+0x1a8c0 and self.rd(n.base+0x17350e0,4)==self.bound
  assert all(self.rd(n.base+cell,8)==self.apis[name] for name,cell in BINDINGS.items())
  assert self.srw_ready and not self.srw_held and self.index in (0,37) and self.epoch in (0x80000000,0x80000020)
  assert self.u.reg_read(UC_ARM64_REG_X18)==self.teb and self.rd(n.base+0x16a3740,4)==self.index
  assert self.rd(self.teb+88,8)==self.array and self.rd(self.array+self.index*8,8)==self.block and self.rd(self.block+16,4)==self.epoch
  assert self.rd(n.base+0x17a4220,4)==0 and all(self.rd(n.base+field,4)==self.sentinel for field in (0x17350ec,0x17350e4))

  assert self.exit_ready and self.exit_alloc_ready and self.crt_ready and self.cv_ready and not self.crt_held and not self.exit_allocated
  assert self.rd(n.base+0x1607b04,4)==self.global_epoch and self.rd(n.base+0x1607000,8)==self.cookie
  assert all(self.rd(self.exit_table+offset,8)==self.encode(0) for offset in (0,8,16))
 def encode(self,pointer):
  shift=self.cookie&63;mask=(1<<64)-1
  return (((pointer<<shift)|(pointer>>(64-shift if shift else 64)))&mask)^self.cookie
 def decode(self,word):
  shift=self.cookie&63;word^=self.cookie;mask=(1<<64)-1
  return ((word>>shift)|(word<<(64-shift if shift else 64)))&mask
 def exit_allocator(self,rva,ret,args,pointer,ready):
  assert rva==0xcc2a50 and ret==self.n.base+0xcb9a30 and args==[0,256] and pointer==self.exit_storage and pointer%16==0
  assert ready and self.exit_alloc_ready and self.crt_ready and self.crt_held and self.held and not self.exit_allocated
  assert self.exit_ready and all(self.rd(self.exit_table+offset,8)==self.encode(0) for offset in (0,8,16))
  assert bytes(self.u.mem_read(pointer,256))==bytes([self.poison])*256
 def published(self):
  n=self.n;self.constructed()
  assert self.exit_allocated and self.decode(self.rd(self.exit_table,8))==self.exit_storage
  assert self.decode(self.rd(self.exit_table+8,8))==self.exit_storage+8 and self.decode(self.rd(self.exit_table+16,8))==self.exit_storage+256
  assert self.decode(self.rd(self.exit_storage,8))==n.base+0xf7b120
  assert all(self.decode(self.rd(self.exit_storage+k*8,8))==0 for k in range(1,32))
  assert self.rd(n.base+0x1607b04,4)==self.rd(n.base+0x17a4220,4)==self.rd(self.block+16,4)==self.published_epoch
  assert self.wakes==1 and not self.crt_held and not self.srw_held and self.held
 def allocator(self,target,ret,args,pointer,owned):
  n=self.n;k=self.alloc_count
  assert k<2 and target==0xcae740 and ret==n.base+(0x2ee1d0 if k==0 else 0x2ee218)
  assert args==[self.reservations[k][1]] and pointer==self.reservations[k][0] and owned
  assert pointer%16==0 and self.constructor is not None and self.held and not self.srw_held and self.rd(n.base+0x17a4220,4)==0xffffffff
  assert self.leases==self.reservations[:k] and bytes(self.u.mem_read(pointer,args[0]))==bytes([self.poison])*args[0]
  if k==0:assert self.rd(self.container,4)==0 and self.rd(self.container+8,8)==self.rd(self.container+16,8)==0
  else:
   assert self.rd(self.head,8)==self.rd(self.head+8,8)==self.head and self.rd(self.head+16,8)==0
   assert self.rd(self.container,4)==0x3f800000 and self.rd(self.container+8,8)==self.head
   assert self.rd(self.container+16,8)==self.rd(self.container+24,8)==self.rd(self.container+32,8)==self.rd(self.container+40,8)==0
   assert self.rd(self.container+48,8)==7 and self.rd(self.container+56,8)==8
 def constructed(self):
  assert self.alloc_count==2 and self.leases==self.reservations
  obj=self.container;head=self.head;array=self.array_storage
  assert self.rd(obj,4)==0x3f800000 and self.rd(obj+8,8)==head and self.rd(obj+16,8)==0
  assert self.rd(obj+24,8)==array and self.rd(obj+32,8)==self.rd(obj+40,8)==array+128
  assert self.rd(obj+48,8)==7 and self.rd(obj+56,8)==8
  assert self.rd(head,8)==self.rd(head+8,8)==head and self.rd(head+16,8)==0
  assert all(self.rd(array+k*8,8)==head for k in range(16))
 def dependency(self,name,ret,args,ready,held):
  n=self.n;k=self.next_dep;assert ready and name==self.expected_deps[k]
  if k==0:
   assert ret==n.base+0x1df68 and args==[5,65535,n.base+0x1352650,n.base+0x1352590,41,self.resource] and not held
  elif k==1:
   assert ret==n.base+0x1df78 and args==[self.resource] and not held
  else:
   assert held and self.held
   if k in (2,3,6,7):
    assert self.srw_ready and self.srw_held==(k in (3,7)) and args==[n.base+0x16a3738]
    assert ret==n.base+{2:0xce7b08,3:0xce7b80,6:0xce7a74,7:0xce7ab4}[k]
   elif k in (4,5):
    assert self.crt_ready and self.crt_held==(k==5) and args==[n.base+0x16a2f10]
    assert ret==n.base+(0xcaffb4 if k==4 else 0xcaffc8)
   else:
    assert k==8 and self.cv_ready and not self.srw_held and args==[n.base+0x16a3730] and ret==n.base+0xce7ac4
 def patch_stack(self,a,data):
  if self.n.stack<=a and a+len(data)<=self.n.stack+65536:
   self.expected_stack[a-self.n.stack:a-self.n.stack+len(data)]=data
  else:
   site=self.u.reg_read(UC_ARM64_REG_PC)-self.n.base;field=a-self.n.base;value=int.from_bytes(data,"little")
   assert self.fields.get((site,a,len(data)))==value,("unowned source store",hex(site),len(data))
   assert (site,a,len(data)) not in self.field_order
   if self.n.heap<=a<self.n.heap+0x30000:
    assert any(at<=a and a+len(data)<=at+size for at,size in self.leases+([(self.exit_storage,256)] if self.exit_allocated else [])),"store outside live owned allocation"
   self.field_order.append((site,a,len(data)));self.field_stores+=1
   key=next(k for k in self.before if k[0]<=a and a+len(data)<=k[1]+1)
   if key not in self.models:self.models[key]=bytearray(self.before[key])
   self.models[key][a-key[0]:a-key[0]+len(data)]=data

 def code(self,u,pc,z,_):
  n=self.n;assert not self.pending
  if self.callback and pc==self.callback["ret"]:
   assert all(u.reg_read(r)==v for r,v in self.callback["saved"].items()),"callback callee ABI did not restore"
   self.callback=None;self.callbacks+=1
  r=pc-n.base
  if self.guard_callback and pc==self.guard_callback["ret"]:
   assert all(u.reg_read(k)==v for k,v in self.guard_callback["saved"].items()),"guard callee ABI did not restore"
   self.guard_callback=None;self.guard_returns+=1
  if self.constructor and pc==self.constructor["ret"]:
   assert all(u.reg_read(k)==v for k,v in self.constructor["saved"].items()),"constructor ABI did not restore"
   assert u.reg_read(UC_ARM64_REG_X0)==self.container
   self.constructed();self.constructor=None;self.constructor_returns+=1
  if self.frames and pc==self.frames[-1]["ret"]:
   frame=self.frames.pop();assert all(u.reg_read(k)==v for k,v in frame["saved"].items()),"CRT/publication callee ABI did not restore"
   if frame["result"] is not None:assert u.reg_read(UC_ARM64_REG_X0)==frame["result"]
   self.frame_returns+=1
  if r==0x5b8104:
   assert self.held and not self.crt_held and not self.srw_held and not self.frames and self.next_dep==9
   self.published();self.stopped=True;u.emu_stop();return
  returns={0xca34a0:(0x5b90a0,0),0xca3450:(0xca34b0,n.base+0xf7b120),0xcb0388:(0xca3488,0),0xcaff90:(0xcb03c0,0),
   0xcb7300:(0xcaffb4,None),0xcb0030:(0xcaffbc,0),0xcb99c0:(0xcb00c4,self.exit_storage),
   0xf5e600:(0xcb9a50,self.exit_storage),0xcb7398:(0xcaffc8,None),0xcb1650:(0xcb00d0,None),0xce7a48:(0x5b90ac,None)}
  if r in returns:
   ret,result=returns[r];assert u.reg_read(UC_ARM64_REG_LR)==n.base+ret
   if r in (0xca34a0,0xca3450):assert u.reg_read(UC_ARM64_REG_X0)==n.base+0xf7b120
   if r==0xcb1650:assert u.reg_read(UC_ARM64_REG_X0)==0
   if r==0xcb99c0:assert [u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2)]==[0,32,8]
   if r==0xf5e600:assert [u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1),u.reg_read(UC_ARM64_REG_X2)]==[self.exit_storage,0,256]
   if r==0xce7a48:assert u.reg_read(UC_ARM64_REG_X0)==n.base+0x17a4220 and self.rd(n.base+0x17a4220,4)==0xffffffff
   self.frames.append({"entry":r,"ret":n.base+ret,"result":result,"saved":{k:u.reg_read(k) for k in NONVOL}})
  if r==0xcc2a50:
   ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0),u.reg_read(UC_ARM64_REG_X1)];pointer=self.exit_storage
   self.exit_allocator(r,ret,args,pointer,True)
   self.reject(self.exit_allocator,[(r+4,ret,args,pointer,True),(r,ret+4,args,pointer,True),(r,ret,[1,256],pointer,True),(r,ret,[0,255],pointer,True),(r,ret,args+[0],pointer,True),(r,ret,args,pointer+16,True),(r,ret,args,pointer,False)])
   for flag,value in (("crt_held",False),("exit_alloc_ready",False),("exit_allocated",True)):
    old=getattr(self,flag);setattr(self,flag,value)
    try:self.reject(self.exit_allocator,[(r,ret,args,pointer,True)])
    finally:setattr(self,flag,old)
   old=bytes(u.mem_read(pointer,1));u.mem_write(pointer,bytes([self.poison^1]))
   try:self.reject(self.exit_allocator,[(r,ret,args,pointer,True)])
   finally:u.mem_write(pointer,old)
   self.exit_allocated=True;u.reg_write(UC_ARM64_REG_X0,pointer);u.reg_write(UC_ARM64_REG_PC,ret);return
  if r==0x2ee1a0:
   assert self.held and not self.srw_held and self.constructor is None and self.rd(n.base+0x17a4220,4)==0xffffffff
   assert u.reg_read(UC_ARM64_REG_X0)==self.container and u.reg_read(UC_ARM64_REG_X1)==65535 and u.reg_read(UC_ARM64_REG_LR)==n.base+0x5b9094
   self.constructor={"ret":u.reg_read(UC_ARM64_REG_LR),"saved":{k:u.reg_read(k) for k in NONVOL}}
  if r==0xcae740:
   k=self.alloc_count;ret=u.reg_read(UC_ARM64_REG_LR);args=[u.reg_read(UC_ARM64_REG_X0)];pointer,size=self.reservations[k]
   self.allocator(r,ret,args,pointer,True)
   self.reject(self.allocator,[(r+4,ret,args,pointer,True),(r,ret+4,args,pointer,True),(r,ret,[size+1],pointer,True),(r,ret,args+[0],pointer,True),(r,ret,args,pointer+16,True),(r,ret,args,pointer,False)])
   old=bytes(u.mem_read(pointer,1));u.mem_write(pointer,bytes([self.poison^1]))
   try:self.reject(self.allocator,[(r,ret,args,pointer,True)])
   finally:u.mem_write(pointer,old)
   old_held=self.held;self.held=False
   try:self.reject(self.allocator,[(r,ret,args,pointer,True)])
   finally:self.held=old_held
   self.leases.append((pointer,size))
   try:self.reject(self.allocator,[(r,ret,args,pointer,True)])
   finally:self.leases.pop()
   self.leases.append((pointer,size));self.alloc_count+=1
   u.reg_write(UC_ARM64_REG_X0,pointer);u.reg_write(UC_ARM64_REG_PC,ret);return
  if r==0x5b80a8:
   assert u.reg_read(UC_ARM64_REG_X0)==0 and u.reg_read(UC_ARM64_REG_LR)==n.base+0x5de844
  if r==0xce7ad8:
   assert self.guard_callback is None and u.reg_read(UC_ARM64_REG_X0)==n.base+0x17a4220 and u.reg_read(UC_ARM64_REG_LR)==n.base+0x5b9074
   self.guard_callback={"ret":u.reg_read(UC_ARM64_REG_LR),"saved":{k:u.reg_read(k) for k in NONVOL}}

  if r==0x1aca8 or pc in self.reverse:
   if r==0x1aca8:
    name="diagnostic_enter" if self.next_dep==0 else "diagnostic_leave"
    args=[u.reg_read(globals()["UC_ARM64_REG_X"+str(k)]) for k in range(6)]
   else:
    name=self.reverse[pc]
    if self.next_dep in (4,5):name="CRT_enter" if self.next_dep==4 else "CRT_leave"
    args=[u.reg_read(UC_ARM64_REG_X0)]
   ret=u.reg_read(UC_ARM64_REG_LR)
   self.dependency(name,ret,args,self.ready,self.held)
   tests=[(name,ret+4,args,self.ready,self.held),(name,ret,args+[0],self.ready,self.held),(name,ret,args,False,self.held),(name,ret,args,self.ready,not self.held)]
   for k in range(len(args)):
    a=args.copy();a[k]+=1;tests.append((name,ret,a,self.ready,self.held))
   if name in ("AcquireSRWLockExclusive","ReleaseSRWLockExclusive"):
    old=self.srw_held;self.srw_held=not old
    try:self.reject(self.dependency,[(name,ret,args,self.ready,self.held)])
    finally:self.srw_held=old
    old=self.srw_ready;self.srw_ready=False
    try:self.reject(self.dependency,[(name,ret,args,self.ready,self.held)])
    finally:self.srw_ready=old
   if name in ("CRT_enter","CRT_leave","WakeAllConditionVariable"):
    flags=("crt_ready","crt_held") if name!="WakeAllConditionVariable" else ("cv_ready",)
    for flag in flags:
     old=getattr(self,flag);setattr(self,flag,not old)
     try:self.reject(self.dependency,[(name,ret,args,self.ready,self.held)])
     finally:setattr(self,flag,old)
   self.reject(self.dependency,tests)
   if name=="EnterCriticalSection":self.held=True
   elif name=="LeaveCriticalSection":self.held=False
   elif name=="AcquireSRWLockExclusive":self.srw_held=True
   elif name=="ReleaseSRWLockExclusive":self.srw_held=False
   elif name=="CRT_enter":self.crt_held=True
   elif name=="CRT_leave":self.crt_held=False
   elif name=="WakeAllConditionVariable":self.wakes+=1
   self.next_dep+=1;self.dep_names.append(name)
   # Void/no-effect dependency adapters deliberately return arbitrary volatile X0 values.
   u.reg_write(UC_ARM64_REG_X0,self.diag_clobber if name.startswith("diagnostic") else self.api_clobber)
   u.reg_write(UC_ARM64_REG_PC,ret);return
  assert r in INS and bytes(u.mem_read(pc,4))==PE.get_data(r,4),("unqualified code reached",hex(r))
  if r in (0x1df30,0x1df90):
   assert self.callback is None and u.reg_read(UC_ARM64_REG_X0)==self.obj
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+(0x5de7b4 if r==0x1df30 else 0x5df6e4)
   self.callback={"ret":u.reg_read(UC_ARM64_REG_LR),"saved":{k:u.reg_read(k) for k in NONVOL}}
  if r==0x1a8c0:
   assert u.reg_read(UC_ARM64_REG_LR)==n.base+(0x5de7b0 if not self.held else 0x5df6e0)
   self.cfg_visits+=1
  assert len(self.trace)<1200;self.trace.append(r);i=INS[r]
  if i.mnemonic.startswith(("str","stp","stnp","st1","stur")):
   memory=next(o for o in i.operands if o.type==capstone.arm64.ARM64_OP_MEM)
   assert not memory.mem.index
   at=reg(u,C.reg_name(memory.mem.base))+memory.mem.disp
   ops=[o for o in i.operands if o.type==capstone.arm64.ARM64_OP_REG] if i.mnemonic=="st1" else i.operands[:2] if i.mnemonic in ("stp","stnp") else i.operands[:1]
   for k,o in enumerate(ops):
    name=C.reg_name(o.reg)
    if i.mnemonic=="st1":
     assert name.startswith("v") and o.vas==capstone.arm64.ARM64_VAS_16B
     name="q"+name[1:]
    size=16 if name.startswith("q") else 8 if name.startswith(("x","d")) or name in ("fp","lr") else 4
    addr=at+k*size;v=reg(u,name)&((1<<(size*8))-1)
    data=v.to_bytes(size,"little")
    for offset in range(0,size,8):
     chunk=data[offset:offset+8];chunk_at=addr+offset;value=int.from_bytes(chunk,"little")
     self.patch_stack(chunk_at,chunk);self.pending[chunk_at,len(chunk)]=value
 def write(self,u,access,at,size,value,_):
  value&=(1<<(size*8))-1
  assert self.pending.pop((at,size),None)==value
  self.stores+=1
 def read(self,u,access,at,size,value,_):
  n=self.n
  if n.stack<=at and at+size<=n.stack+65536:return
  allowed={(n.base+0x1607000,8),(n.base+0x160a218,8),(n.base+0x1608858,4),
   (self.obj,8),(n.base+0x1330a70,8),(n.base+0x1330a78,8),(n.base+0xf7e7b8,8),
   (n.base+0x17350e0,4)}|{(n.base+cell,8) for cell in BINDINGS.values()}
  allowed|={(n.base+0x5df760,8),(n.base+0x5df768,8),(n.base+0x16a3740,4),(n.base+0x17a4220,4),(self.teb+88,8),(self.array+self.index*8,8),(self.block+16,4)}
  allowed|={(self.container+offset,8) for offset in (8,24,32,40)}
  allowed|={(self.exit_table+offset,8) for offset in (0,8,16)}|{(n.base+0x1607b04,4)}
  assert (at,size) in allowed,("unowned nonstack read",hex(at-n.base),size)
 def run(self):
  n=self.n;u=self.u
  args=(0x5de700,self.stacktop,n.end,self.obj,self.ready,self.held);self.entry(*args)
  bad=[]
  for k in range(4):
   a=list(args);a[k]+=4;bad.append(tuple(a))
  bad.extend([(*args[:4],False,False),(*args[:4],True,True)])
  self.reject(self.entry,bad)
  checks=[(self.obj,n.base+0x1330a70,8),(n.base+0x1330a70,n.base+0x1df34,8),(n.base+0x1330a78,n.base+0x1df94,8),(n.base+0xf7e7b8,n.base+0x1a8c4,8),(n.base+0x17350e0,(self.bound+1)&0xffffffff,4)]
  checks+=[(n.base+cell,self.apis[name]+4,8) for name,cell in BINDINGS.items()]
  checks+=[(n.base+0x16a3740,self.index+1,4),(self.teb+88,self.array+8,8),(self.array+self.index*8,self.block+8,8),(self.block+16,self.epoch+1,4),(n.base+0x17a4220,1,4)]
  checks+=[(n.base+field,self.sentinel^1,4) for field in (0x17350ec,0x17350e4)]
  checks+=[(n.base+0x1607b04,self.global_epoch+1,4)]+[(self.exit_table+offset,self.encode(0)^1,8) for offset in (0,8,16)]
  for flag in ("exit_ready","exit_alloc_ready","crt_ready","cv_ready"):
   old=getattr(self,flag);setattr(self,flag,False)
   try:self.reject(self.entry,[args])
   finally:setattr(self,flag,old)

  for at,v,size in checks:
   old=bytes(u.mem_read(at,size));self.wr(at,v,size)
   try:self.reject(self.entry,[args])
   finally:u.mem_write(at,old)
  self.before=self.snapshot();self.expected_stack=bytearray(u.mem_read(n.stack,65536))
  saved={k:u.reg_read(k) for k in NONVOL}
  hooks=[u.hook_add(UC_HOOK_CODE,self.code),u.hook_add(UC_HOOK_MEM_WRITE,self.write),u.hook_add(UC_HOOK_MEM_READ,self.read)]
  try:u.emu_start(n.base+0x5de700,n.end,count=2000)
  finally:
   for h in hooks:u.hook_del(h)
  assert not self.pending and self.callback is None
  assert self.dep_names==self.expected_deps
  assert self.callbacks==1 and self.guard_returns==1
  assert self.cfg_visits==self.callbacks
  assert self.stopped and u.reg_read(UC_ARM64_REG_PC)==n.base+0x5b8104 and self.held and not self.srw_held
  assert self.guard_callback is None and self.constructor is None and self.constructor_returns==1 and self.field_order==list(self.fields) and self.field_stores==122 and self.frame_returns==11 and not self.frames
  self.published()
  self.constructed()
  after=self.snapshot();assert after.keys()==self.before.keys()
  for k,v in self.before.items():
   assert after[k]==(bytes(self.expected_stack) if k[0]==n.stack else bytes(self.models[k]) if k in self.models else v),"whole mapped memory mismatch"

  return {"stack_bias":self.bias,"loader_index":self.index,"thread_epoch":self.epoch,"initial_bound_sentinel":self.sentinel,"diagnostic_X0":self.diag_clobber,"OS_void_X0":self.api_clobber,
   "allocation_poison":self.poison,"constructor_returns_ABI_exact":self.constructor_returns,"owned_allocation_calls":self.alloc_count,"owned_allocation_bytes":152,"allocation_redzones_and_relations_exact":True,
   "original_instruction_visits":len(self.trace),"constructor_instruction_visits":sum(0x2ee1a0<=r<=0x2ee2a3 for r in self.trace),"registration_wrapper_instruction_visits":sum(0xca34a0<=r<=0xca34c3 for r in self.trace),"first_helper_instruction_visits":sum(0x5b80a8<=r<=0x5b90af for r in self.trace),
   "guard_instruction_visits":sum(0xce7ad8<=r<=0xce7b93 for r in self.trace),"frame_helper_instruction_visits":sum(r<0x1300 for r in self.trace),
   "callback_returns_ABI_exact":self.callbacks,"guard_returns_ABI_exact":self.guard_returns,"owned_OS_API_calls":8,"owned_diagnostic_calls":1,
   "stack_store_chunks":self.stores-self.field_stores,"nonstack_field_store_chunks":self.field_stores,"invalid_owned_dependency_requests_rejected":self.negatives,
   "whole_mapped_memory_and_permissions_exact":True,"immutable_source_and_unmodified_loader_regions":True,"thread_epoch_update_exact":True,"registry_logical_lock_held":self.held,"SRW_logical_lock_held":self.srw_held,
   "initial_global_epoch":self.global_epoch,"published_epoch":self.published_epoch,"original_registration_publication_returns_ABI_exact":self.frame_returns,
   "original_CRT_registration_instruction_visits":sum(r>=0xca0000 and not(0xce7a48<=r<=0xce7b93) for r in self.trace),
   "publication_instruction_visits":sum(0xce7a48<=r<=0xce7ad3 for r in self.trace),"owned_exit_reallocation_calls":int(self.exit_allocated),"owned_exit_reallocation_bytes":256,
   "exit_table_used_pointer_entries":1,"exit_table_capacity_pointer_entries":32,"owned_wake_calls":self.wakes,"CRT_logical_lock_held":self.crt_held,
   "stop_before_RVA":"0x5b8104","next_factory_pointer_RVA":"0x1731880","parent_returned":False,"first_helper_returned":False}


def main():
 rows=[]
 for bias in (0,16,128,512):
  for index in (0,37):
   for epoch in (0x80000000,0x80000020):
    for sentinel in (0,0xffffffff):
     for diag in (0,0x8877665544332211):
      for api in (0,0xffeeddccbbaa9988):
       for poison in (0xa5,0x5a):
        for global_epoch in (0x80000040,41):
         rows.append(Case(bias,index,epoch,sentinel,diag,api,poison,global_epoch).run())
 fields=("original_instruction_visits","first_helper_instruction_visits","guard_instruction_visits","frame_helper_instruction_visits","constructor_instruction_visits","registration_wrapper_instruction_visits","original_CRT_registration_instruction_visits","publication_instruction_visits",
 "callback_returns_ABI_exact","guard_returns_ABI_exact","constructor_returns_ABI_exact","original_registration_publication_returns_ABI_exact","owned_OS_API_calls","owned_diagnostic_calls","owned_allocation_calls","owned_allocation_bytes","owned_exit_reallocation_calls","owned_exit_reallocation_bytes","owned_wake_calls","stack_store_chunks","nonstack_field_store_chunks","invalid_owned_dependency_requests_rejected")
 report={"experiment":"E011DR","status":"PASS_BOUNDED_ORIGINAL_CLEANUP_REGISTRATION_AND_GUARD_PUBLICATION","scenarios":len(rows),"source_pins":PINS,"image_sha256":M.DLL_SHA,
 "original_cleanup_callback_RVA":"0xf7b120","original_exit_table_RVA":"0x16a2760","original_exit_table_words":3,"exit_used_entries":1,"exit_capacity_entries":32,
 "original_registration_wrapper_RVA":"0xca34a0","registration_wrapper_caller_return_RVA":"0x5b90a0",
 "original_registration_RVA":"0xca3450","registration_caller_return_RVA":"0xca34b0","original_guard_publication_RVA":"0xce7a48","guard_publication_caller_return_RVA":"0x5b90ac",
 "guard_field_RVA":"0x17a4220","global_epoch_RVA":"0x1607b04","TLS_thread_epoch_offset":"0x10",
 "owned_exit_allocator_RVA":"0xcc2a50","owned_exit_allocator_caller_return_RVA":"0xcb9a30","owned_exit_allocator_arguments":[0,256],
 "stop_before_RVA":"0x5b8104","next_factory_pointer_RVA":"0x1731880","next_factory_pointer_read_RVA":"0x5b8108",
 "loader_TLS_OS_readiness_and_fresh_allocation_are_owned_models":True,"CRT_empty_encoded_exit_table_readiness_is_owned_model":True,"CRT_native_initialization_qualified":False,
 "cleanup_registration_or_guard_result_fixture_used":False,"cleanup_callback_execution_or_teardown_qualified":False,"native_allocator_failure_or_existing_table_growth_qualified":False,
 "whole_mapped_memory_and_permissions_exact":True,"immutable_source_and_unmodified_loader_regions":True,"thread_epoch_update_exact":True,"all_declared_callee_return_ABIs_exact":True,
 "original_cleanup_registration_qualified":True,"original_helper_guard_publication_qualified":True,"first_helper_complete_return_qualified":False,"cold_parent_return_or_unlock_qualified":False,
 "full_cold_registry_initialization_qualified":False,"full_metadata_descriptor_construction_allocation_and_publication_qualified":False,"native_Windows_OS_resources_qualified":False,
 "selected_runtime_reader_profile_qualified":False,"populated_RS_identity_generation_lifetime_qualified":False,"normal_AFD_input_authority_closed":False,
 "complete_deterministic_source_bootstrap_closed":False,"independent_enabled_output_retirement_proven":False,"native_rear_runtime_allowed":False,
 "new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"production_code_changed":False,"private_raw_material_exported":False,"next_experiment":"E011DS",
 "details":rows,"totals":{k:sum(r[k] for r in rows) for k in fields}}
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({k:report[k] for k in ("status","scenarios","totals","next_experiment")}),flush=True)
if __name__=="__main__":main()
