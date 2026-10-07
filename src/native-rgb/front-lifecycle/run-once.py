#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One-use development probe, under its dedicated boot. Optical pixels remain private on SP11."""
import fcntl
import json
import os
import hashlib
import re
from pathlib import Path
import runpy
import subprocess
import time

D = Path("/var/lib/sp11-camera-native-lifecycle-20261007-03")
TOKEN = "sp11_camera_native_lifecycle_20261007_03=1"
ENTRY = "sp11_entry=7.1.5-sp11-camera-native-lifecycle-20261007-03"
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
        result["phase"] = "public_libcamera_same_camera_restart_and_reacquire"
        os.umask(0o077)
        environment = os.environ.copy()
        environment.update(LD_LIBRARY_PATH=str(D / "lib"),
            LIBCAMERA_PIPELINES_MATCH_LIST="camss-x1e", LIBCAMERA_LOG_LEVELS="*:DEBUG")
        try:
            process = subprocess.run([str(D / "capture-lifecycle")],
                capture_output=True, text=True, timeout=55, env=environment)
        except subprocess.TimeoutExpired as exc:
            for stream,value in [("STDOUT",exc.stdout),("STDERR",exc.stderr)]:
                if isinstance(value,bytes): value=value.decode(errors="replace")
                (D / ("PRIVATE-LIFECYCLE-"+stream+".txt")).write_text(value or "")
            result["application_timed_out"] = True
            raise RuntimeError("public libcamera lifecycle application timed out") from exc
        (D / "PRIVATE-LIFECYCLE-STDOUT.txt").write_text(process.stdout)
        (D / "PRIVATE-LIFECYCLE-STDERR.txt").write_text(process.stderr)
        result["application_exit_code"] = process.returncode
        rounds = [json.loads(line.split(" ",1)[1]) for line in process.stdout.splitlines()
                  if line.startswith("LIFECYCLE_ROUND ")]
        result["rounds"] = rounds
        result["hardware_streams_completed"] = len(rounds)
        need(process.returncode == 0 and "PASS_LIBCAMERA_FRONT_LIFECYCLE_1_80_80" in process.stdout,
             "public libcamera lifecycle application failed")
        need(len(rounds) == 3 and [r["frames"] for r in rounds] == [1,80,80] and
             [r["round"] for r in rounds] == [0,1,2], "three lifecycle rounds required")
        pairs = [tuple(map(int, p)) for p in re.findall(
            r"CAMSS_X1E_PAIR request=(\d+) frame=(\d+) source=(\d+) stream=(\d+) timestamp_match=1",
            process.stderr)]
        stream_ids = list(dict.fromkeys(p[3] for p in pairs))
        need(len(pairs) == 161 and len(stream_ids) == 3, "fresh stream identity each start")
        for round,stream in zip(rounds,stream_ids):
            count = round["frames"]
            association = [p for p in pairs if p[3] == stream]
            need([p[0] for p in association] == list(range(count)) and
                 [p[1] for p in association] == list(range(4,4+count)) and
                 [p[2] for p in association] == list(range(5,5+count)),
                 "request/statistics identities across restart")
            need(round["sequences"] == list(range(4,4+count)) and
                 round["clean_stop"] and round["same_camera"] and round["all_sensors_suspended"] and
                 all(b>a for a,b in zip(round["timestamps_ns"],round["timestamps_ns"][1:])),
                 "public API sequence/timestamp/stop result")
            round["stream_id"] = stream
            if count > 1:
                round["frame_rate"] = (count-1)*1e9/(round["timestamps_ns"][-1]-round["timestamps_ns"][0])
        result["rounds"] = rounds
        result["hardware_streams_completed"] = 3
        private_log = run(["dmesg"])
        stops = re.findall(r"NATIVE_FRONT_QUEUE_STOPPED completed=(\d+) stop_requested=(\d+) error=(-?\d+)", private_log)
        need(len(stops) == 3 and all(s[1:] == ("1","0") for s in stops) and
             all(int(s[0]) >= count+4 for s,count in zip(stops,[1,80,80])),
             "three clean explicit STREAMOFF completions")
        result["queue_stops"] = [{"completed":int(s[0]),"stop_requested":True,"error":0} for s in stops]
        owner_blocks = []
        parameter_blocks = []
        for stop in re.finditer(r"NATIVE_FRONT_QUEUE_STOPPED completed=\d+ stop_requested=\d+ error=-?\d+",private_log):
            block = private_log[:stop.start()] if not owner_blocks else private_log[previous:stop.start()]
            previous = stop.end()
            matches = re.findall(r"NATIVE_FRONT_OWNER_MATCH group=(\d+) sequence=(\d+)",block)
            groups = {g:[int(seq) for group,seq in matches if int(group)==g] for g in range(5)}
            count = int(re.search(r"completed=(\d+)",stop.group()).group(1))
            need(all(seq == list(range(1,count+1)) for seq in groups.values()),
                 "all owner groups reset and retire before reuse")
            owner_blocks.append({"checks":len(matches),"retirements":count,"groups":groups})
            accepted = re.findall(r"NATIVE_FRONT_PARAMS_ACCEPT request=(\d+) mask=(\d+)",block)
            need([int(req) for req,mask in accepted] == list(range(5,5+len(accepted))) and
                 all(mask == "0" for req,mask in accepted) and len(accepted) >= count+3,
                 "semantic FIFO starts fresh on restart")
            parameter_blocks.append({"requests_accepted":len(accepted),"raw_per_frame_capsules":False})
        need("NATIVE_FRONT_OWNER_REJECT" not in private_log, "owner rejected")
        for marker in ["BUG:","Oops:","WARNING:","Kernel panic","teardown unsafe","intentionally pinned"]:
            need(marker not in private_log,"critical kernel failure: "+marker)
        need(private_log.count("NATIVE_FRONT_PROFILE_LOADED data_only=1 raw_control=0") == 3,
             "kernel loads and retires private profile for each stream")
        result["consumed_owner_rounds"] = owner_blocks
        result["typed_parameter_rounds"] = parameter_blocks
        result["kernel_profile_loads"] = 3
        run(["sha256sum", "-c", str(D / "ASSETS.sha256")])
        idle()
        need(classify(run(["media-ctl","-d",media,"-p"]))[0] == "neutral",
             "camera release must leave neutral route")
        result.update(status="PASS_NATIVE_FRONT_LIBCAMERA_LIFECYCLE_1_80_80",
                      same_camera_restart_proven=True,same_camera_reacquire_proven=True,
                      one_frame_finite_capture_proven=True,final_route="neutral",
                      all_sensors_suspended=True,automatic_3a_proven=False,
                      optical_quality_parity_proven=False)
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
