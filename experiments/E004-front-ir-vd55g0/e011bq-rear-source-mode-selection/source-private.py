#!/usr/bin/env python3
"""E011BQ: source-derived mode hierarchy and exact native profile selection."""
from pathlib import Path
import importlib.util,json,struct,hashlib,collections
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;EX=HERE.parent
sp=importlib.util.spec_from_file_location("bq_ownership",EX/"e011bp-rear-aec-output-ownership/source-private.py")
BP=importlib.util.module_from_spec(sp);sp.loader.exec_module(BP)
class Model:
 def __init__(self,records):
  self.r=records;self.ordinary={sid:[] for sid in records};self.flagged={sid:[] for sid in records};self.links={}
  for sid,row in records.items():
   if row[4] not in records and row[4]!=0xffffffff:raise ValueError("invalid source primary reference")
   parent=row[3]
   if parent not in [sid,0xffffffff]:(self.flagged if row[2] else self.ordinary)[parent].append(sid)
  for sid,row in records.items():
   seen=set();cur=sid
   while cur is not None:
    if cur in seen:raise ValueError("source primary-reference cycle")
    seen.add(cur);n=records[cur][4];cur=None if n==0xffffffff else n
   parent=row[3] if row[3] not in [sid,0xffffffff] else None
   peers=(self.flagged if row[2] else self.ordinary)[parent] if parent is not None else []
   i=peers.index(sid) if parent is not None else 0
   a=self.ordinary[sid];b=self.flagged[sid]
   self.links[sid]={16:None if row[4]==0xffffffff else row[4],24:parent,32:a[0] if a else None,40:a[-1] if a else None,48:parent if row[2] else None,56:b[0] if b else None,64:b[-1] if b else None,72:peers[i+1] if peers and i+1<len(peers) else None}
 def child(self,sid,key):
  while self.links[sid][16] is not None:sid=self.links[sid][16]
  for child in self.ordinary[sid]:
   mode=self.r[child][1]
   if (mode&65535,mode>>16)==(key[0]&65535,key[1]&65535):return child
  return None
 def group(self,sid,keys,count,start):
  primary=self.links[sid][16]
  if primary is not None:return self.group(primary,keys,count,start)
  for key in keys[:count]:
   child=self.child(sid,key)
   if child is not None:
    after=start+1
    if after<count:child=self.group(child,keys,count,after)
    if child is not None:return child
  return None
 def select(self,keys):
  sid=0;index=1
  while index<len(keys):
   stop=index+1
   while stop<len(keys) and keys[stop][0]==keys[index][0]:stop+=1
   group=keys[index:stop];primary=self.links[sid][16]
   if primary is not None:sid=self.group(primary,group,len(group),0)
   else:
    out=None
    for key in group:
     out=self.child(sid,key)
     if out is not None and len(group)>1:out=self.group(out,group,len(group),1)
     if out is not None:break
    sid=out
   if sid is None:return None
   index=stop
  return sid
 def path(self,sid):
  out=[]
  while True:
   row=self.r[sid];out.append((row[1]&65535,row[1]>>16))
   if row[3] in [sid,0xffffffff]:break
   sid=row[3]
  return list(reversed(out))
