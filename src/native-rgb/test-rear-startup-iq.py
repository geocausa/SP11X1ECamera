#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Real rear BF finalizer/CST/BPC binder tests; optional same-SP11 private oracle."""
import argparse,ctypes,importlib.util,json,os,shutil,subprocess,tempfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
def checked(args,env=None):
 r=subprocess.run(args,capture_output=True,text=True,env=env)
 if r.returncode: raise RuntimeError(r.stdout+r.stderr)
 return r
BRIDGE=r"""
#include "rear-iq-host-fixture.h"
#include "../../experiments/E004-front-ir-vd55g0/e008z-rear-af-default-rectangle/af-default-rectangle.h"
int native_rear_iq_private_bf(float first_zoom,u8 *out){
 struct e008o_rear_packet_semantics base[4];
 struct native_rear_startup_iq_input input;
 struct e008z_af_default_inputs in={
  .camif_width=4064,.camif_height=2286,.width_fraction=0.25f,
  .height_fraction=0.25f,.mode_scale=1.0f,.pd_width_scale=1.0f,.pd_height_scale=1.0f,
 };
 struct e008z_af_rect rect;unsigned p;int ret;
 native_rear_iq_test_initialize(base,&input);
 for(p=1;p<4;p++){
  in.zoom=p==1?first_zoom:1.0f;
  if(e008z_af_default_rect(&in,&rect))return -EINVAL;
  input.packet[p].af=(struct native_rear_af_rect){rect.x,rect.y,rect.width,rect.height};
 }
 ret=native_rear_bind_startup_iq(base,&input);if(ret)return ret;
 for(p=0;p<4;p++){
  ret=e007e_bfstats25_dmi(e008t_rear_bf_dmi(&base[p].dmi),1,out+p*300,300);
  if(ret)return ret;
 }
 return 0;
}
"""
def private_oracle(staged,tmp):
 if not str(ROOT).startswith("/home/geoca/Documents/SP11-PROJECT/"):
  raise RuntimeError("private oracle requires same-SP11 project workspace")
 source=ROOT/"experiments/E004-front-ir-vd55g0/e008u-rear-bf-roi-geometry-audit/audit-private.py"
 spec=importlib.util.spec_from_file_location("retained_bf_iq",source)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
 actual=module.observed()
 # Existing physically observed request-stage scalar; oracle input only.
 # Upstream transient calculation remains open. Never a driver constant.
 report=json.loads((ROOT/"experiments/E004-front-ir-vd55g0/e009e-rear-af-live-zoom-forward/RESULT.json").read_text())
 first_zoom=report["same_sp11_live_first_normal_zoom"]
 code=tmp/"private-iq.c";code.write_text(BRIDGE)
 libfile=tmp/"private-iq.so"
 checked(["gcc","-std=gnu11","-Wall","-Wextra","-Werror","-shared","-fPIC",
          "-I"+str(HERE),"-I"+str(staged),str(code),"-o",str(libfile)])
 lib=ctypes.CDLL(str(libfile));fn=lib.native_rear_iq_private_bf
 fn.argtypes=[ctypes.c_float,ctypes.POINTER(ctypes.c_ubyte)];fn.restype=ctypes.c_int
 out=(ctypes.c_ubyte*1200)();control=(ctypes.c_ubyte*1200)()
 if fn(first_zoom,out) or fn(1.0,control):raise RuntimeError("private BF binding rejected")
 clean=bytes(out);neutral=bytes(control);phases=[]
 for p in range(4):
  target=actual["startup"+str(p)]
  matches=sum(x==y for x,y in zip(clean[p*300:(p+1)*300],target))
  if len(target)!=300 or matches!=300:raise RuntimeError("private BF aggregate mismatch phase "+str(p))
  phases.append({"phase":p,"bytes_present":300,"bytes_exact":matches})
 negative=sum(x==y for x,y in zip(neutral[300:600],actual["startup1"]))
 if negative!=250:raise RuntimeError("private BF negative control drift")
 return {"status":"PASS_RETAINED_BF_SELECTOR1_ALL_FOUR","phases":phases,
         "bytes_present":1200,"bytes_exact":1200,"request1_zoom_one_negative_control_matches":negative,
         "AF_rect_source_forward_from_observed_caller_zoom":True,
         "independent_upstream_transient_zoom_policy_proven":False,
         "CST_BPC_controls_synthetic_in_BF_oracle":True,
         "wire_bytes_or_image_data_exported":False}
def main():
 p=argparse.ArgumentParser();p.add_argument("--staged",type=Path,required=True)
 p.add_argument("--report",type=Path,required=True);p.add_argument("--private-retained-oracle",action="store_true")
 a=p.parse_args()
 if a.report.exists():raise SystemExit("report already exists")
 staged=a.staged.resolve()
 if (staged/"native-rear-startup-iq.inc").read_bytes()!=(HERE/"native-rear-startup-iq.inc").read_bytes():
  raise RuntimeError("staged IQ binder differs from tested source")
 results=[]
 with tempfile.TemporaryDirectory(prefix="sp11-rear-iq-") as directory:
  tmp=Path(directory)
  for compiler in ["gcc","clang"]:
   executable=shutil.which(compiler)
   if not executable:raise RuntimeError("required compiler missing")
   binary=tmp/compiler
   checked([executable,"-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g",
            "-fsanitize=address,undefined","-fno-omit-frame-pointer",
            "-I"+str(staged),str(HERE/"test-rear-startup-iq.c"),"-o",str(binary)])
   r=checked([str(binary)],env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",
                                   UBSAN_OPTIONS="halt_on_error=1:print_stacktrace=1"))
   if "NATIVE_REAR_IQ_PASS" not in r.stdout:raise RuntimeError("missing IQ test result")
   results.append({"compiler":compiler,"Werror":True,"ASAN_UBSAN":True,
                   "stdout":r.stdout.strip(),"stderr":r.stderr})
  report={"status":"PASS_HOSTED_REAR_IQ_BINDING","results":results,
          "actual_seed_finalizer_and_CST_BPC_packers":True,
          "unrelated_full_fields_omitted_in_host_fixture":True,
          "explicit_caller_tuning_inputs_not_independent_tuning_producer":True,
          "all_or_none_four_packet_mutation":True,"hardware_access":False,
          "readiness_sealing_or_runtime_permission_granted":False}
  if a.private_retained_oracle:report["retained_oracle"]=private_oracle(staged,tmp)
 a.report.write_text(json.dumps(report,indent=2)+"\n");print(json.dumps(report))
if __name__=="__main__":main()
