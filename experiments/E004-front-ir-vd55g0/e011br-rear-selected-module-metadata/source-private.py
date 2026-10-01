from pathlib import Path
import importlib.util,struct,json,collections,hashlib,bisect
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;R=HERE.parent
sp=importlib.util.spec_from_file_location("br_bq",R/"e011bq-rear-source-mode-selection/source-private.py")
BQ=importlib.util.module_from_spec(sp);sp.loader.exec_module(BQ)
class Production(BQ.Production):
 def __init__(self,blob,bias):
  super().__init__(blob,bias);self.br_pending=None;self.br_modules={};self.br_checks=collections.Counter();self.br_stores=[]
 def loader_watch(self,u,pc,size,user):
  super().loader_watch(u,pc,size,user)
  if self.phase!="loader":return
  r=pc-self.n.base
  if r==0x6f35ac:
   assert self.br_pending is None
   rr=u.reg_read(UC_ARM64_REG_X1);sid=self.readi(rr+8);assert rr==self.table+sid*224 and sid in self.sy
   off=self.sy[sid]["record_offset"];raw=self.blob[off:off+56];selector=struct.unpack_from("<I",raw,44)[0]
   assert selector in self.records
   self.br_pending=(sid,raw,selector)
  elif r==0x6f35b0:
   assert self.br_pending is not None
   sid,raw,selector=self.br_pending;self.br_pending=None;module=u.reg_read(UC_ARM64_REG_X0)
   if not module:self.br_checks["null_module_returns"]+=1;return
   ix=bisect.bisect_right(self.allocs,module,key=lambda item:item[0])-1;ptr,extent=self.allocs[ix]
   assert ptr==module and extent>=288 and ptr not in self.released
   name=raw[4:36].split(b"\0")[0];profile=BQ.BP.BO.BO.BM.BL.text(self.records,selector).encode()
   filename=self.blob[88:].split(b"\0",1)[0][:64];nameptr=self.readq(module+8)
   tests={"owned_name":bytes(u.mem_read(nameptr,len(name)+1))==name+b"\0",
    "embedded_name":bytes(u.mem_read(module+16,len(name)+1))==name+b"\0",
    "version":bytes(u.mem_read(module+60,8))==raw[36:44],
    "selector":self.readi(module+68)==selector,
    "numeric_profile":bytes(u.mem_read(module+72,8))==struct.pack("<2I",*self.records[selector][1:3]),
    "profile_text":bytes(u.mem_read(module+80,len(profile)+1))==profile+b"\0",
    "header_name":bytes(u.mem_read(module+208,len(filename)+1))==filename+b"\0",
    "symbol_ID":self.readi(module+56)==sid}
   self.br_checks["positive_module_returns"]+=1
   for key,passed in tests.items():
    if key!="owned_name":assert passed,"source common metadata mismatch: "+key
    self.br_checks[key+("_match" if passed else "_mismatch")]+=1
   assert module not in self.br_modules
   self.br_modules[module]=(sid,selector,name)
  elif r==0x6f3654:
   module=u.reg_read(UC_ARM64_REG_X23);assert module in self.br_modules
   sid,selector,name=self.br_modules[module];leaf=u.reg_read(UC_ARM64_REG_X22);owner=u.reg_read(UC_ARM64_REG_X27)
   self.br_checks["store_leaf_match" if leaf==self.nodes+160*selector else "store_leaf_mismatch"]+=1
   self.br_checks["store_owner_match" if owner==(self.readq(leaf+48) or leaf) else "store_owner_mismatch"]+=1
   assert leaf==self.nodes+160*selector
   assert owner==(self.readq(leaf+48) or leaf)
   self.br_stores.append((owner,module,selector,name,u.reg_read(UC_ARM64_REG_X0)))

 def headers(self):
  u=self.n.u;count=0;self.starts=[p for p,z in self.allocs];self.sizes=dict(self.allocs)
  for module,(sid,selector,name) in self.br_modules.items():
   self.active(module,288)
   raw=self.blob[self.sy[sid]["record_offset"]:self.sy[sid]["record_offset"]+56]
   profile=BQ.BP.BO.BO.BM.BL.text(self.records,selector).encode()
   header_name=self.blob[88:].split(b"\0",1)[0][:64]
   fields={16:name+b"\0",56:raw[:4],60:raw[36:44],68:raw[44:48],
    72:struct.pack("<2I",*self.records[selector][1:3]),80:profile+b"\0",208:header_name+b"\0"}
   for at,expected in fields.items():
    assert bytes(u.mem_read(module+at,len(expected)))==expected;count+=1
   nameptr=self.readq(module+8);self.active(nameptr)
   allocated_name=self.name_bytes(nameptr,64);assert len(allocated_name)<64
   self.active(nameptr,len(allocated_name)+1)
  return count
 def key_plan(self):
  self.starts=[p for p,z in self.allocs];self.sizes=dict(self.allocs);final={};excluded=0
  reachable={}
  for kind,keys in self.cases():
   sid=self.model.select(keys)
   if sid is not None:reachable.setdefault(sid,keys)
  for owner,module,selector,name,slot in self.br_stores:
   ownerid=(owner-self.nodes)//160
   final[(ownerid,name)]=(module,selector,slot)
  # Existing-key semantics only: inspect owned key before native lookup, never insert an unknown name.
  plan=[];excluded_owners=collections.Counter()
  for (ownerid,name),(module,selector,slot) in final.items():
   assert self.readq(slot)==module
   entry,extent,off=self.active(slot,8);assert extent==56 and off==48
   key=entry+16 if self.readq(entry+40)<=15 else self.readq(entry+16)
   keyname=self.name_bytes(key,64);assert len(keyname)<64
   assert self.readq(entry+32)==len(keyname)
   if key!=entry+16:self.active(key,len(keyname)+1)
   assert keyname==self.name_bytes(self.readq(module+8),64)
   if keyname!=name:
    excluded+=1;excluded_owners[ownerid]+=1;continue
   assert ownerid in reachable,"source-exact map owner lacks tested independent query"
   plan.append((ownerid,name,module,selector,slot,reachable[ownerid]))
  return plan,{"final_unique_source_bindings":len(final),"source_exact_existing_keys":len(plan),
   "different_owned_name_keys_excluded":excluded,"different_owned_name_profile_owners":len(excluded_owners),
   "source_exact_nonroot_profile_owners":len({owner for owner,n,m,s,p,k in plan if owner}),
   "owned_map_keys_equal_actual_module_owned_names":True}
 def retrieval(self,plan):
  self.phase="selected_module";u=self.n.u;counts=collections.Counter()
  before_end=self.next;before=bytes(u.mem_read(self.arena,before_end-self.arena))
  heap_before=bytes(u.mem_read(self.n.heap,0x30000));before_alloc=len(self.allocs);before_release=len(self.released)
  for ownerid,name,module,selector,slot,keys in plan:
   q=self.n.heap+0x1000+self.bias;tmp=self.n.heap+0x2000+self.bias;src=self.n.heap+0x2100+self.bias
   u.mem_write(q,b"".join(struct.pack("<2I",*key) for key in keys))
   self.invoke_low(0x6f3bd0,[self.manager,q,len(keys)])
   selected=u.reg_read(UC_ARM64_REG_X0);assert selected==self.nodes+160*ownerid
   allocs=len(self.allocs);u.mem_write(tmp,bytes(32));u.mem_write(src,name+b"\0")
   # Original string construction from independently typed source name, not an emulated capture.
   self.invoke_low(0x2e2e0,[tmp,src,len(name)])
   self.invoke_low(0x6f3f48,[selected+96,tmp]);got=u.reg_read(UC_ARM64_REG_X0)
   assert got==slot and self.readq(got)==module
   assert len(self.allocs)-allocs==(1 if len(name)>15 else 0)
   if self.readq(tmp+24)>15:self.invoke_low(0xf078,[self.readq(tmp)])
   u.mem_write(q,b"\xa5"*(len(keys)*8));u.mem_write(tmp,b"\xa5"*32);u.mem_write(src,b"\xa5"*(len(name)+1))
   counts["root_map_returns" if ownerid==0 else "nonroot_map_returns"]+=1
   counts["selector_returns"]+=1
  assert bytes(u.mem_read(self.arena,before_end-self.arena))==before
  assert bytes(u.mem_read(self.n.heap,0x30000))==heap_before
  assert len(self.allocs)-before_alloc==len(self.released)-before_release
  self.bounds()
  return dict(counts)
 def qualify(self):
  result=self.run_full();self.tree();assert self.br_pending is None
  assert len(self.br_modules)==self.dispatches==len(self.br_stores) and not self.br_checks["null_module_returns"]
  header_checks=self.headers();plan,scope=self.key_plan();before=self.retrieval(plan)
  result=self.ownership(result);self.tree();header_checks+=self.headers()
  after=self.retrieval(plan);header_checks+=self.headers();assert before==after
  return {**result,**scope,"common_source_metadata_fields_per_module":7,"common_source_metadata_checks_after_return_and_retirement":header_checks,
   "actual_module_metadata_positive_returns":len(self.br_modules),"metadata_return_checks":dict(self.br_checks),
   "root_existing_key_map_returns":before.get("root_map_returns",0)+after.get("root_map_returns",0),
   "nonroot_existing_key_map_returns":before.get("nonroot_map_returns",0)+after.get("nonroot_map_returns",0),
   "original_selected_profile_returns":before["selector_returns"]+after["selector_returns"],
   "exact_source_hierarchy_pointer_checks":self.link_checks,
   "existing_map_lookup_independent_of_retired_source_context":True,
   "lookup_no_missing_key_insertions":True,"all_preexisting_allocation_bytes_and_heap_preserved":True}
