#!/usr/bin/env python3
"""Detached four-packet replay with tuning-produced cold AEC/AWB fields."""
from pathlib import Path
import contextlib,hashlib,importlib.util,io,json,struct,subprocess,tempfile
OUT=Path(__file__).resolve().parent;EX=OUT.parent;ROOT=OUT.parents[2];PRIVATE=ROOT.parent/"private"
def load(name,path):
 s=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(s);s.loader.exec_module(m);return m
AV=load("bw_previous",EX/"e011av-rear-source-cold-awb-quad/verify-private.py")
SRC=load("bw_source",OUT/"source-private.py")
def harness():
 c=AV.harness();replace=AV.ah.replace_once
 old='#include "'+str(AV.OUT/"host-source-weight-quad-check.h")+'"'
 new='#include "'+str(OUT/"cold-aec-source.h")+'"\n#include "'+str(AV.AL/"weight-quad-producer.h")+'"\nstatic struct e011al_weight_quad_output e011bw_cold_output;\n#include "'+str(OUT/"host-source-weight-quad-check.h")+'"'
 c=replace(c,old,new)
 mark=" CHECK(e011av_decode_cold_quad(tuning,93,1,0,&e011av_cold_quad)==0);"
 addition=mark+"""
 uint8_t grid_wire[404];uint32_t source_weight_bits[3];
 read_exact(grid_wire,404);
 CHECK(e011bw_decode_invariant_cold_weights(grid_wire,404,0,0,4,source_weight_bits)==0);
 struct e011al_weight_quad_input source_input={{source_weight_bits[0],source_weight_bits[1],source_weight_bits[2]},e011av_cold_quad};
 CHECK(e011al_produce_weight_quad(&source_input,&e011bw_cold_output)==0);
"""
 return replace(c,mark,addition)
def normal_weight_quad():
 # Cold capture records are never read as producer inputs in this derivative.
 cap=PRIVATE/"E011AK-20260930-1025A/capture"
 normal=struct.unpack("<3I",(cap/"AECPRODUCE03_FRAME.bin").read_bytes()[0x44:0x50])
 quad=struct.unpack_from("<I",(cap/"AWBPRODUCE01_IO.bin").read_bytes(),0x54)[0]
 validator=load("bw_normal_validator",EX/"e011ak-rear-stats-input-observer/validate-private.py")
 with contextlib.redirect_stdout(io.StringIO()):validator.main()
 with tempfile.TemporaryDirectory(prefix="e011bw-normal-",dir=PRIVATE) as tmp:
  binary=Path(tmp)/"check"
  build=subprocess.run(["gcc","-std=c11","-Wall","-Wextra","-Werror",str(AV.AL/"weight-quad-check.c"),"-o",str(binary)],capture_output=True)
  assert build.returncode==0,"normal weight build failed"
  run=subprocess.run([str(binary)],input=struct.pack("<4I",*normal,quad),capture_output=True)
  assert run.returncode==0 and len(run.stdout)==4
 return [(255,255,255,255),tuple(run.stdout)]
