#!/usr/bin/env python3
"""Source-qualified selector-node lookup and original reader/callback check; originals stay SP11."""
from pathlib import Path
import hashlib,importlib.util,json,struct,copy
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
BM=load("by_reader",EX/"e011bm-rear-aec-original-context/source-private.py")
BB=load("by_grids",EX/"e011bb-rear-aec-four-grid-deserialization/source-private.py")
PRIVATE=ROOT.parent/"private/E011BX-20261002-0030A-captured"
def source_fields(blob):
 h,sy,wire,info=BB.source(blob);_,_,_,records=BM.BL.describe(blob)
 r=sy[info["root_symbol_id"]];raw=blob[r["record_offset"]:r["record_offset"]+56]
 serialization_mode=struct.unpack_from("<I",raw,40)[0]
 selector=struct.unpack_from("<I",raw,44)[0]
 assert serialization_mode==r["mode_id"]==0
 assert selector==r["mode_symbol_id"]==6 and records[selector]==(6,0,6,0,0xffffffff)
 fields={16:raw[4:36].split(b"\0",1)[0]+b"\0",56:raw[:4],60:raw[36:44],68:raw[44:48],
  72:struct.pack("<2I",*records[selector][1:3]),
  80:BM.BL.text(records,selector).encode()+b"\0",208:blob[88:].split(b"\0",1)[0][:64]+b"\0"}
 assert fields[72]!=struct.pack("<2I",*records[serialization_mode][1:3])
 return fields,info,selector,serialization_mode
def matches(obj,fields):
 assert len(obj)==384
 return all(obj[at:at+len(value)]==value for at,value in fields.items())