class Production(BP.Production):
 def __init__(self,blob,bias):
  super().__init__(blob,bias);self.model=Model(self.records);self.link_checks=0;self.helper_calls=collections.Counter()
  # The callbacks observe exact original helper entries, without changing execution.
  for rva in [0x6f1d68,0x6f1db8]:
   type(self.n.u).hook_add(self.n.u,UC_HOOK_CODE,self.select_watch,begin=self.n.base+rva,end=self.n.base+rva)
 def select_watch(self,u,pc,size,user):
  if self.phase=="select":self.helper_calls[pc-self.n.base]+=1
 def tree(self):
  for sid,fields in self.model.links.items():
   for offset,target in fields.items():
    expected=0 if target is None else self.nodes+160*target
    assert self.readq(self.nodes+160*sid+offset)==expected,"source hierarchy field mismatch"
    self.link_checks+=1
 def prefix(self):
  super().prefix();self.tree()
 def cases(self):
  m=self.model;cases=[];absent=next((kind,value) for kind in [65535,65534,65533] for value in range(65535,65530,-1) if all((r[1]&65535,r[1]>>16)!=(kind,value) for r in self.records.values() if not r[2]))
  for sid,row in self.records.items():
   if row[2]:continue
   keys=m.path(sid)
   cases.append(("source_path",keys))
   cases.append(("unmatched_tail",keys+[absent]))
   cases.append(("ignored_index0",[(0x12345678,0x87654321)]+keys[1:]))
   cases.append(("U16_match_with_U32_queries",[(a|0x10000,b|0x20000) for a,b in keys]))
  for parent,children in m.ordinary.items():
   groups=collections.defaultdict(list)
   for sid in children:
    value=self.records[sid][1];groups[value&65535].append((value&65535,value>>16))
   for group in groups.values():
    if not group:continue
    prefix=m.path(parent)
    cases.append(("repeated_category",prefix+group+group[:1]))
    cases.append(("reversed_repeated_category",prefix+list(reversed(group))+group[:1]))
    if len(group)>1:cases.append(("split_full_U32_category",prefix+[group[0],(group[1][0]|0x10000,group[1][1])]))
  cases.extend([("zero_count",[]),("one_count_ignored",[(0xffffffff,0xffffffff)])])
  return cases
 def selection(self):
  self.phase="select";u=self.n.u;query=self.n.heap+0x1000+self.bias
  before_arena=bytes(u.mem_read(self.arena,self.arena_size));before_heap=bytes(u.mem_read(self.n.heap,0x30000))
  allocations=len(self.allocs);releases=len(self.released);results=collections.Counter();categories=collections.Counter();max_query=0
  for kind,keys in self.cases():
   raw=b"".join(struct.pack("<2I",*key) for key in keys);max_query=max(max_query,len(raw));assert len(raw)<=2048
   u.mem_write(query,raw);expected_sid=self.model.select(keys)
   self.invoke_low(0x6f3bd0,[self.manager,query if keys else 0,len(keys)])
   actual=u.reg_read(UC_ARM64_REG_X0);expected=0 if expected_sid is None else self.nodes+160*expected_sid
   assert actual==expected,"native selector/source model mismatch"
   results["returns"]+=1;results["null_returns" if expected_sid is None else "root_returns" if expected_sid==0 else "nonroot_returns"]+=1;categories[kind]+=1
  single_returns=0;single_nonnull=0
  for sid in self.records:
   target=sid
   while self.model.links[target][16] is not None:target=self.model.links[target][16]
   children=self.model.ordinary[target]
   value=self.records[children[0]][1] if children else 0xffffffff
   key=(value&65535,value>>16);raw=struct.pack("<2I",*key);u.mem_write(query,raw);max_query=max(max_query,8)
   expected_sid=self.model.child(sid,key);self.invoke_low(0x6f1d68,[self.nodes+160*sid,query])
   assert u.reg_read(UC_ARM64_REG_X0)==(0 if expected_sid is None else self.nodes+160*expected_sid)
   single_returns+=1;single_nonnull+=expected_sid is not None
  u.mem_write(query,b"\xa5"*max_query)
  assert bytes(u.mem_read(self.arena,self.arena_size))==before_arena
  assert bytes(u.mem_read(self.n.heap,0x30000))==before_heap
  assert len(self.allocs)==allocations and len(self.released)==releases
  self.bounds()
  return {**dict(results),"direct_single_helper_returns":single_returns,"direct_single_helper_nonnull_returns":single_nonnull,"query_categories":dict(categories),"original_single_helper_entries":self.helper_calls[0x6f1d68],"original_group_helper_entries":self.helper_calls[0x6f1db8],"all_query_memory_preserved":True}
 def qualify(self):
  result=self.run_full();self.tree();self.selection();before=self.helper_calls.copy()
  result=self.ownership(result);self.tree();queries=self.selection()
  assert self.helper_calls==before+before
  return {**result,"exact_source_hierarchy_pointer_checks":self.link_checks,
   "source_wire16_to_runtime16_primary_link_verified":True,"flagged_runtime48_parent_map_owner_verified":True,
   "ordinary_children32_40_flagged_children56_64_and_sibling72_verified":True,
   "source_physical_record_order_retained_in_child_lists":True,
   "selector_results_before_and_after_retired_source_identical":True,
   "original_selector_returns":2*queries["returns"],"original_selector_nonroot_returns":2*queries["nonroot_returns"],
   "original_selector_null_returns":2*queries["null_returns"],"original_selector_root_returns":2*queries["root_returns"],
   "original_direct_single_helper_returns":2*queries["direct_single_helper_returns"],"original_direct_single_helper_nonnull_returns":2*queries["direct_single_helper_nonnull_returns"],
   "query_categories_per_phase":queries["query_categories"],"original_single_helper_entries":self.helper_calls[0x6f1d68],
   "original_group_helper_entries":self.helper_calls[0x6f1db8],"selector_changes_no_source_heap_or_allocation_bytes":True}
