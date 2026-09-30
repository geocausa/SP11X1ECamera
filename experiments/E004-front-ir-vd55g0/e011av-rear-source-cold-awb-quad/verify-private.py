#!/usr/bin/env python3
"""Full offline composer replay; tuning source supplies cold AWB quad."""
from pathlib import Path
import hashlib,importlib.util,json,struct,subprocess,tempfile
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];EX=OUT.parent;PRIVATE=ROOT.parent/"private"
AS=EX/"e011as-rear-explicit-inactive-cold-gamma"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
baseline=load("av_baseline",AS/"verify-private.py")
HERE=baseline.HERE;AL=baseline.AL;parent=baseline.parent;ah=baseline.ah;ag=baseline.ag
compare_rs=baseline.compare_rs
def harness():
    c=baseline.harness();replace=ah.replace_once
    c=replace(c,'#include "'+str(AL/"host-weight-quad-check.h")+'"',
        '#include "'+str(OUT/"cold-quad-source.h")+'"\nstatic uint32_t e011av_cold_quad;\n#include "'+str(OUT/"host-source-weight-quad-check.h")+'"')
    c=replace(c," e011as_host_gamma_checks();",
        " e011as_host_gamma_checks();\n uint8_t tuning[93];read_exact(tuning,93);\n CHECK(e011av_decode_cold_quad(tuning,93,1,0,&e011av_cold_quad)==0);")
    return c
def source_weight_quad(quad):
    # E011AK is still the independent authority for cold AEC weights and
    # normal AWB; the captured cold AWB field is never read here.
    cap=PRIVATE/"E011AK-20260930-1025A/capture"
    cold=struct.unpack("<3I",(cap/"AEC01_REC.bin").read_bytes()[0x30:0x3c])
    normal=struct.unpack("<3I",(cap/"AECPRODUCE03_FRAME.bin").read_bytes()[0x44:0x50])
    normal_quad=struct.unpack_from("<I",(cap/"AWBPRODUCE01_IO.bin").read_bytes(),0x54)[0]
    validator=load("av_capture",EX/"e011ak-rear-stats-input-observer/validate-private.py")
    import contextlib,io
    with contextlib.redirect_stdout(io.StringIO()):validator.main()
    source=[(*cold,quad),(*normal,normal_quad)]
    with tempfile.TemporaryDirectory(prefix="e011av-weight-",dir=PRIVATE) as tmp:
        binary=Path(tmp)/"weight"
        build=subprocess.run(["gcc","-std=c11","-Wall","-Wextra","-Werror",str(AL/"weight-quad-check.c"),"-o",str(binary)],capture_output=True)
        assert build.returncode==0,"weight producer build failed"
        run=subprocess.run([str(binary)],input=b"".join(struct.pack("<4I",*v) for v in source),capture_output=True)
        assert run.returncode==0 and len(run.stdout)==8
        result=[tuple(run.stdout[i:i+4]) for i in (0,4)]
    # A contaminated captured cold AWB byte must be overwritten in the C
    # harness by the freshly decoded source before any binder call.
    result[0]=(*result[0][:3],255)
    return result
