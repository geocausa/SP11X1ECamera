#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Prepare a fresh disposable generation/stop diagnostic; no install or reboot.
Private compiler-bound semantic firmware and its digest stay on this SP11.
"""
import argparse,hashlib,importlib.util,json,os,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent;NATIVE=HERE.parent;ROOT=NATIVE.parents[1]
PROJECT=ROOT.parents[1];OUT=PROJECT/"02-kernel/native-rgb-rear-generation-20261007-08"
PRIVATE=ROOT.parent/"private/NATIVE-REAR-GENERATION-20261007-08"
HEAD="5233d8e87049d8b8a3aa57075756fd373be5b6a4"
SOURCE=PROJECT/"06-camera/reference/libcamera-native-rgb-rear-20261007-15"
LIBBUILD=PROJECT/"02-kernel/libcamera-native-rgb-rear-20261007-15"
KSOURCE=PROJECT/"02-kernel/e003i-front-production-src"
KOUTPUT=PROJECT/"02-kernel/build-runtime-v4-headers-20260826"
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,path)
 m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
def replace(path,old,new):
 t=path.read_text()
 if t.count(old)!=1:raise RuntimeError("candidate anchor drift: "+path.name)
 path.write_text(t.replace(old,new,1))
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def guard():
 r=subprocess.run(["bash",str(ROOT/"tools/camera-overlap-guard.sh"),
    "--require-golden","--require-no-camera-process","--expect-head",HEAD,"--expect-origin",HEAD],
    cwd=ROOT,capture_output=True,text=True)
 if r.returncode:raise RuntimeError("overlap guard failed")
def main():
 os.umask(0o077);guard()
 for path in [OUT,PRIVATE,Path("/var/lib/sp11-camera-native-rear-generation-20261007-06"),
              Path("/boot/sp11-7.1.5-camera-native-rear-generation-20261007-06")]:
  if path.exists():raise RuntimeError("candidate path already exists; audit first")
 build=load("native_rear_build",NATIVE/"build.py")
 result=build.assemble(OUT,nv12_trial=True,front_owner_trial=True,front_queue_trial=True,
   front_meta_trial=True,front_params_trial=True,front_profile_trial=True,front_sof_trial=True,
   front_control_trace_trial=True)
 camss=OUT/"camss";PRIVATE.mkdir(mode=0o700)
 verify=load("native_rear_current_verify",NATIVE/"verify-rear-startup-private.py")
 wire,ag,bpc,adaptive=verify.producer_wire(SOURCE,LIBBUILD,PRIVATE)
 code=PRIVATE/"profile-check.c"
 text=(NATIVE/"rear-startup-private-check.c").read_text().replace("/* CST_SOURCE */",verify.cst_source())
 needle="CHECK(native_rear_compose_startup(set,in)==0);"
 assert text.count(needle)==1
 text=text.replace(needle,'write_private(argv[1],"input",0,0,in,sizeof(*in));\n '+needle)
 code.write_text(text)
 binary=PRIVATE/"profile-check"
 verify.checked(["gcc","-std=gnu11","-Wall","-Wextra","-Werror","-O1","-g",
   "-fsanitize=address,undefined","-fno-omit-frame-pointer","-I"+str(NATIVE),
   "-I"+str(camss),str(code),"-o",str(binary)],PRIVATE)
 output=PRIVATE/"profile-output";output.mkdir()
 run=verify.checked([str(binary),str(output)],PRIVATE,input=wire,
     env=dict(os.environ,ASAN_OPTIONS="detect_leaks=1:halt_on_error=1",UBSAN_OPTIONS="halt_on_error=1"))
 phases,counts,exact=verify.compare(output,ag,bpc,adaptive)
 if not exact:raise RuntimeError("candidate profile private preflight mismatch")
 profile=output/"p0-input-0.bin";digest=hashlib.sha256(profile.read_bytes()).digest()
 identity=camss/"native-rear-generation-identity.h"
 identity.write_text(
  '#define NATIVE_REAR_GENERATION_FIRMWARE "qcom/sp11/rear-generation-20261007-06.bin"\n'
  +f'#define NATIVE_REAR_GENERATION_INPUT_BYTES {profile.stat().st_size}U\n'
  +'static const u8 native_rear_generation_input_sha256[32]={'
  +','.join(str(x) for x in digest)+'};\n')
 # The private digest is omitted from public scalar reports.
 hook="native-rear-generation-hook.inc";ctrl="native-rear-generation-control.inc"
 (camss/hook).write_bytes((HERE/hook).read_bytes())
 (camss/ctrl).write_bytes((HERE/ctrl).read_bytes())
 replace(camss/"camss.h","bool camss_x1e_native_front_profile_trial_allowed(struct camss *camss);",
  "bool camss_x1e_native_front_profile_trial_allowed(struct camss *camss);\n"
  "bool camss_x1e_rear_generation_trial_allowed(struct camss *camss);\n"
  "int camss_x1e_rear_generation_once(struct camss_video *video);")
 replace(camss/"camss-vfe-680.c",'#include "native-rear-prepared-commands.inc"',
  'static bool native_rear_diagnostic_active;\n#include "native-rear-prepared-commands.inc"')
 replace(camss/"camss-vfe-680.c",'#include "native-rear-startup-entry.inc"',
  '#include "native-rear-startup-entry.inc"\n#include "'+hook+'"')
 for name,func in [("camss-vfe-e008k-rear-runner.inc","e008k_rear_runtime_authorization"),
                   ("camss-vfe-e008o-rear-semantic-state.inc","e008o_rear_runtime_authorization")]:
  replace(camss/name,func+"(void)\n{\n\treturn -EOPNOTSUPP;",
   func+"(void)\n{\n\tif (READ_ONCE(native_rear_diagnostic_active))\n\t\treturn 0;\n\treturn -EOPNOTSUPP;")
 # Register-only diagnostics after pipeline power; no pixel/DMA reads.
 observe="native-rear-generation-observe.inc"
 (camss/observe).write_bytes((HERE/observe).read_bytes())
 replace(camss/"camss-e008k-rear-bridge.h",
  "int csid680_native_rear_configure(struct csid_device *csid);",
  "int csid680_native_rear_configure(struct csid_device *csid);\n"
  "void csid680_native_rear_generation_snapshot(struct csid_device *, const char *);")
 replace(camss/"camss-csid-680.c",'#include "native-rear-csid-config.inc"',
  '#include "native-rear-csid-config.inc"\n#include "'+observe+'"')
 replace(camss/"camss-vfe-e008k-rear-runner.inc",
  "\tret = csid680_native_rear_configure(csid);\n\tif (ret)\n\t\tgoto out_pin;",
  '\tcsid680_native_rear_generation_snapshot(csid, "before_transport");\n'
  "\tret = csid680_native_rear_configure(csid);\n\tif (ret)\n\t\tgoto out_pin;\n"
  '\tcsid680_native_rear_generation_snapshot(csid, "after_transport");')
 replace(camss/"camss-vfe-e008k-rear-runner.inc",
  "\tresult->packet_submitted[0] = true;",
  "\tresult->packet_submitted[0] = true;\n"
  '\tcsid680_native_rear_generation_snapshot(csid, "after_packet0");\n')
 replace(camss/"camss-vfe-e008k-rear-runner.inc",
  "\tresult->packet_submitted[1] = true;",
  "\tresult->packet_submitted[1] = true;\n"
  '\tcsid680_native_rear_generation_snapshot(csid, "after_packet1");')
 replace(camss/"camss-vfe-e008k-rear-runner.inc",
  "\t/* First Epoch0 owns slot1 address retarget, then E007y packet2. */",
  '\tcsid680_native_rear_generation_snapshot(csid, "after_sensor_start");\n'
  "\t/* First Epoch0 owns slot1 address retarget, then E007y packet2. */")
 # A deliberate post-stop hold must not repeat CSID/BUS stop.
 replace(camss/"camss-vfe-e008k-rear-runner.inc",
  "\tif (ret)\n\t\tgoto out_pin;\n\n\t/* The two DMA sets have been reclaimed;",
  "\tif (ret == -EINPROGRESS && result->dma_intentionally_pinned &&\n"
  "\t    result->both_frames_complete && result->csid_quiesced &&\n"
  "\t    result->bus_stopped && result->rtcdm_stopped && result->source_stopped) {\n"
  '\t\tcsid680_native_rear_generation_snapshot(csid, "complete_stopped_pinned");\n'
  "\t\t(void)e005y_vfe1_owner_release(&camss->e005y_vfe1_owner,\n"
  "\t\t\tE005Y_VFE1_OWNER_REAR, owner_epoch, false);\n"
  "\t\tkfree(pair);\n\t\treturn ret;\n\t}\n"
  "\tif (ret)\n\t\tgoto out_pin;\n\n\t/* The two DMA sets have been reclaimed;")
 replace(camss/"camss-vfe-e008k-rear-runner.inc",
  "\t\te008k_rear_emergency_pin(camss, vfe, csid, csiphy, req->sensor,",
  '\t\tcsid680_native_rear_generation_snapshot(csid, "before_emergency_stop");\n'
  "\t\te008k_rear_emergency_pin(camss, vfe, csid, csiphy, req->sensor,")
 replace(camss/"camss-vfe-e008k-rear-runner.inc",
  "\t\t/* PM ref + DMA stay pinned intentionally until reboot. */",
  '\t\tcsid680_native_rear_generation_snapshot(csid, "after_emergency_stop");\n'
  "\t\t/* PM ref + DMA stay pinned intentionally until reboot. */")
 # Candidate-only media-bus admission retains front RGGB and adds rear GRBG.
 # No video STREAMON or NV12 claim is made by this generation-only diagnostic.
 replace(camss/"camss-vfe.c",
  "\t{ MEDIA_BUS_FMT_SRGGB10_1X10, 10, V4L2_PIX_FMT_NV12, 1,\n"
  "\t  PER_PLANE_DATA(0, 1, 1, 2, 3, 8) },\n};",
  "\t{ MEDIA_BUS_FMT_SRGGB10_1X10, 10, V4L2_PIX_FMT_NV12, 1,\n"
  "\t  PER_PLANE_DATA(0, 1, 1, 2, 3, 8) },\n"
  "\t{ MEDIA_BUS_FMT_SGRBG10_1X10, 10, V4L2_PIX_FMT_QC10C, 1,\n"
  "\t  PER_PLANE_DATA(0, 1, 1, 1, 1, 10) },\n};")
 # First physical proof must stop BEFORE freeing any output/command DMA.
 replace(camss/"camss-vfe-e008k-rear-runner.inc",
  "\tresult->source_stopped = true;\n\n\tret = e011i_rear_reclaim_after_stop",
  "\tresult->source_stopped = true;\n\n"
  "\tif (READ_ONCE(native_rear_diagnostic_active)) {\n"
  "\t\tresult->dma_intentionally_pinned = true;\n"
  "\t\treturn -EINPROGRESS; /* Proof candidate: hold PM/owner/DMA until reboot. */\n"
  "\t}\n\n\tret = e011i_rear_reclaim_after_stop")
 replace(camss/"camss-vfe-e008k-rear-runner.inc",
  "\tsensor_streaming = true;\n\tret = e008k_rear_subdev_stream(req->sensor, true);",
  '\tdev_info(camss->dev, "NATIVE_REAR_GENERATION_SENSOR_START_ATTEMPT\\n");\n'
  "\tsensor_streaming = true;\n\tret = e008k_rear_subdev_stream(req->sensor, true);")
 replace(camss/"camss-vfe-e008k-rear-runner.inc",
  "out_pin:\n\tif (hardware_touched", "out_pin:\n"
  "\tresult->epoch0_seq = epoch_seq;\n\tresult->done_events = done_cursor;\n"
  "\tif (hardware_touched")
 replace(camss/"camss-video.c","static int video_check_format(struct camss_video *video)",
  '#include "'+ctrl+'"\n\nstatic int video_check_format(struct camss_video *video)')
 replace(camss/"camss-video.c",
  "\t\tif (video->ctrl_handler.error) {",
  "\t\tif (camss_x1e_rear_generation_trial_allowed(video->camss))\n"
  "\t\t\tv4l2_ctrl_new_custom(&video->ctrl_handler, &video_rear_generation_ctrl, NULL);\n"
  "\t\tif (video->ctrl_handler.error) {")
 for p in camss.iterdir():
  if p.suffix in (".c",".h",".inc"):
   for name in re.findall(r'^#include "([^"]+)"',p.read_text(),re.M):
    if not (camss/name).is_file():raise RuntimeError("include closure failed")
 result.update(status="BUILD_REAR_GENERATION_DIAGNOSTIC_IN_PROGRESS",
  candidate_identity="E-NATIVE-REAR-GENERATION-06",candidate_base_commit=HEAD,
  rear_optin_single_use_control_available=True,private_compiler_bound_data_only_input=True,
  post_stop_output_command_DMA_and_PM_pinned_until_reboot=True,
  source_profile_register_words_exact=sum(x["register_instances"] for x in phases),
  source_profile_DMI_matches=counts,source_profile_hosted=json.loads(run.stdout),
  runtime_actions_performed=False,installed=False)
 result["staged_sources"]={}
 for directory in [camss,OUT/"imx681",OUT/"ov13858"]:
  for p in directory.iterdir():
   if p.is_file():
    result["staged_sources"][str(p.relative_to(OUT))]=sha(p)
 (OUT/"source-manifest.json").write_text(json.dumps(result,indent=2)+"\n")
 try:
  for name in ["camss","imx681","ov13858"]:
   with (OUT/(name+"-compile.log")).open("w") as log:
    subprocess.run(["make","-C",str(KSOURCE),"O="+str(KOUTPUT),"M="+str(OUT/name),
     "CONFIG_VIDEO_QCOM_CAMSS=m","W=1","KCFLAGS=-Werror","-j4","modules"],
     stdout=log,stderr=subprocess.STDOUT,check=True)
  modules={}
  for name in ["camss/qcom-camss.ko","imx681/imx681.ko","ov13858/ov13858.ko"]:
   modules[name]={"sha256":sha(OUT/name),"vermagic":subprocess.check_output(
    ["modinfo","-F","vermagic",str(OUT/name)],text=True).strip()}
  result.update(status="PASS_REAR_GENERATION_SOURCE_BUILD_NOT_INSTALLED",modules=modules)
 except Exception:
  result["status"]="FAILED_REAR_GENERATION_SOURCE_BUILD"
  raise
 finally:(OUT/"build-result.json").write_text(json.dumps(result,indent=2)+"\n")
 print(json.dumps({"status":result["status"],"candidate_identity":result["candidate_identity"],
   "profile_register_words_exact":result["source_profile_register_words_exact"],
   "installed":False,"runtime_actions_performed":False,"output_DMA_reclaim_disabled_for_proof":True}))
if __name__=="__main__":main()
