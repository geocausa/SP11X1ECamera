#!/usr/bin/env python3
"""Owned original CRT file-opening boundary; no file API return or native execution."""
from pathlib import Path
import importlib.util,json,hashlib,collections,struct,ntpath
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean')
OUT=Path(__file__).resolve().parent
BASE='bed8af72a659484c1670a471e9000424e8ccc738'
P=ROOT/'experiments/E004-front-ir-vd55g0/e011cr-original-unicode-conversion/source-private.py'
PIN='2a4933fe06074024b17dffdb4e4cf86b2454dacf66fcf4bf3a0d1c47845fb8b8'
assert hashlib.sha256(P.read_bytes()).hexdigest()==PIN
spec=importlib.util.spec_from_file_location('cs_cr',P);CR=importlib.util.module_from_spec(spec);spec.loader.exec_module(CR)
CP=CR.CP;CF=CR.CF;CASES=[]
RANGES=[{'RVA': '0xcb7300', 'bytes': 28, 'sha256': 'e1f73058a5d75230088e8935971d1150dff0eb2a2335a632e38dda91ba8c7d18'}, {'RVA': '0xcb7398', 'bytes': 28, 'sha256': 'ba0fb2d4a1e1a1d1effa82370b5d86970cbf56048020dfd66c1702bb8237af60'}, {'RVA': '0xcc08e8', 'bytes': 80, 'sha256': '4f177a21963336a3f142db64bcec525abf01b65831d4676d14866dda85f83b89'}, {'RVA': '0xcc0970', 'bytes': 72, 'sha256': '8498a7e738c7b95e3b2a1b26a363c54ee7b125df8fffbee548de781297eddaf4'}, {'RVA': '0xcc09bc', 'bytes': 24, 'sha256': '546eb09e8450abb32c04a6d542bf45aa9f91e0ce84936ef638d7e57b750c4353'}, {'RVA': '0xcc09f0', 'bytes': 56, 'sha256': 'c1a72af2034e8c8d470c597e6975134cfe05a30459b7c67af8143b6d12763976'}, {'RVA': '0xcfd0b0', 'bytes': 64, 'sha256': '7cdf908405da8f2bf5066fc78d1a79ae3a36d3470a4ee54da40e82f05200a23f'}, {'RVA': '0xcfd130', 'bytes': 28, 'sha256': 'eb02b969e65a793bcf179127e4743ff80c828205d0f4b05b0954b84b0816cac1'}, {'RVA': '0xcfd174', 'bytes': 8, 'sha256': 'cdcf225db2b62b265c48a639c4a9537387aceb5b726356d04af9383f459fd682'}, {'RVA': '0xcfd1b4', 'bytes': 48, 'sha256': '29598bdf2964f5c247a198fb72486ca828eb5899c6d594b767aae32446548b73'}, {'RVA': '0xcfd1f8', 'bytes': 16, 'sha256': '11aa07d874a055c02c0191635411f79d7dcd777e3903cb4079ac66b6604a30eb'}, {'RVA': '0xcfd224', 'bytes': 16, 'sha256': 'a7aa91d90bd0af173ebd28a341106e60ae9f751c773bfc65df80f062d7314c30'}, {'RVA': '0xcfd240', 'bytes': 4, 'sha256': '493aab44dab9d62e9361785d627095e37d1290cf67f391be1ac2a57fc6871b16'}, {'RVA': '0xcfd278', 'bytes': 4, 'sha256': '69b0fd73cb3fa65c9be17681a2873b41eb3abeb55f22e49055e15f4ab5b4d923'}, {'RVA': '0xcfd294', 'bytes': 4, 'sha256': '86482bc1516451d120ae8b4393c2270eb85e48deb13912b482b366b66b525e76'}, {'RVA': '0xcfd2bc', 'bytes': 4, 'sha256': 'e6ba70e42753d32f6b191913c9b5b8d1d35719ddb343728776aaef15081d60cf'}, {'RVA': '0xcfd2cc', 'bytes': 4, 'sha256': '0ec41b409d6246a98309f174f6110afe43c13713f2bbfda23a3d9bdeaaa9c739'}, {'RVA': '0xcfd2dc', 'bytes': 4, 'sha256': 'b99e930ce2618fb63905c625b52a16befb60b6d6d8dbba2aaeb335508d79acc5'}, {'RVA': '0xcfd2ec', 'bytes': 4, 'sha256': '90f9c25ad3f66005440ad03bd7640d53cc3001e9299554e60b5215e3963ef34e'}, {'RVA': '0xcfd2fc', 'bytes': 24, 'sha256': 'fc2e88e0d6a1b88946cb11ba6dffdc0af22333b5b838912054d6f890b91eee53'}, {'RVA': '0xcfd4e8', 'bytes': 8, 'sha256': 'c6a9dbad1ebee24f6afed92dc5f6ea7fd7536a2f6c2520644fe4d84a03117998'}, {'RVA': '0xcfd4f8', 'bytes': 32, 'sha256': 'fa83a79a40f1aa80c9193306c376dd76ac820786f2fee7c795fd4a715807b5e9'}, {'RVA': '0xcfd570', 'bytes': 92, 'sha256': '1dbc24508576ac4341cf13d72ad84c79d3ba9a23de5d1e54e8e4637358d456e7'}, {'RVA': '0xcfd5e8', 'bytes': 16, 'sha256': '4042e74c7e9085fa898bcf39f8876473d13463b8492cb8430e10c3c8a9a4bfb7'}, {'RVA': '0xcfd618', 'bytes': 68, 'sha256': '2eb9e8664fef7bb3f591bff4a3f17811d9dca8939723b00fbdde4541646fb142'}]
OLD_ATTACH=CP.attach
def attach(n):
 b=OLD_ATTACH(n);old=b.runtime_mutex;b.opening_active=False;b.opening_locks=[]
 def mutex(name,receiver,ret):
  if not b.opening_active:return old(name,receiver,ret)
  assert name in ('EnterCriticalSection','LeaveCriticalSection')
  records=next(at for at,size in b.allocs if size==64*72)
  assert receiver in b.lock_objects
  contract={('EnterCriticalSection',b.global_mutex(7),0xcc090c),('EnterCriticalSection',records,0xcc09cc),('LeaveCriticalSection',b.global_mutex(7),0xcc0978)}
  assert (name,receiver,ret) in contract
  assert b.depths[receiver]==(0 if name=='EnterCriticalSection' else 1)
  b.depths[receiver]+=1 if name=='EnterCriticalSection' else -1
  b.opening_locks.append({'operation':name,'receiver':'global7' if receiver==b.global_mutex(7) else 'initialized_record0','return_RVA':hex(ret)})
  b.api_events[name]+=1
 b.runtime_mutex=mutex;return b
