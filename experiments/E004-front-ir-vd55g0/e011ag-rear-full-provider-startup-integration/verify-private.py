#!/usr/bin/env python3
"""SP11-only full-provider offline integration; only aggregate evidence leaves."""
from pathlib import Path
import hashlib,importlib.util,json,re,struct,subprocess,tempfile
HERE=Path(__file__).resolve().parent
EX=HERE.parent
PRIVATE=HERE.parents[2].parent/"private"
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def includes():
    stage=(EX/"e007y-rear-full-startup-offline-materializer/stage-build-once.sh").read_text()
    names=re.findall(r'"([^"]+)"',re.search(r"names=\[(.*?)\]",stage,re.S).group(1))
    paths=[]
    for name in names:
        found=list(EX.glob("*/"+name));assert len(found)==1;paths.extend(found)
    for tag in ("e008l","e008o","e011ae","e011z"):
        found=list(EX.glob(tag+"*/*.inc"));assert len(found)==1;paths.extend(found)
    return paths
def source_wire():
    af=load("e011ag_af",EX/"e011af-rear-live-aec-trigger-lineage/verify-live-private.py")
    # Return only after all original lineage, source and retained-output checks.
    source=af.main(return_source=True)
    result=bytearray()
    for s in source["common"]:
        fields=s["signed10"]+s["unsigned9"]+s["nibble4"]
        for key in ("byte_group0","byte_group1","nibble_group"):
            fields+=s[key][0]+s[key][1]
        result.extend(struct.pack("<2h2H26B",*fields))
    adaptive=load("e011ag_adaptive",EX/"e011z-rear-startup-clean-lsc-gtm-replay/replay.py")
    _,lsc=adaptive.clean_lsc();_,gtm=adaptive.clean_gtm()
    result.extend(lsc["phase0"][0]+lsc["phase1"][0]+lsc["phase0"][1]+lsc["phase1"][1]+gtm)
    return bytes(result),source,{"lsc":lsc,"gtm":gtm}
def compare(path,source,adaptive):
    decoder=load("e011ag_decode",EX/"e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py")
    corpus=json.loads((PRIVATE/"e006a/E006A-PRIVATE-RECORDS-v2.json").read_text(encoding="utf-8-sig"))
    owners=json.loads((EX/"e006l-rear-startup-register-ownership/STARTUP-REGISTER-OWNER-MAP.json").read_text())
    owner={int(x["register"],16):x["owner"] for key in ("startup_only","steady_dynamic","startup_differs_from_steady") for x in owners[key]}
    phases=[]
    lsc_slots=gtm_slots=gic_slots=0
    for p in range(4):
        own=decoder.decode((path/f"p{p}-main-0.bin").read_bytes())
        record=next(r for r in corpus["records"] if r["n"]==p and r["idx"]==1 and r["complete"])
        oracle=decoder.decode(bytes.fromhex(record["hex"]))
        assert [(r,off,k) for r,v,off,k in own["writes"]]==[(r,off,k) for r,v,off,k in oracle["writes"]]
        ov={r:v for r,v,off,k in own["writes"]};wv={r:v for r,v,off,k in oracle["writes"]}
        lsc=adaptive["lsc"]["phase1" if p else "phase0"]
        for i,slot in enumerate(own["dmis"]):
            blob=(path/f"p{p}-dmi-{i}.bin").read_bytes()
            if slot["dmi_register_offset"]==0x4308 and slot["dmi_sel"] in (1,2):
                assert blob==lsc[slot["dmi_sel"]-1];lsc_slots+=1
            if slot["dmi_register_offset"]==0x5a08:
                assert blob==adaptive["gtm"];gtm_slots+=1
            if slot["dmi_register_offset"]==0x4708:
                assert blob==lsc[0][558:]+lsc[1][:186];gic_slots+=1
        # Independent packer from the validated upstream semantic producer.
        af=load("e011ag_pack",EX/"e011ae-rear-request-generic-trigger-producer/producer.py")
        expected=af.S.AC.P.pack(source["common"][min(p,2)])
        present={r for r in expected if r in ov}
        assert all(ov[r]==expected[r] for r in present)
        assert all(ov[r]==wv[r] for r in present)
        families={}
        for r,v in ov.items():
            if r not in expected and (v & 0x1f if r==0x8c else v)!=(wv[r] & 0x1f if r==0x8c else wv[r]):
                family=owner.get(r,"STEADY_SINGLETON")
                families[family]=families.get(family,0)+1
        phases.append({"phase":p,"remaining_fixture_mismatch_families":families,"register_instances":len(own["writes"]),
            "bpc_present_words_exact":len(present),
            "host_fixture_other_register_match_count":sum((v & 0x1f if r==0x8c else v)==(wv[r] & 0x1f if r==0x8c else wv[r]) for r,v in ov.items() if r not in expected),
            "host_fixture_other_register_mismatch_count":sum((v & 0x1f if r==0x8c else v)!=(wv[r] & 0x1f if r==0x8c else wv[r]) for r,v in ov.items() if r not in expected),
            "other_base_inputs_are_fixture_not_full_source_production":True,
            "dmi_shape_exact":own["dmis"] and
                [(d["dmi_register_offset"],d["dmi_sel"],d["payload_bytes"]) for d in own["dmis"]]==
                [(d["dmi_register_offset"],d["dmi_sel"],d["payload_bytes"]) for d in oracle["dmis"]]})
    assert [x["bpc_present_words_exact"] for x in phases]==[7,7,7,0]
    assert (lsc_slots,gtm_slots,gic_slots)==(4,4,3)
    return phases,{"lsc_selector_slots_exact":lsc_slots,"gtm_slots_exact":gtm_slots,"gic_alias_slots_exact":gic_slots}
