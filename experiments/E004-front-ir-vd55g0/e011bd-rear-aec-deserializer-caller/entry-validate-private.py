#!/usr/bin/env python3
"""Recheck original entry records locally; no original bytes are emitted."""
from pathlib import Path
import argparse, hashlib, importlib.util, json, re, struct
import pefile, capstone
HERE=Path(__file__).resolve().parent; ROOT=HERE.parents[2]
p=argparse.ArgumentParser();p.add_argument("identity");a=p.parse_args()
assert re.fullmatch(r"E011BD-\d{8}-\d{4}[A-Z]",a.identity)
private=ROOT.parent/"private"/(a.identity+"-captured");cap=private/"capture"
raw=(private/"cdb-observer.raw").read_text(errors="replace")
assert not re.search(r"Syntax error|Memory access error|Couldn.t resolve|E011BD_(CHILD_)?AUTHORITY_FAIL",raw)
def events(name):
 return [dict(re.findall(r"([A-Za-z]+)=([0-9a-fA-F\x60]+)",m.group(1))) for m in re.finditer(r"^E011BD_"+name+r" ([^\r\n]+)",raw,re.M)]
def ptr(x):return int(x.replace(chr(96),""),16)
def rec(name,size):
 b=(cap/(name+".bin")).read_bytes();assert len(b)==size;return b
def q(b,o=0):return struct.unpack_from("<Q",b,o)[0]
def w(b,o=0):return struct.unpack_from("<I",b,o)[0]
mb=ptr(events("MODULE_BASE")[0]["base"]);entries=events("ENTRY")
assert 1<=len(entries)<=4
ps=json.loads((private/"ENTRY-SAFE.json").read_text(encoding="utf-8-sig"))
for item in ps["record_hashes"]:
 b=(cap/item["name"]).read_bytes()
 assert len(b)==item["bytes"] and hashlib.sha256(b).hexdigest()==item["sha256"]
spec=importlib.util.spec_from_file_location("bd_source",HERE.parent/"e011ay-rear-aec-cache-construction/scalar-private.py")
ay=importlib.util.module_from_spec(spec);spec.loader.exec_module(ay)
files=json.loads((HERE.parent/"e011bc-rear-aec-parser-alignment-authority/SOURCE-SAFE.json").read_text())["SHA_pinned_sources"]
archive=ROOT.parents[1]/"00-RE-archive/sp11-driverdump";sources=[]
for item in files:
 blob=(archive/item["source"]).read_bytes();assert hashlib.sha256(blob).hexdigest()==item["sha256"]
 wire,info=ay.source(blob)
 header=ay.DEC.parse_header(blob);symbols,_=ay.DEC.parse_symbol_table(blob,header["sections"][0],header["sections"][1])
 root=ay.DEC.data_bytes(blob,header["sections"][1],symbols[info["root_symbol_id"]])
 sources.append((item["source"],root,wire))
dll=archive/"surfacecamavs8380.inf_arm64_2b9eaefcbe9d3342/QcDeviceMFT8380.dll"
blob=dll.read_bytes();assert hashlib.sha256(blob).hexdigest()=="c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35"
pe=pefile.PE(data=blob);base=pe.OPTIONAL_HEADER.ImageBase
md=capstone.Cs(capstone.CS_ARCH_ARM64,capstone.CS_MODE_ARM);md.detail=True;md.skipdata=True
results=[];captured_callers=set()
for index,e in enumerate(entries,1):
 assert int(e["n"])==index
 obj=rec(f"ENTRY{index:02}_OBJECT",384);slot=rec(f"ENTRY{index:02}_SLOT",8)
 reader=rec(f"ENTRY{index:02}_READER",224);ctx=rec(f"ENTRY{index:02}_CONTEXT",64)
 root=rec(f"ENTRY{index:02}_ROOT",48);child=rec(f"ENTRY{index:02}_CHILD",224);grid=rec(f"ENTRY{index:02}_GRID",404)
 assert q(obj)-mb==ptr(e["table"])-mb==0x1335598
 assert q(slot)-mb==ptr(e["slot"])-mb==0x123cc0
 assert q(reader)==q(child) and w(reader,200)==48 and w(child,200)==404
 assert w(root,24)==4 and w(root,28)<=w(ctx,24)
 matched=[path for path,r,g in sources if root==r and grid==g]
 alignment=int(e["alignment"]);assert alignment>0
 caller=ptr(e["lr"])-mb;source_window_match=False;call_is_indirect=False
 if 0x1080<=caller<0x1a00000:
  captured=rec(f"ENTRY{index:02}_CALLER",192);original=pe.get_data(caller-128,192)
  source_window_match=captured==original
  if source_window_match:
   instructions=list(md.disasm(original,base+caller-128))
   call=[i for i in instructions if i.address==base+caller-4]
   call_is_indirect=bool(call and call[0].mnemonic=="blr")
   captured_callers.add(caller)
 results.append(dict(index=index,alignment_matches_fixture_one=alignment==1,
   qualified_instance_slot=True,reader_context_and_child_bounds_match=True,
   source_root_and_grid_candidate_matches=matched,caller_return_rva=hex(caller) if caller>=0 else "outside_module",
   caller_code_window_matches_pinned_original=source_window_match,caller_is_original_indirect_call=call_is_indirect))
assert len(entries)==ps["entry_cases"]
assert sum(r["alignment_matches_fixture_one"] for r in results)==ps["alignment_one_cases"]
safe=dict(experiment="E011BD",identity=a.identity,status="PASS_INDEPENDENT_LIVE_ENTRY_RECHECK",
 entry_cases=len(results),entry_results=results,
 actual_entry_alignment_observed=True,actual_caller_alignment_policy_closed=False,
 exact_loaded_tuning_filename_closed=False,full_profile_materialization_closed=False,
 raw_original_bytes_exported=False,captured_scalars_used_as_producer_inputs=False,native_rear_runtime_allowed=False)
(HERE/"ENTRY-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
print(json.dumps(safe,indent=2,sort_keys=True))
