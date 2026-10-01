#!/usr/bin/env python3
"""Bounded original grid weight-array reader; no original bytes exported."""
from pathlib import Path
import importlib.util,hashlib,json,random,struct
from unicorn import UC_HOOK_CODE
from unicorn.arm64_const import *
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
AV=load("ay_files",HERE.parent/"e011av-rear-source-cold-awb-quad/native-private.py")
DEC=load("ay_container",ROOT/"experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py")
def source(blob):
 h=DEC.parse_header(blob);sy,_=DEC.parse_symbol_table(blob,h["sections"][0],h["sections"][1])
 roots=[r for r in sy.values() if r["type"]=="aecxhwstatsconfig"]
 assert len(roots)==1,"ambiguous named module"
 r=roots[0];assert (r["version_major"],r["version_minor"],r["mode_id"],r["data_bytes"])==(10,0,0,48)
 sec=h["sections"][2];assert sec["size"]%20==0
 nodes=[struct.unpack_from("<5I",blob,o) for o in range(sec["offset"],sec["end"],20)]
 by={x[0]:x for x in nodes};assert len(by)==len(nodes)
 assert by[r["mode_symbol_id"]]==(6,0,6,0,0xffffffff)
 assert by[0]==(0,0,0,0,0xffffffff)
 parent=DEC.data_bytes(blob,h["sections"][1],r)
 count,sid=struct.unpack_from("<II",parent,24)
 assert count==4 and sid in sy
 child=sy[sid]
 assert (child["type"],child["version_major"],child["version_minor"],child["mode_id"],child["mode_symbol_id"],child["data_bytes"])==("gridStatsConfig",0,0,0,0xffffffff,404)
 return DEC.data_bytes(blob,h["sections"][1],child),{
  "root_symbol_id":r["symbol_id"],"root_mode":"Default","root_version":[10,0],
  "root_serialized_bytes":48,"candidate_grid_array_count":count,
  "candidate_grid_child_reference_wire_offset":28,"grid_symbol_id":sid,
  "grid_serialized_bytes":404,"original_parent_child_materialization_qualified":False}
class Prefix:
 def __init__(self):
  self.n=load("ay_original",HERE.parent/"e011ai-rear-neutral-scalar-full-integration/native-private.py").Native()
  self.events=[]
  def hook(uc,pc,size,_):
   if pc==self.n.base+0xf5d480:
    u=self.n.u
    self.events.append((u.reg_read(UC_ARM64_REG_X1)-self.src,
                        u.reg_read(UC_ARM64_REG_X0)-self.out,
                        u.reg_read(UC_ARM64_REG_X2)))
  self.n.u.hook_add(UC_HOOK_CODE,hook)
 def run(self,wire,bias):
  n=self.n;u=n.u;reader=n.heap+0x1000+bias;self.out=n.heap+0x4000+bias;self.src=n.heap+0x10000+bias
  self.events.clear();u.mem_write(n.heap,bytes(0x30000));u.mem_write(n.stack,bytes(0x10000))
  u.mem_write(self.src,wire);u.mem_write(reader+0xc8,struct.pack("<I",len(wire)))
  u.mem_write(reader+0xd0,struct.pack("<Q",self.src))
  canary=bytes([0xa5])*32;u.mem_write(self.out-32,canary);u.mem_write(self.out+0x400,canary)
  for reg,val in [(UC_ARM64_REG_X0,reader),(UC_ARM64_REG_X1,self.out),
                  (UC_ARM64_REG_X2,0),(UC_ARM64_REG_SP,n.stack+0xf000),(UC_ARM64_REG_LR,n.end)]:
   u.reg_write(reg,val)
  # Stop immediately after the first memcpy. Array bookkeeping and aggregate tail
  # need ARM64EC context and are deliberately outside this bounded fixture.
  u.emu_start(n.base+0x123550,n.base+0x123818,count=100000)
  assert u.reg_read(UC_ARM64_REG_PC)==n.base+0x123818
  assert self.events==[(20,20,12)],"unexpected original scalar-array route"
  result=bytes(u.mem_read(self.out+20,12));assert result==wire[20:32]
  assert bytes(u.mem_read(self.src,len(wire)))==wire
  assert bytes(u.mem_read(self.out-32,32))==canary
  assert bytes(u.mem_read(self.out+0x400,32))==canary
  return result
def main():
 roots=[];audit=[]
 for name,sha in AV.FILES:
  blob=(AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  wire,info=source(blob);roots.append(wire);audit.append(dict(info,path=name,sha256=sha))
 cases=list(roots)
 for value in [0,1,0x3f800000,0x80000000,0x7fc00000,0xffffffff]:
  b=bytearray(roots[-1]);b[20:32]=struct.pack("<3I",value,value,value);cases.append(bytes(b))
 rng=random.Random(0xe011a9)
 for _ in range(128):
  b=bytearray(roots[-1]);b[20:32]=rng.randbytes(12);cases.append(bytes(b))
 native=Prefix();executions=0
 for bias in [0,0x200,0x400,0x800]:
  for b in cases:native.run(b,bias);executions+=1
 assert all(x[20:32]==roots[-1][20:32] for x in roots)
 capture=ROOT.parent/"private/E011AX-20261001-0055A-captured/capture/INIT01_CACHE.bin"
 observed=capture.read_bytes();assert len(observed)==96
 assert native.run(roots[-1],0)==observed[20:32];executions+=1
 report={"experiment":"E011AY","status":"PASS_BOUNDED_GRID_WEIGHT_ARRAY_READER_CANDIDATE",
  "original_DLL_sha256":"c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35",
  "qualified_named_Default_roots":3,"source_files":audit,
  "unique_scalar_cases":len(cases),"fixture_base_variants":4,
  "original_prefix_executions":executions,"original_reader_rva":"0x123550",
  "prefix_stop_rva":"0x123818","original_scalar_memcpy_call_rva":"0x123814",
  "serialized_weight_offset":20,"runtime_grid_weight_offset":20,
  "matching_weight_bytes_per_case":12,"native_memcpy_stubbed":False,
  "source_and_checked_neighbor_bytes_preserved":True,
  "three_installed_Default_candidate_weight_arrays_equal":True,
  "private_E011AX_weight_comparison_matching_bytes":12,
  "captured_weights_used_as_producer_inputs":False,
  "parent_grid_child_materialization_qualified":False,
  "array_bookkeeping_and_aggregate_tail_qualified":False,
  "live_named_tuning_source_selection_qualified":False,
  "numeric_initialization_policy_closed":False,
  "whole_deterministic_bootstrap_closed":False,"native_rear_runtime_allowed":False,
  "production_C_changed":False,"runtime_actions_performed":False,"private_original_bytes_exported":False}
 (HERE/"SCALAR-SAFE.json").write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
 print(json.dumps({k:v for k,v in report.items() if k!="source_files"}))
if __name__=="__main__":main()
