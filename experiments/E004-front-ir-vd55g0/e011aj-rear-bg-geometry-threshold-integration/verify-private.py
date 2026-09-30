#!/usr/bin/env python3
"""Private full provider replay with clean geometry/threshold BG lowering."""
from pathlib import Path
import hashlib,importlib.util,json,struct,subprocess,tempfile
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[2];EX=HERE.parent;PRIVATE=ROOT.parent/"private"
AI=EX/"e011ai-rear-neutral-scalar-full-integration"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
parent=load("e011aj_ai",AI/"verify-private.py")
def harness():
    c=parent.harness();replace=parent.parent.replace_once
    needle='#include "'+str(AI/"camss-e011ai-startup-scalar-bind.inc")+'"'
    c=replace(c,needle,needle+'\n#include "'+str(HERE/"camss-e011aj-startup-bg-bind.inc")+'"')
    c=replace(c,"int main(int argc,char **argv) {",
        '#include "'+str(HERE/"host-bg-check.h")+'"\nint main(int argc,char **argv) {')
    c=replace(c,"init_base(base);e011ai_host_bind(base);",
        "init_base(base);e011aj_host_bind(base);e011ai_host_bind(base);")
    c=replace(c,'scalar_producer_negative_cases\\":%u}',
        'scalar_producer_negative_cases\\":%u,\\"bg_negative_cases\\":%u,\\"bg_producer_negative_cases\\":%u}')
    c=replace(c,"scalar_negative_cases,scalar_producer_negative_cases);",
        "scalar_negative_cases,scalar_producer_negative_cases,bg_negative_cases,bg_producer_negative_cases);")
    return c
def compare_bg(path):
    decoder=load("e011aj_decode",EX/"e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py")
    corpus_path=PRIVATE/"e006a/E006A-PRIVATE-RECORDS-v2.json"
    assert hashlib.sha256(corpus_path.read_bytes()).hexdigest()=="2b3701d0e77971f578a8f472d5cfda466f937b4903e8f38f25a18eaacb4fbb69"
    corpus=json.loads(corpus_path.read_text(encoding="utf-8-sig"))
    wanted={r+d for r in (0xb06c,0xb070,0xb074,0xb078,0xb080,0xb084,0xb088,0xb08c,0xb090) for d in (0,0x800)}
    phases=[]
    for p in range(4):
        own=decoder.decode((path/f"p{p}-main-0.bin").read_bytes())
        rec=next(r for r in corpus["records"] if r["n"]==p and r["idx"]==1 and r["complete"])
        oracle=decoder.decode(bytes.fromhex(rec["hex"]))
        a={r:v for r,v,off,k in own["writes"] if r in wanted}
        b={r:v for r,v,off,k in oracle["writes"] if r in wanted}
        assert a==b,{"phase":p,"matching_geometry_threshold_registers":sum(a.get(r)==v for r,v in b.items())}
        assert len(a)==(18 if p<2 else 0)
        phases.append({"phase":p,"geometry_threshold_registers_exact":len(a)})
    return phases
