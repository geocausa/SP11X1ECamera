#!/usr/bin/env python3
"""Validate E011AU private original-process evidence on the same SP11."""
import argparse,hashlib,json,pathlib,re,struct
ap=argparse.ArgumentParser();ap.add_argument("private",type=pathlib.Path);ap.add_argument("--output",type=pathlib.Path);a=ap.parse_args()
p=a.private;c=p/"capture"
expected={"QUALIFIED_CREATE_CODE.bin":24,"QUALIFIED_LOOKUP_CODE.bin":80,"QUALIFIED_AFTER_CODE.bin":16,"CREATE_CONFIG_INPUT.bin":128,"CREATE_PRE_RETAINED_BG.bin":92,"WRITER_PRE_RETAINED_BG.bin":92,"WRITER_AFTER_RETAINED_BG.bin":92,"BGSTATSCONFIG_SOURCE.bin":96,"BGSTATSCONFIG_SOURCE_AFTER.bin":96}
assert {x.name:x.stat().st_size for x in c.iterdir() if x.is_file()}==expected
data={n:(c/n).read_bytes() for n in expected}
codehashes={"QUALIFIED_CREATE_CODE.bin":"bc6742dbc7ad42cf2aadceeffbb80492ae9fa2dfbe55911982d414f1d9c1ab60","QUALIFIED_LOOKUP_CODE.bin":"c076a90c21deeab1e383fd9c56b1ca3f4c5124b4a346d8ddec9753d421256aba","QUALIFIED_AFTER_CODE.bin":"a850729ebf00777af9c71f13ef15a5a080e985371fa2b80a4cc2586feab808da"}
for n,h in codehashes.items():assert hashlib.sha256(data[n]).hexdigest()==h
source=data["BGSTATSCONFIG_SOURCE.bin"];before=data["WRITER_PRE_RETAINED_BG.bin"];after=data["WRITER_AFTER_RETAINED_BG.bin"]
assert source==data["BGSTATSCONFIG_SOURCE_AFTER.bin"]
assert before==data["CREATE_PRE_RETAINED_BG.bin"]
u32=lambda b,n:struct.unpack_from("<I",b,n)[0]
assert u32(source,0x20)==u32(after,0x54)==1
assert u32(before,0x54)==0
raw=(p/"cdb-observer.raw").read_text(errors="replace")
events=re.findall(r"(?m)^E011AU_(CREATE_CALL|WRITER_SOURCE|WRITER_AFTER) tid=([^\r\n]+)",raw)
assert [e[0] for e in events]==["CREATE_CALL","WRITER_SOURCE","WRITER_AFTER"]
assert len({e[1].split()[0] for e in events})==1
assert all("tidMatch=1 actorMatch=1" in e[1] for e in events[1:])
assert all("lookup=0000000000000000" not in e[1] and "source=0000000000000000" not in e[1] for e in events)
assert "rva=682224" in events[0][1] and "rva=687e48" in events[1][1] and "rva=688434" in events[2][1]
errors=re.findall(r"(?im)^.*(?:Syntax error|Memory access error|Unable to read memory|Could not open.*cmd|Couldn't resolve error).*?$",raw)
assert not errors, "capture/debugger command diagnostics"
holder_bytes=(p/"holder.log").read_bytes()
holder=holder_bytes.decode("utf-16" if holder_bytes.startswith((b"\xff\xfe",b"\xfe\xff")) else "utf-8-sig",errors="strict")
assert len(re.findall(r"(?m)^.* START_BEGIN\r?$",holder))==1
assert holder.count("START_STATUS=Success")==1
assert holder.count("STOP_BEGIN")==1
m=re.search(r"STOP_PASS valid_4k_handles=(\d+)",holder);assert m and int(m[1])==713
assert holder.count("E011AU_HOLDER_END")==1
r={"experiment":"E011AU","attempt":"E011AU-20260930-2327B","status":"PASS_LIVE_NAMED_CONFIG_TO_RETAINED_QUAD_WRITE","original_code_ranges_exact":3,"valid_events":3,"same_thread_and_actor":True,"pre_record_stable_bytes":92,"source_stable_bytes":96,"source_quad":u32(source,0x20),"retained_quad_before":u32(before,0x54),"retained_quad_after":u32(after,0x54),"files":len(expected),"private_capture_bytes":sum(expected.values()),"valid_4k_handles":int(m[1]),"single_start":True,"clean_stop":True,"capture_command_diagnostics":0,"raw_sha256":hashlib.sha256((p/"cdb-observer.raw").read_bytes()).hexdigest(),"phase":"CreateAWBAlgorithm and config parser during StartAsync after completed InitializeAsync","source_profile_independently_materialized":False,"deterministic_full_bootstrap_closed":False,"WM16_retirement_closed":False,"native_rear_ISP_runtime_allowed":False}
out=json.dumps(r,indent=2)+"\n"
if a.output:a.output.write_text(out)
print(out,end="")
