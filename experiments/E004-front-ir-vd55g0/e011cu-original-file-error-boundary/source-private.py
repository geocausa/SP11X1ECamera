#!/usr/bin/env python3
"""Original file-failure prefix under exact measured external API contracts; no thread-slot result supplied."""
from pathlib import Path
import importlib.util,json,hashlib,struct,collections
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_PROT_READ,UC_PROT_EXEC
from unicorn.arm64_const import *
ROOT=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean');OUT=Path(__file__).resolve().parent
P=ROOT/'experiments/E004-front-ir-vd55g0/e011cs-original-file-opening-boundary/source-private.py'
PIN='dd702d68c66b7c7225dd5ab36228d45c72f81e7657d686a36435d0103601df46'
assert hashlib.sha256(P.read_bytes()).hexdigest()==PIN
spec=importlib.util.spec_from_file_location('cu_cs',P);CS=importlib.util.module_from_spec(spec);spec.loader.exec_module(CS)
CP=CS.CP;CF=CS.CF
OBS_PATH=ROOT/'experiments/E004-front-ir-vd55g0/e011ct-windows-file-api-oracle/WINDOWS-FILE-API-SAFE.json'
assert hashlib.sha256(OBS_PATH.read_bytes()).hexdigest()=='be5aa0b6b117d74dc3675b464514d49753b768e3bf9966543592ae02db3a2747'
OBS=json.loads(OBS_PATH.read_text());assert OBS['identity']=='E011CT-OS-002' and OBS['process_architecture']=='ARM64'
assert not OBS['valid_handle'] and OBS['Win32_last_error']==OBS['native_thread_last_error']==OBS['NTDLL_thread_last_error']==3
API_BASE=0x93000000
RANGES=[{'RVA':'0xcaec20','bytes':24,'sha256':'5ab54a47cecf13bf4d1e91b07664062643845ce88d1093f5277ee20baa1fe73e'},{'RVA':'0xcb3f88','bytes':52,'sha256':'e694b98652128676855088839ee6f169f8f822f9ca91d70ddeee538ab431d8f9'},{'RVA':'0xcb41d0','bytes':36,'sha256':'ae5a8b5b11857782740c3ffbd89a163fe1bad0f8dae05759a3cd36a96aec283e'},{'RVA':'0xcb4230','bytes':40,'sha256':'038cd6ccc094c86ac1a1be86f27576f83789a4d6462f6f970a74da877767c6c6'},{'RVA':'0xcb4260','bytes':8,'sha256':'96ff7c717ce66ef87a48a0b6adf3063d1f3f657f7fc68466882056f0e40d3d53'},{'RVA':'0xcb4270','bytes':8,'sha256':'6afaaf0a49acb5e2cf133b8341b072bd5574af7b7b97b3bf3adf2e1f0f53cb92'},{'RVA':'0xcba190','bytes':8,'sha256':'1a9d71a54f394bf3beff00fd677f340e94c0457e613e218375dd07facb16cd84'},{'RVA':'0xcfd658','bytes':52,'sha256':'7bea17cb29263475d319b019b2da719a3081509811187c64853d60076cfc9620'},{'RVA':'0xcfd6c8','bytes':60,'sha256':'43fd8e809d6302857fbb86c36fbf0574ae0a2b7f4cb2bf4bf1304860638c5d73'}]
OLD_ATTACH=CP.attach
def attach(n):
 b=OLD_ATTACH(n);n.u.mem_map(API_BASE,4096,UC_PROT_READ|UC_PROT_EXEC)
 n.u.mem_write(n.base+0xf7e3b8,struct.pack('<Q',API_BASE));n.u.mem_write(n.base+0xf7e468,struct.pack('<Q',API_BASE+32))
 return b