CP.attach=attach
class Opening:
 def __init__(self,o):
  self.o=o;self.n=o.n;self.u=o.u;self.b=o.crt;self.api=self.b.api;self.active=False;self.pending={};self.instructions={}
  for r in RANGES:
   a=int(r['RVA'],16);z=r['bytes']
   assert hashlib.sha256(CF.p.get_data(a,z)).hexdigest()==r['sha256']
   for i in CF.c.disasm(CF.p.get_data(a,z),self.n.base+a):self.instructions[i.address]=i
  type(self.u).hook_add(self.u,UC_HOOK_CODE,self.code);type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.memory)
 def code(self,u,pc,z,user):
  if not self.active:return
  assert not self.pending
  if pc==self.n.base+0xcfd658:u.emu_stop();return
  if pc not in self.instructions:
   assert pc in (0x90070000,0x90070020),('unqualified dependency',hex(pc))
   call=self.b.opening_locks[-1]
   assert u.reg_read(UC_ARM64_REG_PC)==self.n.base+int(call['return_RVA'],16)
   assert call['operation']==('EnterCriticalSection' if pc==0x90070000 else 'LeaveCriticalSection')
   self.adapter_calls+=1;return
  i=self.instructions[pc];self.counts[pc]+=1;self.pending_pc=pc
  if i.mnemonic.startswith(('stp','str','stur')):
   mem=next(op.mem for op in i.operands if op.type==3);assert not mem.index
   at=self.api.reg(CF.c.reg_name(mem.base))+mem.disp
   name=CF.c.reg_name(i.operands[0].reg)
   width=2 if i.mnemonic.endswith('h') else 1 if i.mnemonic.endswith('b') else 16 if name.startswith('q') else 8 if name in ('fp','lr') or name.startswith(('x','d')) else 4
   operands=i.operands[:2] if i.mnemonic=='stp' else i.operands[:1]
   for j,op in enumerate(operands):
    address=at+j*width;value=self.api.reg(CF.c.reg_name(op.reg))&((1<<(8*width))-1)
    if self.n.stack<=address and address+width<=self.n.stack+0x10000:
     off=address-self.n.stack;self.stack_model[off:off+width]=value.to_bytes(width,'little')
    else:
     assert (pc-self.n.base,address,width,value) in [(0xcc0a14,self.records+56,1,1),(0xcc0a20,self.records+40,8,0xffffffffffffffff)]
     off=address-self.b.own;assert self.crt_model[off:off+width]==value.to_bytes(width,'little')
    for chunk in range(0,width,8):
     z=min(width-chunk,8);self.pending[(address+chunk,z)]=(value>>(8*chunk))&((1<<(8*z))-1)
 def memory(self,u,access,at,z,value,user):
  if not self.active:return
  assert u.reg_read(UC_ARM64_REG_PC)==self.pending_pc and (at,z) in self.pending
  assert value&((1<<(8*z))-1)==self.pending.pop((at,z))
  self.writes[(self.pending_pc,at,z)]+=1
 def snapshots(self):
  n=self.n;u=self.u;f=self.o.f;b=self.b
  return {name:bytes(u.mem_read(at,z)) for name,at,z in [('stack',n.stack,0x10000),('CRT',b.own,b.extent),('image',n.base,CF.p.OPTIONAL_HEADER.SizeOfImage),('native_heap',n.heap,0x30000),('camera_arena',f.arena,f.arena_size),('serialized',f.map,f.map_size)]}
 def negatives(self):
  b=self.b;records=self.records
  cases=[('EnterCriticalSection',b.global_mutex(8),0xcc090c),('EnterCriticalSection',self.n.stack,0xcc090c),('EnterCriticalSection',b.global_mutex(7),0xcc090d),('EnterCriticalSection',records,0xcc09cd),('LeaveCriticalSection',records,0xcc0978),('UnknownMutexOperation',b.global_mutex(7),0xcc090c),('EnterCriticalSection',records,0xcc09cc),('LeaveCriticalSection',b.global_mutex(7),0xcc0978)]
  baseline=self.snapshots();depths=b.depths.copy();events=b.api_events.copy();locks=list(b.opening_locks)
  b.opening_active=True
  try:
   for args in cases:
    try:b.runtime_mutex(*args)
    except AssertionError:pass
    else:raise AssertionError('invalid opening lock accepted')
    assert b.depths==depths and b.api_events==events and b.opening_locks==locks and self.snapshots()==baseline
    b.policy.check_pages()
  finally:b.opening_active=False
  return len(cases)
 def run(self):
  n=self.n;u=self.u;b=self.b
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0xcfd4e8
  before=self.snapshots();self.stack_model=bytearray(before['stack']);self.crt_model=bytearray(before['CRT'])
  self.records=next(at for at,size in b.allocs if size==64*72);off=self.records-b.own
  self.crt_model[off+56]=1;struct.pack_into('<Q',self.crt_model,off+40,0xffffffffffffffff)
  depths=b.depths.copy();assert depths[self.records]==depths[b.global_mutex(7)]==0
  allocations=list(b.allocs);next_alloc=b.next_alloc
  self.counts=collections.Counter();self.writes=collections.Counter();self.adapter_calls=0
  self.active=True;b.opening_active=True
  try:u.emu_start(n.base+0xcfd4e8,n.end,count=10000)
  finally:self.active=False;b.opening_active=False
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0xcfd658 and not self.pending
  after=self.snapshots()
  assert after['stack']==self.stack_model and after['CRT']==self.crt_model
  assert all(after[k]==v for k,v in before.items() if k not in ('stack','CRT'))
  expected_depths=depths.copy();expected_depths[self.records]=1
  assert b.depths==expected_depths and b.allocs==allocations and b.next_alloc==next_alloc
  assert b.opening_locks==[{'operation':'EnterCriticalSection','receiver':'global7','return_RVA':'0xcc090c'},{'operation':'EnterCriticalSection','receiver':'initialized_record0','return_RVA':'0xcc09cc'},{'operation':'LeaveCriticalSection','receiver':'global7','return_RVA':'0xcc0978'}]
  assert self.adapter_calls==3 and sum(self.counts.values())==183 and sum(self.writes.values())==47
  args=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(7)]
  assert args[0]==b.utf_output and args[1:3]==[0x80000000,1] and args[4:]==[3,128,0]
  assert n.stack<=args[3] and args[3]+24<=n.stack+0x10000
  assert bytes(u.mem_read(args[3],24))==b'\x18'+b'\0'*15+b'\x01'+b'\0'*7
  wide=bytes(u.mem_read(args[0],b.utf_bytes));assert b.utf_bytes==74 and wide[-2:]==b'\0\0'
  text=wide[:-2].decode('utf-16-le')
  assert hashlib.sha256(text.encode('ascii')+b'\0').hexdigest()=='4cbd98d9784913d9111d301111dba46a1ec9d90e9545d450fc616bca635c432d'
  drive,tail=ntpath.splitdrive(text);assert drive.upper()=='C:' and tail.startswith('\\')
  assert self.o.f.readq(self.o.output)==0;b.policy.check_pages()
  return {'stop_before_CreateFileW_RVA':'0xcfd658','original_opening_instruction_count':sum(self.counts.values()),'exact_opening_store_chunks':sum(self.writes.values()),'independent_entire_stack_model':True,'independent_entire_CRT_model':True,'whole_other_regions_unchanged':True,'strict_initialized_mutex_calls':b.opening_locks,'global7_lock_balanced':True,'record0_lock_held':True,'descriptor0_reserved':True,'descriptor_record_bytes':72,'reserved_flag_offset':56,'invalid_handle_offset':40,'CreateFileW_desired_access':0x80000000,'CreateFileW_share_mode':1,'CreateFileW_creation_disposition':3,'CreateFileW_attributes':128,'CreateFileW_template_handle':0,'security_attributes_bytes':24,'security_descriptor_null':True,'security_inherit_handle':True,'owned_filename_UTF16_bytes':74,'path_drive_C_absolute':True,'path_content_exported':False,'CreateFileW_executed':False,'CreateFileW_result_supplied':False,'UTF16_owner_retained':True,'public_output_zero':True,'rejected_mutex_contract_requests':self.negatives()}
