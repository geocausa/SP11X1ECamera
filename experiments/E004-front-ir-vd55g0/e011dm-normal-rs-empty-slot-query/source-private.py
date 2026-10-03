#!/usr/bin/env python3
"""SP11-only unchanged-reader tag initialization with unchanged CRT guard bodies.
Registry/settings, node/context/pool/empty slots and OS SRW/CV are owned models.
The original query and selected empty-slot helper execute without return fixtures.
No Windows DLL execution, device access, original bytes or optical export.
"""
from pathlib import Path
import hashlib,importlib.util,json,random,struct
import pefile,capstone
from unicorn import UC_HOOK_CODE,UC_HOOK_MEM_WRITE,UC_HOOK_MEM_READ
from unicorn.arm64_const import *
ROOT=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-clean")
OUT=Path(__file__).resolve().parent
EX=ROOT/"experiments/E004-front-ir-vd55g0"
IMAGE_SHA="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
PINS={0x740e70:(1792,"904c4309b9ddae9adffdf2e5dacf92a84c829edc839921be18a56b226b5cc08e"),
0xce7ad8:(188,"d310e3f40e9666c9e47bb67e2bef87de0f68142b0413af59613ad85d362f6efc"),
0x5d4d30:(2144,"cb1f18cbcf4bf0c7dc34f9081c2d83b148e36a213ba92a0686ea3585698dcdff"),
0x5c3758:(1340,"0db48188ba17a0501542acc05e83a79d648f821ccbe32eddd6581bb98ffe4ff8"),
0xce7a48:(140,"6f84e7a29bab93d10f7570516c2e5be4717e748b87314a6c75857f05ce4455d2")}
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
IMAGE=load("dl_image",next(EX.glob("e011ai-*/native-private.py")))
blob=IMAGE.DLL.read_bytes();assert hashlib.sha256(blob).hexdigest()==IMAGE_SHA
pe=pefile.PE(data=blob)
for r,(size,pin) in PINS.items():assert hashlib.sha256(pe.get_data(r,size)).hexdigest()==pin
cs=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);cs.detail=True
instructions={i.address:i for r,(size,pin) in PINS.items() for i in cs.disasm(pe.get_data(r,size),r)}
qsites=sorted(i.address for i in instructions.values() if i.mnemonic=="bl" and i.operands[0].imm==0x5d4d30)
assert len(qsites)==14
QCALLERS={site+4:k//2 for k,site in enumerate(qsites)}
TAG=0x17a30e0;GUARD=0x1b303fc;EPOCH=0x1607b04;INDEX=0x16a3740
FIELDS=(0xc0,0xd8,0x48,0x60,0x78,0x90,0xa8)
TAGWRITERS=(0x741544,0x741544,0x741550,0x741550,0x74155c,0x74155c,0x741564)
REGISTRY_SETS=[tuple(0x1000+i for i in range(7)),tuple(0x2000+3*i for i in range(7))]
SAVED=[*[globals()["UC_ARM64_REG_X"+str(i)] for i in range(19,30)],
       *[globals()["UC_ARM64_REG_D"+str(i)] for i in range(8,16)]]
def reject(fn,args,mutations):
 count=0
 for bad in mutations:
  try:fn(*bad)
  except AssertionError:count+=1
  else:raise AssertionError("invalid dependency admitted")
 return count
def scenario(bias,index,epoch,values,capacity,request):
 mode="absent"
 n=IMAGE.Native();u=n.u;b=n.base
 use_fallback=request==0 or bool(request&(1<<63))
 settings=0x73000000;teb=0x74000000;api=0x75000000
 u.mem_map(settings,0x400000);u.mem_map(teb,0x30000);u.mem_map(api,0x1000)
 node=n.heap+bias;dest=n.heap+0x10000+bias;registry=n.heap+0x8000;context=n.heap+0x9000
 array=teb+0x10000;block=teb+0x20000
 def wr(at,v,z=4):u.mem_write(at,int(v).to_bytes(z,"little"))
 def rd(at,z=4):return int.from_bytes(u.mem_read(at,z),"little")
 wr(settings+0x10,settings+0x1000,8);wr(settings+0x1010,settings+0x2000,8)
 wr(teb+0x58,array,8);wr(array+index*8,block,8)
 wr(b+INDEX,index);wr(b+EPOCH,epoch);wr(block+16,epoch);wr(b+GUARD,0)
 u.reg_write(UC_ARM64_REG_X18,teb);u.reg_write(UC_ARM64_REG_TPIDR_EL0,teb)
 wr(node+0x400,context,8);wr(node+0x33f4,1)
 wr(block+0x138,request,8)
 pools=[settings+0x10000+k*0x1000 for k in range(4)]
 slots=[[settings+0x20000+k*0x80000+t*0x6000 for t in range(capacity)] for k in range(4)]
 for k,offset in enumerate((0x490,0x498,0x4a8,0x4b0)):
  wr(node+offset,pools[k],8);wr(pools[k]+0x278,capacity)
  for t,slot in enumerate(slots[k]):wr(pools[k]+0x298+t*8,slot,8)
 for off,value in zip(FIELDS,values):wr(registry+off,value)
 canary=bytes((k*31+9)&255 for k in range(28));u.mem_write(b+TAG,canary)
 targets={name:api+0x100+k*0x10 for k,name in enumerate(("AcquireSRWLockExclusive","ReleaseSRWLockExclusive","WakeAllConditionVariable"))}
 reverse={v:k for k,v in targets.items()};bindings={}
 for module in pe.DIRECTORY_ENTRY_IMPORT:
  for item in module.imports:
   name=item.name.decode("ascii") if item.name else ""
   if name in targets:
    cell=b+item.address-pe.OPTIONAL_HEADER.ImageBase;wr(cell,targets[name],8);bindings[cell]=targets[name]
 assert len(bindings)==3
 expected_tags=tuple(v|0x08000000 for v in values);expected_vector=struct.pack("<7I",*expected_tags)
 rows=[]
 # Cold same-thread initialization; same-thread reuse; stale-thread synchronization.
 for phase in ("cold","warm","stale_thread"):
  if phase!="cold":
   for off,value in zip(FIELDS,values):wr(registry+off,value^0x55aa55aa)
  if phase=="stale_thread":wr(block+16,epoch)
  prior=bytes((k*11+3)&255 for k in range(132));u.mem_write(dest+0x2c50,prior)
  u.mem_write(n.stack,bytes(0x10000));sp=n.stack+0xf000
  for reg in SAVED:u.reg_write(reg,0x12340000+reg+bias)
  u.reg_write(UC_ARM64_REG_X0,node);u.reg_write(UC_ARM64_REG_X1,dest)
  u.reg_write(UC_ARM64_REG_SP,sp);u.reg_write(UC_ARM64_REG_LR,n.end)
  saved={reg:u.reg_read(reg) for reg in SAVED}
  settings_start_mask=rd(settings+0x2020)
  before={(lo,hi,perm):bytes(u.mem_read(lo,hi-lo+1)) for lo,hi,perm in u.mem_regions()}
  expected={}
  def patch(at,data):
   region=next(k for k in before if k[0]<=at and at+len(data)<=k[1]+1)
   if region not in expected:expected[region]=bytearray(before[region])
   expected[region][at-region[0]:at-region[0]+len(data)]=data
  patch(settings+0x2020,struct.pack("<I",0x08000000))
  if phase=="cold":
   patch(b+TAG,expected_vector);patch(b+GUARD,struct.pack("<I",epoch+1))
   patch(b+EPOCH,struct.pack("<I",epoch+1));patch(block+16,struct.pack("<I",epoch+1))
  elif phase=="stale_thread":patch(block+16,struct.pack("<I",epoch+1))
  visits=[];returns=[];query_pending=[None];settingswrites=[];tagwrites=[];query_slots=[];rs_queries=[];stack_arguments=[];slot_lookups=[];pool_reads=[];api_calls=[];held=[False];wake=[0];negative=[0]
  def query_contract(ret,args):
   assert ret in QCALLERS and len(args)==8
   assert args==[node,b+TAG,sp-0xf0,QCALLERS[ret],args[4],0,0,1]
   assert args[4]==(request if not use_fallback or len(query_slots)%2==0 else 1),json.dumps({"request":request,"query_count":len(query_slots),"slot":args[3],"selector":args[4],"ret":hex(ret)})
   assert bytes(u.mem_read(b+TAG,28))==expected_vector
  def api_contract(name,ret,args,ownership):
   assert name in targets and len(args)==1
   assert args==[b+(0x16a3730 if name=="WakeAllConditionVariable" else 0x16a3738)]
   if name=="AcquireSRWLockExclusive":assert ret in (0xce7b08,0xce7a74) and not ownership
   elif name=="ReleaseSRWLockExclusive":assert ret in (0xce7b80,0xce7ab4) and ownership
   else:assert ret==0xce7ac4 and not ownership
  def code(uc,address,size,user):
   if address==n.end:uc.emu_stop();return
   rva=address-b;ret=uc.reg_read(UC_ARM64_REG_LR)-b
   if address in reverse:
    name=reverse[address];args=[uc.reg_read(UC_ARM64_REG_X0)]
    api_contract(name,ret,args,held[0])
    negative[0]+=reject(api_contract,(name,ret,args,held[0]),[
     (name,ret+4,args,held[0]),(name,ret,[args[0]+8],held[0]),
     (name,ret,args+[0],held[0]),(name,ret,args,not held[0])])
    if name=="AcquireSRWLockExclusive":held[0]=True
    elif name=="ReleaseSRWLockExclusive":held[0]=False
    else:wake[0]+=1
    api_calls.append(name);uc.reg_write(UC_ARM64_REG_X0,0);uc.reg_write(UC_ARM64_REG_PC,b+ret);return
   if rva==query_pending[0]:
    query_pending[0]=None
    assert len(query_slots)>len(returns)
    assert rd(sp-0xf0+query_slots[-1]*8,8)==0
    returns.append(query_slots[-1])
   if rva==0x5d4d30:
    assert query_pending[0] is None
    query_pending[0]=ret
    args=[uc.reg_read(UC_ARM64_REG_X0+k) for k in range(8)];query_contract(ret,args)
    negatives=[]
    for k,change in ((0,8),(1,4),(2,8),(3,1),(5,1),(6,1),(7,1)):
     bad=args.copy();bad[k]+=change;negatives.append((ret,bad))
    negatives.extend(((ret+4,args),(ret,args+[0])))
    negative[0]+=reject(query_contract,(ret,args),negatives)
    ninth=rd(uc.reg_read(UC_ARM64_REG_SP));stack_arguments.append(ninth)
    def stack_contract(v):assert v==0
    stack_contract(ninth)
    negative[0]+=reject(stack_contract,(ninth,),[(1,),(0xffffffff,),(0xffffffffffffffff,)])
    query_slots.append(args[3])
    if args[3]==5:rs_queries.append(args[4])
   if rva==0x5c3758:
    receiver=uc.reg_read(UC_ARM64_REG_X0);key=uc.reg_read(UC_ARM64_REG_X1)
    q=query_slots[-1];selector=request if not use_fallback or (len(query_slots)-1)%2==0 else 1
    actual=[receiver,key,uc.reg_read(UC_ARM64_REG_X2),uc.reg_read(UC_ARM64_REG_X3)]
    def slot_contract(a):
     assert a==[slots[0][selector%capacity],expected_tags[q]&~0x08000000,1,node+0x78]
    slot_contract(actual)
    mutations=[]
    for k in range(4):
     bad=actual.copy();bad[k]+=1;mutations.append((bad,))
    for foreign in (slots[1][selector%capacity],slots[0][selector%capacity]+8):
     bad=actual.copy();bad[0]=foreign;mutations.append((bad,))
    negative[0]+=reject(slot_contract,(actual,),mutations)
    slot_lookups.append((q,selector,receiver))
   if rva in (0x5b80a8,0x5bde08):
    assert 0x740e70<=ret<0x741570 or 0x5d4d30<=ret<0x5d5590
    if rva==0x5b80a8:uc.reg_write(UC_ARM64_REG_X0,registry)
    elif rva==0x5bde08:uc.reg_write(UC_ARM64_REG_X0,settings)
    uc.reg_write(UC_ARM64_REG_PC,b+ret);return
   allowed=rva in instructions or 0x11d0<=rva<0x1220
   assert allowed,"unqualified original code boundary"
   assert bytes(uc.mem_read(address,4))==pe.get_data(rva,4)
   visits.append(rva)
  def memory(uc,access,address,size,value,user):
   rva=uc.reg_read(UC_ARM64_REG_PC)-b
   if b+TAG<=address<b+TAG+28:
    k=(address-(b+TAG))//4
    assert phase=="cold" and size==4 and address==b+TAG+k*4
    assert rva==TAGWRITERS[k] and value==expected_tags[k]
    tagwrites.append(k)
   elif settings<=address and address+size<=settings+0x400000:
    if not(size==4 and {(0x740f58,0x2020):settings_start_mask,(0x740f68,0x2014):0,(0x740f78,0x200c):0,(0x740f88,0x2020):0x08000000,(0x5d4d8c,0x2020):0x08000000,(0x5d4d9c,0x2014):0,(0x5d4dac,0x200c):0,(0x5d4dbc,0x2020):0x08000000}.get((rva,address-settings))==value):
     (OUT/"SETTINGS-DIAGNOSTIC-SAFE.json").write_text(json.dumps({"source_RVA":hex(rva),"settings_field_offset":hex(address-settings),"bytes":size,"derived_scalar":value,"phase":phase}))
     raise AssertionError("unsupported settings mutation")
    settingswrites.append((rva,address-settings,size))
   elif n.stack<=address and address+size<=n.stack+0x10000:
    assert sp-0x500<=address and address+size<=sp
   elif dest+0x2c50<=address and address+size<=dest+0x2cd4:
    assert mode!="absent" and 0x740e70<=rva<0x741570
   else:
    allowed={(0x740f58,settings+0x2020,4):0,(0xce7b14,b+GUARD,4):0xffffffff,
     (0xce7a84,b+EPOCH,4):epoch+1,(0xce7a88,b+GUARD,4):epoch+1,
     (0xce7aa4,block+16,4):epoch+1,(0xce7b6c,block+16,4):epoch+1}
    if allowed.get((rva,address,size))!=(value&((1<<(8*size))-1)):
     (OUT/"WRITE-DIAGNOSTIC-SAFE.json").write_text(json.dumps({"source_RVA":hex(rva),"destination_relative_image":hex(address-b),"bytes":size,"expected_store_site":(rva,address,size) in allowed,"phase":phase,"field_value":value if address in (b+GUARD,b+EPOCH,block+16,settings+0x2020) else None}))
     raise AssertionError("unowned original nonstack write")
  def read(uc,access,address,size,value,user):
   rva=uc.reg_read(UC_ARM64_REG_PC)-b
   if rva==0x5d5018:
    assert address==pools[0]+0x278 and size==4
   if rva==0x5d5038:
    selector=request if not use_fallback or (len(query_slots)-1)%2==0 else 1
    assert address==pools[0]+0x298+(selector%capacity)*8 and size==8
    pool_reads.append(selector)
  hooks=[u.hook_add(UC_HOOK_CODE,code),u.hook_add(UC_HOOK_MEM_WRITE,memory),u.hook_add(UC_HOOK_MEM_READ,read)]
  try:u.emu_start(b+0x740e70,n.end,count=20000)
  finally:
   for handle in hooks:u.hook_del(handle)
  assert u.reg_read(UC_ARM64_REG_PC)==n.end and u.reg_read(UC_ARM64_REG_SP)==sp
  assert all(u.reg_read(reg)==value for reg,value in saved.items())
  assert bytes(u.mem_read(n.stack,0xeb00))==bytes(0xeb00) and bytes(u.mem_read(sp,0x1000))==bytes(0x1000)
  assert not held[0]
  expected_apis=["AcquireSRWLockExclusive","ReleaseSRWLockExclusive"]*(2 if phase=="cold" else 1 if phase=="stale_thread" else 0)
  if phase=="cold":expected_apis+=["WakeAllConditionVariable"]
  assert api_calls==expected_apis and wake[0]==int(phase=="cold")
  assert tagwrites==(list(range(7)) if phase=="cold" else [])
  assert mode=="absent" and rs_queries==([request,1] if use_fallback else [request])
  assert query_slots==[q for q in range(7) for _ in range(2 if use_fallback else 1)] and len(slot_lookups)==len(query_slots) and len(pool_reads)==len(query_slots)
  assert returns==query_slots
  assert bytes(u.mem_read(b+TAG,28))==expected_vector
  after={(lo,hi,perm):bytes(u.mem_read(lo,hi-lo+1)) for lo,hi,perm in u.mem_regions()}
  assert after.keys()==before.keys()
  stack_region=next(k for k in before if k[0]==n.stack)
  assert all(after[k]==expected.get(k,v) for k,v in before.items() if k!=stack_region),"whole nonstack memory mismatch"
  rows.append({"phase":phase,"owned_settings_store_sites":[[hex(r),hex(o),z] for r,o,z in dict.fromkeys(settingswrites)],"owned_settings_stores":len(settingswrites),"reader_instruction_visits":sum(0x740e70<=r<0x741570 for r in visits),
   "initializer_instruction_visits":sum(0x741518<=r<0x741570 for r in visits),
   "original_guard_instruction_visits":sum(0xce7a48<=r<0xce7ad4 or 0xce7ad8<=r<0xce7b94 for r in visits),
   "all_original_instruction_visits":len(visits),"tag_field_stores":len(tagwrites),
   "actual_query_calls":len(query_slots),"actual_null_results":len(returns),
   "query_instruction_visits":sum(0x5d4d30<=r<0x5d5590 for r in visits),"slot_helper_instruction_visits":sum(0x5c3758<=r<0x5c3c94 for r in visits),"actual_empty_slot_lookups":len(slot_lookups),"zero_ninth_stack_arguments":len(stack_arguments),"owned_standard_API_calls":len(api_calls),
   "invalid_dependency_requests_rejected":negative[0]})
 return rows
def main():
 rows=[]
 for bias in (0,16,128,512):
  for index in (0,37):
   for epoch in (0x80000000,0xffffff00):
    for pattern,values in enumerate(REGISTRY_SETS):
     for capacity in (1,3,5,9):
      for request in (0,1,17,0x100000007,0xffffffffffffffff):
       phases=scenario(bias,index,epoch,values,capacity,request)
       rows.append({"placement":bias,"loader_index":index,"initial_epoch":epoch,"registry_pattern":pattern,"pool_capacity":capacity,"request_selector":request,"record_state":"empty","phases":phases})
       if len(rows)%32==0:print(json.dumps({"scenarios_passed":len(rows)}),flush=True)
 totals={key:sum(phase[key] for row in rows for phase in row["phases"]) for key in rows[0]["phases"][0] if key not in ("phase","owned_settings_store_sites")}
 report={"experiment":"E011DM","status":"PASS_BOUNDED_ORIGINAL_RS_QUERY_EMPTY_SELECTED_SLOTS",
 "original_image_sha256":IMAGE_SHA,"source_pins":{hex(r):{"bytes":size,"sha256":pin} for r,(size,pin) in PINS.items()},
 "scenarios":len(rows),"reader_phase_cases":len(rows)*3,"totals":totals,"details":rows,
 "node_pool_offsets":["0x490","0x498","0x4a8","0x4b0"],"selected_pool_offset":"0x490",
 "pool_capacity_offset":"0x278","inline_slot_array_offset":"0x298","empty_slot_state_offset":"0x30",
 "TLS_request_selector_offset":"0x138","ninth_query_stack_argument":0,
 "registry_settings_node_context_pools_empty_slots_and_OS_SRW_CV_are_owned_models":True,
 "query_result_fixture_used":False,"slot_helper_result_fixture_used":False,
 "runtime_tag_vector_result_fixture_used":False,"original_guard_result_fixture_used":False,
 "whole_nonstack_memory_and_mapping_permissions_exact":True,"stack_redzones_and_preserved_ABI_exact":True,
 "original_code_and_owned_pool_slot_objects_immutable":True,"actual_empty_query_path_qualified":True,
 "actual_registry_content_qualified":False,"populated_record_identity_and_lifetime_qualified":False,
 "metadata_registry_initialization_qualified":False,"concurrent_wait_and_real_Windows_loader_qualified":False,
 "upstream_AFD_normal_count_policy_closed":False,"complete_deterministic_source_bootstrap_closed":False,
 "independent_enabled_output_retirement_proven":False,"native_rear_runtime_allowed":False,
 "new_camera_starts":0,"new_reboots":0,"new_kernel_build":False,"private_bytes_exported":False}
 (OUT/"SOURCE-SAFE.json").write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps({k:v for k,v in report.items() if k not in ("details","source_pins")}),flush=True)
if __name__=="__main__":main()
