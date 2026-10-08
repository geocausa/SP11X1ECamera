#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One rear generation proof, no optical file access, automatic Golden return."""
import json,os,re,runpy,subprocess,time
from pathlib import Path
D=Path("/var/lib/sp11-camera-native-rear-generation-20261007-24")
ROOT=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-driver")
MARKER="sp11_camera_native_rear_generation_20261007_24=1"
def need(condition,message):
 if not condition:raise RuntimeError(message)
def run(args,timeout=25):
 return subprocess.check_output([str(x) for x in args],text=True,stderr=subprocess.STDOUT,timeout=timeout,
  env=dict(os.environ,GIT_CONFIG_COUNT="1",GIT_CONFIG_KEY_0="safe.directory",GIT_CONFIG_VALUE_0=str(ROOT)))
def save(result): (D/"RESULT.json").write_text(json.dumps(result,indent=2)+"\n")
def camera_clock_snapshot(result,phase):
 # Observational CCF rates/counts only; no hardware writes and no imaging data.
 try:
  text=Path("/sys/kernel/debug/clk/clk_summary").read_text()
  (D/("PRIVATE-CLOCKS-"+phase+".txt")).write_text(text)
  rates={}
  for line in text.splitlines():
   fields=line.split()
   if len(fields)>=5 and fields[0].startswith(("cam_cc_","gcc_cam")) and all(x.isdigit() for x in fields[1:5]):
    rates[fields[0]]={"enable_count":int(fields[1]),"prepare_count":int(fields[2]),
                      "protect_count":int(fields[3]),"rate_hz":int(fields[4])}
  result.setdefault("camera_clock_snapshots",{})[phase]=rates
 except Exception as exc:
  result.setdefault("camera_clock_snapshot_errors",{})[phase]=str(exc)

def sensors():
 result={}
 for path in Path("/sys/bus/i2c/devices").glob("*"):
  if (path/"name").exists():
   name=(path/"name").read_text().strip()
   if name in ("imx681","ov13858","sp11-vd55g0"):
    need(name not in result,"duplicate sensor");result[name]=path
 need(set(result)=={"imx681","ov13858","sp11-vd55g0"},"all three sensor devices required")
 return result
def states():
 return {name:{"bound":(p/"driver").is_symlink(),"runtime_status":(p/"power/runtime_status").read_text().strip()}
         for name,p in sensors().items()}
def validate_formats(graph,pads):
 # Read back every configured pad rather than trusting S_FMT.
 for name,pad in pads:
  block=re.search(r"- entity [0-9]+: "+re.escape(name)+r" \(.*?(?=\n- entity|\Z)",graph,re.S)
  need(block is not None,"pad entity absent")
  desc=re.search(r"pad"+str(pad)+r":.*?(?=\n\s*pad[0-9]+:|\Z)",block[0],re.S)
  # Generic VFE source crop is 16-pixel aligned; the public FULL output is independently checked as 4K NV12.
  geometry="4064x2286"
  need(desc is not None and re.search(r"\[(?:stream:0 )?fmt:SGRBG10_1X10/"+geometry+r"(?: |\])",desc[0]) is not None,"pad format drift:"+name+":"+str(pad))