class Startup(CR.Startup):
 def invoke_entry(self):
  super().invoke_entry();CASES.append(Opening(self).run())
CP.Startup=Startup
def main():
 inherited,camera=CR.authority();sources=[]
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  for mode in ('ANSI','OEM'):
   CP.CP_MODE=mode;CASES.clear();CR.CASES.clear();CR.CQ.CASES.clear()
   row=CP.integrated(blob,pin,camera);assert len(CASES)==len(CR.CASES)==1
   row['cases'][0].update(CR.CASES[0]);row['cases'][0].update(CASES[0]);sources.append(row)
   print(json.dumps({'policy':mode,'source_sha256':pin,'stop_before_CreateFileW':'0xcfd658','owned_UTF16_bytes':74}),flush=True)
 cases=[row['cases'][0] for row in sources]
 result={'experiment':'E011CS','status':'PASS_BOUNDED_ORIGINAL_FILE_OPENING_BOUNDARY','base_commit':BASE,'inherited_CR_verifier_sha256':PIN,'original_code_authority':RANGES,'sources':sources,'integrated_camera_cases':len(cases),'distinct_tuning_sources':3,'original_opening_instructions':sum(c['original_opening_instruction_count'] for c in cases),'exact_opening_store_chunks':sum(c['exact_opening_store_chunks'] for c in cases),'strict_initialized_mutex_calls':18,'global7_balanced_pairs':6,'record0_locks_held':6,'mutex_contract_rejections':sum(c['rejected_mutex_contract_requests'] for c in cases),'independent_entire_stack_and_CRT_models':True,'CreateFileW_executed':False,'CreateFileW_result_supplied':False,'actual_Windows_filesystem_or_last_error_qualified':False,'UTF16_owner_cleanup_qualified':False,'whole_outer_return_qualified':False,'final_output_publication_qualified':False,'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,'runtime_or_image_test':False,'next_experiment':'E011CT'}
 assert len(cases)==6 and result['original_opening_instructions']==1098 and result['exact_opening_store_chunks']==282 and result['mutex_contract_rejections']==48
 (OUT/'OPENING-SAFE.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(list,dict))}),flush=True)
if __name__=='__main__':main()