def main():
 roots,source_audit=SRC.source_roots()
 source_wire,quad,scalar_audit=load("bw_awb",AV.OUT/"native-private.py").main(return_source=True)
 rs,arithmetic=load("bw_rs",AV.HERE/"native-private.py").main(return_source=True)
 weight=normal_weight_quad()
 bg,_=load("bw_geometry",AV.parent.AJ/"native-private.py").main(return_source=True)
 ai=AV.parent.parent.parent
 scalar,_=load("bw_scalar",ai.HERE/"native-private.py").main(return_source=True)
 old_wire,bpc,adaptive=AV.ag.source_wire()
 grid=roots[-1][0]
 wire=source_wire+grid+b"".join(struct.pack("<8I",*v) for v in rs)+b"".join(bytes(v) for v in weight)+b"".join(struct.pack("<10I",*v) for v in bg)+b"".join(struct.pack("<4H4I2H",*v) for v in scalar)+old_wire
 AV.ah.verify_l4_authority();oracle,audit=AV.ah.oracle_bf();reports=[]
 with tempfile.TemporaryDirectory(prefix="e011bw-full-private-",dir=PRIVATE) as tmp:
  td=Path(tmp);src=td/"check.c";src.write_text(harness())
  for compiler in ["gcc","clang"]:
   binary=td/compiler
   build=subprocess.run([compiler,"-std=c11","-Wall","-Wextra","-Werror","-fsanitize=address,undefined","-ffp-contract=off","-fno-omit-frame-pointer","-g",str(src),"-lm","-o",str(binary)],capture_output=True)
   if build.returncode:
    (PRIVATE/(td.name+"-"+compiler+"-build-failure.raw")).write_bytes(build.stderr)
    raise RuntimeError("full replay compile failed; diagnostic remains private on SP11")
   output=td/(compiler+"-out")
   report=AV.ah.run_binary(binary,output,wire);report["compiler"]=compiler;reports.append(report)
   phases,adaptive_matches=AV.ag.compare(output,bpc,adaptive)
   bg_matches=AV.parent.parent.compare_bg(output);scalar_matches=ai.compare_scalar(output)
   bf_matches=AV.ah.compare_bf(output,oracle,audit);wq_matches=AV.parent.compare_weight_quad(output);rs_matches=AV.compare_rs(output)
   assert [p["host_fixture_other_register_mismatch_count"] for p in phases]==[0,0,0,0]
   assert all(not p["remaining_fixture_mismatch_families"] for p in phases)
 assert {k:v for k,v in reports[0].items() if k!="compiler"}=={k:v for k,v in reports[1].items() if k!="compiler"}
 prior=json.loads((AV.OUT/"INTEGRATION-SAFE.json").read_text())
 paths=[]
 for lock in prior["source_locks"]:
  p=ROOT/lock["path"];assert hashlib.sha256(p.read_bytes()).hexdigest()==lock["sha256"];paths.append(p)
 paths.extend([AV.OUT/"verify-private.py",AV.OUT/"host-source-weight-quad-check.h",EX/"e011bb-rear-aec-four-grid-deserialization/source-private.py"])
 paths.extend(OUT/f for f in ["source-private.py","cold-aec-source.h","weights-check.c","verify-private.py","host-source-weight-quad-check.h"])
 safe={"experiment":"E011BW","status":"PASS_FULL_DETACHED_REPLAY_WITH_SOURCE_COLD_AEC_AND_AWB",
  "base_commit":SRC.BASE_COMMIT,"compiler_runs":reports,"source_files":source_audit,
  "cold_AEC_weights_produced_by_C_from_qualified_invariant_Default_grid_wire":True,
  "cold_AWB_quad_produced_by_C_from_qualified_Default_wire":True,
  "captured_cold_weight_and_quad_inputs_replaced_by_invalid_sentinels":True,
  "captured_cold_weight_and_quad_read_as_producer_authority":False,
  "cold_source_numeric_producibility_verified":True,"live_first_source_to_prepublication_frame_pointer_join_closed":False,
  "cold_numeric_live_policy_closed":False,"exact_opened_tuning_filename_profile_closed":False,
  "normal_dynamic_weights_quad_and_RS_still_use_independently_observed_inputs":True,
  "remaining_semantic_register_mismatches_by_phase":[0,0,0,0],
  "phase_comparison":phases,"weight_quad_phase_comparison":wq_matches,"RS_phase_comparison":rs_matches,
  "bg_phase_comparison":bg_matches,"scalar_phase_comparison":scalar_matches,"bf_phase_comparison":bf_matches,
  "adaptive_payload_matches":adaptive_matches,"native_RS_differential":arithmetic["compiler_runs"],
  "runner_preflight_function_tested":True,"runner_preflight_negative_cases":6,
  "invariant_source_shape_only_no_unsupported_selection_fallback":True,
  "RS_normal_count_policy_and_whole_frame_offset_authority_closed":False,
  "complete_deterministic_source_bootstrap_closed":False,"WM16_retirement_closed":False,
  "native_rear_runtime_allowed":False,"new_kernel_build":False,"new_camera_starts":0,"new_reboots":0,"private_bytes_exported":False,
  "source_locks":[{"path":str(p.relative_to(ROOT)),"sha256":hashlib.sha256(p.read_bytes()).hexdigest()} for p in dict.fromkeys(paths)]}
 (OUT/"INTEGRATION-SAFE.json").write_text(json.dumps(safe,indent=2,sort_keys=True)+"\n")
 print(json.dumps({"experiment":"E011BW","compiler_runs":reports,"remaining_by_phase":[0,0,0,0],
  "cold_AEC_and_AWB_source_produced":True,"cold_live_policy_still_open":True}),flush=True)
if __name__=="__main__":main()