def main():
 results=[];reader_returns=callback_returns=0
 for name,sha in BB.AZ.AV.FILES:
  blob=(BB.AZ.AV.ARCHIVE/name).read_bytes();assert hashlib.sha256(blob).hexdigest()==sha
  fields,info,selector,serialization=source_fields(blob)
  for bias in [0,1,0x1230,0x8010]:
   f=BM.Joined(blob,bias);f.prefix();u=f.n.u;n=f.n
   # Preserve original mode-prefix state, then execute only the independently typed root reader.
   prefix_heap=bytes(u.mem_read(n.heap,0x30000));rr=n.heap+0x8000+bias
   cursor=n.heap+0x9000+bias;context=n.heap+0xa000+bias
   root_record=f.sy[info["root_symbol_id"]];off=root_record["record_offset"];record=blob[off:off+56]
   u.mem_write(cursor,struct.pack("<Q",off));u.mem_write(context,bytes(128));u.mem_write(rr,struct.pack("<Q",context))
   before_reader=bytes(u.mem_read(n.heap,0x30000))
   f.invoke_low(0x6f47b8,[rr,f.filebase,len(blob),cursor,f.h["sections"][1]["offset"],f.manager,1])
   expected_reader=bytearray(before_reader)
   for at,value in [(8,record[:4]),(12,record[4:36]+b"\0"),(52,record[36:44]),(60,fields[72]),(68,record[44:48]),
     (200,record[52:56]),(208,struct.pack("<Q",f.filebase+f.h["sections"][1]["offset"]+struct.unpack_from("<I",record,48)[0]))]:
    ix=rr-n.heap+at;expected_reader[ix:ix+len(value)]=value
   ix=rr-n.heap+72;profile=bytearray(before_reader[ix:ix+128]);profile[0]=0
   expected_reader[ix:ix+128]=BM.BL.profile_buf(profile,f.records,selector)
   ix=cursor-n.heap;expected_reader[ix:ix+8]=struct.pack("<Q",off+56)
   assert bytes(u.mem_read(n.heap,0x30000))==expected_reader,"original root reader complete byte/guard contract"
   f.root_reader=rr
   assert f.readi(f.root_reader+68)==selector
   assert bytes(u.mem_read(f.root_reader+60,8))==fields[72]
   assert f.name_bytes(f.root_reader+72,127)+b"\0"==fields[80]
   reader_returns+=1
   out=n.heap+0x1000+bias;text=n.heap+0x1100+bias
   before=bytes(u.mem_read(n.heap,0x30000));mode_before=bytes(u.mem_read(f.nodes,len(f.records)*160))
   u.mem_write(out,b"\xa5"*8);u.mem_write(text,b"\xa5"*128)
   f.invoke_low(0x6f3b50,[f.manager,selector,out,text])
   assert bytes(u.mem_read(out,8))==fields[72]
   expected=bytearray(b"\xa5"*128);expected[0]=0
   expected=BM.BL.profile_buf(expected,f.records,selector)
   assert bytes(u.mem_read(text,128))==bytes(expected)
   assert bytes(u.mem_read(f.nodes,len(f.records)*160))==mode_before
   expected_heap=bytearray(before);ix=out-n.heap;expected_heap[ix:ix+8]=fields[72]
   ix=text-n.heap;expected_heap[ix:ix+128]=expected
   assert bytes(u.mem_read(n.heap,0x30000))==expected_heap
   u.mem_write(n.heap,prefix_heap);f.bounds()
   assert bytes(u.mem_read(f.map,f.map_size))==f.file_before
   callback_returns+=1
  live=[]
  for i in range(1,5):
   obj=(PRIVATE/f"capture/NAMED{i:02}_OBJECT.bin").read_bytes()
   if matches(obj,fields):live.append(i)
  results.append({"source_sha256":sha,"selector_node_wire_offset":44,"selector_node_id":selector,
   "serialization_mode_wire_offset":40,"serialization_mode_id":serialization,
   "original_reader_and_profile_callback_placements":4,"seven_field_live_module_matches":live})
  print(json.dumps({"experiment":"E011BY","phase":"metadata_source","source_cases_completed":len(results)}),flush=True)
 assert results[-1]["seven_field_live_module_matches"]==[1,2,3,4]
 blob=(BB.AZ.AV.ARCHIVE/BB.AZ.AV.FILES[-1][0]).read_bytes();fields,info,_,_=source_fields(blob)
 base=(PRIVATE/"capture/NAMED01_OBJECT.bin").read_bytes();rejected=[]
 for at in fields:
  obj=bytearray(base);obj[at]^=1
  assert not matches(bytes(obj),fields);rejected.append("module_field_"+str(at))
 wrong=dict(fields);wrong[72]=bytes(8);assert not matches(base,wrong);rejected.append("wrong_serialization_mode_lookup")
 _,sy,_,_=BB.source(blob);off=sy[info["root_symbol_id"]]["record_offset"]
 for at,val in [(40,1),(44,0),(44,0xffffffff)]:
  b=bytearray(blob);struct.pack_into("<I",b,off+at,val)
  try:source_fields(bytes(b))
  except (AssertionError,KeyError,ValueError):rejected.append("wrong_wire_"+str(at)+"_"+str(val))
  else:raise AssertionError("wrong source mode/selector accepted")
 out={"experiment":"E011BY","status":"PASS_CORRECTED_SOURCE_SELECTOR_AND_ALL_SEVEN_LIVE_METADATA_FIELDS",
  "base_commit":"b074d4730289253ef8580b61c00f01506444683b","original_DLL_sha256":BB.AZ.SHA,
  "source_cases":results,"original_mode_loader_prefixes_and_root_reader_returns":reader_returns,
  "all_source_symbol_readers_built":False,"root_reader_alignment1_explicit_owned_fixture":True,
  "original_profile_callback_returns":callback_returns,"owned_placements_per_source":4,
  "corrected_profile_node_reference_wire_offset":44,"serialization_mode_wire_offset":40,
  "mode_node_not_serialization_mode_controls_profile":True,"previous_E011BX_generator_used_wrong_schema_field":True,
  "historical_SOURCE_EXPECTED_private_bytes_unchanged":True,"original_live_log_payloads_unchanged":True,
  "matched_live_modules":4,"matched_source_metadata_fields_each":7,"metadata_field_checks":28,
  "source_mode_tables_and_blobs_unchanged":True,"source_authority_negative_cases":len(rejected),
  "negative_families":rejected,"captured_profile_values_used_as_producer_constants":False,
  "source_header_match_is_not_OS_file_open_identity":True,"actual_opened_filename_closed":False,
  "full_live_inner_query_receiver_qualification_closed":False,"new_camera_Starts":0,"new_reboots":0,
  "native_rear_runtime_allowed":False,"original_bytes_exported":False}
 (HERE/"METADATA-SAFE.json").write_text(json.dumps(out,indent=2,sort_keys=True)+"\n");print(json.dumps(out),flush=True)
if __name__=="__main__":main()
