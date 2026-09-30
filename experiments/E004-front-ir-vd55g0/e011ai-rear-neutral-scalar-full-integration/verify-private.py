#!/usr/bin/env python3
"""SP11-only clean L4 scalar production through the full real composer."""
from pathlib import Path
import hashlib,importlib.util,json,struct,subprocess,tempfile
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
EX=HERE.parent
PRIVATE=ROOT.parent/"private"
AH=EX/"e011ah-rear-request-af-roi-full-integration"
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
parent=load("e011ai_ah",AH/"verify-private.py")
def harness():
    c=parent.harness()
    c=parent.replace_once(c,'#include "'+str(AH/"camss-e011ah-request-af-roi.inc")+'"',
        '#include "'+str(AH/"camss-e011ah-request-af-roi.inc")+'"\n#include "'+str(HERE/"camss-e011ai-startup-scalar-bind.inc")+'"')
    c=parent.replace_once(c,"int main(int argc,char **argv) {",
        '#include "'+str(HERE/"host-scalar-check.h")+'"\nint main(int argc,char **argv) {')
    c=parent.replace_once(c,"init_base(base);e011ah_host_check(base,argc==3);",
        "init_base(base);e011ai_host_bind(base);e011ah_host_check(base,argc==3);")
    c=parent.replace_once(c,'af_map_checks\\":%u}',
        'af_map_checks\\":%u,\\"scalar_negative_cases\\":%u,\\"scalar_producer_negative_cases\\":%u}')
    c=parent.replace_once(c,"payload_bytes,af_negative_cases,af_axis_checks,af_map_checks);",
        "payload_bytes,af_negative_cases,af_axis_checks,af_map_checks,scalar_negative_cases,scalar_producer_negative_cases);")
    return c
def compare_scalar(path):
    decoder=load("e011ai_decode",EX/"e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py")
    corpus_path=PRIVATE/"e006a/E006A-PRIVATE-RECORDS-v2.json"
    corpus=json.loads(corpus_path.read_text(encoding="utf-8-sig"))
    meta=json.loads((EX/"e011x-rear-neutral-3a-scalar-source-recon/LIVE-VALIDATION-SAFE.json").read_text())
    assert hashlib.sha256(corpus_path.read_bytes()).hexdigest()==meta["private_e006a_corpus_sha256"]
    scalar_regs={0x3b70,0x3b74,0x3d78,0x3d7c,0x3d80,0x3d84,0x456c,0x4570}
    phases=[]
    for p in range(4):
        own=decoder.decode((path/f"p{p}-main-0.bin").read_bytes())
        record=next(r for r in corpus["records"] if r["n"]==p and r["idx"]==1 and r["complete"])
        oracle=decoder.decode(bytes.fromhex(record["hex"]))
        a={r:v for r,v,off,k in own["writes"] if r in scalar_regs}
        b={r:v for r,v,off,k in oracle["writes"] if r in scalar_regs}
        assert a==b,{"phase":p,"scalar_matches":sum(a.get(r)==v for r,v in b.items())}
        assert len(a)==(2 if p==3 else 8)
        phases.append({"phase":p,"present_scalar_registers":len(a),"exact_scalar_registers":len(a)})
    return phases