def malformed():
 records={0:(0,0,0,0xffffffff,0xffffffff),1:(1,1,0,0,0xffffffff)};bad=[]
 x=dict(records);x[1]=(1,1,0,0,9);bad.append(x)
 x=dict(records);x[1]=(1,1,0,0,1);bad.append(x)
 x=dict(records);x[0]=(0,0,0,0xffffffff,1);x[1]=(1,1,0,0,0);bad.append(x)
 count=0
 for x in bad:
  try:Model(x)
  except ValueError:count+=1
  else:raise AssertionError("invalid primary shape accepted")
 return count
def owned_group_variants():
 # Independent owned typed graph. The original loader input is left unchanged.
 name,sha=BP.BO.BO.BM.BL.BH.FIXTURE.AV.FILES[-1]
 blob=(BP.BO.BO.BM.BL.BH.FIXTURE.AV.ARCHIVE/name).read_bytes();f=Production(blob,1);f.prefix();f.phase="select"
 records={0:(0,0,0,0xffffffff,0xffffffff),1:(1,0x00010001,0,0,0xffffffff),
  2:(2,0x00020001,0,1,0xffffffff),3:(3,0x00030001,0,2,0xffffffff),
  4:(4,0x00040001,0,0,0xffffffff),5:(5,0x00020001,0,4,0xffffffff),
  6:(6,0x00010002,0,0,1)}
 m=Model(records);u=f.n.u;n=f.n;nodes=n.heap+0x8001;size=160*len(records);before=bytes(u.mem_read(nodes,size));root_before=bytes(u.mem_read(f.manager+1064,8))
 for sid,row in records.items():
  raw=bytearray(160);struct.pack_into("<3I",raw,0,*row[:3])
  for offset,target in m.links[sid].items():struct.pack_into("<Q",raw,offset,0 if target is None else nodes+160*target)
  u.mem_write(nodes+160*sid,bytes(raw))
 u.mem_write(f.manager+1064,struct.pack("<Q",nodes));graph_before=bytes(u.mem_read(nodes,size));query=n.heap+0x1001
 cases=[[(0,0),(1,1),(1,2)],[(0,0),(1,2),(1,1)],[(0,0),(1,1),(1,2),(1,3)],
  [(0,0),(1,4),(1,2)],[(0,0),(1,1),(0x10001,2)],[(0,0),(2,1),(1,2)],
  [(0,0),(1,9),(1,2)],[(0,0),(1,1),(1,9)],[(0,0),(1,1),(1,2),(1,9)]]
 results=[];max_query=0;start_calls=f.helper_calls.copy()
 for keys in cases:
  raw=b"".join(struct.pack("<2I",*key) for key in keys);u.mem_write(query,raw);max_query=max(max_query,len(raw));expected=m.select(keys)
  f.invoke_low(0x6f3bd0,[f.manager,query,len(keys)]);assert u.reg_read(UC_ARM64_REG_X0)==(0 if expected is None else nodes+160*expected)
  results.append({"query_records":len(keys),"positive_repeated_group_return":expected not in [None,0],"null_return":expected is None})
 assert any(x["positive_repeated_group_return"] for x in results) and any(x["null_return"] for x in results)
 assert bytes(u.mem_read(nodes,size))==graph_before
 u.mem_write(nodes,before);u.mem_write(f.manager+1064,root_before);u.mem_write(query,b"\xa5"*max_query);f.bounds()
 return {"owned_graph_nodes":len(records),"owned_graph_allowed_extent":size,"query_cases":results,
  "original_selector_returns":len(results),"original_group_helper_entries":f.helper_calls[0x6f1db8]-start_calls[0x6f1db8],
  "original_source_file_and_original_source_nodes_unmodified":True,"owned_graph_and_manager_scratch_restored":True,
  "original_loader_acceptance_of_mutated_mode_category_not_claimed":True}
