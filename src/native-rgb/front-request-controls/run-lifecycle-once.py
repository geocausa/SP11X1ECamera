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

D = Path("/var/lib/sp11-camera-native-request-controls-20261007-02")
TOKEN = "sp11_camera_native_request_controls_20261007_02=1"
ENTRY = "sp11_entry=7.1.5-sp11-camera-native-request-controls-20261007-02"
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
        result["phase"]="start_control_reset_and_reacquire"
        environment=os.environ.copy();environment.pop("LIBCAMERA_CAMSS_X1E_CONTROL_TIMING",None)
        environment.update(LD_LIBRARY_PATH=str(D/"lib"),LIBCAMERA_PIPELINES_MATCH_LIST="camss-x1e",
            LIBCAMERA_LOG_LEVELS="*:DEBUG",LIBCAMERA_IPA_MODULE_PATH=str(D/"ipa"),
            LIBCAMERA_IPA_PROXY_PATH=str(D/"proxy"),LIBCAMERA_IPA_FORCE_ISOLATION="1")
        result["capture_started_utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
        lifecycle=subprocess.run([str(D/"capture-lifecycle")],capture_output=True,text=True,
                                 timeout=25,env=environment)
        (D/"PRIVATE-LIFECYCLE-STDOUT.txt").write_text(lifecycle.stdout)
        (D/"PRIVATE-LIFECYCLE-STDERR.txt").write_text(lifecycle.stderr)
        result["capture_completed_utc"]=datetime.datetime.now(datetime.timezone.utc).isoformat()
        result["lifecycle_exit_code"]=lifecycle.returncode
        rounds=[json.loads(p) for p in re.findall(r"LIFECYCLE_ROUND (\{[^\n]+\})",lifecycle.stdout)]
        result["hardware_streams_completed"]=len(rounds)
        result["rounds"]=rounds
        need(lifecycle.returncode==0 and len(rounds)==3 and [p["frames"] for p in rounds]==[1,24,24] and
             "PASS_LIBCAMERA_REQUEST_CONTROLS_LIFECYCLE_1_24_24" in lifecycle.stdout,
             "custom start, same-configuration default reset, release/reacquire reset")
        need("CAMSS_X1E_CONTROL_TIMING" not in lifecycle.stderr,"no diagnostic control path")
        need(lifecycle.stderr.count("initializing camss_x1e proxy in isolation: loading IPA from "+str(D/"ipa/ipa_camss_x1e.so"))==1,
             "actual single isolated IPA across lifecycle")
        log=run(["dmesg"])
        checks=runpy.run_path(str(D/"checks.py"))
        critical=checks["critical_signatures"](log);need(not critical,"critical kernel signature")
        result["critical_signature_count"]=0
        stops=list(re.finditer(r"NATIVE_FRONT_QUEUE_STOPPED completed=(\d+) stop_requested=(\d+) error=(-?\d+)",log))
        need(len(stops)==3 and all(p.groups()[1:]==("1","0") for p in stops),"three clean STOPs")
        prior=0;owners=[]
        for stop,limit in zip(stops,[1,24,24]):
            owner=checks["owner_groups"](log[prior:stop.start()]);owners.append(owner);prior=stop.end()
            need(owner["last"]-owner["first"]+1>=limit+4,"every startup/application owner retires")
        result["owner_rounds"]=owners
        result["queue_stops"]=[{"completed":int(p.group(1)),"stop_requested":True,"error":0} for p in stops]
        pairs=[tuple(map(int,p)) for p in re.findall(r"CAMSS_X1E_APPLIED_CONTROL request=(\d+) frame=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+)",lifecycle.stderr)]
        need(len(pairs)==49 and pairs[0][2:]==(3554,2000,512,512) and
             all(p[2:]==(3554,1000,0,256) for p in pairs[1:]),"start/reset/reacquire applied control tuples")
        result["applied_controls"]=pairs
        readbacks=[tuple(map(int,p)) for p in re.findall(r"NATIVE_IMX681_CONTROL_READBACK sequence=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+) error=(-?\d+) timestamp=(\d+)",log)]
        need(len(readbacks)==3 and [p[1:5] for p in readbacks]==[(3554,2000,512,512),(3554,1000,0,256),(3554,1000,0,256)] and
             all(p[5]==0 for p in readbacks),"three matching stream-start CCI readbacks")
        result["known_register_readbacks"]=readbacks
        result["control_lifecycle"]={"start_controls_proven":True,"same_configuration_restart_defaults_proven":True,
            "release_reacquire_defaults_proven":True,"all_public_metadata_match":True,
            "SensorTimestamp_published":False,"automatic_feedback_enabled":False}
        run(["sha256sum","-c",str(D/"ASSETS.sha256")]);idle()
        need(classify(run(["media-ctl","-d",media,"-p"]))[0]=="neutral","final neutral graph")
        result.update(status="PASS_NATIVE_FRONT_DELAYED_CONTROL_START_RESET_REACQUIRE_1_24_24",
            final_route="neutral",all_sensors_suspended=True,optical_quality_parity_proven=False)
    except Exception as exc:
        result["error"]=str(exc)
        try:
            result["failure_sensor_states"]={p.name:{"bound":(p/"driver").is_symlink(),
                "runtime_status":(p/"power/runtime_status").read_text().strip()} for p in sensors().values()}
        except Exception:pass
        raise
    finally:
        result["candidate_boot_id"]=Path("/proc/sys/kernel/random/boot_id").read_text().strip()
        (D/"RESULT.json").write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
if __name__=="__main__":main()