def main():
 results=[]
 for name,sha in BQ.BP.BO.BO.BM.BL.BH.FIXTURE.AV.FILES[1:]:
  blob=(BQ.BP.BO.BO.BM.BL.BH.FIXTURE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  for bias in [0,1]:
   f=Production(blob,bias);result=f.qualify();results.append({"source_sha256":sha,**result});print(json.dumps(results[-1]),flush=True)
 totals={key:sum(r[key] for r in results) for key in ["source_reader_full_returns","original_module_dispatches","actual_module_metadata_positive_returns",
  "common_source_metadata_checks_after_return_and_retirement","root_existing_key_map_returns","nonroot_existing_key_map_returns",
  "original_selected_profile_returns","different_owned_name_keys_excluded","exact_source_hierarchy_pointer_checks"]}
 out={"experiment":"E011BR","status":"PASS_BOUNDED_COMMON_MODULE_METADATA_AND_SOURCE_EXACT_NONROOT_RETRIEVAL",
  "base_commit":"ac96bf38e0947345ad9eae6b4206791d779dde7b","original_full_loader_returns":len(results),"source_cases":results,**totals,
  "all_map_key_naming_rules_qualified":False,"all_module_payload_fields_qualified":False,"entire_manager_source_lifetime_closed":False,
  "factory_destruction_and_storage_reuse_qualified":False,"arbitrary_platform_sources_qualified":False,
  "retained_shims":["0x11D0","0x11F0","0xCAE740","0xF5E600","0xCAE730"],
  "originals_exported":False,"captured_scalars_as_producer_inputs":False,"new_camera_starts":0,"new_reboots":0,
  "native_rear_runtime_allowed":False,"production_C_changed":False,"kernel_build_performed":False,"whole_camera_stack_parity_closed":False}
 (HERE/"RETRIEVAL-SAFE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps({"status":out["status"],"totals":totals}),flush=True)
if __name__=="__main__":main()
