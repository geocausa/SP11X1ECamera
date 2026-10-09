#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One rear generation proof, no optical file access, automatic Golden return."""
import json,os,re,runpy,subprocess,time
from pathlib import Path
D=Path("/var/lib/sp11-camera-native-rear-generation-20261007-43")
ROOT=Path("/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-driver")
MARKER="sp11_camera_native_rear_generation_20261007_43=1"
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
def live_observation(log):
 records=re.findall(r"NATIVE_REAR_LIVE_REPLACEMENT ([^\n]+)",log)
 need(len(records)==1,"one live replacement observation required")
 fields=records[0].split()
 need(all(re.fullmatch(r"\w+=-?[0-9]+",x) for x in fields),"malformed live replacement observation")
 pairs=[x.split("=",1) for x in fields]
 keys={"ret","owner","old_complete","next_complete","receipts","enabled","programmed","consumed_addr","published","consumed","cursor","epoch_before","epoch_after","live_release"}
 need(len(pairs)==len(keys) and {k for k,v in pairs}==keys,"live replacement fields drift")
 facts={k:int(v) for k,v in pairs}
 need(facts["live_release"]==0,"observation must not release live DMA")
 observed=(facts["ret"]==0 and
  all(facts[k]==1 for k in ["owner","old_complete","next_complete","receipts"]) and
  all(facts[k]==1023 for k in ["enabled","programmed","consumed_addr"]) and
  0<facts["published"]<2**32-1 and facts["published"]==facts["consumed"]==facts["cursor"] and
  2<=facts["epoch_before"]<2**32-1 and facts["epoch_before"]==facts["epoch_after"])
 need(facts["ret"]!=0 or observed,"successful live observation lacks complete evidence")
 return facts,observed

def live_retirement(log):
 records=re.findall(r"NATIVE_REAR_LIVE_FULL_RETIRE ([^\n]+)",log)
 need(len(records)==1,"one live FULL retirement result required")
 fields=records[0].split()
 need(all(re.fullmatch(r"\w+=-?[0-9]+",x) for x in fields),"malformed live FULL retirement")
 pairs=[x.split("=",1) for x in fields]
 keys={"ret","released","old_valid","next_pinned","aux_pinned","stop_flags","vb2_complete","requeue"}
 need(len(pairs)==len(keys) and {k for k,v in pairs}==keys,"live FULL retirement fields drift")
 facts={k:int(v) for k,v in pairs}
 need(facts["stop_flags"]==facts["vb2_complete"]==facts["requeue"]==0,
      "live retirement must not claim stops, complete VB2 or requeue")
 retired=(facts["ret"]==0 and
          facts["released"]==facts["old_valid"]==facts["next_pinned"]==1 and
          facts["aux_pinned"]==8)
 need(facts["ret"]!=0 or retired,"live FULL retirement lacks complete evidence")
 need(facts["released"]==int(retired),"uncertain live FULL release evidence")
 return facts,retired

def live_aux_retirement(log):
 records=re.findall(r"NATIVE_REAR_LIVE_AUX_RETIRE ([^\n]+)",log)
 need(len(records)==1,"one live auxiliary retirement result required")
 fields=records[0].split()
 need(all(re.fullmatch(r"\w+=-?[0-9]+",x) for x in fields),"malformed live auxiliary retirement")
 pairs=[x.split("=",1) for x in fields]
 keys={"ret","released","old_valid","next_aux_pinned","next_FULL_pinned","stop_flags","vb2_complete","requeue"}
 need(len(pairs)==len(keys) and {k for k,v in pairs}==keys,"live auxiliary retirement fields drift")
 facts={k:int(v) for k,v in pairs}
 need(facts["stop_flags"]==facts["vb2_complete"]==facts["requeue"]==0,
      "auxiliary retirement must not claim stops, complete VB2 or requeue")
 retired=(facts["ret"]==0 and facts["released"]==facts["next_aux_pinned"]==8 and
          facts["old_valid"]==facts["next_FULL_pinned"]==1)
 need(facts["ret"]!=0 or retired,"successful auxiliary retirement lacks complete evidence")
 need(facts["released"]==8*int(retired),"uncertain live auxiliary release evidence")
 return facts,retired


