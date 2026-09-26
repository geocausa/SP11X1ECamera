#!/usr/bin/env python3
import argparse, hashlib, json, re, struct
from collections import defaultdict
from pathlib import Path

MARK = re.compile(r'^E006B_(START|STEADY)(?: P=([0-9a-f]+))? U=([0-9a-f]+) N=([0-9a-f]+)$', re.I)
DUMP = re.compile(r'^([0-9a-f]+)\x60([0-9a-f]+)\s{2}(.+?)(?:\s{2,}.*)?$', re.I)

WINDOWS = [
    ("startup0", 0xF1C, 0x00000, "E006B-START0-SOURCE.bin"),
    ("startup1", 0xEBC, 0x09000, "E006B-START1-SOURCE.bin"),
    ("startup2", 0xA00, 0x12000, "E006B-START2-SOURCE.bin"),
    ("startup3", 0x658, 0x1E000, "E006B-START3-SOURCE.bin"),
    ("steady_ac8", 0xAC8, 0x24000, "E006B-STEADY-AC8-SOURCE.bin"),
]

def fail(s): raise SystemExit("FAIL: "+s)
def h(b): return hashlib.sha256(b).hexdigest()
def hx(v): return f"0x{v:x}"

def dump_bytes(line):
    m=DUMP.match(line)
    if not m: return None
    area=m.group(3).replace("-"," ")
    out=[]
    for tok in area.split():
        if re.fullmatch(r'[0-9a-fA-F]{2}', tok):
            out.append(int(tok,16))
        else:
            break
    return bytes(out)

def parse_log(path):
    lines=path.read_text(errors="replace").replace("\r","\n").splitlines()
    caps=[]; i=0
    while i < len(lines):
        m=MARK.match(lines[i].strip())
        if not m:
            i+=1; continue
        kind=m.group(1).lower(); p=m.group(2)
        u=int(m.group(3),16); n=int(m.group(4),16)
        i+=1
        while i < len(lines) and lines[i].strip()!="E006B_PATCHSET": i+=1
        if i==len(lines): fail("missing PATCHSET")
        i+=1; blob=bytearray()
        while i < len(lines) and lines[i].strip()!="E006B_SRCMAP":
            b=dump_bytes(lines[i].strip())
            if b: blob.extend(b)
            i+=1
        need=n*24
        if len(blob)<need: fail(f"patch bytes short U={u:x}: {len(blob)} < {need}")
        blob=blob[:need]
        recs=[]
        for k in range(n):
            off=k*24
            recs.append({
                "dst_handle": struct.unpack_from("<Q",blob,off)[0],
                "dst_offset": struct.unpack_from("<I",blob,off+8)[0],
                "src_handle": struct.unpack_from("<Q",blob,off+12)[0],
                "src_offset": struct.unpack_from("<I",blob,off+20)[0],
            })
        if len({r["dst_handle"] for r in recs}) != 1: fail(f"multiple dst handles U={u:x}")
        if len({r["src_handle"] for r in recs}) != 1: fail(f"multiple src handles U={u:x}")
        caps.append({"kind":kind,"p":int(p,16) if p else None,"u":u,"n":n,"records":recs})
        i+=1
    return caps