CP.attach=attach
CASES=[]
class Failure:
 def __init__(self,o):
  self.o=o;self.n=o.n;self.u=o.u;self.b=o.crt;self.active=False;self.calls=[];self.pending={};self.instructions={}
  for row in RANGES:
   at=int(row['RVA'],16);size=row['bytes'];assert hashlib.sha256(CF.p.get_data(at,size)).hexdigest()==row['sha256']
   for i in CF.c.disasm(CF.p.get_data(at,size),self.n.base+at):self.instructions[i.address]=i
  type(self.u).hook_add(self.u,UC_HOOK_CODE,self.code);type(self.u).hook_add(self.u,UC_HOOK_MEM_WRITE,self.memory)
 def snapshots(self):
  n=self.n;b=self.b;f=self.o.f;u=self.u
  rows=[('stack',n.stack,0x10000),('CRT',b.own,b.extent),('image',n.base,CF.p.OPTIONAL_HEADER.SizeOfImage),('native_heap',n.heap,0x30000),('camera_arena',f.arena,f.arena_size),('serialized',f.map,f.map_size),('API_page',API_BASE,4096)]
  return {name:bytes(u.mem_read(at,z)) for name,at,z in rows}
 def contract(self,name,args,ret):
  b=self.b;n=self.n;u=self.u
  assert self.active and b.depths[self.records]==1
  schedule=[('CreateFileW',0xcfd65c),('GetLastError',0xcfd700),('GetLastError',0xcb423c),('GetLastError',0xcb3fa8)]
  assert len(self.calls)<len(schedule) and (name,ret)==schedule[len(self.calls)]
  if name=='CreateFileW':
   assert len(args)==7 and args[0]==b.utf_output and args[1:3]==[0x80000000,1] and args[4:]==[3,128,0]
   assert n.stack<=args[3] and args[3]+24<=n.stack+0x10000
   assert bytes(u.mem_read(args[3],24))==b'\x18'+bytes(15)+b'\x01'+bytes(7)
   wide=bytes(u.mem_read(args[0],b.utf_bytes));assert b.utf_bytes==74 and wide[-2:]==bytes(2)
   assert hashlib.sha256(wide[:-2].decode('utf-16-le').encode('ascii')+b'\0').hexdigest()==OBS['source_filename_sha256']
   value=0xffffffffffffffff
  else:value=OBS['Win32_last_error']
  self.calls.append({'name':name,'return_RVA':hex(ret),'measured_external_result':value});return value
 def code(self,u,pc,z,user):
  if not self.active:return
  assert not self.pending
  if pc==self.n.base+0xcba198:
   self.stopped=True;u.emu_stop();return
  if pc in [API_BASE,API_BASE+32]:
   name='CreateFileW' if pc==API_BASE else 'GetLastError'
   args=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(7)]
   ret=u.reg_read(UC_ARM64_REG_LR)-self.n.base;value=self.contract(name,args,ret)
   u.reg_write(UC_ARM64_REG_X0,value);u.reg_write(UC_ARM64_REG_PC,self.n.base+ret);return
  assert pc in self.instructions,('unqualified failure dependency',hex(pc))
  i=self.instructions[pc];assert bytes(u.mem_read(pc,4))==CF.p.get_data(pc-self.n.base,4)
  self.counts[pc]+=1;self.pending_pc=pc
  if i.mnemonic.startswith(('stp','str','stur')):
   mem=next(op.mem for op in i.operands if op.type==3);assert not mem.index
   at=self.b.api.reg(CF.c.reg_name(mem.base))+mem.disp;name=CF.c.reg_name(i.operands[0].reg)
   width=2 if i.mnemonic.endswith('h') else 1 if i.mnemonic.endswith('b') else 16 if name.startswith('q') else 8 if name in ('fp','lr') or name.startswith(('x','d')) else 4
   operands=i.operands[:2] if i.mnemonic=='stp' else i.operands[:1]
   for k,op in enumerate(operands):
    address=at+k*width;value=self.b.api.reg(CF.c.reg_name(op.reg))&((1<<(8*width))-1)
    if self.n.stack<=address and address+width<=self.n.stack+0x10000:
     off=address-self.n.stack;self.stack_model[off:off+width]=value.to_bytes(width,'little')
    else:
     assert (pc-self.n.base,address,width,value)==(0xcfd6f0,self.records+56,1,0)
     off=address-self.b.own;assert self.crt_model[off:off+width]==bytes(width)
    for j in range(0,width,8):
     size=min(width-j,8);self.pending[(address+j,size)]=(value>>(8*j))&((1<<(8*size))-1)
 def memory(self,u,access,at,z,value,user):
  if not self.active:return
  assert u.reg_read(UC_ARM64_REG_PC)==self.pending_pc and (at,z) in self.pending
  assert value&((1<<(8*z))-1)==self.pending.pop((at,z));self.writes[(self.pending_pc,at,z)]+=1
 def negatives(self):
  u=self.u;n=self.n;b=self.b
  args=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(7)]
  cases=[]
  for k in [0,1,2,3,4,5,6]:
   changed=args.copy();changed[k]+=1;cases.append(('CreateFileW',changed,0xcfd65c))
  cases.extend([('CreateFileW',args,0xcfd660),('GetLastError',args,0xcfd700),('UnknownFileAPI',args,0xcfd65c)])
  before=self.snapshots();depths=b.depths.copy();events=b.api_events.copy();regs=[u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(31)];pc=u.reg_read(UC_ARM64_REG_PC)
  self.active=True
  try:
   for request in cases:
    try:self.contract(*request)
    except AssertionError:pass
    else:raise AssertionError('invalid file API request admitted')
    assert self.calls==[] and self.snapshots()==before and b.depths==depths and b.api_events==events
    assert [u.reg_read(globals()['UC_ARM64_REG_X'+str(k)]) for k in range(31)]==regs and u.reg_read(UC_ARM64_REG_PC)==pc
    b.policy.check_pages()
  finally:self.active=False
  return len(cases)
 def run(self):
  u=self.u;n=self.n;b=self.b;assert u.reg_read(UC_ARM64_REG_PC)==n.base+0xcfd658
  self.records=next(at for at,size in b.allocs if size==64*72)
  rejected=self.negatives()
  before=self.snapshots();self.stack_model=bytearray(before['stack']);self.crt_model=bytearray(before['CRT']);self.crt_model[self.records-b.own+56]=0
  depths=b.depths.copy();allocs=b.allocs.copy();next_alloc=b.next_alloc;events=b.api_events.copy()
  self.counts=collections.Counter();self.writes=collections.Counter();self.stopped=False
  self.active=True
  try:u.emu_start(n.base+0xcfd658,n.end,count=10000)
  finally:self.active=False
  assert self.stopped and not self.pending and u.reg_read(UC_ARM64_REG_PC)==n.base+0xcba198
  after=self.snapshots();assert after['stack']==self.stack_model and after['CRT']==self.crt_model
  assert all(after[k]==v for k,v in before.items() if k not in ['stack','CRT'])
  assert b.depths==depths and b.allocs==allocs and b.next_alloc==next_alloc and b.api_events==events
  assert len(self.calls)==4 and sum(self.counts.values())==72 and sum(self.writes.values())==16
  assert u.reg_read(UC_ARM64_REG_W0)==0xffffffff and u.reg_read(UC_ARM64_REG_X1)==0xffffffffffffffff
  assert self.o.f.readq(self.o.output)==0 and bytes(u.mem_read(b.utf_output,b.utf_bytes))==before['CRT'][b.utf_output-b.own:b.utf_output-b.own+b.utf_bytes]
  b.policy.check_pages()
  return {'original_failure_instructions':sum(self.counts.values()),'exact_failure_store_chunks':sum(self.writes.values()),'external_API_contract_calls':self.calls,'negative_API_requests':rejected,'independent_entire_stack_and_CRT_models':True,'all_other_entire_regions_unchanged':True,'descriptor0_reserved_flag_cleared':True,'descriptor0_handle_still_invalid':True,'descriptor0_lock_still_held':True,'UTF16_owner_retained':True,'stop_before_original_FlsSetValue_branch':'0xcba198','FlsSetValue_IAT_RVA':'0xf7e218','CRT_FLS_slot_global_RVA':'0x1607168','CRT_FLS_slot_file_image_value':'0xffffffff','requested_slot_unallocated':True,'requested_FLS_value':'0xffffffffffffffff','FlsSetValue_executed':False,'original_CFE600_not_executed':True,'public_output_zero':True,'full_original_cleanup_or_outer_return_qualified':False}
