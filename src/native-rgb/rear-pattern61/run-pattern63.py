#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One-shot rear pattern calibration capture, run by systemd in the candidate boot.

Reuses the qualified rear60 kernel/modules/route setup. Disables nothing on
Golden. ExecStopPost (return-golden.sh) always reboots back to Golden.
"""
import json,os,re,runpy,subprocess,time
from pathlib import Path
D=Path("/var/lib/sp11-camera-rear-pattern-63")
MARKER="sp11_camera_rear_pattern_63=1"
GOLDEN="sp11-audio-fullio-v19c"
H=runpy.run_path(str(D/"helpers60.py"))
def run(args,timeout=25):
 return subprocess.check_output([str(x) for x in args],text=True,stderr=subprocess.STDOUT,timeout=timeout)
def save(r):
 (D/"RESULT.json").write_text(json.dumps(r,indent=1)+"\n");os.sync()
def need(ok,msg):
 if not ok:raise RuntimeError(msg)
def main():
 os.umask(0o077)
 need(MARKER in Path("/proc/cmdline").read_text().split(),"candidate command line mismatch")
 fd=os.open(D/"CONSUMED",os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 os.write(fd,Path("/proc/sys/kernel/random/boot_id").read_bytes());os.close(fd)
 r={"identity":"E-REAR-PATTERN-63","status":"STARTED","boot_id":Path("/proc/sys/kernel/random/boot_id").read_text().strip(),"started_utc":time.time()}
 try:
  run(["grub-reboot",GOLDEN])
  r["phase"]="modules";save(r)
  loaded=Path("/proc/modules").read_text()
  need(not any(re.search(r"^"+m+r" ",loaded,re.M) for m in ["qcom_camss","imx681","ov13858","sp11_vd55g0"]),"camera modules already loaded")
  for module in ["i2c_qcom_cci","mc","videodev","v4l2_async","v4l2_fwnode","videobuf2_common","videobuf2_memops","videobuf2_v4l2","videobuf2_dma_sg","videobuf2_vmalloc","v4l2_cci"]:
   run(["modprobe",module])
  run(["insmod",D/"modules/qcom-camss.ko","e004j_ir_dphy_windows_parity=1","native_linear_nv12_trial=1","native_front_owner_trial=1","native_front_queue_trial=1","native_front_meta_trial=1","native_front_params_trial=1","native_front_profile_trial=1","native_front_sof_trial=1","native_rear_generation_trial=1"])
  for name in ["ov13858","imx681","sp11-vd55g0"]:run(["insmod",D/("modules/"+name+".ko")])
  for _ in range(400):
   initial=H["states"]()
   if all(x["bound"] and x["runtime_status"]=="suspended" for x in initial.values()):break
   time.sleep(0.05)
  need(all(x["bound"] and x["runtime_status"]=="suspended" for x in initial.values()),"sensor initial idle")
  classify=runpy.run_path(str(D/"route-contract.py"))["classify"]
  parse=runpy.run_path(str(D/"discover-unified.py"))["parse_entities"]
  candidates=[]
  for media in Path("/dev").glob("media*"):
   graph=run(["media-ctl","-d",media,"-p"])
   if "ov13858 " in graph and "imx681 " in graph:candidates.append((str(media),graph))
  need(len(candidates)==1,"one complete graph required");media,graph=candidates[0]
  phase,_=classify(graph)
  need(phase in ("neutral","rear-only"),"unexpected initial route "+phase)
  if phase=="rear-only":
   run(["media-ctl","-d",media,"-l",'"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'])
   run(["media-ctl","-d",media,"-l",'"msm_csiphy1":1 -> "msm_csid0":0 [0]'])
  r["phase"]="route";save(r)
  run(["media-ctl","-d",media,"-l",'"msm_csiphy1":1 -> "msm_csid1":0 [1]'])
  run(["media-ctl","-d",media,"-l",'"msm_csid1":4 -> "msm_vfe1_pix":0 [1]'])
  entities=parse(run(["media-ctl","-d",media,"-p"]))
  rear=[n for n in entities if re.fullmatch(r"ov13858 [0-9]+-0010",n)]
  need(len(rear)==1,"unique rear sensor")
  pads=[(rear[0],0),("msm_csiphy1",0),("msm_csiphy1",1),("msm_csid1",0),("msm_csid1",4),("msm_vfe1_pix",0),("msm_vfe1_pix",1)]
  for name,pad in pads:
   run(["media-ctl","-d",media,"-V",f'"{name}":{pad} [fmt:SGRBG10_1X10/4064x2286 field:none]'])
  graph=run(["media-ctl","-d",media,"-p"]);(D/"PRIVATE-GRAPH.txt").write_text(graph)
  need(classify(graph)[0]=="rear-pix-only","rear PIX route")
  H["validate_formats"](graph,pads)
  r["phase"]="capture";save(r)
  out=D/"private-pattern";out.mkdir(mode=0o700)
  stats=Path("/var/lib/sp11-camera-rear-pattern-61/private-statistics/session-2");stats.mkdir(mode=0o700)  # lib19 accepts only the run-61 statistics root
  env=dict(os.environ,LD_LIBRARY_PATH=str(D/"lib"),LIBCAMERA_IPA_MODULE_PATH=str(D/"lib/ipa"),LIBCAMERA_IPA_PROXY_PATH=str(D/"lib/proxy"),
           LIBCAMERA_PIPELINES_MATCH_LIST="camss-x1e-rear",LIBCAMERA_LOG_LEVELS="CAMSSX1ERear:DEBUG,V4L2:INFO,Camera:INFO",
           SP11_REAR_STATISTICS_DIR=str(stats),SP11_PATTERN_DIR=str(out),SP11_PATTERN_FRAMES_PER_PHASE="900")
  p=subprocess.run([str(D/"capture-pattern")],capture_output=True,text=True,timeout=480,env=env)
  (D/"PRIVATE-CAPTURE-STDOUT.txt").write_text(p.stdout);(D/"PRIVATE-CAPTURE-STDERR.txt").write_text(p.stderr)
  r["capture_exit"]=p.returncode
  if p.stdout.strip():r["capture"]=json.loads(p.stdout.strip().splitlines()[-1])
  r["meter_lines"]=len(re.findall("NATIVE_REAR_METER",p.stderr))
  need(p.returncode==0,"capture failed")
  r["status"]="PASS_REAR_PATTERN_63"
 except Exception as exc:
  r["status"]="FAIL_REAR_PATTERN_63";r["error"]=str(exc)
 finally:
  try:(D/"PRIVATE-DMESG.txt").write_text(run(["dmesg"]))
  except Exception:pass
  r["finished_utc"]=time.time();r["phase"]="return_Golden";save(r)
 print(json.dumps({k:r.get(k) for k in ("status","error","capture_exit")}))
 if not r["status"].startswith("PASS"):raise SystemExit(1)
if __name__=="__main__":main()
