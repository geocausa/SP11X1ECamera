#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Prepare fresh private NV12 boot assets. Does not arm or reboot."""
import hashlib
import json
import shlex
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
PROJECT = ROOT.parents[1]
BUILD = PROJECT / "02-kernel/native-front-param-queue-20261010-03"
MODULES = PROJECT / "02-kernel/native-rgb-front-param-queue-20261010-36"
D = Path("/var/lib/sp11-camera-native-front-param-queue-20261010-03")
B = Path("/boot/sp11-7.1.5-camera-native-front-param-queue-20261010-03")
G = Path("/etc/grub.d/99zzzzzz_sp11_camera_native_front_param_queue_20261010_03")
S = Path("/etc/systemd/system/sp11-camera-native-front-param-queue-20261010-03.service")
T=Path(str(S).replace(".service","-watchdog.timer"))
W=Path(str(S).replace(".service","-watchdog.service"))
ID = "sp11-camera-native-front-param-queue-20261010-03"
LIBBUILD = PROJECT / "02-kernel/libcamera-native-front-param-queue-20261010-16"
F = Path("/lib/firmware/qcom/sp11/imx681-2560x1440-nv12-v1.bin")
GOLDEN = Path("/boot/sp11-7.1.5-audio-fullio-v19c")

def run(args):
    return subprocess.check_output([str(x) for x in args], text=True)
def sudo(*args):
    return run(["sudo", "-n", *args])
def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()
def copy(source, destination, mode="0600"):
    sudo("install", "-m", mode, source, destination)
def write(text, destination, mode="0700"):
    temporary = BUILD / (destination.name + ".install-input")
    assert not temporary.exists()
    temporary.write_text(text)
    copy(temporary, destination, mode)

