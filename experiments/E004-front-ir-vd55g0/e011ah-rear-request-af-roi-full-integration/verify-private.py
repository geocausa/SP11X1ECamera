#!/usr/bin/env python3
"""SP11-only AF rectangle binding through the complete real startup composer."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
HERE=Path(__file__).resolve().parent
EX=HERE.parent
ROOT=HERE.parents[2]
PRIVATE=ROOT.parent/"private"
AG=EX/"e011ag-rear-full-provider-startup-integration"
HARNESS_SHA="de0a9a47a71797de31da627c4d90deb35eb6881b4c4b4a0cfc67e5c9c6dfe7f3"
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
parent=load("e011ah_parent",AG/"verify-private.py")
def replace_once(text,needle,value):
    assert text.count(needle)==1, "parent harness seam changed"
    return text.replace(needle,value)
def harness():
    path=AG/"integration-check.c"
    assert hashlib.sha256(path.read_bytes()).hexdigest()==HARNESS_SHA
    c=path.read_text()
    c=replace_once(c,"/* PROVIDERS */","\n".join('#include "'+str(p)+'"' for p in parent.includes()))
    c=replace_once(c,"/* BF_PROVIDER */",'#include "'+str(EX/"e008t-rear-packet-aware-bf-semantic-composer/camss-vfe-e008t-rear-bf-semantic.inc")+'"')
    c=replace_once(c,'#include "camss-e011ag-startup-compose.inc"','#include "'+str(AG/"camss-e011ag-startup-compose.inc")+'"\n#include "'+str(HERE/"camss-e011ah-request-af-roi.inc")+'"')
    tune=json.loads((EX/"e006r-rear-cst12-tuning-packer/TUNING-SAFE.json").read_text())
    reserve=tune["reserve"];fields={"enabled":1}
    for col,key in ((0,"c_x0"),(1,"c_x1")):
        for row,value in enumerate(reserve[key]):fields[f"c{row}{col}"]=value
    for i,value in enumerate(reserve["m_q10_roundf"]):fields[f"m{i//3}{i%3}"]=value
    for key in ("o","s"):
        for i,value in enumerate(reserve[key]):fields[f"{key}{i}"]=value
    c=replace_once(c,"/* CST_SOURCE */","r->cst=(struct e006r_cst12_state){"+",".join(f".{k}={v}" for k,v in fields.items())+"};")
    c=replace_once(c,"int main(int argc,char **argv) {",'#include "'+str(HERE/"host-af-check.h")+'"\nint main(int argc,char **argv) {')
    c=replace_once(c,"init_base(base);memcpy(saved,base,4*sizeof(*base));",
        "init_base(base);e011ah_host_check(base,argc==3);memcpy(saved,base,4*sizeof(*base));")
    c=replace_once(c,"if(argc==2)","if(argc>=2)")
    needle='cold_bf_gamma_emitted\\":false}'
    c=replace_once(c,needle,'cold_bf_gamma_emitted\\":false,\\"af_negative_cases\\":%u,\\"af_axis_checks\\":%u,\\"af_map_checks\\":%u}')
    c=replace_once(c,"dmi_counts[2],dmi_counts[3],payload_bytes);",
        "dmi_counts[2],dmi_counts[3],payload_bytes,af_negative_cases,af_axis_checks,af_map_checks);")
    return c
def verify_l4_authority():
    e=json.loads((EX/"e009e-rear-af-live-zoom-forward/RESULT.json").read_text())
    assert e["same_sp11_live_first_normal_zoom_float32_bits"]=="3f7f3f0f"
    assert not e["live_zoom_upstream_calculation_source_closed"]
    tuning=Path("/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/surfacecamrearsensor_extension8380.inf_arm64_9e667d808f1a7021/com.surface.tuned.rfc_ov13858.bin").read_bytes()
    assert hashlib.sha256(tuning).hexdigest()=="4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635"
    d=load("e011ah_tune",ROOT/"experiments/E003-front-imx681-cphy/e003h-iq-producer-0073-static/decode_imx681_chromatix.py")
    h=d.parse_header(tuning)
    records,_=d.parse_symbol_table(tuning,h["sections"][0],h["sections"][1])
    haf=d.data_bytes(tuning,h["sections"][1],records[0xb6])
    assert struct.unpack_from("<2f",haf,0x28)==(0.25,0.25)
def oracle_bf():
    audit=load("e011ah_roi",EX/"e008u-rear-bf-roi-geometry-audit/audit-private.py")
    meta=json.loads((EX/"e006b-windows-rear-dmi-source-payloads/PARTIAL-RESULT.json").read_text())
    result={}
    for cap in meta["captured"]["captures"]:
        if cap["label"] not in [f"startup{p}" for p in range(4)]:continue
        blob=(PRIVATE/"e006b"/audit.FILES[cap["label"]]).read_bytes()
        assert hashlib.sha256(blob).hexdigest()==cap["private_source_file_sha256"]
        for slot in cap["payloads"]:
            if slot["dmi_register_offset"]!="0xbc08":continue
            start=int(slot["source_offset"],16)-int(cap["captured_source_window_base"],16)
            n=slot["payload_bytes"];assert start>=0 and start+n<=len(blob)
            result[(int(cap["label"][-1]),slot["selector"])]=blob[start:start+n]
    assert len(result)==7
    return result,audit
def compare_bf(path,oracle,audit,control=False):
    decoder=load("e011ah_decode",EX/"e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py")
    phases=[]
    for p in range(4):
        packet=decoder.decode((path/f"p{p}-main-0.bin").read_bytes());slots=[]
        for i,slot in enumerate(packet["dmis"]):
            if slot["dmi_register_offset"]!=0xbc08:continue
            generated=(path/f"p{p}-dmi-{i}.bin").read_bytes()
            expected=oracle[(p,slot["dmi_sel"])]
            assert len(generated)==len(expected)==slot["payload_bytes"]
            exact=sum(a==b for a,b in zip(generated,expected))
            if control and p==1 and slot["dmi_sel"]==1:
                assert exact==250 and generated!=expected
            else: assert generated==expected
            item={"selector":slot["dmi_sel"],"payload_bytes":len(generated),"matching_bytes":exact}
            if slot["dmi_sel"]==1:
                a,b=audit.decode(generated),audit.decode(expected)
                item["matching_fields"]={k:sum(x[k]==y[k] for x,y in zip(a,b)) for k in audit.FIELDS}
                if not control or p!=1:assert all(v==25 for v in item["matching_fields"].values())
            slots.append(item)
        assert [x["selector"] for x in slots]==([1] if p==0 else [1,2])
        phases.append({"phase":p,"bf_payloads":slots})
    return phases
def run_binary(binary,output,wire,control=False):
    output.mkdir()
    run=subprocess.run([str(binary),str(output)]+(["neutral-control"] if control else []),input=wire,capture_output=True)
    if run.returncode:
        diagnostic=PRIVATE/(output.parent.name+"-"+output.name+"-failure.raw")
        diagnostic.write_bytes(run.stderr)
        raise RuntimeError("host check failed; private diagnostic retained at "+str(diagnostic))
    return json.loads(run.stdout)
def main():
    assert PRIVATE.is_dir(),"SP11 private authority required; never transfer it"
    verify_l4_authority();wire,source,adaptive=parent.source_wire()
    oracle,audit=oracle_bf();results=[]
    with tempfile.TemporaryDirectory(prefix="e011ah-private-",dir=PRIVATE) as temp:
        td=Path(temp);src=td/"check.c";src.write_text(harness())
        for compiler in ("gcc","clang"):
            binary=td/(compiler+"-check")
            build=subprocess.run([compiler,"-std=c11","-Wall","-Wextra","-Werror",
                "-fsanitize=address,undefined","-fno-omit-frame-pointer","-g",str(src),"-o",str(binary)],capture_output=True)
            if build.returncode:
                (PRIVATE/(td.name+"-"+compiler+"-build-failure.raw")).write_bytes(build.stderr)
                raise RuntimeError("host build failed; compiler diagnostic retained privately")
            output=td/compiler
            report=run_binary(binary,output,wire);report["compiler"]=compiler;results.append(report)
            phases,adaptive_matches=parent.compare(output,source,adaptive)
            bf_matches=compare_bf(output,oracle,audit)
            if compiler=="gcc":
                neutral=td/"neutral"
                run_binary(binary,neutral,wire,True)
                control_matches=compare_bf(neutral,oracle,audit,True)
        assert {k:v for k,v in results[0].items() if k!="compiler"}=={k:v for k,v in results[1].items() if k!="compiler"}
    locks=parent.includes()+[AG/"integration-check.c",AG/"camss-e011ag-startup-compose.inc",
        HERE/"camss-e011ah-request-af-roi.inc",HERE/"host-af-check.h",
        EX/"e008t-rear-packet-aware-bf-semantic-composer/camss-vfe-e008t-rear-bf-semantic.inc",
        EX/"e008z-rear-af-default-rectangle/af-default-rectangle.h",
        EX/"e008x-rear-af-bf-roi-map/af-bf-roi-map.h"]
    safe={"experiment":"E011AH","status":"PASS_REQUEST_AF_ROI_FULL_PROVIDER_INTEGRATION",
        "parent_git_revision":"2f35a08454e7322ee29db88143d216a4b444351d",
        "linux_slice":"L4 caller AF rectangle -> L2 offline BF ROI lowering/materialization",
        "profile":"rear Color VideoRecord NV12 3840x2160; offline only",
        "evidence":"S source-derived E008z/E009c/E008x/E008t; prior P-observed E009e scalar and private E006b comparison; D detached caller handoff",
        "compiler_runs":results,"bf_phase_comparison":bf_matches,
        "neutral_control_phase1_roi_matching_bytes":control_matches[1]["bf_payloads"][0]["matching_bytes"],
        "bf_roi_slots_exact":4,"bf_roi_matching_bytes":1200,"bf_gamma_slots_exact":3,"bf_gamma_matching_bytes":384,
        "source_adaptive_payload_matches":adaptive_matches,"phase_comparison":phases,
        "full_recursive_e008o_validation_exercised":True,"actual_e008l_layout_and_e007y_materializer_exercised":True,
        "binder_rejects_before_mutation":True,"normal_roi_ids_flags_and_all_other_fields_preserved":True,
        "cold_packet_preserved_byte_for_byte":True,"integer_lowering_float_reference_domain_max":16384,
        "first_normal_zoom_authority":"existing E009e physically observed float32 0x3f7f3f0f; subsequent zoom1.0",
        "first_normal_zoom_upstream_calculation_source_closed":False,
        "live_af_to_rtcdm_packet_identity_directly_tagged":False,
        "cold_gamma_state":"unchanged host-only valid unused completion; enable zero, selector2 absent",
        "remaining_bases":"neutral scalar and some statistics caller fixtures; source/live provenance is not reopened",
        "source_locks":[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in locks],
        "complete_source_produced_e008o_composition_closed":False,"vfe1_wm16_retirement_closed":False,
        "native_rear_linux_runtime_allowed":False,"runtime_actions_performed":False,
        "private_values_or_generated_packet_bytes_exported":False}
    (HERE/"INTEGRATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in safe.items() if k not in ("source_locks","phase_comparison")},indent=2))
if __name__=="__main__":main()