def command_receipts(log):
 records=re.findall(r"NATIVE_REAR_COMMAND_RECEIPTS ([^\n]+)",log)
 need(len(records)==1,"one command receipt observation required")
 fields=records[0].split()
 need(all(re.fullmatch(r"\w+=-?[0-9]+",x) for x in fields),"malformed command receipts")
 pairs=[x.split("=",1) for x in fields]
 expected=dict(ret=0,packets=4,BL_complete=22,first_seq=1,last_seq=22,
               command_arenas_pinned=4,live_release=0,rewrite=0,requeue=0)
 need(len(pairs)==len(expected) and {k for k,v in pairs}==set(expected),"command receipt fields drift")
 facts={k:int(v) for k,v in pairs}
 need(facts["live_release"]==facts["rewrite"]==facts["requeue"]==0,
      "command observation must retain allocations and forbid live reuse")
 observed=facts==expected
 need(facts["ret"]!=0 or observed,"successful command observation lacks exact receipts")
 return facts,observed

def command_retirement(log,owner_epoch=1):
 need(owner_epoch in (1,2,3),"expected exact session owner")
 records=re.findall(r"NATIVE_REAR_COMMAND_RETIRE ([^\n]+)",log)
 need(len(records)==1,"one live command retirement record required")
 fields=records[0].split()
 need(all(re.fullmatch(r"\w+=-?[0-9]+",x) for x in fields),"malformed command retirement")
 pairs=[x.split("=",1) for x in fields]
 expected=dict(ret=0,released=4,retired_valid=1,command_arenas_pinned=0,owner=owner_epoch,
               BL_complete=22,stop_flags=0,vb2_complete=0,requeue=0)
 need(len(pairs)==len(expected) and {k for k,v in pairs}==set(expected),"command retirement fields drift")
 facts={k:int(v) for k,v in pairs}
 need(facts["stop_flags"]==facts["vb2_complete"]==facts["requeue"]==0,"live retirement stop/delivery/requeue forbidden")
 retired=facts==expected
 need(facts["ret"]!=0 or retired,"successful live command retirement lacks exact evidence")
 need(retired or (facts["released"]==0 and facts["retired_valid"]==0 and facts["command_arenas_pinned"]==4 and facts["BL_complete"]==0 and facts["owner"]==owner_epoch),"uncertain partial command release")
 return facts,retired

def rear_queue(log):
 records=re.findall(r"NATIVE_REAR_QUEUE ([^\n]+)",log)
 need(len(records)==1,"one rolling queue result required")
 fields=records[0].split()
 need(all(re.fullmatch(r"\w+=-?[0-9]+",x) for x in fields),"malformed rolling queue")
 pairs=[x.split("=",1) for x in fields]
 keys={"ret","live_completed","handoffs","output_updates","cursor","starved","command_resubmissions","cpu_pixel_copy"}
 need(len(pairs)==len(keys) and {k for k,v in pairs}==keys,"rolling queue fields drift")
 facts={k:int(v) for k,v in pairs}
 need(all(0<=facts[k]<2**32-1 for k in keys-{"ret"}),"rolling queue range")
 proven=(facts["ret"]==0 and facts["live_completed"]>=80 and facts["handoffs"]>=79 and facts["output_updates"]==facts["handoffs"] and
         facts["cursor"]>16 and facts["starved"]==facts["command_resubmissions"]==facts["cpu_pixel_copy"]==0)
 need(facts["ret"]!=0 or proven,"successful rolling queue lacks 80 live completions")
 return facts,proven


def rear_cadence(log,queue):
 records=re.findall(r"NATIVE_REAR_CADENCE ([^\n]+)",log)
 need(len(records)==1,"one queue cadence record required")
 fields=records[0].split()
 need(all(re.fullmatch(r"\w+=[0-9]+",x) for x in fields),"malformed cadence")
 pairs=[x.split("=",1) for x in fields]
 stages=["drain_ns","pending_ns","prepare_ns","observe_ns","epoch_wait_ns","program_ns","collect_ns","retire_ns"]
 keys=set(stages)|{"elapsed_ns","epoch_delta","handoffs","policy_changes","pixel_bytes_read"}
 need(len(pairs)==len(keys) and {k for k,v in pairs}==keys,"cadence fields drift")
 f={k:int(v) for k,v in pairs}
 need(0<f["elapsed_ns"]<75_000_000_000,"cadence elapsed range")
 need(f["handoffs"]==queue["handoffs"] and 79<=f["handoffs"]<2**32-1,"cadence handoffs")
 need(f["handoffs"]-1<=f["epoch_delta"]<2**32-1,"cadence epoch scope")
 need(f["policy_changes"]==1 and f["pixel_bytes_read"]==f["epoch_wait_ns"]==0,"exact epoch-wait removal policy required")
 need(all(0<=f[k]<=f["elapsed_ns"] for k in stages),"stage elapsed range")
 need(sum(f[k] for k in stages)<=f["elapsed_ns"],"overlapping or corrupted stage accounting")
 return f