class Startup(CS.Startup):
 def invoke_entry(self):
  super().invoke_entry();CASES.append(Failure(self).run())
CP.Startup=Startup
def main():
 inherited,camera=CS.CR.authority();sources=[]
 assert CF.p.get_dword_at_rva(0x1607168)==0xffffffff
 for name,pin in CF.CC.CA.BB.AZ.AV.FILES:
  blob=(CF.CC.CA.BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==pin
  for mode in ['ANSI','OEM']:
   CP.CP_MODE=mode;CASES.clear();CS.CASES.clear();CS.CR.CASES.clear();CS.CR.CQ.CASES.clear()
   row=CP.integrated(blob,pin,camera);assert len(CASES)==1;row['cases'][0].update(CASES[0]);sources.append(row)
   print(json.dumps({'policy':mode,'source_sha256':pin,'stop_before_original_FlsSetValue':'0xcba198','original_file_failure_instructions':72}),flush=True)
 cases=[row['cases'][0] for row in sources]
 result={'experiment':'E011CU','status':'PASS_BOUNDED_ORIGINAL_FILE_FAILURE_TO_UNALLOCATED_THREAD_SLOT','base_commit':'279cd57f8573f8ff540fc0bb28eee0900b42eb1c','inherited_CS_verifier_sha256':PIN,'measured_Windows_input_identity':OBS['identity'],'evidence_class':'UNCHANGED_ORIGINAL_SOURCE_WITH_STRICT_MEASURED_EXTERNAL_FILE_ERROR_CONTRACTS_IN_OWNED_FIXTURES','original_code_authority':RANGES,'sources':sources,'integrated_camera_cases':len(cases),'distinct_tuning_sources':3,'original_failure_instructions':sum(c['original_failure_instructions'] for c in cases),'exact_failure_store_chunks':sum(c['exact_failure_store_chunks'] for c in cases),'external_file_contract_calls':6,'external_thread_error_contract_calls':18,'negative_API_requests':sum(c['negative_API_requests'] for c in cases),'independent_entire_stack_and_CRT_models':True,'all_other_entire_regions_unchanged':True,'all_lock_depths_and_allocations_unchanged':True,'descriptor0_flag_cleared':True,'descriptor0_lock_held':True,'UTF16_owner_retained':True,'source_FlsSetValue_executed':False,'CRT_FLS_slot_initialization_qualified':False,'original_CFE600_qualified':False,'full_original_cleanup_or_outer_return_qualified':False,'native_rear_runtime_allowed':False,'new_camera_Starts':0,'new_reboots':0,'new_Linux_image_tests':0,'next_experiment':'E011CV'}
 assert len(cases)==6 and result['original_failure_instructions']==432 and result['exact_failure_store_chunks']==96 and result['negative_API_requests']==60
 (OUT/'FILE-ERROR-SAFE.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if not isinstance(v,(list,dict))}),flush=True)
if __name__=='__main__':main()
