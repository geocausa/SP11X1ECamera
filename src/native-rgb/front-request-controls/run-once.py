#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One-use development probe, under its dedicated boot. Optical pixels remain private on SP11."""
import fcntl
import datetime
import json
import os
import hashlib
import re
from pathlib import Path
import runpy
import subprocess
import time

D = Path("/var/lib/sp11-camera-native-request-controls-20261007-01")
TOKEN = "sp11_camera_native_request_controls_20261007_01=1"
ENTRY = "sp11_entry=7.1.5-sp11-camera-native-request-controls-20261007-01"
def need(value, reason):
    if not value:
        raise RuntimeError(reason)
def run(args, timeout=10):
    process = subprocess.run(args, text=True, capture_output=True, timeout=timeout)
    if process.returncode:
        raise RuntimeError(str(args[0]) + " failed: " + process.stderr[-2000:])
    return process.stdout

def sensors():
    found = {}
    for path in Path("/sys/bus/i2c/devices").glob("*-*"):
        compatible = path / "of_node/compatible"
        if not compatible.exists():
            continue
        value = compatible.read_bytes().rstrip(b"\0")
        if value in (b"sony,imx681", b"ovti,ov13858", b"microsoft,sp11-vd55g0"):
            need(value not in found, "duplicate sensor")
            found[value] = path
    need(len(found) == 3, "sensor topology")
    return found

def idle():
    for path in sensors().values():
        need((path / "power/runtime_status").read_text().strip() == "suspended",
             "sensor not suspended: " + path.name)
    # No camera FDs may remain before graph writes. The exclusive probe is
    # single-process; its capture child is synchronously reaped before this.
    for process in Path("/proc").glob("[0-9]*"):
        try:
            for descriptor in (process / "fd").iterdir():
                target = os.readlink(descriptor)
                need(not target.startswith(("/dev/video", "/dev/media", "/dev/v4l-subdev")),
                     "camera descriptor remains")
        except (FileNotFoundError, ProcessLookupError):
            continue