def rear_dma_timing(log,cadence):
 records=re.findall(r"NATIVE_REAR_DMA_TIMING ([^\n]+)",log)
 need(len(records)==1,"one DMA timing record required")
 fields=records[0].split()
 need(all(re.fullmatch(r"\w+=[0-9]+",x) for x in fields),"malformed DMA timing")
 pairs=[x.split("=",1) for x in fields]
 durations=["full_get_ns","aux_alloc_ns","full_put_ns","aux_zero_ns","aux_free_ns"]
 calls=["full_get_calls","aux_alloc_calls","full_put_calls","aux_free_calls"]
 need(len(pairs)==11 and {k for k,v in pairs}==set(durations+calls+["scope","pixel_bytes_read"]),"DMA timing fields drift")
 f={k:int(v) for k,v in pairs}
 n=cadence["handoffs"]
 need(f["scope"]==1 and f["pixel_bytes_read"]==0,"queue-only diagnostic scope")
 need(f["full_get_calls"]==f["full_put_calls"]==n and f["aux_alloc_calls"]==f["aux_free_calls"]==8*n,"exact successful handoff operation counts")
 need(all(0<f[k]<=cadence["elapsed_ns"] for k in durations),"DMA timing range")
 need(f["full_get_ns"]+f["aux_alloc_ns"]<=cadence["prepare_ns"],"allocation timing coverage")
 need(f["full_put_ns"]+f["aux_zero_ns"]+f["aux_free_ns"]<=cadence["retire_ns"],"retirement timing coverage")
 return f

def validate_probe_cadence(p):
 import math
 need(p.get("callback_intervals")==79 and p.get("timestamp_kind")=="driver_completion_not_sensor_SOF","exact callback interval scope")
 for k in ["callback_span_seconds","callback_interval_rate_fps","start_to_first_callback_seconds","last_callback_to_release_seconds","stop_release_seconds"]:
  need(type(p.get(k)) in (float,int) and math.isfinite(p[k]) and 0<p[k]<75,"finite bounded application timing")
 need(abs(p["callback_interval_rate_fps"]*p["callback_span_seconds"]-79)<0.002,"interval rate consistency")
 for k in ["completion_timestamp_span_ns","completion_gap_min_ns","completion_gap_max_ns"]:
  need(type(p.get(k)) is int and 0<p[k]<75_000_000_000,"bounded completion timing")
 need(p["completion_gap_min_ns"]*79<=p["completion_timestamp_span_ns"]<=p["completion_gap_max_ns"]*79,"completion gap bounds")
 need(p["stop_release_seconds"]<=p["last_callback_to_release_seconds"],"stop within final release")
 need(abs(p["start_to_first_callback_seconds"]+p["callback_span_seconds"]+p["last_callback_to_release_seconds"]-p["elapsed_seconds"])<0.002,"application timing coverage")

def session_log(log,session):
 need(session in (1,2,3),"session range")
 pattern=r"NATIVE_REAR_GENERATION_ATTEMPT identity=43 consumed=1 session=([0-9]+)(?:\n|\Z)"
 markers=list(re.finditer(pattern,log))
 current=[m for m in markers if int(m[1])==session]
 need(len(current)==1,"exact unique current session marker required")
 tail=log[current[0].start():]
 need(tail.count("NATIVE_REAR_GENERATION_ATTEMPT")==1,"later or malformed session start")
 # Earlier ring history may rotate. Current marker and all mandatory typed
 # records must still survive; no missing current evidence is accepted.
 return tail

