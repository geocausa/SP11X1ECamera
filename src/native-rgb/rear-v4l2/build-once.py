#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Fresh source-only rear public-buffer admission build; no runtime/install."""
import hashlib,importlib.util,json,os,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;NATIVE=HERE.parent;ROOT=NATIVE.parents[1];PROJECT=ROOT.parents[1]
OUT=PROJECT/"02-kernel/native-rgb-rear-v4l2-20261008-04"
HEAD="05cfcf88d9f9302af1364b52c6d1661c7f84499e"
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
 os.umask(0o077)
 subprocess.run(["bash",str(ROOT/"tools/camera-overlap-guard.sh"),"--require-golden","--require-no-camera-process","--expect-head",HEAD,"--expect-origin",HEAD],check=True,stdout=subprocess.DEVNULL)
 assert not OUT.exists()
 build=load("native_rgb_public_source_build",NATIVE/"build.py")
 result=build.assemble(OUT,nv12_trial=True,front_owner_trial=True,front_queue_trial=True,front_meta_trial=True,front_params_trial=True,front_profile_trial=True,front_sof_trial=True,front_control_trace_trial=True)
 linear=load("native_rgb_public_linear_overlay",NATIVE/"rear-linear-nv12/apply.py")
 result["rear_linear_storage"]=linear.apply(OUT/"camss",public_dma_admission=True)
 public=load("native_rear_public_outputs",HERE/"apply-public-output.py")
 result["public_outputs"]=public.apply(OUT/"camss")
 result["base_commit"]=HEAD
 result["public_rear_runtime_callbacks_installed"]=False
 result["private_firmware_loaded"]=False
 result["source_inputs"]={str(p.relative_to(ROOT)):sha(p) for p in [HERE/"native-rear-video-dma.h",HERE/"native-rear-video-dma.inc",HERE/"native-rear-video-lease.inc",HERE/"apply-public-output.py",NATIVE/"rear-linear-nv12/native-rear-nv12-layout.h",NATIVE/"rear-linear-nv12/apply.py"]}
 result["staged_sources"]={}
 for directory in [OUT/"camss",OUT/"imx681",OUT/"ov13858"]:
  for p in directory.iterdir():
   if p.is_file():result["staged_sources"][str(p.relative_to(OUT))]=sha(p)
 (OUT/"source-manifest.json").write_text(json.dumps(result,indent=2)+"\n")
 for name in ["camss","imx681","ov13858"]:
  with (OUT/(name+"-compile.log")).open("x") as log:
   subprocess.run(["make","-C",str(PROJECT/"02-kernel/e003i-front-production-src"),"O="+str(PROJECT/"02-kernel/build-runtime-v4-headers-20260826"),"M="+str(OUT/name),"CONFIG_VIDEO_QCOM_CAMSS=m","W=1","KCFLAGS=-Werror","-j4","modules"],stdout=log,stderr=subprocess.STDOUT,check=True)
  assert not re.search(r"\b(?:warning:|error:)",(OUT/(name+"-compile.log")).read_text())
 result["modules"]={n:dict(sha256=sha(OUT/n),vermagic=subprocess.check_output(["modinfo","-F","vermagic",str(OUT/n)],text=True).strip()) for n in ["camss/qcom-camss.ko","imx681/imx681.ko","ov13858/ov13858.ko"]}
 result.update(status="PASS_REAR_VB2_DMA_ADMISSION_SOURCE_BUILD_NOT_INSTALLED",module_compile_diagnostics=0,runtime_actions_performed=False)
 (OUT/"build-result.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({k:result[k] for k in ["status","module_compile_diagnostics","runtime_actions_performed","public_rear_runtime_callbacks_installed"]}))
if __name__=="__main__":main()