def main():
 results=[];rejected=malformed()
 for name,sha in BP.BO.BO.BM.BL.BH.FIXTURE.AV.FILES[1:]:
  blob=(BP.BO.BO.BM.BL.BH.FIXTURE.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  for bias in [0,1]:
   f=Production(blob,bias);r=f.qualify();results.append({"source_sha256":sha,**r});print(json.dumps(results[-1]),flush=True)
 variants=owned_group_variants()
 summary={"experiment":"E011BQ","status":"PASS_BOUNDED_SOURCE_HIERARCHY_AND_NONROOT_NATIVE_SELECTION",
  "base_commit":"8569913d3a7d4b669748a9e2dad7d1136015547c","source_cases":results,"owned_group_graph":variants,"malformed_primary_shapes_rejected_before_execution":rejected,
  "original_full_loader_returns":len(results),"original_exact_reader_returns":sum(x["source_reader_full_returns"] for x in results),
  "exact_source_hierarchy_pointer_checks":sum(x["exact_source_hierarchy_pointer_checks"] for x in results),
  "original_selector_returns":sum(x["original_selector_returns"] for x in results),
  "original_selector_nonroot_returns":sum(x["original_selector_nonroot_returns"] for x in results),
  "original_selector_null_returns":sum(x["original_selector_null_returns"] for x in results),
  "original_direct_single_helper_returns":sum(x["original_direct_single_helper_returns"] for x in results),
  "original_direct_single_helper_nonnull_returns":sum(x["original_direct_single_helper_nonnull_returns"] for x in results),
  "original_single_helper_entries":sum(x["original_single_helper_entries"] for x in results),"original_group_helper_entries":sum(x["original_group_helper_entries"] for x in results),
  "source_primary_ref_and_flagged_parent_and_both_child_lists_policy_qualified":True,
  "query_grouping_uses_full_U32_category_match_uses_U16_category_and_value":True,
  "arbitrary_platform_sources_and_all_nonroot_module_consumers_qualified":False,"entire_manager_source_lifetime_closed":False,
  "factory_destruction_and_storage_reuse_qualified":False,"remaining_module_root_grid_padding_fields_qualified":False,
  "captured_scalars_as_producer_inputs":False,"originals_exported":False,"new_camera_starts":0,"new_reboots":0,
  "production_C_changed":False,"kernel_build_performed":False,"native_rear_runtime_allowed":False,
  "retained_shims":["0x11D0","0x11F0","0xCAE740","0xF5E600","0xCAE730"]}
 (HERE/"SELECTION-SAFE.json").write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"status":summary["status"],"selector_returns":summary["original_selector_returns"],"nonroot_returns":summary["original_selector_nonroot_returns"]}),flush=True)
if __name__=="__main__":main()