def main():
    assert PRIVATE.is_dir(),"run on SP11; private authority must never be transferred"
    wire,source,adaptive=source_wire();paths=includes()
    c=(HERE/"integration-check.c").read_text()
    c=c.replace("/* PROVIDERS */","\n".join('#include "'+str(p)+'"' for p in paths))
    tune=json.loads((EX/"e006r-rear-cst12-tuning-packer/TUNING-SAFE.json").read_text())
    reserve=tune["reserve"];fields={"enabled":1}
    for col,key in ((0,"c_x0"),(1,"c_x1")):
        for row,value in enumerate(reserve[key]):fields[f"c{row}{col}"]=value
    for i,value in enumerate(reserve["m_q10_roundf"]):fields[f"m{i//3}{i%3}"]=value
    for key in ("o","s"):
        for i,value in enumerate(reserve[key]):fields[f"{key}{i}"]=value
    c=c.replace("/* CST_SOURCE */","r->cst=(struct e006r_cst12_state){"+",".join(f".{k}={v}" for k,v in fields.items())+"};")
    c=c.replace("/* BF_PROVIDER */",'#include "'+str(EX/"e008t-rear-packet-aware-bf-semantic-composer/camss-vfe-e008t-rear-bf-semantic.inc")+'"')
    results=[]
    with tempfile.TemporaryDirectory(prefix="e011ag-private-",dir=PRIVATE) as temp:
        td=Path(temp);src=td/"check.c";src.write_text(c)
        for compiler in ("gcc","clang"):
            binary=td/(compiler+"-check")
            build=subprocess.run([compiler,"-std=c11","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-fno-omit-frame-pointer",
                "-g","-I",str(HERE),str(src),"-o",str(binary)],capture_output=True)
            if build.returncode:
                raise RuntimeError(build.stderr.decode(errors="replace"))
            output=td/compiler;output.mkdir()
            run=subprocess.run([str(binary),str(output)],input=wire,capture_output=True)
            if run.returncode:
                diagnostic=PRIVATE/(td.name+"-"+compiler+"-failure.raw")
                diagnostic.write_bytes(run.stderr)
                raise RuntimeError("Host C check failed; private diagnostic: "+str(diagnostic))
            report=json.loads(run.stdout);report["compiler"]=compiler;results.append(report)
            phases,adaptive_matches=compare(output,source,adaptive)
        comparable=[{k:v for k,v in r.items() if k!="compiler"} for r in results]
        assert comparable[0]==comparable[1]
    safe={"experiment":"E011AG","status":"PASS_FULL_REAL_PROVIDER_OFFLINE_INTEGRATION",
        "evidence":"D design/host integration; S source-produced BPC/LSC/GTM with previously P-bound inputs",
        "linux_slice":"L2 CSI/ISP offline startup composition; caller semantic seam from L4",
        "profile":"rear Color VideoRecord NV12 3840x2160; offline only",
        "real_provider_include_count":len(paths),"providers":[{"path":str(p.relative_to(HERE.parents[2])),
            "sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
        "compiler_runs":results,"phase_comparison":phases,"source_adaptive_payload_matches":adaptive_matches,
        "full_recursive_e008o_validation_exercised":True,"actual_e008l_layout_and_e007y_materializer_exercised":True,
        "allocator_backend":"host malloc with synthetic 32-bit IOVAs; no kernel DMA allocator or hardware",
        "bpc_source_state_count":3,"bpc_schedule":[0,1,2,2],"bpc_captured_startup_word_matches":21,
        "lsc_source_state_count":2,"lsc_schedule":[0,1,1,1],"gtm_source_state_count":1,
        "other_base_fields":"source-derived CST12/disabled BC101/BF filters and mode geometry; neutral scalar/statistics caller fixtures remain; no captured register inverse input",
        "period_comparison_uses_source_semantic_mask_0x1f":True,
        "cold_gamma_state":"host-only valid completion, hardware enable zero, selector2 absent; Windows seed not inferred",
        "complete_source_produced_e008o_composition_closed":False,"vfe1_wm16_retirement_closed":False,
        "native_rear_linux_runtime_allowed":False,"runtime_actions_performed":False,
        "private_values_or_generated_packet_bytes_exported":False}
    (HERE/"INTEGRATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in safe.items() if k!="providers"},indent=2))
if __name__=="__main__":main()
