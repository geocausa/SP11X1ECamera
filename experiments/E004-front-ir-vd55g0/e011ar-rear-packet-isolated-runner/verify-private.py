#!/usr/bin/env python3
"""Full detached startup replay with bounded clean RS production."""
from pathlib import Path
import hashlib,importlib.util,json,struct,subprocess,tempfile
OUT=Path(__file__).resolve().parent;HERE=OUT.parent/"e011am-rear-rs-full-startup-integration";ROOT=HERE.parents[2];EX=HERE.parent;PRIVATE=ROOT.parent/"private"
AL=EX/"e011al-rear-bg-weight-quad-integration"
def load(name,path):
    s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
parent=load("e011am_al",AL/"verify-private.py");ah=parent.ah;ag=parent.ag
def harness():
    c=parent.harness();replace=ah.replace_once
    needle='#include "'+str(AL/"camss-e011al-startup-weight-quad-bind.inc")+'"'
    c=replace(c,needle,needle+'\n#include "'+str(HERE/"camss-e011am-startup-rs-bind.inc")+'"')
    c=replace(c,"int main(int argc,char **argv) {",
        '#include "'+str(HERE/"host-rs-check.h")+'"\nint main(int argc,char **argv) {')
    c=replace(c,"init_base(base);e011al_host_bind(base);",
        "init_base(base);e011am_host_bind(base);e011al_host_bind(base);")
    c=replace(c,'weight_quad_producer_negative_cases\\":%u}',
        'weight_quad_producer_negative_cases\\":%u,\\"rs_negative_cases\\":%u,\\"rs_producer_negative_cases\\":%u}')
    c=replace(c,"weight_quad_negative_cases,weight_quad_producer_negative_cases);",
        "weight_quad_negative_cases,weight_quad_producer_negative_cases,rs_negative_cases,rs_producer_negative_cases);")
    source=(OUT/"camss-vfe-e011ar-rear-runner.inc").read_text()
    struct=source[source.index("struct e011ar_rear_request {"):source.index("struct e011ar_rear_result {")]
    a=source.index("static int\ne011ar_rear_materialize_all")
    b=source.index("static int\ne011ar_rear_collect_done",a)
    adapter="struct v4l2_subdev;\n#ifndef U64_MAX\n#define U64_MAX UINT64_MAX\n#endif\n"+struct+source[a:b]
    c=replace(c,"int main(int argc,char **argv) {",adapter+"int main(int argc,char **argv) {")
    needle="CHECK(e008o_rear_materialize_commands(s,&commands)==0);"
    c=replace(c,needle,"""struct e011ar_rear_request runner={.sensor=(struct v4l2_subdev *)s,
        .semantics=s,.commands=&commands,.first_request_generation=1};
    CHECK(e011ar_rear_materialize_all(&runner)==0);
    for(unsigned int p=0;p<4;p++) {
        CHECK(!memcmp(&runner.packet[p],e008l_rear_command_output(&commands,p),sizeof(runner.packet[p])));
        struct e007y_rear_startup_output *out=&runner.packet[p];
        if(argc>=2) {
            write_private(argv[1],"main",p,0,out->main,out->main_bytes);
            for(size_t i=0;i<out->dmi_count;i++)
                write_private(argv[1],"dmi",p,(unsigned int)i,out->dmi[i].cpu,out->dmi[i].bytes);
        }
    }
    struct e007y_rear_startup_output snapshots[4];memcpy(snapshots,runner.packet,sizeof(snapshots));
    runner.first_request_generation=UINT64_MAX;
    CHECK(e011ar_rear_materialize_all(&runner)!=0);
    CHECK(!memcmp(snapshots,runner.packet,sizeof(snapshots)));
    runner.first_request_generation=1;commands.hardware_exposed=true;
    CHECK(e011ar_rear_materialize_all(&runner)!=0);
    CHECK(!memcmp(snapshots,runner.packet,sizeof(snapshots)));commands.hardware_exposed=false;
    for(unsigned int p=0;p<4;p++) {
        u8 phase=s->packet[p].regs.scalar.startup_phase;
        s->packet[p].regs.scalar.startup_phase=4;
        CHECK(e011ar_rear_materialize_all(&runner)!=0);
        CHECK(!memcmp(snapshots,runner.packet,sizeof(snapshots)));
        s->packet[p].regs.scalar.startup_phase=phase;
    }
    """)
    return c
def compare_rs(path):
    decoder=load("e011am_decode",EX/"e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py")
    corpus_path=PRIVATE/"e006a/E006A-PRIVATE-RECORDS-v2.json"
    assert hashlib.sha256(corpus_path.read_bytes()).hexdigest()=="2b3701d0e77971f578a8f472d5cfda466f937b4903e8f38f25a18eaacb4fbb69"
    corpus=json.loads(corpus_path.read_text(encoding="utf-8-sig"));phases=[]
    for p in range(4):
        own=decoder.decode((path/f"p{p}-main-0.bin").read_bytes())
        rec=next(r for r in corpus["records"] if r["n"]==p and r["idx"]==1 and r["complete"])
        oracle=decoder.decode(bytes.fromhex(rec["hex"]))
        a={r:v for r,v,off,k in own["writes"] if r in (0xbe60,0xbe68,0xbe6c,0xbe70)}
        b={r:v for r,v,off,k in oracle["writes"] if r in (0xbe60,0xbe68,0xbe6c,0xbe70)}
        assert a==b,{"phase":p,"matching_RS_registers":sum(a.get(r)==v for r,v in b.items())}
        phases.append({"phase":p,"RS_register_instances_exact":len(a)})
    return phases
def main():
    rs,arithmetic=load("e011am_native",HERE/"native-private.py").main(return_source=True)
    weight,_=load("e011am_weight",AL/"native-private.py").main(return_source=True)
    bg,_=load("e011am_geometry",parent.AJ/"native-private.py").main(return_source=True)
    ai=parent.parent.parent
    scalar,_=load("e011am_scalar",ai.HERE/"native-private.py").main(return_source=True)
    old_wire,bpc,adaptive=ag.source_wire()
    wire=b"".join(struct.pack("<8I",*v) for v in rs)+b"".join(bytes(v) for v in weight)+b"".join(struct.pack("<10I",*v) for v in bg)+b"".join(struct.pack("<4H4I2H",*v) for v in scalar)+old_wire
    ah.verify_l4_authority();oracle,audit=ah.oracle_bf();reports=[]
    with tempfile.TemporaryDirectory(prefix="e011ar-full-private-",dir=PRIVATE) as tmp:
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
    paths += [OUT/"camss-vfe-e011ar-rear-runner.inc",OUT/"verify-private.py"]
    safe={"runner_preflight_function_tested":True,"runner_preflight_negative_cases":6,"experiment":"E011AR","status":"PASS_FULL_OFFLINE_STARTUP_PARITY_WITH_SOURCE_INPUT_RECORDS",
        "parent_git_revision":"a48adb34c012287e8b8dd767cab3e0670ee512be",
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
        "cold_gamma_state":"unchanged unused host-only completion",
        "vfe1_wm16_retirement_closed":False,"native_rear_linux_runtime_allowed":False,
        "runtime_actions_performed":False,"private_bytes_exported":False,
        "source_locks":[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in dict.fromkeys(paths)]}
    (OUT/"INTEGRATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
    print(json.dumps({"experiment":"E011AR","compiler_runs":reports,"remaining_by_phase":[0,0,0,0],"runner_preflight_function_tested":True}))
if __name__=="__main__":main()
