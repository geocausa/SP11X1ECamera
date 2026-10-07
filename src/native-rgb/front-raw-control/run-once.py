#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One-use development probe, under its dedicated boot. Sparse RAW metrology only; no pixel export."""
import fcntl
import datetime
import re
import json
import os
from pathlib import Path
import runpy
import subprocess
import time

D = Path("/var/lib/sp11-camera-native-raw-control-20261007-01")
TOKEN = "sp11_camera_native_raw_control_20261007_01=1"
ENTRY = "sp11_entry=7.1.5-sp11-camera-native-raw-control-20261007-01"
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
    need((D / "ARMED").is_file(), "explicit arm required")
    with (D / "ATTEMPT-CONSUMED").open("x") as consumed:
        consumed.write(Path("/proc/sys/kernel/random/boot_id").read_text())
    lock = (D / "camera.lock").open("w")
    fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
    result = {"status": "FAILED_FRONT_RAW_CONTROL_PROBE", "hardware_streams_completed": 0,
              "sparse_pixel_metrology": True, "pixel_export": False,
              "sensor_delay_qualified": False, "matched_windows_reference": False, "retry": False}
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
        run(["insmod", str(D / "modules/qcom-camss.ko"), "e004j_ir_dphy_windows_parity=1"])
        for name in ("ov13858", "imx681", "sp11-vd55g0"):
            run(["insmod", str(D / ("modules/" + name + ".ko"))] +
                (["native_control_timing_trace=1","native_control_timing_readback=1"] if name == "imx681" else []))
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
        (D / "PRIVATE-MEDIA-INITIAL.txt").write_text(initial)
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
        result["phase"] = "front_raw_320_frame_control_response"
        result["capture_started_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            proc = subprocess.run([str(D / "front-raw-control-probe"),
                discovery["front_rdi_video_device"], discovery["front_sensor_device"]],
                capture_output=True,text=True,timeout=40)
        except subprocess.TimeoutExpired as exc:
            for name,value in [("STDOUT.jsonl",exc.stdout),("STDERR.txt",exc.stderr)]:
                if isinstance(value,bytes): value=value.decode(errors="replace")
                (D / ("PRIVATE-PROBE-"+name)).write_text(value or "")
            result["probe_timed_out"] = True
            raise RuntimeError("RAW probe timeout; no same-boot retry") from exc
        (D / "PRIVATE-PROBE-STDOUT.jsonl").write_text(proc.stdout)
        (D / "PRIVATE-PROBE-STDERR.txt").write_text(proc.stderr)
        result["capture_completed_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
        need(proc.returncode == 0, "RAW probe exit")
        records = [json.loads(line) for line in proc.stdout.splitlines()]
        frames = [r for r in records if r.get("kind") == "frame"]
        commands = [r for r in records if r.get("kind") == "command"]
        summaries = [r for r in records if r.get("status") == "PASS_FRONT_RAW_CONTROL_CAPTURE"]
        need(len(summaries)==1 and summaries[0]["frames"]==320 and
             summaries[0]["streamoff"] is True and summaries[0]["fps"]>=29,
             "RAW capture timing/stop")
        result["hardware_streams_completed"] = 1
        need(len(frames)==320 and [r["sequence"] for r in frames]==list(range(320)),
             "sequential RAW metrology")
        need(len(commands)==20 and [r["step"] for r in commands]==[0,*range(1,19),0],
             "bounded commands and final restore")
        need(all(c["cached_controls_match"] for c in commands), "cached controls")
        log=run(["dmesg"])
        (D / "PRIVATE-DMESG.txt").write_text(log)
        writes=[tuple(map(int,m)) for m in re.findall(
            r"NATIVE_IMX681_CONTROL_COMMIT sequence=(\d+) start=(\d+) end=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+) error=(-?\d+)",log)]
        reads=[tuple(map(int,m)) for m in re.findall(
            r"NATIVE_IMX681_CONTROL_READBACK sequence=(\d+) fll=(\d+) exposure=(\d+) again=(\d+) dgain=(\d+) error=(-?\d+) timestamp=(\d+)",log)]
        need(len(writes)==19 and len(reads)==19 and
             [w[0] for w in writes]==list(range(19)), "known register trace counts")
        for i,(w,r) in enumerate(zip(writes,reads)):
            need(w[0]==r[0] and w[3:7]==r[1:5] and w[7]==r[5]==0 and
                 w[2]>=w[1] and r[6]>=w[2], "register retention")
            c=commands[i]
            need(w[3:7]==(c["fll"],c["exposure"],c["again"],c["dgain"]),
                 "command/register association")
            if i:
                need(c["start_ns"]<=w[1]<=w[2]<=r[6]<=c["end_ns"],
                     "in-stream transaction timestamp association")
        result.update(observation=summaries[0],frames=frames,commands=commands,
            register_writes=[list(w) for w in writes],
            register_reads=[list(r) for r in reads],
            known_register_readback_matched=True, known_register_readback_count=len(reads),
            frame_sync_source="none on RAW route",
            timestamp_semantics="MONOTONIC buffer completion; not sensor exposure/SOF",
            isp_enabled=False,automatic_feedback_enabled=False)
        result["raw_response_analysis"] = runpy.run_path(str(D / "analyze.py"))["analyze"](frames)
        idle()
        result["phase"] = "neutralize_after_verified_stop"
        need(classify(run(["media-ctl", "-d", media, "-p"]))[0] == "front-rdi-only",
             "route drift after capture")
        run(["media-ctl", "-d", media, "-l", '"msm_csid1":1 -> "msm_vfe1_rdi0":0 [0]'])
        run(["media-ctl", "-d", media, "-l", '"msm_csiphy2":1 -> "msm_csid1":0 [0]'])
        need(classify(run(["media-ctl", "-d", media, "-p"]))[0] == "neutral", "final neutral")
        idle()
        (D / "PRIVATE-MEDIA-FINAL.txt").write_text(run(["media-ctl","-d",media,"-p"]))
        result.update(status="PASS_FRONT_RAW_CONTROL_CAPTURE_AND_READBACK",
                      final_route="neutral", all_sensors_suspended=True)
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