def main():
    need(os.geteuid() == 0, "root-only diagnostic")
    command = Path("/proc/cmdline").read_text().split()
    need(TOKEN in command and ENTRY in command, "dedicated boot required")
    need(run(["uname", "-r"]).strip() == "7.1.5-sp11-render-parity-v4+", "kernel")
    need((D / "ARMED").is_file(), "explicit one-use arm required")
    with (D / "ATTEMPT-CONSUMED").open("x") as consumed:
        consumed.write(Path("/proc/sys/kernel/random/boot_id").read_text())
    lock = (D / "camera.lock").open("w")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    result = {"status": "FAILED_NATIVE_NV12_PROBE", "hardware_streams_completed": 0,
              "pixels_private_on_sp11": True, "retry": False}
    result["comparison_session"] = "front-room-light-20261007-01"
    result["comparison_role"] = "standard-request-control-qualification"
    result["environment"] = {"room_lights_on_user_report_utc":"2026-10-07T18:26:29Z",
        "user_asked_keep_lighting_position_unchanged":True,
        "illuminance_measured":False,"scene_continuity_independently_verified":False,
        "outdoor_rain_cloud_user_report_date":"2026-10-07"}
    try:
        for unit in ("grub-initrd-fallback.service", "grub2-common.service"):
            state = {}
            for key in ("Result", "ConditionResult", "ExecMainStatus",
                        "ExecMainStartTimestampMonotonic", "ExecMainExitTimestampMonotonic"):
                state[key] = run(["systemctl", "show", unit, "-p", key, "--value"]).strip()
            need(state["Result"] == "success" and state["ConditionResult"] == "yes" and
                 state["ExecMainStatus"] == "0" and
                 int(state["ExecMainStartTimestampMonotonic"]) > 0 and
                 int(state["ExecMainExitTimestampMonotonic"]) >=
                 int(state["ExecMainStartTimestampMonotonic"]), "boot writer did not execute")
            result[unit] = state
        need(int(result["grub-initrd-fallback.service"]["ExecMainExitTimestampMonotonic"]) <=
             int(result["grub2-common.service"]["ExecMainStartTimestampMonotonic"]), "writer order")
        environment = run(["grub-editenv", "/boot/grub/grubenv", "list"]).splitlines()
        need("saved_entry=sp11-audio-fullio-v19c" in environment and
             not any(line.startswith("next_entry=") and line != "next_entry=" for line in environment),
             "Golden boot protection")
        run(["sha256sum", "-c", str(D / "ASSETS.sha256")])
        for name in ("qcom_camss", "imx681", "ov13858", "sp11_vd55g0", "v4l2loopback"):
            need(not (Path("/sys/module") / name).exists(), "camera module already loaded")
        need(not list(Path("/dev").glob("video*")) and
             not list(Path("/dev").glob("media*")), "camera node already exists")
        for module in ("i2c_qcom_cci", "mc", "videodev", "v4l2_async", "v4l2_fwnode",
                       "videobuf2_common", "videobuf2_memops", "videobuf2_v4l2",
                       "videobuf2_dma_sg", "videobuf2_vmalloc", "v4l2_cci"):
            run(["modprobe", module])
        run(["insmod", str(D / "modules/qcom-camss.ko"), "e004j_ir_dphy_windows_parity=1",
             "native_linear_nv12_trial=1", "native_front_owner_trial=1", "native_front_queue_trial=1", "native_front_meta_trial=1", "native_front_params_trial=1", "native_front_profile_trial=1", "native_front_sof_trial=1"])
        for name in ("ov13858", "imx681", "sp11-vd55g0"):
            run(["insmod", str(D / ("modules/" + name + ".ko"))] +
                (["native_control_timing_trace=1", "native_control_timing_readback=1"] if name == "imx681" else []))
        result["phase"] = "sensor_bind_and_initial_suspend"
        for attempt in range(400):
            found = sensors()
            if all((path / "driver").is_symlink() and
                   (path / "power/runtime_status").read_text().strip() == "suspended"
                   for path in found.values()):
                break
            time.sleep(0.05)
        result["initial_sensor_states"] = {path.name: {"bound": (path / "driver").is_symlink(),
            "runtime_status": (path / "power/runtime_status").read_text().strip()} for path in sensors().values()}
        idle()
        result["phase"] = "discover_and_select_front_pix_route"
        discover = runpy.run_path(str(D / "discover-unified.py"))["discover"]
        classify = runpy.run_path(str(D / "route-contract.py"))["classify"]
        candidates = []
        for path in sorted(Path("/dev").glob("media*")):
            graph = run(["media-ctl", "-d", str(path), "-p"])
            if "imx681 " in graph and "ov13858 " in graph:
                candidates.append((str(path), graph))
        need(len(candidates) == 1, "one complete camera graph required")
        media, initial = candidates[0]
        discovery = discover(initial, media)
        entities = runpy.run_path(str(D / "discover-unified.py"))["parse_entities"](initial)
        need("msm_vfe1_stats" in entities and entities["msm_vfe1_stats"]["device"],
             "frame metadata node absent")
        metadata = entities["msm_vfe1_stats"]["device"]
        phase, _ = classify(initial)
        need(phase in ("neutral", "rear-only"), "unexpected initial route")
        if phase == "rear-only":
            run(["media-ctl", "-d", media, "-l", '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'])
            run(["media-ctl", "-d", media, "-l", '"msm_csiphy1":1 -> "msm_csid0":0 [0]'])
        need(classify(run(["media-ctl", "-d", media, "-p"]))[0] == "neutral", "neutral")
        idle()
        result["phase"] = "standard_libcamera_public_requests"
        os.umask(0o077)
        environment = os.environ.copy()
        environment.pop("LIBCAMERA_CAMSS_X1E_CONTROL_TIMING", None)
        environment.update(LD_LIBRARY_PATH=str(D / "lib"),
            LIBCAMERA_PIPELINES_MATCH_LIST="camss-x1e", LIBCAMERA_LOG_LEVELS="*:DEBUG",
            LIBCAMERA_IPA_MODULE_PATH=str(D / "ipa"),
            LIBCAMERA_IPA_PROXY_PATH=str(D / "proxy"), LIBCAMERA_IPA_FORCE_ISOLATION="1")
        result["capture_started_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            process = subprocess.run([str(D / "cam"), "--camera=sp11-front-imx681",
                "--capture=120", "--stream=width=2560,height=1440,pixelformat=NV12,role=viewfinder",
                "--strict-formats", "--metadata", "--script=" + str(D / "controls.yaml"),
                "--file=" + str(D / "frame-#.bin")], capture_output=True, text=True,
                timeout=30, env=environment)
        except subprocess.TimeoutExpired as exc:
            for stream,value in [("STDOUT",exc.stdout),("STDERR",exc.stderr)]:
                if isinstance(value,bytes): value=value.decode(errors="replace")
                (D / ("PRIVATE-CAM-"+stream+".txt")).write_text(value or "")
            result["cam_timed_out"] = True
            raise RuntimeError("standard cam request capture timed out") from exc
        (D / "PRIVATE-CAM-STDOUT.txt").write_text(process.stdout)
        (D / "PRIVATE-CAM-STDERR.txt").write_text(process.stderr)
        result["capture_completed_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result["cam_exit_code"] = process.returncode
        need(process.returncode == 0, "standard cam public request capture failed")
        result["hardware_streams_completed"] = 1
        need("CAMSS_X1E_CONTROL_TIMING" not in process.stderr, "diagnostic control path forbidden")
        pairs = [tuple(map(int,p)) for p in re.findall(
            r"CAMSS_X1E_PAIR request=(\d+) frame=(\d+) source=(\d+) stream=(\d+) timestamp_match=1",process.stderr)]
        need(len(pairs)==120 and [p[0] for p in pairs]==list(range(120)) and
             all(p[2]==p[1]+1 for p in pairs) and len({p[3] for p in pairs})==1 and
             all(b[1]>a[1] for a,b in zip(pairs,pairs[1:])), "request/frame/statistics pairing")
        captures = [tuple(map(int,p)) for p in re.findall(
            r"(?m)^(\d+)\.(\d{6}) \([^)]+ fps\).*seq: (\d+) bytesused: (\d+)/(\d+)$",process.stdout)]
        need(len(captures)==120 and [p[2] for p in captures]==[p[1] for p in pairs] and
             all(p[3:]==(3686400,1843200) for p in captures), "120 real NV12 frame planes")
        need("SensorTimestamp = " not in process.stdout, "SensorTimestamp still unqualified")
        timestamps = {p[2]:p[0]*1000000000+p[1]*1000 for p in captures}
        meters = [(int(f),int(st),int(ts),float(y)) for f,st,ts,y in re.findall(
            r"CAMSS_X1E_IPA_METER frame=(\d+) stream=(\d+) timestamp=(\d+) luma=([-+0-9.eE]+)",process.stderr)]
        need(len(meters)>=124 and [p[0] for p in meters]==list(range(len(meters))) and
             all(p[1]==pairs[0][3] for p in meters), "ordered isolated IPA metering")
        meter_map={p[0]:p for p in meters}
        need(all(meter_map[seq][2]//1000*1000==ts for seq,ts in timestamps.items()),"IPA timestamp pairing")
        need(process.stderr.count("initializing camss_x1e proxy in isolation: loading IPA from "+str(D/"ipa/ipa_camss_x1e.so"))==1,
             "actual isolated IPA")
        commands=[tuple(map(int,p)) for p in re.findall(
            r"CAMSS_X1E_REQUEST_CONTROL request=(\d+) target=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+)",process.stderr)]
        script_frames=[0,12,24,36,48,60,72,84,96]
        tuples=[(3554,1000,0,256),(3554,2000,0,256),(3554,1000,0,256),
                (3554,1000,512,256),(3554,1000,0,256),(3554,1000,0,512),
                (3554,1000,0,256),(7108,1000,0,256),(3554,1000,0,256)]
        need(len(commands)==9 and [p[0] for p in commands]==script_frames and
             [p[2:] for p in commands]==tuples and all(p[1]==pairs[p[0]][1] for p in commands),
             "public request controls admitted to their actual output slots")
        applied=[tuple(map(int,p)) for p in re.findall(
            r"CAMSS_X1E_APPLIED_CONTROL request=(\d+) frame=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+)",process.stderr)]
        expected=[];current=tuples[0];change=dict(zip(script_frames,tuples))
        for request in range(120):
            current=change.get(request,current);expected.append(current)
        need(len(applied)==120 and [p[:2] for p in applied]==[p[:2] for p in pairs] and
             [p[2:] for p in applied]==expected,"all 120 applied control snapshots match the requested frame")
        writes=[tuple(map(int,p)) for p in re.findall(
            r"CAMSS_X1E_DELAYED_WRITE sof=(\d+) effective=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+) cache_match=1",process.stderr)]
        need(len(writes)==9 and [p[1] for p in writes]==[p[1] for p in commands] and
             [p[2:] for p in writes]==tuples and all(p[1]==p[0]+2 for p in writes),
             "standard DelayedControls measured two-frame writes and cached readback")
        # Read actual public metadata independently of the pipeline's own log.
        blocks=re.split(r"(?m)^\d+\.\d{6} \([^)]+ fps\).*seq: \d+ bytesused: \d+/\d+$",process.stdout)[1:]
        need(len(blocks)==120,"one public metadata block per frame")
        for block,target in zip(blocks,expected):
            def val(name):
                found=re.search(r"(?m)^\s*"+name+r" = ([^\n]+)$",block)
                need(found is not None,"missing public metadata "+name)
                return found.group(1).strip()
            fll,exposure,analogue,digital=target
            duration=lambda lines:(lines*422+22)//45
            need(int(val("ExposureTime"))==duration(exposure) and
                 abs(float(val("AnalogueGain"))-1024/(1024-analogue))<1e-5 and
                 abs(float(val("DigitalGain"))-digital/256)<1e-5 and
                 int(val("FrameDuration"))==duration(fll) and val("AeEnable").lower() in ("false","0") and
                 int(val("ExposureTimeMode"))==1 and int(val("AnalogueGainMode"))==1,
                 "public applied metadata differs")
        private_log=run(["dmesg"])
        commits=[tuple(map(int,p)) for p in re.findall(
            r"NATIVE_IMX681_CONTROL_COMMIT sequence=(\d+) start=(\d+) end=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+) error=(-?\d+)",private_log)]
        readbacks=[tuple(map(int,p)) for p in re.findall(
            r"NATIVE_IMX681_CONTROL_READBACK sequence=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+) error=(-?\d+) timestamp=(\d+)",private_log)]
        need(len(commits)==9 and [p[0] for p in commits]==list(range(9)) and
             [p[3:7] for p in commits]==tuples and all(p[-1]==0 for p in commits),
             "one initial commit and eight changed clustered writes")
        need(len(readbacks)==9 and [p[1:5] for p in readbacks]==tuples and all(p[5]==0 for p in readbacks),
             "all independent known CCI register reads match")
        irq_sofs=[tuple(map(int,p)) for p in re.findall(r"NATIVE_FRONT_SOF sequence=(\d+) timestamp=(\d+)",private_log)]
        need([p[0] for p in irq_sofs]==list(range(len(irq_sofs))),"ordered SOF IRQs")
        for write,commit in zip(writes[1:],commits[1:]):
            sof=write[0]
            need(irq_sofs[sof][1]<=commit[1]<=commit[2]<irq_sofs[sof+1][1],
                 "CCI group release must fall within the intended SOF interval")
        stops=re.findall(r"NATIVE_FRONT_QUEUE_STOPPED completed=(\d+) stop_requested=(\d+) error=(-?\d+)",private_log)
        need(len(stops)==1 and int(stops[0][0])>=124 and stops[0][1:]==("1","0"),"clean explicit queue stop")
        need("NATIVE_FRONT_OWNER_REJECT" not in private_log,"no consumed-owner rejection")
        matches=re.findall(r"NATIVE_FRONT_OWNER_MATCH group=(\d+) sequence=(\d+)",private_log)
        groups={g:[int(s) for group,s in matches if int(group)==g] for g in range(5)}
        need(all(seq==groups[0] and seq==list(range(len(seq))) for seq in groups.values()),"all owner groups contiguous")
        result["request_controls"]={"standard_DelayedControls":True,"all_delays_frames":2,
            "all_priority_writes":False,"public_app":"libcamera cam --script",
            "requests":120,"explicit_requests":9,"changed_sensor_writes":8,
            "frame_admission_includes_internal_buffers":True,"all_applied_metadata_match":True,
            "all_known_register_reads_match":True,"all_CCI_writes_in_intended_SOF_interval":True,
            "commands":commands,"writes":writes,"applied":applied,"register_readbacks":readbacks,
            "SensorTimestamp_published":False,"automatic_feedback_enabled":False}
        result["ipa"]={"isolated_proxy_proven":True,"metered_frames":len(meters),"shared_statistics_buffers":8,
            "automatic_feedback_enabled":False,"metering_domain_optically_qualified":False}
        result["front_consumed_owner"]={"checks":len(matches),"rejections":0}
        files=sorted(D.glob("frame-*.bin"));need(len(files)==120,"120 private optical files")
        observations=[]
        for path in files:
            seq=int(re.search(r"-(\d+)\.bin$",path.name).group(1));image=path.read_bytes()
            need(len(image)==5529600 and path.stat().st_mode&0o077==0,"private frame mode/size")
            sparse=memoryview(image)[:3686400:64]
            observations.append({"sequence":seq,"completion_timestamp_ns":timestamps[seq],
                "sparse_y_mean":sum(sparse)/len(sparse),"sparse_y_max":max(sparse)})
        need([p["sequence"] for p in observations]==[p[1] for p in pairs],"private image identities")
        result["observation"]={"frames":120,"width":2560,"height":1440,"stride":2560,
            "metadata_pairs":120,"observations":observations,"pixels_private_on_sp11":True,
            "frame_rate_not_fixed_due_to_scripted_FLL":True,"optical_quality_parity_proven":False}
        idle();need(classify(run(["media-ctl","-d",media,"-p"]))[0]=="neutral","cam releases neutral route")
        result["phase"]="public_control_restart_and_reacquire"
        lifecycle=subprocess.run([str(D/"capture-lifecycle")],capture_output=True,text=True,
                                 timeout=25,env=environment)
        (D/"PRIVATE-LIFECYCLE-STDOUT.txt").write_text(lifecycle.stdout)
        (D/"PRIVATE-LIFECYCLE-STDERR.txt").write_text(lifecycle.stderr)
        rounds=[json.loads(p) for p in re.findall(r"LIFECYCLE_ROUND (\{[^\n]+\})",lifecycle.stdout)]
        result["hardware_streams_completed"]+=len(rounds)
        need(lifecycle.returncode==0 and len(rounds)==3 and [p["frames"] for p in rounds]==[1,24,24] and
             "PASS_LIBCAMERA_REQUEST_CONTROLS_LIFECYCLE_1_24_24" in lifecycle.stdout,
             "start controls, same-object reset and reacquire lifecycle")
        result["control_lifecycle"]={"rounds":rounds,"start_controls_proven":True,
            "same_configuration_restart_defaults_proven":True,"release_reacquire_defaults_proven":True,
            "all_public_metadata_match":True,"SensorTimestamp_published":False}
        final_log=run(["dmesg"])
        final_stops=re.findall(r"NATIVE_FRONT_QUEUE_STOPPED completed=(\d+) stop_requested=(\d+) error=(-?\d+)",final_log)
        need(len(final_stops)==4 and all(p[1:]==("1","0") for p in final_stops),"four clean STOPs")
        result["queue_stops"]=[{"completed":int(p[0]),"stop_requested":True,"error":0} for p in final_stops]
        critical=re.findall(r"(?im)^.*(?:BUG:|Oops:|Kernel panic|Call trace:|IOMMU.*fault|arm-smmu.*fault|NATIVE_FRONT_OWNER_REJECT).*$",final_log)
        need(not critical,"critical kernel signature")
        result["critical_signature_count"]=0
        run(["sha256sum","-c",str(D/"ASSETS.sha256")]);idle()
        need(classify(run(["media-ctl","-d",media,"-p"]))[0]=="neutral","final neutral route")
        result.update(status="PASS_NATIVE_FRONT_STANDARD_REQUEST_CONTROLS_AND_RESTART",
            final_route="neutral",all_sensors_suspended=True,optical_quality_parity_proven=False)
    except Exception as exc:
        result["error"]=str(exc)
        try:
            result["failure_sensor_states"]={p.name:{"bound":(p/"driver").is_symlink(),
                "runtime_status":(p/"power/runtime_status").read_text().strip()} for p in sensors().values()}
        except Exception: pass
        raise
    finally:
        result["candidate_boot_id"]=Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        (D/"RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")

if __name__=="__main__": main()
