#!/usr/bin/env python3
"""Validate E011AT private same-SP11 evidence without exporting payloads."""
import argparse, hashlib, json, pathlib, re

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

ap=argparse.ArgumentParser()
ap.add_argument("root",nargs="?",type=pathlib.Path,
    default=pathlib.Path("/home/geoca/Documents/SP11-PROJECT/06-camera/private/E011AT-20260930-2029A-captured"))
a=ap.parse_args(); root=a.root; cap=root/"capture"
assert sha(root/"cdb-observer.raw")=="d28d8f9db5db707ff19d2e235381229f47446b754080dd9cfb2f0f082e87a8a0"
assert sha(root/"holder.log")=="3caf95a2e1f797fe7d34e3291e99a85a91e1863e95a4bd2ed37ebeec62926e07"
raw=(root/"cdb-observer.raw").read_text(errors="replace")
holder=(root/"holder.log").read_text(encoding="utf-16")
for s in ("START_STATUS=Success","STOP_PASS valid_4k_handles=714","E011AT_HOLDER_END"):
    assert holder.count(s)==1
assert holder.count("START_BEGIN")==1
labels=[
"E011AT_ARMED_5_OUTER_ONESHOT_BP","E011AT_OUTER",
"E011AT_INNER_AND_QUAD_WATCH_ARMED","E011AT_CORRECTED_BREAKPOINTS",
"E011AT_DATA_WATCH_DROPPED","E011AT_SET_ENTRY","E011AT_SET_RETURN",
"E011AT_OUTER_RETURN","E011AT_GET2_BEFORE","E011AT_PUBLISH",
"E011AT_CONSUMER","E011AT_TUNING_HELPER","E011AT_DETACH"]
positions=[]
for label in labels:
    hits=[m.start() for m in re.finditer(r"(?m)^"+re.escape(label)+r"(?:\s|$)",raw)]
    assert len(hits)==1,(label,len(hits))
    positions.append(hits[0])
assert positions==sorted(positions)
assert re.search(r"^E011AT_SET_ENTRY .*tidMatch=1 actorMatch=1 callbackMatch=1 rva=68c090",raw,re.M)
assert re.search(r"^E011AT_SET_RETURN .*tidMatch=1 .*result=0 rva=681cbc",raw,re.M)
assert re.search(r"^E011AT_OUTER_RETURN .*tidMatch=1 result=0",raw,re.M)
assert re.search(r"^E011AT_GET2_BEFORE .*sameThread=1 .*quad=1",raw,re.M)
assert re.search(r"^E011AT_PUBLISH .*property=5000001d size=80",raw,re.M)
assert re.search(r"^E011AT_CONSUMER .*req=1",raw,re.M)
assert re.search(r"^E011AT_TUNING_HELPER .*tidMatch=1 actorArgMatch=1 rva=689228",raw,re.M)
assert raw.count("Unable to insert breakpoint")==1
assert raw.count("Too many data breakpoints")==2
assert "Access violation" not in raw
names=["SET_ENTRY_RETAINED_BG.bin","SET_RETURN_RETAINED_BG.bin",
       "OUTER_RETURN_RETAINED_BG.bin","GET2_BEFORE_RETAINED_BG.bin",
       "HELPER_RETAINED_BG.bin"]
blobs=[(cap/n).read_bytes() for n in names]
assert all(len(b)==92 for b in blobs)
assert len(set(blobs))==1
assert hashlib.sha256(blobs[0]).hexdigest()=="77254025d9f1c5d5df08168d4fdc457b8ea1fd5e9e7d2879924adcc61333f204"
assert all(int.from_bytes(b[0x54:0x58],"little")==1 for b in blobs)
p0=(cap/"OUTER_PARAM.bin").read_bytes(); p1=(cap/"SET_ENTRY_PARAM.bin").read_bytes()
assert len(p0)==len(p1)==40 and p0==p1
pub=(cap/"PUBLISH_REC.bin").read_bytes(); con=(cap/"CONSUMER_REC.bin").read_bytes()
assert len(pub)==len(con)==128
assert int.from_bytes(pub[0x4c:0x50],"little")==1
assert int.from_bytes(con[0x4c:0x50],"little")==1
assert (cap/"OUTER_CALLBACK_CODE.bin").stat().st_size==0
assert (cap/"OUTER_IO_BG.bin").stat().st_size==0
assert (cap/"OUTER_RETURN_IO_BG.bin").stat().st_size==0
assert (cap/"GET2_BEFORE_IO_BG.bin").stat().st_size==0
print(json.dumps({
 "status":"PASS_PRIVATE_E011AT",
 "valid_4k_handles":714,
 "events":len(labels),
 "retained_bytes":92,
 "retained_quad":1,
 "setparam_mutated_retained_BG":False,
 "first_writer_captured":False,
 "invalid_generated_outer_capture_excluded":True
},sort_keys=True))
