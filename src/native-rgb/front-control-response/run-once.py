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

D = Path("/var/lib/sp11-camera-native-control-response-20261007-04")
TOKEN = "sp11_camera_native_control_response_20261007_04=1"
ENTRY = "sp11_entry=7.1.5-sp11-camera-native-control-response-20261007-04"
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
    result["comparison_role"] = "Linux-after-Windows"
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
        result["phase"] = "standard_libcamera_capture_320_frames"
        os.umask(0o077)
        environment = os.environ.copy()
        environment.update(LD_LIBRARY_PATH=str(D / "lib"),
            LIBCAMERA_PIPELINES_MATCH_LIST="camss-x1e", LIBCAMERA_LOG_LEVELS="*:DEBUG",
            LIBCAMERA_IPA_MODULE_PATH=str(D / "ipa"),
            LIBCAMERA_IPA_PROXY_PATH=str(D / "proxy"), LIBCAMERA_IPA_FORCE_ISOLATION="1",
            LIBCAMERA_CAMSS_X1E_CONTROL_TIMING="exposure-gain-v1")
        result["capture_started_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            process = subprocess.run([str(D / "cam"), "--camera=sp11-front-imx681",
                "--capture=320", "--stream=width=2560,height=1440,pixelformat=NV12,role=viewfinder",
                "--strict-formats", "--metadata", "--file=" + str(D / "frame-#.bin")],
                capture_output=True, text=True, timeout=50, env=environment)
        except subprocess.TimeoutExpired as exc:
            for stream,value in [("STDOUT",exc.stdout),("STDERR",exc.stderr)]:
                if isinstance(value,bytes): value=value.decode(errors="replace")
                (D / ("PRIVATE-CAM-"+stream+".txt")).write_text(value or "")
            result["cam_timed_out"] = True
            raise RuntimeError("standard libcamera application timed out") from exc
        (D / "PRIVATE-CAM-STDOUT.txt").write_text(process.stdout)
        (D / "PRIVATE-CAM-STDERR.txt").write_text(process.stderr)
        result["capture_completed_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        result["cam_exit_code"] = process.returncode
        need(process.returncode == 0, "standard libcamera application failed")
        pairs = [tuple(map(int, p)) for p in re.findall(
            r"CAMSS_X1E_PAIR request=(\d+) frame=(\d+) source=(\d+) stream=(\d+) timestamp_match=1",
            process.stderr)]
        need(len(pairs) >= 320, "320 frame-associated libcamera requests required")
        need([p[0] for p in pairs[:320]] == list(range(320)) and
             [p[1] for p in pairs[:320]] == list(range(4,324)) and
             [p[2] for p in pairs[:320]] == list(range(5,325)) and
             len({p[3] for p in pairs}) == 1, "libcamera request/source/stream association")
        captures = [tuple(map(int, p)) for p in re.findall(
            r"(?m)^(\d+)\.(\d{6}) \([^)]+ fps\).*seq: (\d+) bytesused: (\d+)/(\d+)$",
            process.stdout)]
        need(len(captures) == 320, "320 ordinary application frames required")
        need([p[2] for p in captures] == list(range(4,324)) and
             all(p[3:] == (3686400,1843200) for p in captures), "NV12 colour-plane extents")
        need(not re.search(r"SensorTimestamp = ",process.stdout),
             "unqualified sensor exposure timestamp must not be published")
        timestamps = [p[0]*1000000000 + p[1]*1000 for p in captures]
        need(process.stderr.count("initializing camss_x1e proxy in isolation: loading IPA from " +
                                  str(D / "ipa/ipa_camss_x1e.so")) == 1,
             "actual isolated standard IPA proxy required")
        need("Isolation of IPA module " + str(D / "ipa/ipa_camss_x1e.so") +
             " forced through configuration" in process.stderr, "forced IPA isolation proof")
        meters = [(int(f), int(st), int(ts), float(y)) for f,st,ts,y in re.findall(
            r"CAMSS_X1E_IPA_METER frame=(\d+) stream=(\d+) timestamp=(\d+) luma=([-+0-9.eE]+)",
            process.stderr)]
        need(len(meters) >= 324 and [m[0] for m in meters] == list(range(len(meters))) and
             all(m[1] == pairs[0][3] and m[3] >= 0 for m in meters),
             "startup and app frames need ordered actual IPA metering")
        need(all(meters[sequence][2] // 1000 * 1000 == timestamps[sequence-4]
                 for sequence in range(4,324)), "IPA/app completion timestamp association")
        result["ipa"] = {"implementation":"standard libcamera IPA",
            "isolated_proxy_proven":True,"shared_statistics_buffers":8,
            "statistics_requeued_after_matching_result":True,
            "metered_frames":len(meters),
            "metering":[{"sequence":f,"stream":st,"completion_timestamp_ns":ts,"luma":y}
                        for f,st,ts,y in meters],
            "automatic_feedback_enabled":False,"metering_domain_optically_qualified":False}
        files = sorted(D.glob("frame-*.bin"))
        need(len(files) == 320, "320 private app-written frame files required")
        observations = []
        for path in files:
            sequence = int(re.search(r"-(\d+)\.bin$", path.name).group(1))
            image = path.read_bytes()
            need(len(image) == 5529600 and path.stat().st_mode & 0o077 == 0, "private NV12 file size/mode")
            y, uv = memoryview(image)[:3686400], memoryview(image)[3686400:]
            need(max(y) > 0 and max(uv) > 0, "hardware-written planes")
            observations.append({"sequence":sequence,"timestamp_ns":timestamps[sequence-4],
                "y_mean":sum(y)/len(y),"y_max":max(y),"uv_mean":sum(uv)/len(uv),
                "y_storage_saturation_fraction":image.count(255,0,3686400)/3686400,
                "frame_sha256":hashlib.sha256(image).hexdigest()})
        need([o["sequence"] for o in observations] == list(range(4,324)), "private file sequence")
        data = {"status":"PASS_STANDARD_LIBCAMERA_NATIVE_NV12_320_FRAMES", "frames":320,
            "metadata_pairs":320,"sensor_timestamp_published":False,"timestamp_scope":"buffer completion only","startup_frames_internal":4,"paired_request_log_count":len(pairs),
            "frame_rate":319e9/(timestamps[-1]-timestamps[0]),"observations":observations,
            "private_pixel_files_only":True,"standard_app":"libcamera cam", "custom_probe":False,
            "width":2560,"height":1440,"stride":2560,"fixed_manual_iq":True,"automatic_3a_proven":False}
        result["hardware_streams_completed"] = 1
        private_log = run(["dmesg"])
        matches = re.findall(r"NATIVE_FRONT_OWNER_MATCH group=(\d+) sequence=(\d+)", private_log)
        groups = {group: [int(seq) for g, seq in matches if int(g) == group]
                  for group in range(5)}
        need("NATIVE_FRONT_OWNER_REJECT" not in private_log, "consumed owner rejected")
        need(all(len(seq) >= 324 and seq == list(range(seq[0], seq[0] + len(seq)))
                 for seq in groups.values()), "324 consumed completions per group required")
        need(all(seq == groups[0] for seq in groups.values()), "completion group generation drift")
        result["front_consumed_owner"] = {"groups": groups, "checks": len(matches),
                                           "rejections": 0, "session_epoch_checked": True}
        stops = re.findall(r"NATIVE_FRONT_QUEUE_STOPPED completed=(\d+) stop_requested=(\d+) error=(-?\d+)", private_log)
        need(len(stops) == 1 and int(stops[0][0]) >= 324 and stops[0][1:] == ("1", "0"),
             "explicit STREAMOFF clean queue stop required")
        result["queue_stop"] = {"completed":int(stops[0][0]),"stop_requested":True,"error":0}
        accepted = re.findall(r"NATIVE_FRONT_PARAMS_ACCEPT request=(\d+) mask=(\d+)", private_log)
        need(len(accepted) >= 328 and [int(request) for request,mask in accepted] ==
             list(range(5,5+len(accepted))) and all(mask == "0" for request,mask in accepted),
             "kernel semantic parameter sequence")
        result["typed_parameters"] = {"requests_accepted":len(accepted),
            "raw_per_frame_capsules":False,"kernel_owned_banks":16,"producer":"standard libcamera IPA typed defaults"}
        need(private_log.count("NATIVE_FRONT_PROFILE_LOADED data_only=1 raw_control=0") == 1,
             "one kernel firmware profile admission")
        result["startup_profile"] = {"kernel_firmware_loader":True,"data_only":True,
            "raw_command_control_present":False,"application_reads_startup_profile":False}
        irq_sofs = [tuple(map(int,p)) for p in re.findall(
            r"NATIVE_FRONT_SOF sequence=(\d+) timestamp=(\d+)", private_log)]
        app_sofs = [int(p) for p in re.findall(r"CAMSS_X1E_SOF frame=(\d+)",process.stderr)]
        need(len(irq_sofs) >= 324 and [p[0] for p in irq_sofs] == list(range(len(irq_sofs))) and
             all(b[1]>a[1] for a,b in zip(irq_sofs,irq_sofs[1:])), "ordered actual receiver SOF IRQs")
        need(len(app_sofs) >= 324 and app_sofs == list(range(len(app_sofs))) and
             len(app_sofs) <= len(irq_sofs), "standard libcamera frameStart delivery without drops")
        phases = [tuple(map(int,p)) for p in re.findall(
            r"NATIVE_FRONT_FRAME_PHASE source=(\d+) sof_count=(\d+) co_latched_sof=(\d+) timestamp=(\d+)",
            private_log)]
        need(len(phases) >= 324 and [p[0] for p in phases] == list(range(1,len(phases)+1)) and
             all(0 < p[1] <= len(irq_sofs) for p in phases), "receiver/video interrupt phase observations")
        selected = phases[4:324]
        from collections import Counter
        phase_offsets = dict(Counter(p[1]-p[0] for p in selected))
        receiver_to_video_irq_ns = [p[3]-irq_sofs[p[1]-1][1] for p in selected]
        video_irq_to_completion_ns = [timestamps[p[0]-5]-p[3] for p in selected]
        result["frame_start"] = {
            "standard_v4l2_frame_sync":True,"standard_libcamera_frameStart":True,
            "event_source":"CSID680 IPP CAMIF_SOF bit4, existing owning ISR",
            "event_irq_count":len(irq_sofs),"event_app_count":len(app_sofs),
            "event_irq_frame_rate":(len(irq_sofs)-1)*1e9/(irq_sofs[-1][1]-irq_sofs[0][1]),
            "receiver_sof_events":[{"sequence":seq,"monotonic_irq_ns":ts} for seq,ts in irq_sofs],
            "video_interrupt_phase":[{"source_sequence":src,"observed_sof_count":count,
                "co_latched_sof":bool(co),"monotonic_observation_ns":ts} for src,count,co,ts in phases],
            "steady_sof_count_minus_video_source_histogram":phase_offsets,
            "steady_latest_sof_to_video_irq_ns":receiver_to_video_irq_ns,
            "steady_video_irq_to_buffer_completion_ns":video_irq_to_completion_ns,
            "sensor_exposure_timestamp_proven":False,"sensor_control_delays_measured":False,
            "phase_is_observation_not_exposure_identity":True}
        raw_commands = [tuple(map(int,p)) for p in re.findall(
            r"CAMSS_X1E_CONTROL_TIMING step=(\d+) sof=(\d+) begin=(\d+) end=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+) error=(-?\d+)", process.stderr)]
        expected = [(3554,2000 if step%2 else 1000,0,256) if step<=6 else
                    (3554,1000,512 if step%2 else 0,256) if step<=12 else
                    (3554,1000,0,512 if step%2 else 256) for step in range(1,19)]
        need(len(raw_commands)==18 and [p[0] for p in raw_commands]==list(range(1,19)) and
             [p[1] for p in raw_commands]==list(range(16,289,16)) and
             [p[4:8] for p in raw_commands]==expected and
             all(p[-1]==0 and p[3]>=p[2]>0 for p in raw_commands),
             "eighteen bounded clustered changes with restored baseline")
        commits = [tuple(map(int,p)) for p in re.findall(
            r"NATIVE_IMX681_CONTROL_COMMIT sequence=(\d+) start=(\d+) end=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+) error=(-?\d+)", private_log)]
        need(len(commits)==19 and [p[0] for p in commits]==list(range(19)) and
             [p[3:7] for p in commits]==[(3554,1000,0,256)]+expected and
             all(p[-1]==0 and p[2]>=p[1]>0 for p in commits),
             "initial setup plus eighteen successful unique CCI transactions")
        commands = []
        for command,commit in zip(raw_commands,commits[1:]):
            step,sof,begin,end,fll,exposure,analogue,digital,error = command
            need(begin<=commit[1]<=commit[2]<=end and irq_sofs[sof][1]<=begin,
                 "one sensor ioctl after requested SOF brackets each CCI group release")
            commands.append({"step":step,"sof":sof,"ioctl_begin_ns":begin,"ioctl_end_ns":end,
                "cci_begin_ns":commit[1],"cci_end_ns":commit[2],"fll":fll,"exposure":exposure,
                "analogue_code":analogue,"digital_code":digital})
        readbacks = [tuple(map(int,p)) for p in re.findall(
            r"NATIVE_IMX681_CONTROL_READBACK sequence=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+) error=(-?\d+) timestamp=(\d+)", private_log)]
        need(len(readbacks)==19 and [p[0] for p in readbacks]==list(range(19)),
             "all nineteen known-register readback observations required")
        readback_matches = all(p[1:5]==target and p[5]==0 for p,target in
                               zip(readbacks,[(3554,1000,0,256)]+expected))
        intervals = [b[1]-a[1] for a,b in zip(irq_sofs,irq_sofs[1:])]
        import statistics
        expected_period = 3554*6752*1e9/720000000
        need(abs(statistics.mean(intervals[8:320])-expected_period)<expected_period*0.03,
             "fixed frame-length receiver cadence through response experiment")
        analysis = runpy.run_path(str(D / "analyze.py"))["analyze"](
            [m[3] for m in meters], [o["y_mean"] for o in observations], commands,
            phase_offsets=={0:320})
        analysis.update(kind="exposure-gain-v1",standard_sensor_control_ioctl=True,
            commanded_changes=18,baseline_restored_before_stop=True,
            kernel_commit_count=19,commands=commands,receiver_intervals_ns=intervals,
            output_storage_saturation_screen=max(o["y_storage_saturation_fraction"] for o in observations)<0.001,
            baseline_restored_command=(3554,1000,0,256))
        if not analysis["output_storage_saturation_screen"]:
            analysis["all_fields_response_timing_qualified"] = False
            for field in analysis["fields"]:
                field["response_timing_qualified"] = False
                field["observed_response_delay_frames"] = None
                field["reasons"].append("processed storage saturation confounds response")
        analysis["known_register_readback"] = {
            "all_reads_successful":all(p[5]==0 for p in readbacks),
            "all_commanded_values_retained":readback_matches,
            "observations":[{"sequence":p[0],"fll":p[1],"exposure":p[2],"analogue_code":p[3],
                "digital_code":p[4],"error":p[5],"timestamp_ns":p[6]} for p in readbacks],
            "readback_is_not_pixel_application_proof":True}
        if not readback_matches:
            analysis["all_fields_response_timing_qualified"] = False
            for field in analysis["fields"]:
                field["response_timing_qualified"] = False
                field["observed_response_delay_frames"] = None
                field["reasons"].append("known register readback differs or failed")
        result["grouped_control_response"] = analysis
        result["observation"] = data
        run(["sha256sum", "-c", str(D / "ASSETS.sha256")])
        idle()
        need(classify(run(["media-ctl", "-d", media, "-p"]))[0] == "neutral", "libcamera release must leave neutral route")
        idle()
        result.update(status="PASS_NATIVE_FRONT_CONTROL_RESPONSE_CAPTURE_320_FRAMES",
                      final_route="neutral", all_sensors_suspended=True,
                      optical_quality_parity_proven=False, continuous_capture_320_frames_proven=True)
    except Exception as exc:
        # No speculative graph rollback on failure. Service returns Golden.
        result["error"] = str(exc)
        try:
            result["failure_sensor_states"] = {path.name: {"bound": (path / "driver").is_symlink(),
                "runtime_status": (path / "power/runtime_status").read_text().strip()} for path in sensors().values()}
        except Exception:
            pass
        raise
    finally:
        result["candidate_boot_id"] = Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        (D / "RESULT.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")

if __name__ == "__main__":
    main()