def queue_snapshot(log):
 records=re.findall(r"NATIVE_REAR_QUEUE_SNAPSHOT ([^\n]+)",log)
 need(len(records)==1,"one bounded snapshot result required")
 fields=records[0].split()
 need(all(re.fullmatch(r"\w+=-?[0-9]+",x) for x in fields),"malformed snapshot result")
 pairs=[x.split("=",1) for x in fields]
 expected=dict(attempts_limit=256,address_reprograms=0,command_resubmissions=0,irq_disabled=0)
 need(len(pairs)==5 and {k for k,v in pairs}==set(expected)|{"retries"},"snapshot fields drift")
 facts={k:int(v) for k,v in pairs}
 need(all(facts[k]==v for k,v in expected.items()) and 0<=facts["retries"]<2**32-1,"snapshot safety facts")
 return facts

def validate_idle_clocks(snapshot):
 expected={"cam_cc_ife_1_clk":594000000,"cam_cc_ife_1_clk_src":594000000,
           "cam_cc_csid_clk":300000000,"cam_cc_csid_clk_src":300000000,
           "cam_cc_csiphy1_clk":300000000}
 for name,rate in expected.items():
  clock=snapshot.get(name,{})
  need(clock.get("enable_count")==0 and clock.get("prepare_count")==0 and clock.get("rate_hz")==rate,
       "released camera clocks required:"+name)

def session_gate(log,session):
 records=re.findall(r"NATIVE_REAR_SESSION_GATE ([^\n]+)",log)
 need(len(records)==1,"one session gate record required")
 fields=records[0].split()
 need(all(re.fullmatch(r"\w+=-?[0-9]+",x) for x in fields),"malformed session gate")
 pairs=[x.split("=",1) for x in fields]
 expected=dict(attempted=session,completed=session,active=0,poisoned=0,owner=session,
               inner_attempted=session,inner_completed=session,inner_poisoned=0)
 need(len(pairs)==len(expected) and {k for k,v in pairs}==set(expected),"session gate fields drift")
 facts={k:int(v) for k,v in pairs}
 # Exact owner admission also catches stale session state.
 need(facts==expected,"session gate failed to finish cleanly")
 return facts

