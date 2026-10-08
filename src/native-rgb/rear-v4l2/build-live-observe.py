#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Prepare a fresh disposable generation/stop diagnostic; no install or reboot.
Private compiler-bound semantic firmware and its digest stay on this SP11.
"""
import argparse,hashlib,importlib.util,json,os,re,subprocess
from pathlib import Path
HERE=Path(__file__).resolve().parent.parent/"rear-generation";NATIVE=HERE.parent;ROOT=NATIVE.parents[1]
PROJECT=ROOT.parents[1];OUT=PROJECT/"02-kernel/native-rgb-rear-generation-20261007-34"
PRIVATE=ROOT.parent/"private/NATIVE-REAR-GENERATION-20261007-34"
HEAD="44e52987209122b08605b13e2766951f8a3bf136"
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
 # Every diagnostic CSR must match a named non-address field in exact GPL layout.
 validator=load("native_rear_csr_validator",NATIVE/"rear-windows-ccif/validate-registers.py")
 manifest=json.loads((NATIVE/"rear-windows-ccif/registers.json").read_text())
 csr_count=validator.verify(manifest,validator.source_layout(validator.HEADER.read_text()))
 observer=(HERE/"native-rear-generation-vfe-observe.inc").read_text()
 array=re.search(r"static const unsigned int offsets\[\] = \{(.*?)\};",observer,re.S)
 assert array is not None
 assert [int(x,16) for x in re.findall(r"0x[0-9a-f]+",array[1])]==[int(x,16) for x in manifest["VFE1_offsets"]]

 for path in [OUT,PRIVATE,Path("/var/lib/sp11-camera-native-rear-generation-20261007-26"),
              Path("/boot/sp11-7.1.5-camera-native-rear-generation-20261007-26")]:
  if path.exists():raise RuntimeError("candidate path already exists; audit first")
 build=load("native_rear_build",NATIVE/"build.py")
 result=build.assemble(OUT,nv12_trial=True,front_owner_trial=True,front_queue_trial=True,
   front_meta_trial=True,front_params_trial=True,front_profile_trial=True,front_sof_trial=True,
   front_control_trace_trial=True)
 camss=OUT/"camss";PRIVATE.mkdir(mode=0o700)
 # Read back sensor geometry/VTS in standby before the existing stream write.
 sensor=OUT/"ov13858/ov13858.c"
 before="	return ov13858_write_reg(ov13858, OV13858_REG_MODE_SELECT,\n"
 sensor_text=sensor.read_text()
 start=sensor_text.index("static int ov13858_start_streaming(")
 stop=sensor_text.index("/* Stop streaming */",start)
 assert sensor_text[start:stop].count(before)==1
 pos=sensor_text.index(before,start)
 assert pos<stop
 verify_mode="""	{
		u32 width, height, vts, standby;
		ret = ov13858_read_reg(ov13858, 0x3808, 2, &width);
		if (ret)
			return ret;
		ret = ov13858_read_reg(ov13858, 0x380a, 2, &height);
		if (ret)
			return ret;
		ret = ov13858_read_reg(ov13858, 0x380e, 2, &vts);
		if (ret)
			return ret;
		ret = ov13858_read_reg(ov13858, 0x0100, 1, &standby);
		if (ret)
			return ret;
		if (width != 4064 || height != 2286 || vts != 3214 || standby)
			return -EPROTO;
		dev_info(ov13858->dev, "NATIVE_REAR_GENERATION_SENSOR_MODE width=%u height=%u vts=%u standby=%u\\n",
			 width, height, vts, standby);
	}

