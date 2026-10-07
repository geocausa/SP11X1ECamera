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
BUILD = PROJECT / "02-kernel/native-owner-20261007-02"
MODULES = PROJECT / "02-kernel/native-rgb-20261007-audit-16"
D = Path("/var/lib/sp11-camera-native-owner-20261007-02")
B = Path("/boot/sp11-7.1.5-camera-native-owner-20261007-02")
G = Path("/etc/grub.d/99zzzzzz_sp11_camera_native_owner_20261007_02")
S = Path("/etc/systemd/system/sp11-camera-native-owner-20261007-02.service")
ID = "sp11-camera-native-owner-20261007-02"
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
    temporary.write_text(text)
    copy(temporary, destination, mode)

def main():
    run([ROOT / "tools/camera-overlap-guard.sh", "--require-clean-tracked",
         "--require-golden", "--require-no-camera-process"])
    assert ROOT.name == "SP11X1ECamera-driver"
    for path in (D, B, G, S):
        assert subprocess.run(["sudo", "-n", "test", "!", "-e", str(path)]).returncode == 0
    assert ID not in sudo("cat", "/boot/grub/grub.cfg")
    build = json.loads((MODULES / "build-result.json").read_text())
    assert build["status"] == "PASS_NATIVE_SOURCE_BUILD_NOT_INSTALLED"
    for relative, entry in build["modules"].items():
        assert sha(MODULES / relative) == entry["sha256"]
        assert run(["modinfo", "-F", "vermagic", MODULES / relative]).strip() == entry["vermagic"]
    for relative, expected in build["staged_sources"].items():
        assert sha(MODULES / relative) == expected
    dtb = BUILD / "x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb"
    assert sha(dtb) == "3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb"
    ir = ROOT / "src/sp11-camera-stack/authority/sp11-vd55g0-production.ko"
    assert sha(ir) == "4839415eadc41f541606b334d64f06678eada3b8c4ef7e9faf57565b18a65a72"
    assert build["nv12_trial_staged"] is True
    assert build["front_owner_trial_staged"] is True
    bootstrap = ROOT.parent / "SP11X1ECamera-clean/src/front-imx681/userspace/iq/authority/r4-bootstrap.bin"
    assert bootstrap.stat().st_size == 41088
    assert sha(bootstrap) == "1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa"
    checker = BUILD / "audit-bootstrap"
    run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-O2",
         ROOT / "src/native-rgb/front-nv12/audit-bootstrap.c", "-o", checker])
    assert json.loads(run([checker, bootstrap]))["status"] == "PASS_LOCAL_BOOTSTRAP_NATIVE_NV12_TRANSFORM"
    binary = BUILD / "native-nv12-probe"
    run(["cc", "-std=c11", "-Wall", "-Wextra", "-Werror", "-O2",
         ROOT / "src/native-rgb/front-owner/probe.c", "-lm", "-o", binary])
    # A Golden invocation must refuse before opening any device.
    assert subprocess.run(["sudo", "-n", str(binary), "/dev/nonexistent", "/dev/nonexistent", "/dev/nonexistent"]).returncode == 1

    sudo("install", "-d", "-m", "0700", D, D / "modules")
    assets = []
    pairs = [
        (binary, D / "native-nv12-probe", "0700"),
        (ROOT / "src/native-rgb/front-owner/run-once.py", D / "run-once.py", "0700"),
        (ROOT / "src/native-rgb/front-owner/route-contract.py", D / "route-contract.py", "0600"),
        (bootstrap, D / "r4-bootstrap.bin", "0600"),
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
        ("BOOT_IMAGE=", "sp11_entry=", "modprobe.blacklist="))]
    command += ["sp11_entry=7.1.5-sp11-camera-native-owner-20261007-02",
                "sp11_camera_native_owner_20261007_02=1",
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
if grep -qw 'sp11_camera_native_owner_20261007_02=1' /proc/cmdline; then
  printf 'service_result=%s\\nexit_code=%s\\nexit_status=%s\\n' "${{SERVICE_RESULT:-unknown}}" "${{EXIT_CODE:-unknown}}" "${{EXIT_STATUS:-unknown}}" > {D}/SERVICE-RESULT.txt
  dmesg > {D}/PRIVATE-DMESG.txt
  grub-reboot sp11-audio-fullio-v19c
  sync
  systemctl reboot --no-block
fi
"""
    write(returning, D / "return-golden.sh")
    assets.append(sudo("sha256sum", D / "return-golden.sh").split()[0] +
                  "  " + str(D / "return-golden.sh"))
    unit = f"""[Unit]
Description=SP11 native front NV12 diagnostic, one use
Wants=grub-initrd-fallback.service grub2-common.service
After=grub-initrd-fallback.service grub2-common.service
Before=display-manager.service
ConditionKernelCommandLine=sp11_camera_native_owner_20261007_02=1

[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {D}/run-once.py
ExecStopPost={D}/return-golden.sh
TimeoutStartSec=90
TimeoutStopSec=10
KillMode=control-group

[Install]
WantedBy=multi-user.target
"""
    write(unit, S, "0644")
    assets.append(sudo("sha256sum", S).split()[0] + "  " + str(S))
    assets.append(sudo("sha256sum", G).split()[0] + "  " + str(G))
    write("\n".join(assets) + "\n", D / "ASSETS.sha256", "0600")
    write(run(["git", "-C", ROOT, "rev-parse", "HEAD"]), D / "EXPECTED-HEAD", "0600")
    write(json.dumps(protected, indent=2) + "\n", D / "GOLDEN-ASSET-HASHES.json", "0600")
    sudo("systemd-analyze", "verify", S)
    sudo("systemctl", "daemon-reload")
    sudo("systemctl", "enable", S.name)
    sudo("update-grub")
    assert ID in sudo("cat", "/boot/grub/grub.cfg")
    assert "saved_entry=sp11-audio-fullio-v19c" in sudo("grub-editenv", "/boot/grub/grubenv", "list")
    run([ROOT / "tools/camera-overlap-guard.sh", "--require-clean-tracked",
         "--require-golden", "--require-no-camera-process"])
    print("PASS_NV12_CANDIDATE_PREPARED_UNARMED_NO_STREAM_NO_REBOOT")
if __name__ == "__main__":
    main()