def main():
 os.umask(0o077)
 need(os.geteuid()==0,"root required")
 need(MARKER in Path("/proc/cmdline").read_text().split(),"candidate command line mismatch")
 fd=os.open(D/"CONSUMED",os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
 os.write(fd,(Path("/proc/sys/kernel/random/boot_id").read_text()).encode());os.fsync(fd);os.close(fd)
 result={"identity":"E-NATIVE-REAR-GENERATION-40","status":"STARTED",
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
  environment=dict(os.environ,LD_LIBRARY_PATH=str(D/"lib"),
                   LIBCAMERA_PIPELINES_MATCH_LIST="camss-x1e-rear",
                   LIBCAMERA_LOG_LEVELS="CAMSSX1ERear:DEBUG,V4L2:INFO,Camera:INFO")
  previous_owner=0
  result["sessions"]=[]
  for session in range(1,4):
   result["phase"]="same_boot_session_"+str(session)
   need(Path("/proc/sys/kernel/random/boot_id").read_text().strip()==result["boot_id"],"boot drift")
   save(result)
   probe=subprocess.run([str(D/"capture")],capture_output=True,text=True,timeout=25,env=environment)
   result["consumer"]="real_public_libcamera_camera_manager_and_requests"
   result["application_DMA_BUF_import"]=True
   result["IPA_implemented"]=False
   result["continuous_capture_proven"]=False
   result["live_mapping_retirement_proven"]=False
   (D/("PRIVATE-PROBE-STDOUT-"+str(session)+".txt")).write_text(probe.stdout)
   (D/("PRIVATE-PROBE-STDERR-"+str(session)+".txt")).write_text(probe.stderr)
   camera_clock_snapshot(result,"after_session_"+str(session))
   result["probe_exit"]=probe.returncode
   if probe.stdout.strip():result["probe"]=json.loads(probe.stdout)
   full_log=run(["dmesg"]);(D/"PRIVATE-DMESG.txt").write_text(full_log)
   log=session_log(full_log,session)
   need(not re.search(r"(?im)^.*(?:BUG:|WARNING:|Oops:|Call trace:|kernel panic|SError|\bSMMU\b.*\bfault\b|\bIOMMU\b.*\bfault\b).*$",log),
        "kernel hazard blocks further sessions")

   observation,observed=live_observation(log)
   result["live_replacement_observation"]=observation
   result["live_replacement_observed"]=observed
   retirement,retired=live_retirement(log)
   result["live_FULL_retirement"]=retirement
   result["live_public_FULL_retirement_proven"]=retired
   auxiliary,aux_retired=live_aux_retirement(log)
   result["live_auxiliary_retirement"]=auxiliary
   result["live_auxiliary_output_retirement_proven"]=aux_retired
   result["live_all_output_generation_retirement_proven"]=retired and aux_retired
   result["live_command_recycling_proven"]=False
   command_facts,command_observed=command_receipts(log)
   result["command_receipts"]=command_facts
   result["exact_serialized_command_receipts_proven"]=command_observed
   command_retire_facts,commands_retired=command_retirement(log,session)
   result["live_command_retirement"]=command_retire_facts
   result["live_command_arena_retirement_proven"]=commands_retired
   queue_facts,queue_proven=rear_queue(log)
   result["rolling_queue"]=queue_facts
   result["cadence"]=rear_cadence(log,queue_facts)
   result["DMA_timing"]=rear_dma_timing(log,result["cadence"])
   result["queue_snapshot"]=queue_snapshot(log)
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
   need(result["probe"].get("status")=="PASS_LIBCAMERA_REAR_CONTINUOUS_REQUEST_REUSE" and
        result["probe"].get("completed_frames")==80 and result["probe"].get("application_buffers")==4 and result["probe"].get("reused_requests") is True and result["probe"].get("stop_and_release") is True and
        result["probe"].get("SensorTimestamp_present") is False and result["probe"].get("pixel_bytes_read")==0,
        "80 reused libcamera requests and stop/release required")
   validate_probe_cadence(result["probe"])
   need("Rear STREAMOFF failed" not in probe.stderr and "Rear buffer release failed" not in probe.stderr,
        "libcamera pipeline teardown error")
   graph=run(["media-ctl","-d",media,"-p"])
   (D/("PRIVATE-GRAPH-AFTER-LIBCAMERA-"+str(session)+".txt")).write_text(graph)
   need(classify(graph)[0]=="neutral","libcamera release restores neutral links")
   need(public_facts.get("ret")==0 and public_facts.get("frames",0)>=80 and public_facts.get("frames")==queue_facts["live_completed"] and public_facts.get("cpu_pixel_copy")==0,
        "public retained FULL worker proof required")
   required=["composed","once","prepared","slot0","slot1","complete","csid_stop","bus_stop",
             "rtcdm_stop","source_stop","dma_reclaimed","owner_released","arena_released","reboot"]
   need(all(facts.get(k)=="1" for k in required),"incomplete rear generation/stop evidence")
   need(facts.get("ret")=="0" and facts.get("packets")=="1111" and 80<=int(facts.get("epochs","0"))<2**32-1,
        "four startup packets and 80 or more epochs required")
   need(facts.get("dma_pinned")=="0","successful clean stop must release DMA/owner")
   need(result["sensor_start_attempts"]==1,"one sensor start required")
   for _ in range(400):
    final=states()
    if all(x["bound"] and x["runtime_status"]=="suspended" for x in final.values()):break
    time.sleep(0.05)
   result["final_sensors"]=final
   need(all(x["bound"] and x["runtime_status"]=="suspended" for x in final.values()),"all sensors must suspend after clean release")
   idle_phase="after_session_idle_"+str(session)
   camera_clock_snapshot(result,idle_phase)
   validate_idle_clocks(result.get("camera_clock_snapshots",{}).get(idle_phase,{}))
   need(observed and retired and aux_retired and command_observed and commands_retired and queue_proven,"continuous queue and live retirement proof required")
   result["continuous_capture_proven"]=True
   gate=session_gate(log,session)
   need(result["kernel_result"]["owner"]==gate["owner"]>previous_owner,"fresh increasing owner required")
   previous_owner=gate["owner"]
   result["session_gate"]=gate
   result["sessions"].append({k:v for k,v in result.items() if k not in ("sessions","camera_clock_snapshots")})
   save(result)
  need(len(result["sessions"])==3,"three complete sessions required")
  result["sensor_start_attempts"]=sum(x["sensor_start_attempts"] for x in result["sessions"])
  result["completed_application_requests"]=sum(x["probe"]["completed_frames"] for x in result["sessions"])
  need(result["completed_application_requests"]==240,"240 real requests required")
  result["same_boot_restart_proven"]=True
  result["status"]="PASS_REAR_THREE_SAME_BOOT_LIBCAMERA_SESSIONS_AND_CLEAN_RELEASE"

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