def main():
    native=load("e011aj_native",HERE/"native-private.py")
    bg,arithmetic=native.main(return_source=True)
    scalar,_=load("e011aj_scalar",AI/"native-private.py").main(return_source=True)
    old_wire,bpc,adaptive=parent.parent.parent.source_wire()
    wire=b"".join(struct.pack("<10I",*v) for v in bg)+b"".join(struct.pack("<4H4I2H",*v) for v in scalar)+old_wire
    parent.parent.verify_l4_authority();oracle,audit=parent.parent.oracle_bf()
    reports=[]
    with tempfile.TemporaryDirectory(prefix="e011aj-full-private-",dir=PRIVATE) as tmp:
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
            report=parent.parent.run_binary(binary,output,wire);report["compiler"]=compiler;reports.append(report)
            phases,adaptive_matches=parent.parent.parent.compare(output,bpc,adaptive)
            bg_matches=compare_bg(output);scalar_matches=parent.compare_scalar(output)
            bf_matches=parent.parent.compare_bf(output,oracle,audit)
            assert [p["host_fixture_other_register_mismatch_count"] for p in phases]==[3,5,3,0]
    assert {k:v for k,v in reports[0].items() if k!="compiler"}=={k:v for k,v in reports[1].items() if k!="compiler"}
    paths=parent.parent.parent.includes()+[
        EX/"e011ag-rear-full-provider-startup-integration/integration-check.c",
        EX/"e011ag-rear-full-provider-startup-integration/camss-e011ag-startup-compose.inc",
        parent.parent.HERE/"camss-e011ah-request-af-roi.inc",parent.parent.HERE/"host-af-check.h",
        EX/"e008t-rear-packet-aware-bf-semantic-composer/camss-vfe-e008t-rear-bf-semantic.inc",
        EX/"e008z-rear-af-default-rectangle/af-default-rectangle.h",
        EX/"e008x-rear-af-bf-roi-map/af-bf-roi-map.h",
        AI/"camss-e011ai-startup-scalar-bind.inc",AI/"host-scalar-check.h",AI/"scalar-producer.h",
        AI/"scalar-check.c",AI/"authority-private.py",AI/"native-private.py",AI/"verify-private.py",
        HERE/"bg-producer.h",HERE/"bg-check.c",HERE/"camss-e011aj-startup-bg-bind.inc",
        HERE/"host-bg-check.h",HERE/"native-private.py",HERE/"verify-private.py",
        EX/"e011b-aec-bg-cold-slot-map/RESULT.json",
        EX/"e011n-rear-aecbe-request1-producer/RESULT.json",
        EX/"e011q-rear-awbbg-prerequest-seed-prepublish/RESULT.json",
        EX/"e011m-rs-titan680-capability-origin/RESULT.json"]
    safe={"experiment":"E011AJ","status":"PASS_BG_GEOMETRY_THRESHOLD_FULL_PROVIDER_PRIVATE_PARITY",
        "parent_git_revision":"c5fab3f3066d69833aa02a23bc801bee47c10cf2",
        "linux_slice":"L4 bounded BG production -> L2 offline startup binding/materialization",
        "profile":"rear Color VideoRecord NV12 3840x2160; offline only",
        "evidence":"prior P E011B/N/Q/M input semantics; S original geometry differential; D detached binding",
        "source_schedule":[0,1,1,1],"binding_authority":"clean C outputs after independent native comparison",
        "native_geometry_differential":arithmetic["compiler_runs"],"compiler_runs":reports,
        "bg_phase_comparison":bg_matches,"bg_geometry_threshold_register_instances_exact":36,
        "scalar_phase_comparison":scalar_matches,"bf_phase_comparison":bf_matches,
        "source_adaptive_payload_matches":adaptive_matches,"phase_comparison":phases,
        "remaining_semantic_register_mismatches":11,"remaining_mismatches_by_phase":[3,5,3,0],
        "remaining_register_seams":"AEC Q4 luminance weights; AWB quad synchronization; RS startup and normal config",
        "other_fields_and_caller_tags_preserved":True,"atomic_rejection_preserves_all_bases":True,
        "gain_policy":"unity only; live independent gain field binding remains open",
        "cold_gamma_state":"unchanged valid unused host-only completion",
        "complete_source_produced_e008o_composition_closed":False,"vfe1_wm16_retirement_closed":False,
        "native_rear_linux_runtime_allowed":False,"runtime_actions_performed":False,
        "source_locks":[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in dict.fromkeys(paths)],
        "private_values_or_generated_packet_bytes_exported":False}
    (HERE/"INTEGRATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:v for k,v in safe.items() if k not in ("source_locks","bf_phase_comparison","phase_comparison")},indent=2))
if __name__=="__main__":main()
