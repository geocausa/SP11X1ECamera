#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One-use development probe, under its dedicated boot. No pixel access."""
import fcntl
import json
import os
from pathlib import Path
import runpy
import subprocess
import time

D = Path("/var/lib/sp11-camera-native-timing-20261007-02")
TOKEN = "sp11_camera_native_timing_20261007_02=1"
ENTRY = "sp11_entry=7.1.5-sp11-camera-native-timing-20261007-02"
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
    result = {"status": "FAILED_FRONT_TIMING_PROBE", "hardware_streams_completed": 0,
              "pixels_mapped_or_read": False, "retry": False}
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
                       "videobuf2_dma_sg", "v4l2_cci"):
            run(["modprobe", module])
        run(["insmod", str(D / "modules/qcom-camss.ko"), "e004j_ir_dphy_windows_parity=1"])
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
        result["phase"] = "discover_and_select_front_raw_route"
        discover = runpy.run_path(str(D / "discover-unified.py"))["discover"]
        classify = runpy.run_path(str(D / "camera-session-contract.py"))["classify"]
        candidates = []
        for path in sorted(Path("/dev").glob("media*")):
            graph = run(["media-ctl", "-d", str(path), "-p"])
            if "imx681 " in graph and "ov13858 " in graph:
                candidates.append((str(path), graph))
        need(len(candidates) == 1, "one complete camera graph required")
        media, initial = candidates[0]
        discovery = discover(initial, media)
        phase, _ = classify(initial)
        need(phase in ("neutral", "rear-only"), "unexpected initial route")
        if phase == "rear-only":
            run(["media-ctl", "-d", media, "-l", '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]'])
            run(["media-ctl", "-d", media, "-l", '"msm_csiphy1":1 -> "msm_csid0":0 [0]'])
        need(classify(run(["media-ctl", "-d", media, "-p"]))[0] == "neutral", "neutral")
        idle()
        run(["media-ctl", "-d", media, "-l", '"msm_csiphy2":1 -> "msm_csid1":0 [1]'])
        run(["media-ctl", "-d", media, "-l", '"msm_csid1":1 -> "msm_vfe1_rdi0":0 [1]'])
        need(classify(run(["media-ctl", "-d", media, "-p"]))[0] == "front-rdi-only", "front route")
        spec = "SRGGB10_1X10/3840x2160"
        for entity, pad in [(discovery["front_sensor_entity"], 0), ("msm_csiphy2", 0),
                            ("msm_csiphy2", 1), ("msm_csid1", 0), ("msm_csid1", 1),
                            ("msm_vfe1_rdi0", 0), ("msm_vfe1_rdi0", 1)]:
            run(["media-ctl", "-d", media, "-V", f'"{entity}":{pad} [fmt:{spec}]'])
        run(["v4l2-ctl", "-d", discovery["front_rdi_video_device"],
             "--set-fmt-video=width=3840,height=2160,pixelformat=pRAA"])
        observations = []
        for fll in (3554, 7116):
            result["phase"] = "capture_fll_" + str(fll)
            text = run([str(D / "front-timing-probe"), discovery["front_rdi_video_device"],
                        discovery["front_sensor_device"], str(fll)], timeout=30)
            data = json.loads(text)
            need(data["status"] == "PASS_FRONT_RAW_TIMING_MEASUREMENT" and
                 data["frames"] == 120 and data["streamoff"] is True, "capture result")
            observations.append(data)
            result["hardware_streams_completed"] += 1
            idle()
        result["phase"] = "neutralize_after_verified_stop"
        need(classify(run(["media-ctl", "-d", media, "-p"]))[0] == "front-rdi-only",
             "route drift after capture")
        run(["media-ctl", "-d", media, "-l", '"msm_csid1":1 -> "msm_vfe1_rdi0":0 [0]'])
        run(["media-ctl", "-d", media, "-l", '"msm_csiphy2":1 -> "msm_csid1":0 [0]'])
        need(classify(run(["media-ctl", "-d", media, "-p"]))[0] == "neutral", "final neutral")
        idle()
        rates = [observation["inferred_array_rate_hz"] for observation in observations]
        need(abs(rates[0] / rates[1] - 1) <= 0.002,
             "nominal and extended frame-length clocks disagree")
        result["array_rate_estimate_hz"] = sum(rates) / 2
        result["between_measurement_difference_ppm"] = abs(rates[0] / rates[1] - 1) * 1e6
        result.update(status="PASS_TWO_FRONT_TIMING_STREAMS_NEUTRAL",
                      observations=observations, final_route="neutral",
                      all_sensors_suspended=True)
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