"""
 sensor.write_text(sensor_text[:pos]+verify_mode+sensor_text[pos:])

 verify=load("native_rear_current_verify",NATIVE/"verify-rear-startup-private.py")
 wire,ag,bpc,adaptive=verify.producer_wire(SOURCE,LIBBUILD,PRIVATE)
 code=PRIVATE/"profile-check.c"
 text=(NATIVE/"rear-startup-private-check.c").read_text().replace("/* CST_SOURCE */",verify.cst_source())
 needle="CHECK(native_rear_compose_startup(set,in)==0);"
 assert text.count(needle)==1
 text=text.replace(needle,'in->geometry.sensor_width=4064;in->geometry.sensor_height=2286;\n write_private(argv[1],"input",0,0,in,sizeof(*in));\n '+needle)
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
  '#define NATIVE_REAR_GENERATION_FIRMWARE "qcom/sp11/rear-generation-20261007-26.bin"\n'
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
  'static bool native_rear_diagnostic_active;\nstatic bool native_rear_diagnostic_reclaim;\n#include "native-rear-prepared-commands.inc"')
 replace(camss/"camss-vfe-680.c",'#include "native-rear-startup-entry.inc"',
  '#include "native-rear-startup-entry.inc"\n#include "'+hook+'"')
 for name,func in [("camss-vfe-e008k-rear-runner.inc","e008k_rear_runtime_authorization"),
                   ("camss-vfe-e008o-rear-semantic-state.inc","e008o_rear_runtime_authorization")]:
  replace(camss/name,func+"(void)\n{\n\treturn -EOPNOTSUPP;",
   func+"(void)\n{\n\tif (READ_ONCE(native_rear_diagnostic_active))\n\t\treturn 0;\n\treturn -EOPNOTSUPP;")
 # Candidate-only reset selection evidence; source main path has no log.
 replace(camss/"camss-csid-680.c","\tval = native_rear_csid_reset_command(csid);",
  "\tval = native_rear_csid_reset_command(csid);\n"
  "\tif (csid_e004ns_rear_ipp_mode0(csid))\n"
  '\t\tdev_info(csid->camss->dev, "NATIVE_REAR_GENERATION_RESET command=%u exact_rear=1\\n", val);')
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
 # Observe common VFE registers at every existing powered CSI snapshot.
 observe_vfe="native-rear-generation-vfe-observe.inc"
 (camss/observe_vfe).write_bytes((HERE/observe_vfe).read_bytes())
 replace(camss/"camss-vfe-680.c",'#include "native-rear-vfe-config.inc"',
  '#include "native-rear-vfe-config.inc"\n#include "'+observe_vfe+'"')
 runner=camss/"camss-vfe-e008k-rear-runner.inc"
 text=runner.read_text()
 text=re.sub(r'(\t+)csid680_native_rear_generation_snapshot\(csid, ("[^"]+")\);',
  lambda m:m.group(0)+'\n'+m[1]+'native_rear_generation_vfe_snapshot(vfe, '+m[2]+');',text)
 runner.write_text(text)
 replace(runner,"\tret = native_rear_vfe_configure(vfe);\n\tif (ret)\n\t\tgoto out_pin;",
  '\tnative_rear_generation_vfe_snapshot(vfe, "before_vfe_prefix");\n'
  "\tret = native_rear_vfe_configure(vfe);\n\tif (ret)\n\t\tgoto out_pin;\n"
  '\tnative_rear_generation_vfe_snapshot(vfe, "after_vfe_prefix");')
 # Localize the new output violation around the first Epoch and packet2.
 for anchor, phase in [
  ("\tepoch_seq++;\n\tret = e008h_rear_epoch0_retarget_slot1(vfe, pair);", "first_epoch_before_retarget"),
  ("\tresult->slot1_programmed = true;", "after_retarget"),
  ("\tresult->packet_submitted[2] = true;", "after_packet2")]:
  observation="\tcsid680_native_rear_generation_snapshot(csid, \""+phase+"\");\n"+"\tnative_rear_generation_vfe_snapshot(vfe, \""+phase+"\");\n"
  replace(runner,anchor,observation+anchor if phase=="first_epoch_before_retarget" else anchor+"\n"+observation)
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
  "\tif (READ_ONCE(native_rear_diagnostic_active) && !READ_ONCE(native_rear_diagnostic_reclaim)) {\n"
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
 # Observe only safe ownership/size flags, before the corrected all-or-none guard.
 reclaim=camss/"native-rear-reclaim.inc"
 text=reclaim.read_text()
 needle="        return -EBUSY;\n\n    for (s = 0; s < E008H_REAR_SLOTS; s++) {"
 assert text.count(needle)==1
 log=('    dev_info(camss->dev, "NATIVE_REAR_RECLAIM_STATE pair_alloc=%u pair_enabled=%u preload0=%u static0=%u static1=%u prog0=%u prog1=%u size0=%zu size1=%zu\\n",\n'
  '        pair->allocated, pair->enabled, pair->slot0_preloaded_disabled,\n'
  '        pair->dma[0].prepared_disabled, pair->dma[1].prepared_disabled,\n'
  '        pair->programmed[0], pair->programmed[1], pair->dma[0].full.size, pair->dma[1].full.size);\n')
 text=text.replace(needle,"        return -EBUSY;\n\n"+log+"\n    for (s = 0; s < E008H_REAR_SLOTS; s++) {")
 reclaim.write_text(text)
 linear=load("native_rear_linear_overlay",NATIVE/"rear-linear-nv12/apply.py")
 linear_contract=linear.apply(camss,public_dma_admission=True)
 public=load("native_public_FULL_overlay",NATIVE/"rear-v4l2/apply-public-output.py")
 public_contract=public.apply(camss)
 streaming=load("native_public_streaming_overlay",NATIVE/"rear-v4l2/apply-streaming.py")
 streaming_contract=streaming.apply(camss)
 events=load("native_rear_events",NATIVE/"rear-v4l2/apply-events.py")
 event_contract=events.apply(camss)
 live=load("native_rear_live_observation",NATIVE/"rear-v4l2/apply-live-observe.py")
 live_contract=live.apply(camss)
 replace(camss/"native-rear-generation-hook.inc","identity=23 consumed=1","identity=26 consumed=1")

 for p in camss.iterdir():
  if p.suffix in (".c",".h",".inc"):
   for name in re.findall(r'^#include "([^"]+)"',p.read_text(),re.M):
    if not (camss/name).is_file():raise RuntimeError("include closure failed")
 result.update(status="BUILD_REAR_GENERATION_DIAGNOSTIC_IN_PROGRESS",
  candidate_identity="E-NATIVE-REAR-GENERATION-26",candidate_base_commit=HEAD,
  linear_NV12_contract=linear_contract,
  public_FULL_contract=public_contract,public_streaming_contract=streaming_contract,
  public_event_queue_contract=event_contract,
  public_live_observation_contract=live_contract,
  source_validated_non_address_CSR_count=csr_count,
  rear_optin_single_use_control_available=True,private_compiler_bound_data_only_input=True,
  successful_verified_post_stop_release_trial=True,
  exposed_failures_pinned_until_reboot=True,
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
   "installed":False,"runtime_actions_performed":False,"post_stop_reclaim_after_all_completion_and_stop_proofs":True}))
if __name__=="__main__":main()
