#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""One-shot front pattern calibration capture, run by systemd in the candidate boot.

Loads the qualified front param-queue camera modules, installs the private
startup profile only for the capture, runs the configured capture tool and always
returns to Golden through ExecStopPost. Pixels/records stay on SP11.
"""
import json, os, re, shutil, subprocess, sys, time
from pathlib import Path

D = Path(__file__).resolve().parent
CFG = json.loads((D / "run.json").read_text())
MARKER = CFG["marker"] + "=1"
GOLDEN = "sp11-audio-fullio-v19c"
FW = Path("/lib/firmware/qcom/sp11/imx681-2560x1440-nv12-v1.bin")


def run(args, timeout=25):
    return subprocess.check_output([str(x) for x in args], text=True, stderr=subprocess.STDOUT, timeout=timeout)


def save(r):
    (D / "RESULT.json").write_text(json.dumps(r, indent=1) + "\n")
    os.sync()


def need(ok, msg):
    if not ok:
        raise RuntimeError(msg)


def sensors():
    found = {}
    for path in Path("/sys/bus/i2c/devices").glob("*-*"):
        c = path / "of_node/compatible"
        if c.exists():
            v = c.read_bytes().rstrip(b"\0")
            if v in (b"sony,imx681", b"ovti,ov13858", b"microsoft,sp11-vd55g0"):
                found[v.decode()] = path
    return found


def idle_bound():
    s = sensors()
    return len(s) == 3 and all((p / "driver").is_symlink() and
                               (p / "power/runtime_status").read_text().strip() == "suspended" for p in s.values())


def main():
    os.umask(0o077)
    need(MARKER in Path("/proc/cmdline").read_text().split(), "candidate command line mismatch")
    fd = os.open(D / "CONSUMED", os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.write(fd, Path("/proc/sys/kernel/random/boot_id").read_bytes())
    os.close(fd)
    r = {"identity": CFG["identity"], "status": "STARTED",
         "boot_id": Path("/proc/sys/kernel/random/boot_id").read_text().strip(), "started_utc": time.time()}
    fw_installed = False
    try:
        run(["grub-reboot", GOLDEN])
        r["phase"] = "modules"; save(r)
        loaded = Path("/proc/modules").read_text()
        need(not any(re.search(r"^" + m + r" ", loaded, re.M) for m in
                     ["qcom_camss", "imx681", "ov13858", "sp11_vd55g0"]), "camera modules already loaded")
        need(not FW.exists(), "private profile unexpectedly present before capture")
        for m in ["i2c_qcom_cci", "mc", "videodev", "v4l2_async", "v4l2_fwnode", "videobuf2_common",
                  "videobuf2_memops", "videobuf2_v4l2", "videobuf2_dma_sg", "videobuf2_vmalloc", "v4l2_cci"]:
            run(["modprobe", m])
        FW.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(D / "imx681-2560x1440-nv12-v1.bin", FW)
        os.chmod(FW, 0o600)
        fw_installed = True
        for name in CFG.get("firmware_extra", []):  # own measured tables, removed after capture
            shutil.copyfile(D / name, FW.parent / name); os.chmod(FW.parent / name, 0o600)
        run(["insmod", D / "modules/qcom-camss.ko", *CFG["camss_params"]])
        for name in ["ov13858", "imx681", "sp11-vd55g0"]:
            run(["insmod", D / ("modules/" + name + ".ko")])
        for _ in range(400):
            if idle_bound():
                break
            time.sleep(0.05)
        need(idle_bound(), "sensors bound and suspended")
        # Sensor binding precedes media-graph completion; wait for the complete
        # graph (front sensor and parameter node) before libcamera enumerates.
        graph_ok = False
        for _ in range(100):
            for media in Path("/dev").glob("media*"):
                try:
                    g = run(["media-ctl", "-d", media, "-p"])
                except Exception:
                    continue
                if "imx681 " in g and "msm_vfe1_params" in g and "ov13858 " in g:
                    graph_ok = True
            if graph_ok:
                break
            time.sleep(0.1)
        need(graph_ok, "complete media graph")
        time.sleep(1.0)
        r["phase"] = "capture"; save(r)
        out = D / "private-pattern"
        out.mkdir(mode=0o700)
        env = dict(os.environ, LD_LIBRARY_PATH=str(D / "lib"), LIBCAMERA_IPA_MODULE_PATH=str(D / "ipa"),
                   LIBCAMERA_IPA_PROXY_PATH=str(D / "proxy"), LIBCAMERA_PIPELINES_MATCH_LIST="camss-x1e",
                   LIBCAMERA_LOG_LEVELS=CFG.get("log_levels", "CAMSSX1E:DEBUG,Camera:INFO"),
                   LIBCAMERA_IPA_FORCE_ISOLATION="1",
                   SP11_PATTERN_DIR=str(out), SP11_PATTERN_FRAMES_PER_PHASE=str(CFG["frames_per_phase"]))
        if CFG.get("tuning"):
            env["LIBCAMERA_CAMSS_X1E_TUNING_FILE"] = str(D / CFG["tuning"])
        env.update(CFG.get("env", {}))
        stderr = open(D / "PRIVATE-CAPTURE-STDERR.txt", "w")
        p = subprocess.run([str(D / CFG.get("capture", "capture-front-pattern"))], stdout=subprocess.PIPE,
                           stderr=stderr, text=True, timeout=CFG["capture_timeout"], env=env)
        stderr.close()
        (D / "PRIVATE-CAPTURE-STDOUT.txt").write_text(p.stdout)
        r["capture_exit"] = p.returncode
        if p.stdout.strip():
            try:
                r["capture"] = json.loads(p.stdout.strip().splitlines()[-1])
            except ValueError:
                pass
        text = (D / "PRIVATE-CAPTURE-STDERR.txt").read_text(errors="replace")
        r["meter_lines"] = text.count("CAMSS_X1E_IPA_METER")
        r["error_lines"] = len(re.findall(r" ERROR ", text))
        for _ in range(100):
            if idle_bound():
                break
            time.sleep(0.05)
        r["sensors_idle_after"] = idle_bound()
        need(p.returncode == 0, "capture failed")
        r["status"] = "PASS_" + CFG["identity"]
    except Exception as exc:
        r["status"] = "FAIL_" + CFG["identity"]
        r["error"] = str(exc)
    finally:
        if fw_installed:
            try:
                FW.unlink()
            except OSError:
                pass
        for name in CFG.get("firmware_extra", []):
            try:
                (FW.parent / name).unlink()
            except OSError:
                pass
        r["private_profile_removed"] = not FW.exists()
        try:
            dm = run(["dmesg"])
            (D / "PRIVATE-DMESG.txt").write_text(dm)
            r["kernel_oops"] = len(re.findall(r"(Oops|BUG:|Call trace|WARNING: CPU)", dm))
        except Exception:
            pass
        r["finished_utc"] = time.time(); r["phase"] = "return_Golden"; save(r)
    print(json.dumps({k: r.get(k) for k in ("status", "error", "capture_exit")}))
    if not r["status"].startswith("PASS"):
        sys.exit(1)


if __name__ == "__main__":
    main()
