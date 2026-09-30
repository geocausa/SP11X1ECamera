#!/usr/bin/env python3
"""Full detached provider replay with clean AEC weights and AWB quad."""
from pathlib import Path
import hashlib, importlib.util, json, struct, subprocess, tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent;PRIVATE=ROOT.parent/"private"
AJ=EX/"e011aj-rear-bg-geometry-threshold-integration"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
parent=load("e011al_aj",AJ/"verify-private.py")
ah=parent.parent.parent;ag=ah.parent
def harness():
    c=parent.harness();replace=ah.replace_once
    needle='#include "'+str(AJ/"camss-e011aj-startup-bg-bind.inc")+'"'
    c=replace(c,needle,needle+'\n#include "'+str(HERE/"camss-e011al-startup-weight-quad-bind.inc")+'"')
    c=replace(c,"int main(int argc,char **argv) {",
        '#include "'+str(HERE/"host-weight-quad-check.h")+'"\nint main(int argc,char **argv) {')
    c=replace(c,"init_base(base);e011aj_host_bind(base);",
        "init_base(base);e011al_host_bind(base);e011aj_host_bind(base);")
    c=replace(c,'bg_producer_negative_cases\\":%u}',
        'bg_producer_negative_cases\\":%u,\\"weight_quad_negative_cases\\":%u,\\"weight_quad_producer_negative_cases\\":%u}')
    c=replace(c,"bg_negative_cases,bg_producer_negative_cases);",
        "bg_negative_cases,bg_producer_negative_cases,weight_quad_negative_cases,weight_quad_producer_negative_cases);")
    return c
def compare_weight_quad(path):
    decoder=load("e011al_decode",EX/"e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py")
    corpus_path=PRIVATE/"e006a/E006A-PRIVATE-RECORDS-v2.json"
    assert hashlib.sha256(corpus_path.read_bytes()).hexdigest()=="2b3701d0e77971f578a8f472d5cfda466f937b4903e8f38f25a18eaacb4fbb69"
    corpus=json.loads(corpus_path.read_text(encoding="utf-8-sig"));phases=[]
    for p in range(4):
        own=decoder.decode((path/f"p{p}-main-0.bin").read_bytes())
        rec=next(r for r in corpus["records"] if r["n"]==p and r["idx"]==1 and r["complete"])
        oracle=decoder.decode(bytes.fromhex(rec["hex"]))
        a={r:v for r,v,off,k in own["writes"] if r in (0xb068,0xb860)}
        b={r:v for r,v,off,k in oracle["writes"] if r in (0xb068,0xb860)}
        assert a==b,{"phase":p,"matching_weight_quad_registers":sum(a.get(r)==v for r,v in b.items())}
        assert len(a)==(2 if p<2 else 0)
        phases.append({"phase":p,"weight_quad_register_instances_exact":len(a)})
    return phases
def main():
    values,arithmetic=load("e011al_native",HERE/"native-private.py").main(return_source=True)
    bg,_=load("e011al_geometry",AJ/"native-private.py").main(return_source=True)
    scalar,_=load("e011al_scalar",parent.parent.HERE/"native-private.py").main(return_source=True)
    old_wire,bpc,adaptive=ag.source_wire()
    wire=b"".join(bytes(v) for v in values)+b"".join(struct.pack("<10I",*v) for v in bg)+b"".join(struct.pack("<4H4I2H",*v) for v in scalar)+old_wire
    ah.verify_l4_authority();oracle,audit=ah.oracle_bf();reports=[]
    with tempfile.TemporaryDirectory(prefix="e011al-full-private-",dir=PRIVATE) as tmp:
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
            bg_matches=parent.compare_bg(output);scalar_matches=parent.parent.compare_scalar(output)
            bf_matches=ah.compare_bf(output,oracle,audit);wq_matches=compare_weight_quad(output)
            assert [p["host_fixture_other_register_mismatch_count"] for p in phases]==[1,3,3,0]
            assert all(set(p["remaining_fixture_mismatch_families"])<={"RS_STATS14"} for p in phases)
    assert {k:v for k,v in reports[0].items() if k!="compiler"}=={k:v for k,v in reports[1].items() if k!="compiler"}
    prior=json.loads((AJ/"INTEGRATION-SAFE.json").read_text())
    paths=[]
    for lock in prior["source_locks"]:
        p=ROOT/lock["path"];assert hashlib.sha256(p.read_bytes()).hexdigest()==lock["sha256"];paths.append(p)
    paths += [HERE/f for f in ("weight-quad-producer.h","weight-quad-check.c",
        "camss-e011al-startup-weight-quad-bind.inc","host-weight-quad-check.h","native-private.py","verify-private.py")]
    paths += [EX/"e011ak-rear-stats-input-observer"/f for f in ("validate-private.py","VALIDATION-SAFE.json","RESULT.json")]
    safe={"experiment":"E011AL","status":"PASS_CLEAN_WEIGHT_QUAD_FULL_PROVIDER_PRIVATE_PARITY",
        "parent_git_revision":"c8742eb070b69a5a35f67c0d5fd9484ab2962ab7",
        "slice":"L4 integer binary32 quantization -> detached L2 startup binder",
        "profile":"rear Color VideoRecord NV12 3840x2160; offline only",
        "source_schedule":[0,1,1,1],"compiler_runs":reports,"native_differential":arithmetic["compiler_runs"],
        "weight_quad_phase_comparison":wq_matches,"weight_quad_register_instances_exact":4,
        "bg_phase_comparison":bg_matches,"bg_geometry_threshold_register_instances_exact":36,
        "scalar_phase_comparison":scalar_matches,"bf_phase_comparison":bf_matches,
        "source_adaptive_payload_matches":adaptive_matches,"phase_comparison":phases,
        "previous_remaining_semantic_register_mismatches":11,"remaining_semantic_register_mismatches":7,
        "remaining_mismatches_by_phase":[1,3,3,0],"remaining_register_family":"RS_STATS14",
        "binding_authority":"clean C results after original differential; independent L4 input records",
        "cold_weight_quad_initialization_policy_closed":False,"cold_input_authority":"caller-owned observed semantic consumer input",
        "normal_input_authority":"source-verified AEC frame control and AWB IO fields",
        "integer_only_producer_and_binder":True,"retained_outputs_used_as_inputs":False,
        "other_fields_and_caller_tags_preserved":True,"atomic_rejection_preserves_all_bases":True,
        "BG_later_holds":"detached state only; these register ranges are absent in packets2/3",
        "complete_source_produced_e008o_composition_closed":False,
        "cold_gamma_state":"unchanged unused host-only completion",
        "vfe1_wm16_retirement_closed":False,"native_rear_linux_runtime_allowed":False,
        "runtime_actions_performed":False,"private_bytes_exported":False,
        "source_locks":[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in dict.fromkeys(paths)]}
    (HERE/"INTEGRATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in safe.items() if k not in ("source_locks","bf_phase_comparison","phase_comparison")},indent=2))
if __name__=="__main__":main()
