#!/usr/bin/env python3
"""Manage one disposable, ordinary-memory IR capture experiment."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time
import tempfile

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
BUILD = HERE / "build"
BOOT = Path("/boot/sp11-7.1.5-camera-e004ew-native-ir")
ENTRY = Path("/etc/grub.d/99zzzzzz_sp11_camera_e004ew_native_ir")
ENTRY_ID = "sp11-camera-e004ew-native-ir-one-shot"
MARKER = "sp11_camera_e004ew_native_ir=1"
GOLDEN = Path("/boot/sp11-7.1.5-audio-fullio-v19c")
FIRMWARE = Path("/lib/firmware/st/vd55g0-sp11-cut1.bin")
KERNEL = "7.1.5-sp11-render-parity-v4+"
KNOWN_DIRTY = {
    "CONTINUE.md": "0f8943e4fdf5d2c0278c8eaabff2a31a2d7a91b99ee6fdc9a6d5163de5c3844d",
    "HANDOFF.md": "a863241cef45861359d93e75c5595e5993f4cb9391531599bcf90a43d59f9dbf",
    "PROJECT_STATE.md": "890e60cb2b0bc8afc9deb55aa7517c65b17a6dfaa035a819a9e2703b189ec4e8",
    "README.md": "7db78332f9e325c41ddad2bad49048b797f73841301818573965c9fb21776e15",
    "state/project.yaml": "c94ac725165c1e6da2bfe2437b2a071782220f87d5a50abee61e5d74273cd036",
}


def run(args, *, timeout=30, check=True):
    command = [str(a) for a in args]
    # Output goes to a regular file: a kernel-stuck child cannot hold a pipe
    # open and defeat our timeout. Never wait indefinitely while reaping it.
    with tempfile.TemporaryFile(mode="w+b") as output:
        process = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT)
        try:
            status = process.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            process.kill()
            try:
                process.wait(timeout=1)
            except subprocess.TimeoutExpired:
                pass
            output.seek(0)
            raise subprocess.TimeoutExpired(command, timeout, output=output.read())
        output.seek(0)
        text = output.read().decode(errors="replace")
        if status and check:
            raise subprocess.CalledProcessError(status, command, output=text)
        return text


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save(name, value):
    (HERE / "evidence" / name).write_text("\n".join(line.rstrip() for line in value.splitlines()).rstrip() + "\n")


def require(condition, reason):
    if not condition:
        raise RuntimeError(reason)


def verify_files():
    manifest = json.loads((BUILD / "MANIFEST.json").read_text())
    for path, expected in manifest["sources"].items():
        require(sha(REPO / path) == expected, "source drift: " + path)
    for path, expected in manifest["artifacts"].items():
        require(sha(BUILD / path) == expected, "artifact drift: " + path)
    run(["python3", REPO / "src/front-ir-vd55g0/native/validate_dtb.py", BUILD / "ir-only.dtb"])
    return manifest


def verify_boot():
    env = dict(line.split("=", 1) for line in
               run(["sudo", "-n", "grub-editenv", "/boot/grub/grubenv", "list"]).splitlines()
               if "=" in line)
    require(env.get("saved_entry") == "sp11-audio-fullio-v19c", "Golden default changed")
    require(not env.get("next_entry"), "another boot is armed")


def verify_repository():
    changed = set(run(["git", "diff", "--name-only"], check=True).splitlines())
    require(changed == set(KNOWN_DIRTY), "unexpected tracked changes")
    require(not run(["git", "diff", "--cached", "--name-only"]).strip(), "index is not empty")
    for name, expected in KNOWN_DIRTY.items():
        require(sha(REPO / name) == expected, "known local document changed")
    require(not run(["git", "status", "--porcelain", "--untracked-files=all", "--",
                     "src/front-ir-vd55g0/native"]).strip(), "native source is not committed")


def install():
    run([REPO / "tools/camera-overlap-guard.sh", "--require-golden", "--require-no-camera-process"])
    verify_repository()
    verify_files()
    verify_boot()
    require(not BOOT.exists() and not ENTRY.exists(), "candidate already installed")
    require(not FIRMWARE.exists(), "firmware path already exists; audit it first")
    require(not (HERE / "evidence/CONSUMED.json").exists(), "candidate already consumed")
    # Preserve the live Golden arguments, replacing only boot-identifying fields.
    args = [x for x in Path("/proc/cmdline").read_text().split()
            if not x.startswith(("BOOT_IMAGE=", "sp11_entry=", "modprobe.blacklist="))]
    require(all(re.fullmatch(r"[A-Za-z0-9_./:=,+%\-]+", x) for x in args),
            "unexpected GRUB argument syntax")
    args += ["sp11_entry=native-ir-e004ew", MARKER,
             "modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,sp11_vd55g0_native,vd55g0"]
    uuid = run(["findmnt", "-n", "-o", "UUID", "/"]).strip()
    require(re.fullmatch(r"[a-fA-F0-9-]+", uuid) is not None, "invalid root UUID")
    grub = ('#!/bin/sh\nexec tail -n +3 "$0"\n'
            f"menuentry 'SP11 native IR RAW10 experiment' --id '{ENTRY_ID}' {{\n"
            " insmod part_gpt\n insmod ext2\n insmod fdt\n"
            f" search --no-floppy --fs-uuid --set=root {uuid}\n"
            f" devicetree {BOOT}/ir-only.dtb\n"
            f" linux {BOOT}/vmlinuz {' '.join(args)}\n"
            f" initrd {BOOT}/initrd.img\n}}\n")
    (BUILD / "grub-entry").write_text(grub)
    run(["sudo", "-n", "mkdir", str(BOOT)])
    for source, name in [(GOLDEN / ("vmlinuz-" + KERNEL), "vmlinuz"),
                         (GOLDEN / "initrd.img-7.1.5-sp11-fullio-v19c", "initrd.img"),
                         (BUILD / "ir-only.dtb", "ir-only.dtb")]:
        run(["sudo", "-n", "install", "-m", "0644", source, BOOT / name])
        require(sha(source) == sha(BOOT / name), "boot copy mismatch")
    run(["sudo", "-n", "install", "-D", "-m", "0644",
         BUILD / "firmware/st/vd55g0-sp11-cut1.bin", FIRMWARE])
    run(["sudo", "-n", "install", "-m", "0755", BUILD / "grub-entry", ENTRY])
    run(["sudo", "-n", "update-grub"], timeout=60)
    record = {str(p): sha(p) for p in [BOOT / "vmlinuz", BOOT / "initrd.img",
                                     BOOT / "ir-only.dtb", ENTRY, FIRMWARE]}
    save("INSTALL.json", json.dumps(record, indent=2) + "\n")
    verify_boot()
    print("INSTALLED_UNARMED")


def arm():
    verify_repository()
    verify_files()
    verify_boot()
    require(not (HERE / "evidence/CONSUMED.json").exists(), "candidate already consumed")
    run([REPO / "tools/camera-overlap-guard.sh", "--require-golden", "--require-no-camera-process"])
    for path, expected in json.loads((HERE / "evidence/INSTALL.json").read_text()).items():
        require(sha(Path(path)) == expected, "installed artifact drift")
    branch = run(["git", "branch", "--show-current"]).strip()
    remote = run(["git", "ls-remote", "origin", "refs/heads/" + branch]).split()[0]
    require(remote == run(["git", "rev-parse", "HEAD"]).strip(), "candidate not pushed")
    # This is evidence of arming, not evidence that capture started.
    with (HERE / "evidence/ARMED.json").open("x") as f:
        json.dump({"head": remote, "golden_boot": Path("/proc/sys/kernel/random/boot_id").read_text().strip()}, f)
    run(["sudo", "-n", "grub-reboot", ENTRY_ID])
    env = run(["sudo", "-n", "grub-editenv", "/boot/grub/grubenv", "list"])
    require("next_entry=" + ENTRY_ID in env, "one-shot did not arm")
    print("ONE_SHOT_ARMED")


def capture():
    verify_boot()
    verify_files()
    require(MARKER in Path("/proc/cmdline").read_text().split(), "wrong boot")
    for name in ("qcom_camss", "sp11_vd55g0", "sp11_vd55g0_native", "vd55g0", "imx681", "ov13858"):
        require(not Path("/sys/module", name).exists(), "camera module already loaded")
    require(not list(Path("/dev").glob("media*")), "media graph already exists")
    for path, expected in json.loads((HERE / "evidence/INSTALL.json").read_text()).items():
        require(sha(Path(path)) == expected, "installed artifact drift")
    with (HERE / "evidence/CONSUMED.json").open("x") as f:
        json.dump({"boot": Path("/proc/sys/kernel/random/boot_id").read_text().strip(),
                   "time_ns": time.time_ns()}, f)
    runtime = HERE / "runtime"
    runtime.mkdir()
    # Survives a lost PiMaster session. Normal completion also returns to Golden.
    run(["sudo", "-n", "systemd-run", "--unit=sp11-e004ew-golden-return",
         "--on-active=120s", "/usr/bin/systemctl", "reboot"])
    before = len(run(["sudo", "-n", "dmesg"]).splitlines())
    result = {"status": "FAIL", "protected_runtime": False, "gpio_outputs": "disabled",
              "frames_requested": 16, "stream_attempts": 0}
    media = None
    try:
        for mod in ("mc", "videodev", "v4l2_fwnode", "v4l2_async", "videobuf2_common",
                    "videobuf2_v4l2", "videobuf2_dma_sg", "i2c_qcom_cci"):
            run(["sudo", "-n", "modprobe", mod])
        run(["sudo", "-n", "insmod", BUILD / "modules/qcom-camss.ko",
             "e004j_ir_dphy_windows_parity=1"])
        run(["sudo", "-n", "insmod", BUILD / "modules/sp11-vd55g0-native.ko"])
        deadline = time.monotonic() + 12
        sensor = None
        while time.monotonic() < deadline:
            for node in sorted(Path("/dev").glob("media*")):
                graph = run(["media-ctl", "-d", node, "-p"], check=False)
                match = re.search(r"entity \d+: (sp11-vd55g0-native \d+-0060) \(", graph)
                if match and '-> "msm_csiphy0":0 [ENABLED,IMMUTABLE]' in graph:
                    media, sensor = node, match.group(1)
                    break
            if sensor:
                break
            time.sleep(0.1)
        require(sensor is not None, "sensor notifier did not complete")
        save("MEDIA-BEFORE.txt", graph)
        run(["media-ctl", "-d", media, "-r"])
        for link in ('"msm_csiphy0":1 -> "msm_csid0":0 [1]',
                     '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [1]'):
            run(["media-ctl", "-d", media, "-l", link])
        for entity, pad in ((sensor, 0), ("msm_csiphy0", 0), ("msm_csiphy0", 1),
                            ("msm_csid0", 0), ("msm_csid0", 1),
                            ("msm_vfe0_rdi0", 0), ("msm_vfe0_rdi0", 1)):
            run(["media-ctl", "-d", media, "-V",
                 f'"{entity}":{pad} [fmt:Y10_1X10/644x604 field:none]'])
        subdev = run(["media-ctl", "-d", media, "-e", sensor]).strip()
        controls = run(["v4l2-ctl", "-d", subdev, "--list-ctrls"])
        save("CONTROLS.txt", controls)
        require(re.search(r"digital_gain.*min=256.*max=2048.*default=256.*value=256", controls),
                "unity digital gain control unavailable")
        run(["v4l2-ctl", "-d", subdev, "--set-ctrl=test_pattern=0"])
        save("PATTERN-CONTROL.txt", run(["v4l2-ctl", "-d", subdev, "--get-ctrl=test_pattern"]))
        video = run(["media-ctl", "-d", media, "-e", "msm_vfe0_video0"]).strip()
        require(re.fullmatch(r"/dev/video\d+", video) is not None, "invalid video node")
        config = run(["v4l2-ctl", "-d", video,
                      "--set-fmt-video=width=644,height=604,pixelformat=Y10P",
                      "--get-fmt-video"])
        save("FORMAT.txt", config)
        require("Y10P" in config and re.search(r"Width/Height\s*:\s*644/604", config),
                "format was adjusted unexpectedly")
        stride = int(re.search(r"Bytes per Line\s*:\s*(\d+)", config).group(1))
        size = int(re.search(r"Size Image\s*:\s*(\d+)", config).group(1))
        require(stride >= 805 and size >= stride * 604, "invalid RAW10 buffer extent")
        save("MEDIA-CONFIGURED.txt", run(["media-ctl", "-d", media, "-p"]))
        result["stream_attempts"] = 1
        try:
            capture_log = run(["v4l2-ctl", "-d", video, "--verbose",
                               "--stream-mmap=4", "--stream-poll", "--stream-count=16",
                               "--stream-to=" + str(runtime / "frames.bin")], timeout=20)
            save("CAPTURE.txt", capture_log)
        except subprocess.CalledProcessError as exc:
            save("CAPTURE.txt", exc.stdout or "")
            raise
        except subprocess.TimeoutExpired as exc:
            output = exc.stdout or b""
            save("CAPTURE.txt", output.decode(errors="replace") if isinstance(output, bytes) else output)
            raise
        records = re.findall(r"cap dqbuf: \d+ seq:\s+(\d+) bytesused:\s+(\d+)", capture_log)
        require([int(seq) for seq, _ in records] == list(range(16)),
                "missing or nonconsecutive buffer sequences")
        require(all(int(used) == size for _, used in records), "short completed buffer")
        result["sequences"] = [int(seq) for seq, _ in records]
        raw = (runtime / "frames.bin").read_bytes()
        # v4l2-ctl writes bytesused per frame. Require the full expected extent
        # for this first validation rather than silently guessing row padding.
        require(len(raw) == 16 * size, "unexpected capture byte count")
        frame_hashes = [hashlib.sha256(raw[i * size:(i + 1) * size]).hexdigest()
                        for i in range(16)]
        require(any(raw), "capture contains only zero bytes")
        result.update(status="PASS_CAPTURE_PENDING_KERNEL_HEALTH", stride=stride,
                      sizeimage=size, captured_bytes=len(raw), frame_sha256=frame_hashes)
    except Exception as exc:
        result["error"] = str(exc)
    finally:
        if media and "error" not in result:
            try:
                save("MEDIA-AFTER.txt", run(["media-ctl", "-d", media, "-p"], check=False))
                run(["media-ctl", "-d", media, "-r"], check=False)
            except Exception as exc:
                result["route_cleanup_error"] = str(exc)
        time.sleep(2)
        try:
            log = "\n".join(run(["sudo", "-n", "dmesg"]).splitlines()[before:]) + "\n"
            save("KERNEL.txt", log)
            bad = bool(re.search(r"WARNING:|Call trace:|Oops:|BUG:|SError|IOMMU.*fault", log, re.I))
            result["kernel_fault_or_warning"] = bad
            result["sensor_stream_confirmed"] = "native RAW10 stream started; GPIO outputs disabled" in log
            result["test_pattern_verified"] = "native test pattern verified: Disabled" in log
            result["status_snapshots_verified"] = all("native status phase=" + phase + " pixel_clock=" in log for phase in ("initialized", "started", "before-stop")) and "read_error=" not in log
            result["digital_gain_verified"] = "native digital gain verified: 256/256" in log
            result["sensor_stop_confirmed"] = "name=STOP_STANDBY" in log and "stream stop failed" not in log
            sensor_paths = [p for p in Path("/sys/bus/i2c/devices").glob("*-0060")
                            if (p / "driver").is_symlink() and
                            (p / "driver").resolve().name == "sp11-vd55g0-native"]
            result["sensor_pm"] = {p.name: (p / "power/runtime_status").read_text().strip()
                                   for p in sensor_paths}
            if result["status"].startswith("PASS"):
                result["status"] = ("PASS_NATIVE_RAW10_CAPTURE" if not bad and result["status_snapshots_verified"] and result["test_pattern_verified"] and result["digital_gain_verified"] and result["sensor_stream_confirmed"] and
                                    result["sensor_stop_confirmed"] and result["sensor_pm"] and
                                    all(v == "suspended" for v in result["sensor_pm"].values())
                                    else "FAIL_HEALTH_OR_POWER")
        except Exception as exc:
            result["status"] = "FAIL_EVIDENCE"
            result["evidence_error"] = str(exc)
        save("RUNTIME-RESULT.json", json.dumps(result, indent=2) + "\n")
        print(json.dumps(result, indent=2), flush=True)
        # Let the completed tool response reach the client before reboot.
        reboot = ["sudo", "-n", "systemd-run", "--unit=sp11-e004ew-return-now",
                  "--on-active=5s", "/usr/bin/systemctl", "reboot"]
        if result.get("kernel_fault_or_warning"):
            reboot.append("--force")
        run(reboot)


def retire():
    run([REPO / "tools/camera-overlap-guard.sh", "--require-golden", "--require-no-camera-process"])
    verify_boot()
    require((HERE / "evidence/CONSUMED.json").exists(), "no consumed runtime")
    installed = json.loads((HERE / "evidence/INSTALL.json").read_text())
    # Delete only the exact candidate files recorded at installation.
    for path, expected in installed.items():
        p = Path(path)
        require(sha(p) == expected, "refusing to remove changed candidate file")
        run(["sudo", "-n", "rm", "--", p])
    run(["sudo", "-n", "rmdir", "--", BOOT])
    run(["sudo", "-n", "update-grub"], timeout=60)
    verify_boot()
    save("RETIRED.json", json.dumps({"status": "GOLDEN_RESTORED_CANDIDATE_RETIRED",
                                    "boot": Path("/proc/sys/kernel/random/boot_id").read_text().strip()},
                                   indent=2) + "\n")
    print("GOLDEN_RESTORED_CANDIDATE_RETIRED")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("action", choices=("install", "arm", "capture", "retire"))
    action = parser.parse_args().action
    globals()[action]()
