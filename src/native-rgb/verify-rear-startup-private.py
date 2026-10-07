#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Same-SP11 source inputs -> built libipa -> current complete rear composer.
Retained commands are comparison outputs only. No hardware/device access.
Cold policies and scheduling provenance are explicitly not a release tuning proof.
"""
import argparse,contextlib,ctypes,hashlib,importlib.util,io,json,os,struct,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EX=ROOT/"experiments/E004-front-ir-vd55g0"
PRIVATE=ROOT.parent/"private"
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
def checked(command,private,input=None,env=None):
 run=subprocess.run(command,input=input,capture_output=True,env=env)
 if run.returncode:
  (PRIVATE/(private.name+"-failure-diagnostic.raw")).write_bytes(run.stdout+run.stderr)
  raise RuntimeError("private compile/check failed; diagnostic remains on SP11")
 return run
def producer_wire(source,build,temporary):
 helpers=source/"src/ipa/libipa"
 for name in ["camss_x1e_helpers.h","camss_x1e_helpers.cpp"]:
  if (helpers/name).read_bytes()!=(HERE/"libcamera"/name).read_bytes():
   raise RuntimeError("built libipa helper source drift")
 result=json.loads((build/"native-rgb-build-result.json").read_text())
 if result["compiler_warning_lines"] or result["hardware_access"] or result["installed"]:
  raise RuntimeError("libcamera build evidence not admitted")
 if any(t["result"] not in ("OK","SKIP") for t in result["tests"]):
  raise RuntimeError("libcamera tests not admitted")
 scalar=load("current_rear_scalar_inputs",HERE/"verify-rear-scalars-private.py")
 code=temporary/"libipa-bridge.cpp";code.write_text((HERE/"rear-startup-private-bridge.cpp").read_text())
 library=temporary/"libipa-bridge.so"
 checked(["g++","-std=c++17","-Wall","-Wextra","-Werror","-shared","-fPIC",
          "-I"+str(source/"include"),"-I"+str(build/"include"),"-I"+str(helpers),
          str(code),str(build/"src/ipa/libipa/libipa.a"),
          "-L"+str(build/"src/libcamera"),"-L"+str(build/"src/libcamera/base"),
          "-Wl,-rpath,"+str(build/"src/libcamera"),
          "-Wl,-rpath,"+str(build/"src/libcamera/base"),
          "-lcamera","-lcamera-base","-lm","-o",str(library)],temporary)
 lib=ctypes.CDLL(str(library))
 gen=lib.sp11_generate_rear_scalar_envelope
 gen.argtypes=[ctypes.POINTER(scalar.In),ctypes.POINTER(ctypes.c_uint64),ctypes.POINTER(scalar.Capsule)];gen.restype=ctypes.c_int
 samples=json.loads((scalar.PRIVATE/"samples.json").read_text())["samples"]
 inputs=(scalar.In*4)();ids=(ctypes.c_uint64*4)(4,5,6,6)
 for p,index in enumerate([0,1,2,2]):
  item=samples[index];x=inputs[p]
  x.demux_gain=item["demux_gain"];x.bls[:]=item["bls"];x.channel[:]=item["channel"]
  x.awb_g,x.awb_b,x.awb_r=item["pdpc_floats"][2:5]
  x.predictive_gain=item["wb"][3];x.bayer=item["bayer"]
 capsule=scalar.Capsule()
 if gen(inputs,ids,ctypes.byref(capsule)):raise RuntimeError("actual libipa scalar production failed")
 wire=bytearray(bytes(capsule))
 af=lib.sp11_generate_rear_af;af.argtypes=[ctypes.c_float,ctypes.POINTER(ctypes.c_uint16)];af.restype=ctypes.c_int
 first_zoom=json.loads((EX/"e009e-rear-af-live-zoom-forward/RESULT.json").read_text())["same_sp11_live_first_normal_zoom"]
 for zoom in [first_zoom,1.0,1.0]:
  rect=(ctypes.c_uint16*4)()
  if af(zoom,rect):raise RuntimeError("actual libipa AF production failed")
  wire.extend(struct.pack("<4H",*rect))
 weights=load("current_rear_weight_inputs",EX/"e011al-rear-bg-weight-quad-integration/native-private.py")
 with contextlib.redirect_stdout(io.StringIO()):source_weights=weights.source_inputs()
 wfn=lib.sp11_generate_rear_weights
 wfn.argtypes=[ctypes.POINTER(ctypes.c_float),ctypes.c_bool,ctypes.POINTER(ctypes.c_uint8)];wfn.restype=ctypes.c_int
 for item in source_weights:
  vals=(ctypes.c_float*3)(*struct.unpack("<3f",struct.pack("<3I",*item[:3])))
  if item[3] not in (0,1):raise RuntimeError("source AWB quad is not boolean")
  output=(ctypes.c_uint8*4)()
  if wfn(vals,bool(item[3]),output):raise RuntimeError("actual libipa weight production failed")
  wire.extend(bytes(output))
 bg=load("current_rear_bg_inputs",EX/"e011aj-rear-bg-geometry-threshold-integration/native-private.py").source_inputs()
 rsmod=load("current_rear_rs_inputs",EX/"e011am-rear-rs-full-startup-integration/native-private.py")
 with contextlib.redirect_stdout(io.StringIO()):rs=rsmod.source_inputs()
 for item in bg:wire.extend(struct.pack("<14I",*item))
 for item in rs:wire.extend(struct.pack("<6I",*item))
 ag=load("current_rear_adaptive",EX/"e011ag-rear-full-provider-startup-integration/verify-private.py")
 with contextlib.redirect_stdout(io.StringIO()):adaptive_wire,bpc,adaptive=ag.source_wire()
 wire.extend(adaptive_wire)
 return bytes(wire),ag,bpc,adaptive
def cst_source():
 reserve=json.loads((EX/"e006r-rear-cst12-tuning-packer/TUNING-SAFE.json").read_text())["reserve"]
 fields={"enabled":1}
 for col,key in [(0,"c_x0"),(1,"c_x1")]:
  for row,value in enumerate(reserve[key]):fields[f"c{row}{col}"]=value
 for i,value in enumerate(reserve["m_q10_roundf"]):fields[f"m{i//3}{i%3}"]=value
 for key in ["o","s"]:
  for i,value in enumerate(reserve[key]):fields[f"{key}{i}"]=value
 return "iq->cst=(struct e006r_cst12_state){"+",".join(f".{k}={v}" for k,v in fields.items())+"};"
def compare(output,ag,bpc,adaptive):
 phases,adaptive_counts=ag.compare(output,bpc,adaptive)
 if any(p["host_fixture_other_register_mismatch_count"] for p in phases):
  return phases,adaptive_counts,False
 bf=load("current_rear_bf_comparison",EX/"e008u-rear-bf-roi-geometry-audit/audit-private.py").observed()
 decoder=load("current_rear_decoder",EX/"e006a-windows-rear-rtcdm-targeted-corpus/decode_rear_rtcdm.py")
 slots=0
 for p in range(4):
  main=decoder.decode((output/f"p{p}-main-0.bin").read_bytes())
  target=bf["startup"+str(p)]
  selected=[(i,d) for i,d in enumerate(main["dmis"]) if d["dmi_register_offset"]==0xbc08 and d["dmi_sel"]==1]
  if len(selected)!=1:raise RuntimeError("BF selector1 shape mismatch")
  i,_=selected[0]
  if (output/f"p{p}-dmi-{i}.bin").read_bytes()!=target:raise RuntimeError("BF selector1 payload mismatch")
  slots+=1
 adaptive_counts["BF_selector1_slots_exact"]=slots
 return phases,adaptive_counts,True
def main():
 p=argparse.ArgumentParser()
 p.add_argument("--libcamera-source",type=Path,required=True);p.add_argument("--libcamera-build",type=Path,required=True)
 p.add_argument("--kernel-staged",type=Path,required=True);p.add_argument("--report",type=Path,required=True)
 a=p.parse_args()
 if not str(ROOT).startswith("/home/geoca/Documents/SP11-PROJECT/") or not PRIVATE.is_dir():
  raise SystemExit("private verification requires same-SP11 workspace")
 if a.report.exists():raise SystemExit("report identity already exists")
 for name in ["native-rear-startup-compose.inc","native-rear-startup-iq.inc","native-rear-startup-statistics.inc"]:
  if (a.kernel_staged/name).read_bytes()!=(HERE/name).read_bytes():raise RuntimeError("kernel staged source drift")
 os.umask(0o077);runs=[];comparisons=[]
 with tempfile.TemporaryDirectory(prefix="native-rear-current-private-",dir=PRIVATE) as td:
  tmp=Path(td);wire,ag,bpc,adaptive=producer_wire(a.libcamera_source,a.libcamera_build,tmp)
  code=tmp/"compose.c";text=(HERE/"rear-startup-private-check.c").read_text()
  if text.count("/* CST_SOURCE */")!=1:raise RuntimeError("CST source marker drift")
  code.write_text(text.replace("/* CST_SOURCE */",cst_source()))
  for compiler in ["gcc","clang"]:
   binary=tmp/compiler
   checked([compiler,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g",
            "-fsanitize=address,undefined","-fno-omit-frame-pointer",
            "-I"+str(HERE),"-I"+str(a.kernel_staged),str(code),"-o",str(binary)],tmp)
   output=tmp/(compiler+"-output");output.mkdir()
   run=checked([str(binary),str(output)],tmp,input=wire,
       env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
   result=json.loads(run.stdout);result["compiler"]=compiler;runs.append(result)
   phases,counts,exact=compare(output,ag,bpc,adaptive);comparisons.append((phases,counts,exact))
  if {k:v for k,v in runs[0].items() if k!="compiler"}!={k:v for k,v in runs[1].items() if k!="compiler"}:
   raise RuntimeError("compiler scalar evidence differs")
  if comparisons[0]!=comparisons[1]:raise RuntimeError("compiler retained comparison differs")
  phases,counts,exact=comparisons[0]
 report={"status":"PASS_CURRENT_FULL_REAR_SOURCE_INPUT_PREFLIGHT" if exact else "FAIL_CURRENT_FULL_REAR_RETAINED_REGISTER_PARITY",
   "actual_built_libipa_scalar_AF_and_weight_producers":True,
   "actual_current_complete_kernel_composer_and_materializer":True,
   "retained_RTCDM_output_words_used_as_inputs":False,
   "CST_source_selected_tuning":True,"BPC_clean_semantic_producer":True,
   "LSC_GTM_clean_source_producers":True,
   "BG_RS_independent_observed_semantic_inputs":True,
   "cold_initialization_normal_AFD_and_transient_zoom_policy_closed":False,
   "request_schedule_authority":"existing retained source association; explicit 4/5/6/6",
   "zero_black_and_unused_weight_enable_policy":"explicit bounded diagnostic input; release tuning origin unproven",
   "independent_release_tuning_or_complete_runtime_delivery_proven":False,
   "all_present_register_words_exact":exact,"phase_comparison":phases,
   "source_adaptive_payload_matches":counts,"compiler_runs":runs,
   "host_DMA_addresses_and_allocations_simulated":True,"hardware_access":False,
   "private_wire_images_arrays_or_hashes_exported":False,
   "libcamera_build":str(a.libcamera_build),"kernel_stage":str(a.kernel_staged)}
 a.report.write_text(json.dumps(report,indent=2)+"\n")
 print(json.dumps(report))
 if not exact:raise SystemExit(1)
if __name__=="__main__":main()