def shape_for(structural, kind, u, ordinal):
    if kind=="start":
        matches=[x for x in structural["startup"] if x["capture_n"]==ordinal and x["main_bytes"]==u]
    else:
        matches=[x for x in structural["steady"]["main_variants"] if x["main_bytes"]==u]
    if len(matches)!=1: fail(f"shape resolution kind={kind} u={u:x} ordinal={ordinal}: {len(matches)}")
    return matches[0]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--log",type=Path,required=True)
    ap.add_argument("--private-dir",type=Path,required=True)
    ap.add_argument("--structural",type=Path,required=True)
    ap.add_argument("-o","--output",type=Path,required=True)
    a=ap.parse_args()
    st=json.loads(a.structural.read_text())
    caps=parse_log(a.log)
    expected=[("start",0xF1C),("start",0xEBC),("start",0xA00),("start",0x658),("steady",0xAC8)]
    if [(c["kind"],c["u"]) for c in caps] != expected:
        fail("capture sequence drift: "+repr([(c["kind"],hex(c["u"])) for c in caps]))
    if len(caps)!=len(WINDOWS): fail("capture/window count mismatch")

    safe_caps=[]; by_ident=defaultdict(list); start_ord=0
    for cap,(label,expected_u,window_base,fn) in zip(caps,WINDOWS):
        if cap["u"]!=expected_u: fail(label+" U mismatch")
        shape=shape_for(st,cap["kind"],cap["u"],start_ord if cap["kind"]=="start" else -1)
        if cap["kind"]=="start": start_ord+=1
        dmis={int(x["field"],16):x for x in shape["dmi_shape"]}
        if cap["n"] != len(dmis): fail(f"{label}: patch count {cap['n']} != dmi count {len(dmis)}")
        dst=sorted(r["dst_offset"] for r in cap["records"]); fields=sorted(dmis)
        bases={d-f for d,f in zip(dst,fields)}
        if len(bases)!=1: fail(f"{label}: no constant BL destination base: {sorted(bases)}")
        bl_base=bases.pop()
        local={r["dst_offset"]-bl_base:r for r in cap["records"]}
        if set(local)!=set(dmis): fail(f"{label}: local destination fields != decoded DMI fields")
        binp=a.private_dir/fn; bb=binp.read_bytes(); payloads=[]
        for field in fields:
            d=dmis[field]; r=local[field]; n=d["payload_bytes"]
            rel=r["src_offset"]-window_base
            if rel<0 or rel+n>len(bb):
                fail(f"{label}: source slice out of window field={field:x} src={r['src_offset']:x} len={n:x}")
            payload=bb[rel:rel+n]
            item={
                "field":hx(field),
                "dmi_register_offset":d["dmi_register_offset"],
                "selector":d["selector"],
                "payload_bytes":n,
                "source_offset":hx(r["src_offset"]),
                "payload_sha256":h(payload),
                "all_zero":not any(payload),
            }
            payloads.append(item)
            ident=(d["dmi_register_offset"],d["selector"],n)
            by_ident[ident].append((label,item["payload_sha256"]))
        safe_caps.append({
            "label":label,"phase":cap["kind"],"main_bytes":cap["u"],"patch_count":cap["n"],
            "bl_destination_slot_base":hx(bl_base),
            "captured_source_window_base":hx(window_base),
            "captured_source_window_bytes":len(bb),
            "private_source_file_sha256":h(bb),
            "payloads":payloads,
        })

    catalog=[]
    for ident,vals in sorted(by_ident.items()):
        hashes=sorted({v for _,v in vals})
        catalog.append({
            "dmi_register_offset":ident[0],"selector":ident[1],"payload_bytes":ident[2],
            "observations":[{"capture":lab,"sha256":sha} for lab,sha in vals],
            "distinct_hashes":len(hashes),
            "same_payload_across_captured_phases":len(hashes)==1,
        })
    out={
        "schema":"E006b-rear-dmi-source-payload-partial-v1",
        "run_identity":"consumed",
        "camera_acceptance":{
            "start_async":"Success","stop_async":"Success","capture_elapsed_ms":54302,
            "valid_3840x2160_frame_handles":0,"minimum_required":10,"passed":False,
            "classification":"PARTIAL_NO_REPLAY",
            "reason":"manual KD pauses stretched stream timing; no valid frame handles were delivered"
        },
        "private_evidence":{"kd_log_sha256":h(a.log.read_bytes()),"raw_payload_bytes_committed":False,"kernel_addresses_committed":False},
        "captured":{
            "startup_packets":4,"steady_families":["0xac8"],"missing_steady_families":["0xa98","0x8f0","0x658"],
            "captures":safe_caps,"payload_identity_catalog":catalog
        },
        "proven":{
            "patch_record_to_e006a_dmi_field_join_exact":True,
            "startup_source_payloads_captured_for_all_four_startup_main_lists":True,
            "steady_ac8_source_slot_captured":True,
            "steady_ac8_independently_shows_one_0x8000_source_slot":True
        },
        "not_proven":{
            "camera_acceptance":True,"steady_a98_payloads":True,"steady_8f0_payloads":True,
            "steady_658_payloads":True,"rear_materializer_complete":True,"native_rear_linux_isp":True
        },
        "next":"Use a fresh no-manual-pause oracle for missing steady families; prefer automatic/private source-slot capture and post-run reduction.",
        "native_rear_linux_isp_authorized":False
    }
    a.output.write_text(json.dumps(out,indent=2,sort_keys=True)+"\n")
    print("PASS partial reduction")
    print("captures",[(x["label"],hex(x["main_bytes"]),x["patch_count"]) for x in safe_caps])
    print("catalog entries",len(catalog))
    for x in catalog:
        if x["distinct_hashes"]>1:
            print("VARIES",x["dmi_register_offset"],x["selector"],x["payload_bytes"],x["distinct_hashes"])

if __name__=="__main__": main()