def main():
    assert PRIVATE.is_dir(),"SP11 private authority required"
    native=load("e011ai_native",HERE/"native-private.py")
    scalar,arithmetic=native.main(return_source=True)
    # All actual native comparisons pass before clean C results are returned.
    assert arithmetic["bind_inputs_from_clean_C_production_not_native_outputs"]
    scalar_wire=b"".join(struct.pack("<4H4I2H",*v) for v in scalar)
    old_wire,bpc,adaptive=parent.parent.source_wire()
    wire=scalar_wire+old_wire
    parent.verify_l4_authority();oracle,audit=parent.oracle_bf()
    reports=[]
    with tempfile.TemporaryDirectory(prefix="e011ai-full-private-",dir=PRIVATE) as temp:
        td=Path(temp);src=td/"check.c";src.write_text(harness())
        for compiler in ("gcc","clang"):
            binary=td/(compiler+"-check")
            build=subprocess.run([compiler,"-std=c11","-Wall","-Wextra","-Werror",
                "-fsanitize=address,undefined","-ffp-contract=off","-fno-omit-frame-pointer","-g",str(src),
                "-lm","-o",str(binary)],capture_output=True)
            if build.returncode:
                (PRIVATE/(td.name+"-"+compiler+"-build-failure.raw")).write_bytes(build.stderr)
                raise RuntimeError("full host compile failed; private diagnostic retained")
            output=td/compiler
            report=parent.run_binary(binary,output,wire);report["compiler"]=compiler;reports.append(report)
            phases,adaptive_matches=parent.parent.compare(output,bpc,adaptive)
            scalar_matches=compare_scalar(output)
            bf_matches=parent.compare_bf(output,oracle,audit)
            assert [p["host_fixture_other_register_mismatch_count"] for p in phases]==[3,19,3,0]
        assert {k:v for k,v in reports[0].items() if k!="compiler"}=={k:v for k,v in reports[1].items() if k!="compiler"}
    paths=parent.parent.includes()+[
        EX/"e011ag-rear-full-provider-startup-integration/integration-check.c",
        EX/"e011ag-rear-full-provider-startup-integration/camss-e011ag-startup-compose.inc",
        AH/"camss-e011ah-request-af-roi.inc",AH/"host-af-check.h",
        EX/"e008t-rear-packet-aware-bf-semantic-composer/camss-vfe-e008t-rear-bf-semantic.inc",
        EX/"e008z-rear-af-default-rectangle/af-default-rectangle.h",
        EX/"e008x-rear-af-bf-roi-map/af-bf-roi-map.h",
        HERE/"scalar-producer.h",HERE/"scalar-check.c",
        HERE/"camss-e011ai-startup-scalar-bind.inc",HERE/"host-scalar-check.h",
        HERE/"authority-private.py",HERE/"native-private.py",HERE/"verify-private.py"]
    safe={"experiment":"E011AI","status":"PASS_CLEAN_SCALAR_FULL_PROVIDER_PRIVATE_PARITY",
        "parent_git_revision":"6dded7a85953782c6c05b943b34889e4159be671",
        "linux_slice":"L4 portable scalar arithmetic -> L2 offline startup binding/materialization",
        "profile":"rear Color VideoRecord NV12 3840x2160; offline only",
        "evidence":"prior P E011X original input trace; S exact original scalar arithmetic/private differential; D detached caller binding",
        "source_scalar_calculations":3,"source_scalar_schedule":[0,1,2,2],
        "clean_C_production_is_binding_authority":True,
        "live_input_recovery":arithmetic["private_recovery"],
        "native_scalar_differential":arithmetic["compiler_runs"],
        "compiler_runs":reports,"scalar_phase_comparison":scalar_matches,
        "scalar_register_instances_exact":26,"bf_phase_comparison":bf_matches,
        "source_adaptive_payload_matches":adaptive_matches,"phase_comparison":phases,
        "remaining_semantic_register_mismatches":25,"remaining_mismatches_by_phase":[3,19,3,0],
        "cold_request_input_independently_observed":True,
        "scalar_hold_phase3_derived_from_event_order":True,
        "non_scalar_fields_and_tags_preserved":True,"invalid_source_or_late_packet_preserves_all_bases":True,
        "other_base_fields":"statistics remain source-lowering seams; no captured register inverse input",
        "optional_wb_normalization_supported":False,"other_bayer_policies_supported":False,
        "floating_point_in_kernel":False,
        "cold_gamma_state":"unchanged host-only valid unused completion; enable0, selector2 absent",
        "complete_source_produced_e008o_composition_closed":False,"vfe1_wm16_retirement_closed":False,
        "native_rear_linux_runtime_allowed":False,"runtime_actions_performed":False,
        "source_locks":[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths],
        "private_values_or_generated_packet_bytes_exported":False}
    (HERE/"INTEGRATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in safe.items() if k not in ("source_locks","bf_phase_comparison","phase_comparison")},indent=2))
if __name__=="__main__":main()