def main():
 os.umask(0o077)
 need(os.geteuid()==0,"root required")
 need(MARKER in Path("/proc/cmdline").read_text().split(),"candidate command line mismatch")
 fd=os.open(D/"CONSUMED",os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 os.write(fd,(Path("/proc/sys/kernel/random/boot_id").read_text()).encode());os.fsync(fd);os.close(fd)
 result={"identity":"E-NATIVE-REAR-GENERATION-24","status":"STARTED",
  "boot_id":Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
  "single_use":True,"pixel_files_saved":0,"DMA_reclaim_authorized":True}
 try:
  expected=(D/"EXPECTED-HEAD").read_text().strip()
  need(run(["git","-C",ROOT,"rev-parse","HEAD"]).strip()==expected,"source HEAD drift")
  need(not run(["git","-C",ROOT,"status","--porcelain"]).strip(),"checkout drift")
  run(["sha256sum","-c",D/"ASSETS.sha256"])
  result["phase"]="before_module_load";save(result)
  run(["bash",ROOT/"tools/camera-overlap-guard.sh","--expect-head",expected,"--expect-origin",expected])
  run(["grub-reboot","sp11-audio-fullio-v19c"])
  loaded=Path("/proc/modules").read_text()
  need(not any(re.search(r"^"+m+r" ",loaded,re.M) for m in ["qcom_camss","imx681","ov13858","sp11_vd55g0"]),"camera modules already loaded")
  for module in ["i2c_qcom_cci","mc","videodev","v4l2_async","v4l2_fwnode","videobuf2_common",
    "videobuf2_memops","videobuf2_v4l2","videobuf2_dma_sg","videobuf2_vmalloc","v4l2_cci"]:
   run(["modprobe",module])
  run(["insmod",D/"modules/qcom-camss.ko","e004j_ir_dphy_windows_parity=1",
       "native_linear_nv12_trial=1","native_front_owner_trial=1","native_front_queue_trial=1",
       "native_front_meta_trial=1","native_front_params_trial=1","native_front_profile_trial=1",
       "native_front_sof_trial=1","native_rear_generation_trial=1"])
  for name in ["ov13858","imx681","sp11-vd55g0"]:run(["insmod",D/("modules/"+name+".ko")])
  for _ in range(400):
   initial=states()
   if all(x["bound"] and x["runtime_status"]=="suspended" for x in initial.values()):break
   time.sleep(0.05)
  need(all(x["bound"] and x["runtime_status"]=="suspended" for x in initial.values()),"sensor initial idle")
  result["initial_sensors"]=initial
  classify=runpy.run_path(str(D/"route-contract.py"))["classify"]
  parse=runpy.run_path(str(D/"discover-unified.py"))["parse_entities"]
  candidates=[]
  for media in Path("/dev").glob("media*"):
   graph=run(["media-ctl","-d",media,"-p"])
   if "ov13858 " in graph and "imx681 " in graph:candidates.append((str(media),graph))
  need(len(candidates)==1,"one complete graph required");media,initial_graph=candidates[0]
  (D/"PRIVATE-INITIAL-GRAPH.txt").write_text(initial_graph)
  phase,_=classify(initial_graph)
  need(phase in ("neutral","rear-only"),"unexpected initial route")
  if phase=="rear-only":
   run(["media-ctl","-d",media,"-l",'"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'])
   run(["media-ctl","-d",media,"-l",'"msm_csiphy1":1 -> "msm_csid0":0 [0]'])
  need(classify(run(["media-ctl","-d",media,"-p"]))[0]=="neutral","neutral route required")
  result["phase"]="rear_PIX_route_configuration";save(result)
  run(["media-ctl","-d",media,"-l",'"msm_csiphy1":1 -> "msm_csid1":0 [1]'])
  run(["media-ctl","-d",media,"-l",'"msm_csid1":4 -> "msm_vfe1_pix":0 [1]'])
  graph=run(["media-ctl","-d",media,"-p"]);entities=parse(graph)
  rear=[name for name in entities if re.fullmatch(r"ov13858 [0-9]+-0010",name)]
  need(len(rear)==1,"unique rear sensor name")
  pads=[(rear[0],0),("msm_csiphy1",0),("msm_csiphy1",1),
        ("msm_csid1",0),("msm_csid1",4),("msm_vfe1_pix",0),("msm_vfe1_pix",1)]
  for name,pad in pads:
   run(["media-ctl","-d",media,"-V",f'"{name}":{pad} [fmt:SGRBG10_1X10/4064x2286 field:none]'])
  graph=run(["media-ctl","-d",media,"-p"])
  (D/"PRIVATE-REAR-PIX-GRAPH.txt").write_text(graph)
  need(classify(graph)[0]=="rear-pix-only","complete rear PIX-only route")
  entities=parse(graph);video=entities["msm_vfe1_video3"]["device"]
  need(video and Path(video).is_char_device(),"PIX control endpoint")
  validate_formats(graph,pads)
  result["phase"]="standard_V4L2_stream";result["route"]="CSIPHY1->CSID1.IPP->VFE1.PIX";save(result)
  camera_clock_snapshot(result,"before_trigger")
  os.sync()
  probe=subprocess.run([str(D/"probe"),video],capture_output=True,text=True,timeout=15)
  (D/"PRIVATE-PROBE-STDOUT.txt").write_text(probe.stdout)
  (D/"PRIVATE-PROBE-STDERR.txt").write_text(probe.stderr)
  camera_clock_snapshot(result,"after_trigger_released")
  result["probe_exit"]=probe.returncode
  if probe.stdout.strip():result["probe"]=json.loads(probe.stdout)
  log=run(["dmesg"]);(D/"PRIVATE-DMESG.txt").write_text(log)
  result["sensor_start_attempts"]=log.count("NATIVE_REAR_GENERATION_SENSOR_START_ATTEMPT")
  result["linear_NV12_readback_passes"]=log.count("NATIVE_REAR_NV12_READBACK_PASS")
  need(result["linear_NV12_readback_passes"]==1,"one cold FULL NV12 readback required")
  result["rear_FULL_storage"]="linear_NV12"
  result["output_width"]=3840;result["output_height"]=2160
  result["output_stride"]=3840;result["output_image_bytes"]=12441600
  result["FULL_output_bits"]=8;result["DS_output_bits"]=10
  result["optical_pixels_read_or_saved"]=False
  records=re.findall(r"NATIVE_REAR_GENERATION_RESULT ([^\n]+)",log)
  need(len(records)==1,"one kernel result required")
  facts={k:v for k,v in re.findall(r"(\w+)=(-?[0-9]+)",records[0])}
  result["kernel_result"]={k:(v if k=="packets" else int(v)) for k,v in facts.items()}
  save(result)
  public_records=re.findall(r"NATIVE_REAR_PUBLIC_V4L2_RESULT ([^\n]+)",log)
  need(len(public_records)==1,"one public V4L2 worker result required")
  public_facts={k:int(v) for k,v in re.findall(r"(\w+)=(-?[0-9]+)",public_records[0])}
  result["public_V4L2_result"]=public_facts
  need(probe.returncode==0,"standard V4L2 capture or teardown failed")
  need(result["probe"].get("completed_frames")==2 and result["probe"].get("STREAMOFF") is True and result["probe"].get("REQBUFS_zero") is True,
       "two DQBUF frames and STREAMOFF/REQBUFS0 required")
  need(public_facts.get("ret")==0 and public_facts.get("frames")==2 and public_facts.get("cpu_pixel_copy")==0,
       "public retained FULL worker proof required")
  required=["composed","once","prepared","slot0","slot1","complete","csid_stop","bus_stop",
            "rtcdm_stop","source_stop","dma_reclaimed","owner_released","arena_released","reboot"]
  need(all(facts.get(k)=="1" for k in required),"incomplete rear generation/stop evidence")
  need(facts.get("ret")=="0" and facts.get("packets")=="1111" and facts.get("epochs")=="2",
       "four packets/two epochs required")
  need(facts.get("dma_pinned")=="0","successful clean stop must release DMA/owner")
  need(result["sensor_start_attempts"]==1,"one sensor start required")
  for _ in range(400):
   final=states()
   if all(x["bound"] and x["runtime_status"]=="suspended" for x in final.values()):break
   time.sleep(0.05)
  result["final_sensors"]=final
  need(all(x["bound"] and x["runtime_status"]=="suspended" for x in final.values()),"all sensors must suspend after clean release")
  result["status"]="PASS_REAR_PUBLIC_V4L2_NV12_TWO_FRAMES_AND_CLEAN_RELEASE"
 except Exception as exc:
  result["status"]="FAIL_REAR_GENERATION_DIAGNOSTIC"
  result["error"]=str(exc)
  try:
   log=run(["dmesg"]);(D/"PRIVATE-DMESG.txt").write_text(log)
   result["sensor_start_attempts"]=log.count("NATIVE_REAR_GENERATION_SENSOR_START_ATTEMPT")
  except Exception:pass
 finally:
  result["phase"]="return_Golden_mandatory";save(result)
 print(json.dumps(result))
 if not result["status"].startswith("PASS"):raise SystemExit(1)
if __name__=="__main__":main()