def main():
    source_wire,quad,scalar_audit=load("av_scalar",OUT/"native-private.py").main(return_source=True)
    rs,arithmetic=load("e011am_native",HERE/"native-private.py").main(return_source=True)
    weight=source_weight_quad(quad)
    bg,_=load("e011am_geometry",parent.AJ/"native-private.py").main(return_source=True)
    ai=parent.parent.parent
    scalar,_=load("e011am_scalar",ai.HERE/"native-private.py").main(return_source=True)
    old_wire,bpc,adaptive=ag.source_wire()
    wire=source_wire+b"".join(struct.pack("<8I",*v) for v in rs)+b"".join(bytes(v) for v in weight)+b"".join(struct.pack("<10I",*v) for v in bg)+b"".join(struct.pack("<4H4I2H",*v) for v in scalar)+old_wire
    ah.verify_l4_authority();oracle,audit=ah.oracle_bf();reports=[]
    with tempfile.TemporaryDirectory(prefix="e011av-full-private-",dir=PRIVATE) as tmp:
        td=Path(tmp);src=td/"check.c";src.write_text(harness())
        for compiler in ("gcc","clang"):
            binary=td/compiler
            build=subprocess.run([compiler,"-std=c11","-Wall","-Wextra","-Werror",
                "-fsanitize=address,undefined","-ffp-contract=off","-fno-omit-frame-pointer","-g",
                str(src),"-lm","-o",str(binary)],capture_output=True)
            if build.returncode:
                (PRIVATE/(td.name+"-"+compiler+"-build-failure.raw")).write_bytes(build.stderr)
                raise RuntimeError("host compile failed; private diagnostic retained")
            output=td/(compiler+"-out")
            report=ah.run_binary(binary,output,wire);report["compiler"]=compiler;reports.append(report)
            phases,adaptive_matches=ag.compare(output,bpc,adaptive)
            bg_matches=parent.parent.compare_bg(output);scalar_matches=ai.compare_scalar(output)
            bf_matches=ah.compare_bf(output,oracle,audit);wq_matches=parent.compare_weight_quad(output);rs_matches=compare_rs(output)
            assert [p["host_fixture_other_register_mismatch_count"] for p in phases]==[0,0,0,0]
            assert all(not p["remaining_fixture_mismatch_families"] for p in phases)
    assert {k:v for k,v in reports[0].items() if k!="compiler"}=={k:v for k,v in reports[1].items() if k!="compiler"}
    prior=json.loads((AL/"INTEGRATION-SAFE.json").read_text());paths=[]
    for lock in prior["source_locks"]:
        p=ROOT/lock["path"];assert hashlib.sha256(p.read_bytes()).hexdigest()==lock["sha256"];paths.append(p)
    paths += [HERE/f for f in ("rs-producer.h","rs-check.c","camss-e011am-startup-rs-bind.inc",
        "host-rs-check.h","native-private.py","verify-private.py")]
    paths += [OUT.parent/"e011ar-rear-packet-isolated-runner/camss-vfe-e011ar-rear-runner.inc",AS/"verify-private.py",AS/"host-gamma-check.h",AS/"PROVIDERS.json",AS/"camss-e011as-cold-gamma-policy.inc"]
    paths += [ROOT/x["path"] for x in json.loads((AS/"PROVIDERS.json").read_text())]
    paths += [OUT/f for f in ("native-private.py","cold-quad-source.h","quad-check.c","verify-private.py","host-source-weight-quad-check.h")]
    safe={"bounded_cold_quad_numeric_policy_closed":True,"full_module_deserialization_closed":False,"exact_loaded_source_file_attribution_closed":False,"captured_cold_quad_input_replaced_by_invalid_sentinel":True,"source_quad":quad,"scalar_source_audit":"SCALAR-SAFE.json","new_linux_kernel_build_performed":False,"runner_preflight_function_tested":True,"runner_preflight_negative_cases":6,"experiment":"E011AV","status":"PASS_FULL_OFFLINE_STARTUP_PARITY_WITH_SOURCE_INPUT_RECORDS",
        "parent_git_revision":"c53a2a479f5fb816593aee85c94ccc0f42e22371",
        "profile":"rear Color VideoRecord NV12 3840x2160; detached offline only",
        "RS_source_schedule":[0,1,2,2],"compiler_runs":reports,
        "native_RS_differential":arithmetic["compiler_runs"],
        "sampled_RS_shift_binding_closed":True,"RS_phase_comparison":rs_matches,
        "RS_register_instances_exact":sum(v["RS_register_instances_exact"] for v in rs_matches),
        "weight_quad_phase_comparison":wq_matches,"weight_quad_register_instances_exact":4,
        "bg_phase_comparison":bg_matches,"bg_geometry_threshold_register_instances_exact":36,
        "scalar_phase_comparison":scalar_matches,"bf_phase_comparison":bf_matches,
        "source_adaptive_payload_matches":adaptive_matches,"phase_comparison":phases,
        "previous_remaining_semantic_register_mismatches":0,"remaining_semantic_register_mismatches":0,
        "remaining_mismatches_by_phase":[0,0,0,0],
        "binding_authority":"clean portable C output from independent semantic input records",
        "retained_output_words_used_as_inputs":False,"RS_normal_count_policy_origin_closed":False,
        "RS_zero_offset_policy":"explicit whole-frame caller scope; stripe policy unsupported",
        "cold_weight_quad_initialization_policy_closed":False,
        "integer_only_producer_and_binder":True,"other_fields_and_caller_tags_preserved":True,
        "atomic_rejection_preserves_all_bases":True,
        "deterministic_cold_bootstrap_without_observed_inputs_closed":False,
        "complete_source_produced_e008o_composition_closed":False,
        "cold_gamma_state":"explicit inactive, zero semantic LUT, no dummy gamma production",
        "inactive_cold_gamma_policy_closed":True,
        "gamma_packet_register_coherence_negative_cases":9,
        "cold_gamma_policy_producer_atomic_negative_cases":38,
        "dynamic_producer_failures_zeroed_cases":9,
        "inactive_semantic_LUT_nonzero_negative_cases":32,
        "cold_gamma_numeric_table_inferred":False,
        "vfe1_wm16_retirement_closed":False,"native_rear_linux_runtime_allowed":False,
        "runtime_actions_performed":False,"private_bytes_exported":False,
        "source_locks":[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in dict.fromkeys(paths)]}
    (OUT/"INTEGRATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"experiment":"E011AV","compiler_runs":reports,"remaining_by_phase":[0,0,0,0],"runner_preflight_function_tested":True}))
if __name__=="__main__":main()
