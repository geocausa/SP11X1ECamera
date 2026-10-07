#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One-use development probe, under its dedicated boot. Optical pixels remain private on SP11."""
import fcntl
import json
import os
import re
from pathlib import Path
import runpy
import subprocess
import time

D = Path("/var/lib/sp11-camera-native-profile-20261007-01")
TOKEN = "sp11_camera_native_profile_20261007_01=1"
ENTRY = "sp11_entry=7.1.5-sp11-camera-native-profile-20261007-01"
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
    need(not (D / "ATTEMPT-CONSUMED").exists(), "identity already consumed")
    (D / "ATTEMPT-CONSUMED").write_text(Path("/proc/sys/kernel/random/boot_id").read_text())
    lock = (D / "camera.lock").open("w")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    result = {"status": "FAILED_NATIVE_NV12_PROBE", "hardware_streams_completed": 0,
              "pixels_private_on_sp11": True, "retry": False}
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
             "native_linear_nv12_trial=1", "native_front_owner_trial=1", "native_front_queue_trial=1", "native_front_meta_trial=1", "native_front_params_trial=1", "native_front_profile_trial=1"])
        for name in ("ov13858", "imx681", "sp11-vd55g0"):
            run(["insmod", str(D / ("modules/" + name + ".ko"))])
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
        run(["media-ctl", "-d", media, "-l", '"msm_csiphy2":1 -> "msm_csid1":0 [1]'])
        run(["media-ctl", "-d", media, "-l", '"msm_csid1":4 -> "msm_vfe1_pix":0 [1]'])
        need(classify(run(["media-ctl", "-d", media, "-p"]))[0] == "front-pix-only", "front PIX route")
        spec = "SRGGB10_1X10/3840x2160"
        for entity, pad in [(discovery["front_sensor_entity"], 0), ("msm_csiphy2", 0),
                            ("msm_csiphy2", 1), ("msm_csid1", 0), ("msm_csid1", 4),
                            ("msm_vfe1_pix", 0)]:
            run(["media-ctl", "-d", media, "-V", f'"{entity}":{pad} [fmt:{spec}]'])
        # Native FULL is the retained 2560x1440 scaler output. Set matching
        # source-pad compose/crop metadata; these are ordinary V4L2 selections.
        run(["media-ctl", "-d", media, "-V",
             '"msm_vfe1_pix":0 [compose:(0,0)/2560x1440]'])
        run(["media-ctl", "-d", media, "-V",
             '"msm_vfe1_pix":1 [crop:(0,0)/2560x1440]'])
        run(["v4l2-ctl", "-d", discovery["front_video_device"],
             "--set-fmt-video=width=2560,height=1440,pixelformat=NV12"])
        (D / "PRIVATE-GRAPH-BEFORE-CAPTURE.txt").write_text(run(["media-ctl", "-d", media, "-p"]))
        result["phase"] = "capture_native_nv12_four_buffers"
        data = json.loads(run([str(D / "native-nv12-probe"), discovery["front_video_device"],
                               discovery["front_sensor_device"], "/lib/firmware/qcom/sp11/imx681-2560x1440-nv12-v1.bin", metadata], timeout=45))
        need(data["status"] == "PASS_80_NATIVE_FIRMWARE_PROFILE_FRAMES" and data["frames"] == 80 and
             data["streamoff"] is True and data["metadata_pairs"] == 80 and
             data["metadata_streamoff"] is True, "native NV12 capture")
        need(data["firmware_negative_cases"] == 2 and data["raw_command_control_present"] is False,
             "data-only profile rejection gates")
        result["hardware_streams_completed"] = 1
        private_log = run(["dmesg"])
        matches = re.findall(r"NATIVE_FRONT_OWNER_MATCH group=(\d+) sequence=(\d+)", private_log)
        groups = {group: [int(seq) for g, seq in matches if int(g) == group]
                  for group in range(5)}
        need("NATIVE_FRONT_OWNER_REJECT" not in private_log, "consumed owner rejected")
        need(all(len(seq) >= 80 and seq == list(range(seq[0], seq[0] + len(seq)))
                 for seq in groups.values()), "80 consumed completions per group required")
        need(all(seq == groups[0] for seq in groups.values()), "completion group generation drift")
        result["front_consumed_owner"] = {"groups": groups, "checks": len(matches),
                                           "rejections": 0, "session_epoch_checked": True}
        stops = re.findall(r"NATIVE_FRONT_QUEUE_STOPPED completed=(\d+) stop_requested=(\d+) error=(-?\d+)", private_log)
        need(len(stops) == 1 and int(stops[0][0]) >= 80 and stops[0][1:] == ("1", "0"),
             "explicit STREAMOFF clean queue stop required")
        result["queue_stop"] = {"completed":int(stops[0][0]),"stop_requested":True,"error":0}
        accepted = re.findall(r"NATIVE_FRONT_PARAMS_ACCEPT request=(\d+) mask=(\d+)", private_log)
        need([int(request) for request,mask in accepted] == list(range(5,89)),
             "typed parameter acceptance sequence")
        result["typed_parameters"] = {"requests_accepted":len(accepted),
            "raw_per_frame_capsules":False,"kernel_owned_banks":16,
            "negative_control_cases":data["negative_control_cases"]}
        need(private_log.count("NATIVE_FRONT_PROFILE_LOADED data_only=1 raw_control=0") == 1,
             "one kernel firmware profile admission")
        result["startup_profile"] = {"kernel_firmware_loader":True,"data_only":True,
            "raw_command_control_present":False,"missing_and_corrupt_rejections":2}
        result["observation"] = data
        run(["sha256sum", "-c", str(D / "ASSETS.sha256")])
        idle()
        need(classify(run(["media-ctl", "-d", media, "-p"]))[0] == "front-pix-only", "route drift")
        run(["media-ctl", "-d", media, "-l", '"msm_csid1":4 -> "msm_vfe1_pix":0 [0]'])
        run(["media-ctl", "-d", media, "-l", '"msm_csiphy2":1 -> "msm_csid1":0 [0]'])
        need(classify(run(["media-ctl", "-d", media, "-p"]))[0] == "neutral", "final neutral")
        idle()
        result.update(status="PASS_NATIVE_FRONT_DATA_ONLY_PROFILE_80_FRAMES",
                      final_route="neutral", all_sensors_suspended=True,
                      optical_quality_parity_proven=False, continuous_capture_80_frames_proven=True)
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