def main():
    run([ROOT / "tools/camera-overlap-guard.sh", "--require-clean-tracked",
         "--require-golden", "--require-no-camera-process"])
    assert ROOT.name == "SP11X1ECamera-driver"
    need_head = run(["git", "-C", ROOT, "rev-parse", "HEAD"]).strip()
    assert need_head == run(["git", "-C", ROOT, "rev-parse", "origin/work/native-rgb-driver-20261007"]).strip()
    for path in (D, B, G, S, T, W, F, Path(str(F) + ".native-profile-negative")):
        assert subprocess.run(["sudo", "-n", "test", "!", "-e", str(path)]).returncode == 0
    assert ID not in sudo("cat", "/boot/grub/grub.cfg")
    BUILD.mkdir(parents=True, exist_ok=False)
    build = json.loads((MODULES / "build-result.json").read_text())
    assert build["status"] == "PASS_NATIVE_SOURCE_BUILD_NOT_INSTALLED"
    for relative, entry in build["modules"].items():
        assert sha(MODULES / relative) == entry["sha256"]
        assert run(["modinfo", "-F", "vermagic", MODULES / relative]).strip() == entry["vermagic"]
    for relative, expected in build["staged_sources"].items():
        assert sha(MODULES / relative) == expected
    dtb = PROJECT / "02-kernel/native-pipeline-20261007-05/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb"
    assert sha(dtb) == "3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb"
    ir = ROOT / "src/sp11-camera-stack/authority/sp11-vd55g0-production.ko"
    assert sha(ir) == "4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72"
    assert build["nv12_trial_staged"] is True
    assert build["front_owner_trial_staged"] is True
    assert build["front_queue_trial_staged"] is True
    assert build["front_meta_trial_staged"] is True
    assert build["front_params_trial_staged"] is True
    assert build["front_profile_trial_staged"] is True
    assert build["front_sof_trial_staged"] is True
    assert build["front_control_trace_trial_staged"] is True
    assert build["front_param_queue_trial_staged"] is True
    assert "native_front_param_queue_trial:" in run(["modinfo", "-p", MODULES / "camss/qcom-camss.ko"])
    assert "native_control_timing_readback:" in run(["modinfo", "-p", MODULES / "imx681/imx681.ko"])
    profile = PROJECT / "02-kernel/native-front-profile-20261007-01/imx681-2560x1440-nv12-v1.bin"
    assert profile.stat().st_size == 36744
    assert sha(profile) == "c59a54b760a8662af650fa8961aab2224c7c0d2a0cdcdea3c9581370ac5ddd03"
    assert run(["modinfo", "-F", "firmware", MODULES / "camss/qcom-camss.ko"]).strip() == "qcom/sp11/imx681-2560x1440-nv12-v1.bin"
    library = json.loads((LIBBUILD / "native-rgb-build-result.json").read_text())
    assert library["status"] == "PASS_LIBCAMERA_NATIVE_FRONT_PIPELINE_NOT_INSTALLED"
    for relative, expected in library["built_outputs"].items():
        assert sha(LIBBUILD / relative) == expected
    source = PROJECT / "06-camera/reference/libcamera-native-front-param-queue-20261010-16"
    for relative, expected in library["staged_sources"].items():
        assert sha(source / relative) == expected
    assert sha(source / "src/libcamera/pipeline/camss-x1e/camss-x1e.cpp") == sha(ROOT / "src/native-rgb/libcamera/camss-x1e.cpp")
    assert sha(source / "src/libcamera/pipeline/camss-x1e/camss-x1e-admission.h") == sha(ROOT / "src/native-rgb/libcamera/camss-x1e-admission.h")
    assert len(library["tests"])==12 and sum(p["result"]=="OK" for p in library["tests"])==10
    assert {p["name"] for p in library["tests"] if p["result"]=="SKIP"}=={"controls - libcamera:control_info_map","controls - libcamera:control_list"}
    assert all(p["result"] in ["OK","SKIP"] for p in library["tests"])
    assert not library["compiler_warning_lines"]
    assert sha(source/"src/ipa/libipa/front-aec-decoder.h")==sha(ROOT/"src/native-rgb/front-meter/front-aec-decoder.h")
    assert json.loads((PROJECT/"02-kernel/native-front-meter-20261010-01/hosted-decoder.json").read_text())["status"]=="PASS_FRONT_RAW_SUM_COUNT_DECODER"
    run(["python3","-c","import numpy"])
    assert library["DelayedControls_runtime_integrated"] is True
    assert library["ipa_runtime_implemented"] is True
    assert library["automatic_feedback_enabled"] is False
    assert sha(source / "src/ipa/camss-x1e/camss-x1e.cpp") == sha(ROOT / "src/native-rgb/libcamera/camss-x1e-ipa.cpp")
    binary = LIBBUILD / "src/apps/cam/cam"
    run([binary, "--help"]) # No enumeration or capture on Golden.

    sudo("install", "-d", "-m", "0700", D, D / "modules", D / "lib", D / "ipa", D / "proxy")
    sudo("install", "-d", "-m", "0755", F.parent)
    assets = []
    pairs = [
        (binary, D / "cam", "0700"),
        (LIBBUILD / "src/ipa/camss-x1e/ipa_camss_x1e.so", D / "ipa/ipa_camss_x1e.so", "0600"),
        (LIBBUILD / "src/ipa/camss-x1e/ipa_camss_x1e.so.sign", D / "ipa/ipa_camss_x1e.so.sign", "0600"),
        (LIBBUILD / "src/libcamera/proxy/worker/camss_x1e_ipa_proxy", D / "proxy/camss_x1e_ipa_proxy", "0700"),
        (LIBBUILD / "src/libcamera/libcamera.so.0.7.0", D / "lib/libcamera.so.0.7", "0600"),
        (LIBBUILD / "src/libcamera/base/libcamera-base.so.0.7.0", D / "lib/libcamera-base.so.0.7", "0600"),
        (ROOT / "src/native-rgb/front-param-queue/run03.py", D / "run-once.py", "0700"),
        (ROOT / "src/native-rgb/front-request-controls/checks.py", D / "checks.py", "0600"),
        (ROOT / "src/native-rgb/front-param-queue/controls03.yaml", D / "controls.yaml", "0600"),
        (ROOT / "src/native-rgb/front-param-queue/gamma-response.py", D / "gamma-response.py", "0600"),
        (ROOT / "src/native-rgb/front-param-queue/route-contract.py", D / "route-contract.py", "0600"),
        (ROOT / "src/native-rgb/front-request-controls/route-contract.py", D / "base-route-contract.py", "0600"),
        (profile, D / "imx681-2560x1440-nv12-v1.bin", "0600"),
        (profile, F, "0600"),
        (MODULES / "camss/qcom-camss.ko", D / "modules/qcom-camss.ko", "0600"),
        (MODULES / "imx681/imx681.ko", D / "modules/imx681.ko", "0600"),
        (MODULES / "ov13858/ov13858.ko", D / "modules/ov13858.ko", "0600"),
        (ir, D / "modules/sp11-vd55g0.ko", "0600"),
    ]
    base = ROOT / "experiments/E004-front-ir-vd55g0/e004mg-private-optical-rgb-visual-one-shot"
    for name in ("discover-unified.py",):
        pairs.append((base / name, D / name, "0600"))
    for source, destination, mode in pairs:
        copy(source, destination, mode)
        assets.append(sha(source) + "  " + str(destination))
    sudo("install", "-d", "-m", "0755", B)
    protected = {}
    for name in ("vmlinuz-7.1.5-sp11-render-parity-v4+", "initrd.img-7.1.5-sp11-fullio-v19c"):
        original = GOLDEN / name
        protected[str(original)] = sudo("sha256sum", original).split()[0]
        copy(original, B / name, "0644")
        assert sudo("sha256sum", B / name).split()[0] == protected[str(original)]
        assets.append(protected[str(original)] + "  " + str(B / name))
    original_dtb = GOLDEN / "x1e80100-microsoft-denali-sp11-fullio-v19c.dtb"
    protected[str(original_dtb)] = sudo("sha256sum", original_dtb).split()[0]
    copy(dtb, B / dtb.name, "0644")
    assets.append(sha(dtb) + "  " + str(B / dtb.name))

    command = shlex.split(Path("/proc/cmdline").read_text())
    assert any(x.startswith("BOOT_IMAGE=/boot/sp11-7.1.5-audio-fullio-v19c/") for x in command)
    existing_blacklist = []
    for value in command:
        if value.startswith("modprobe.blacklist="):
            existing_blacklist.extend(value.split("=", 1)[1].split(","))
    command = [x for x in command if not x.startswith(
        ("BOOT_IMAGE=", "sp11_entry=", "modprobe.blacklist=", "log_buf_len="))]
    command += ["log_buf_len=4M", "sp11_entry=7.1.5-sp11-camera-native-front-param-queue-20261010-03",
                "sp11_camera_native_front_param_queue_20261010_03=1",
                "modprobe.blacklist=" + ",".join(dict.fromkeys(existing_blacklist + [
                    "qcom_camss", "imx681", "ov13858", "sp11_vd55g0", "vd55g0"]))]
    uuid = run(["findmnt", "-n", "-o", "UUID", "/"]).strip()
    assert uuid == "33e842b7-0434-4749-b03a-299bdcdb8b9f"
    grub = f"""#!/bin/sh
exec tail -n +3 $0
menuentry 'SP11 native front NV12 — one use' --id '{ID}' {{
 load_video
 set gfxpayload=keep
 insmod gzio
 insmod part_gpt
 insmod ext2
 insmod fdt
 search --no-floppy --fs-uuid --set=root {uuid}
 devicetree {B}/{dtb.name}
 linux {B}/vmlinuz-7.1.5-sp11-render-parity-v4+ {' '.join(shlex.quote(x) for x in command)}
 initrd {B}/initrd.img-7.1.5-sp11-fullio-v19c
}}
"""
    syntax = BUILD / "grub-syntax.txt"
    syntax.write_text("\n".join(grub.splitlines()[2:]) + "\n")
    run(["grub-script-check", syntax])
    write(grub, G, "0755")
    returning = f"""#!/usr/bin/env bash
set -Eeuo pipefail
if grep -qw 'sp11_camera_native_front_param_queue_20261010_03=1' /proc/cmdline; then
  if test "${{FRONT_METER_WATCHDOG:-0}}" = 1; then
    printf "WATCHDOG\\n" > {D}/WATCHDOG-FIRED
  else
    printf 'service_result=%s\\nexit_code=%s\\nexit_status=%s\\n' "${{SERVICE_RESULT:-unknown}}" "${{EXIT_CODE:-unknown}}" "${{EXIT_STATUS:-unknown}}" > {D}/SERVICE-RESULT.txt
  fi
  if test -f {F}.native-profile-negative; then
    install -m 0600 {D}/imx681-2560x1440-nv12-v1.bin {F}
    rm {F}.native-profile-negative
  fi
  dmesg > {D}/PRIVATE-DMESG.txt
  grub-reboot sp11-audio-fullio-v19c
  sync
  if test "${{FRONT_METER_WATCHDOG:-0}}" = 1; then
    systemctl reboot --force --force
  else
    systemctl reboot --no-block
  fi
fi
"""
    write(returning, D / "return-golden.sh")
    assets.append(sudo("sha256sum", D / "return-golden.sh").split()[0] +
                  "  " + str(D / "return-golden.sh"))
    unit = f"""[Unit]
Description=SP11 standard libcamera front capture qualification, one use
Wants=grub-initrd-fallback.service grub2-common.service
After=grub-initrd-fallback.service grub2-common.service
Before=display-manager.service
ConditionKernelCommandLine=sp11_camera_native_front_param_queue_20261010_03=1

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {D}/run-once.py
ExecStopPost={D}/return-golden.sh
TimeoutStartSec=300
TimeoutStopSec=10
KillMode=control-group

[Install]
WantedBy=multi-user.target
"""
    watchdog=f"""[Unit]
Description=SP11 front meter independent return watchdog
ConditionKernelCommandLine=sp11_camera_native_front_param_queue_20261010_03=1

[Service]
Type=oneshot
Environment=FRONT_METER_WATCHDOG=1
ExecStart={D}/return-golden.sh
"""
    timer=f"""[Unit]
Description=SP11 front gamma360-second return deadline
ConditionKernelCommandLine=sp11_camera_native_front_param_queue_20261010_03=1

[Timer]
OnBootSec=360
Unit={W.name}
AccuracySec=1

[Install]
WantedBy=timers.target
"""
    for text,path in [(watchdog,W),(timer,T)]:
        write(text,path,"0644")
        assets.append(sudo("sha256sum",path).split()[0]+"  "+str(path))
    write(unit, S, "0644")
    assets.append(sudo("sha256sum", S).split()[0] + "  " + str(S))
    assets.append(sudo("sha256sum", G).split()[0] + "  " + str(G))
    from math import isqrt
    linear=[(n*1023+128)//256 for n in range(257)]
    lift=[min(1023,isqrt(n*1023*1023//256)) for n in range(257)]
    for label in ("linear-before","lift-red","lift-green","lift-blue","linear-after"):
        sd=D/label
        sudo("install","-d","-m","0700",sd)
        for name in ("lib","ipa","proxy","cam","ASSETS.sha256","controls.yaml"):
            sudo("ln","-s",str(D/name),str(sd/name))
        channels={k:linear[:] for k in ("gamma_r","gamma_g","gamma_b")}
        channel={"lift-red":"gamma_r","lift-green":"gamma_g","lift-blue":"gamma_b"}.get(label)
        if channel:channels[channel]=lift[:]
        text="version: 1\nsensor: imx681\nlayout: rgb257-u10\n"
        text+="".join(k+": ["+", ".join(map(str,v))+"]\n" for k,v in channels.items())
        temporary=BUILD/(label+".tuning.install-input")
        assert not temporary.exists()
        temporary.write_text(text)
        copy(temporary,sd/"tuning.yaml","0600")
        assets.append(sudo("sha256sum",sd/"tuning.yaml").split()[0]+"  "+str(sd/"tuning.yaml"))
    write("\n".join(assets) + "\n", D / "ASSETS.sha256", "0600")
    write(run(["git", "-C", ROOT, "rev-parse", "HEAD"]), D / "EXPECTED-HEAD", "0600")
    write(json.dumps(protected, indent=2) + "\n", D / "GOLDEN-ASSET-HASHES.json", "0600")
    sudo("systemd-analyze", "verify", S, W, T)
    sudo("systemctl", "daemon-reload")
    sudo("systemctl", "enable", S.name,T.name)
    sudo("update-grub")
    assert ID in sudo("cat", "/boot/grub/grub.cfg")
    assert "saved_entry=sp11-audio-fullio-v19c" in sudo("grub-editenv", "/boot/grub/grubenv", "list")
    run([ROOT / "tools/camera-overlap-guard.sh", "--require-clean-tracked",
         "--require-golden", "--require-no-camera-process"])
    print("PASS_NV12_CANDIDATE_PREPARED_UNARMED_NO_STREAM_NO_REBOOT")
if __name__ == "__main__":
    main()
