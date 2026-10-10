#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Install (not arm) a one-shot SP11 front camera run from a JSON config.

Golden stays the saved default. The candidate entry uses the Golden kernel and
initrd with the camera device tree, blacklists camera autoload, and its runner
always returns to Golden (ExecStopPost plus an independent watchdog timer).
Arm with: grub-reboot <id> && systemctl reboot
"""
import hashlib, json, shlex, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = Path("/home/geoca/Documents/SP11-PROJECT")
GOLDEN = Path("/boot/sp11-7.1.5-audio-fullio-v19c")
KERNEL = "vmlinuz-7.1.5-sp11-render-parity-v4+"
INITRD = "initrd.img-7.1.5-sp11-fullio-v19c"
DTB_SRC = PROJECT / "02-kernel/native-pipeline-20261007-05/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb"
DTB_SHA = "3d56fd6f610576dee5fc97da809f9c48da16952af9a48a5053ea864b94855beb"
PROFILE = PROJECT / "02-kernel/native-front-profile-20261007-01/imx681-2560x1440-nv12-v1.bin"
PROFILE_SHA = "c59a54b760a8662af650fa8961aab2224c7c0d2a0cdcdea3c9581370ac5ddd03"
IR = PROJECT / "06-camera/SP11X1ECamera-driver/src/sp11-camera-stack/authority/sp11-vd55g0-production.ko"
GOLDEN_SHA = {"vmlinuz": "bca0a336", "initrd": "ac3ba64b"}


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def sh(*a):
    return subprocess.check_output([str(x) for x in a], text=True)


def install(src, dst, mode):
    shutil.copyfile(src, dst)
    Path(dst).chmod(mode)


def main():
    cfg = json.loads(Path(sys.argv[1]).read_text())
    ident, marker = cfg["id"], cfg["marker"]
    D = Path("/var/lib") / ident
    BOOT = Path("/boot") / ident
    G = Path("/etc/grub.d/99zzzzzz_" + ident.replace("-", "_"))
    S = Path("/etc/systemd/system") / (ident + ".service")
    WS = Path("/etc/systemd/system") / (ident + "-watchdog.service")
    WT = Path("/etc/systemd/system") / (ident + "-watchdog.timer")
    assert sh("id", "-u").strip() == "0"
    assert not (D / "CONSUMED").exists(), "identity already consumed; pick a new one"
    assert sha(GOLDEN / KERNEL).startswith(GOLDEN_SHA["vmlinuz"])
    assert sha(GOLDEN / INITRD).startswith(GOLDEN_SHA["initrd"])
    assert sha(DTB_SRC) == DTB_SHA and sha(PROFILE) == PROFILE_SHA
    assert not Path("/lib/firmware/qcom/sp11/imx681-2560x1440-nv12-v1.bin").exists()
    mods = Path(cfg["modules"])
    lib = Path(cfg["libbuild"])
    if D.exists():
        shutil.rmtree(D)
    for d in (D, D / "modules", D / "lib", D / "ipa", D / "proxy"):
        d.mkdir(mode=0o700, parents=True)
    pairs = [
        (mods / "camss/qcom-camss.ko", D / "modules/qcom-camss.ko", 0o600),
        (mods / "imx681/imx681.ko", D / "modules/imx681.ko", 0o600),
        (mods / "ov13858/ov13858.ko", D / "modules/ov13858.ko", 0o600),
        (IR, D / "modules/sp11-vd55g0.ko", 0o600),
        (lib / "src/ipa/camss-x1e/ipa_camss_x1e.so", D / "ipa/ipa_camss_x1e.so", 0o600),
        (lib / "src/ipa/camss-x1e/ipa_camss_x1e.so.sign", D / "ipa/ipa_camss_x1e.so.sign", 0o600),
        (lib / "src/libcamera/proxy/worker/camss_x1e_ipa_proxy", D / "proxy/camss_x1e_ipa_proxy", 0o700),
        (lib / "src/libcamera/libcamera.so.0.7.0", D / "lib/libcamera.so.0.7", 0o600),
        (lib / "src/libcamera/base/libcamera-base.so.0.7.0", D / "lib/libcamera-base.so.0.7", 0o600),
        (PROFILE, D / "imx681-2560x1440-nv12-v1.bin", 0o600),
        (HERE / "run-front-pattern.py", D / "run.py", 0o700),
    ]
    for src, dst in cfg.get("extra", {}).items():
        pairs.append((Path(src), D / dst, 0o700 if dst.startswith("capture") else 0o600))
    for src, dst, mode in pairs:
        install(src, dst, mode)
    (D / "run.json").write_text(json.dumps(cfg, indent=1) + "\n")
    BOOT.mkdir(mode=0o755, exist_ok=True)
    install(DTB_SRC, BOOT / DTB_SRC.name, 0o644)
    command = shlex.split(Path("/proc/cmdline").read_text())
    assert any(x.startswith("BOOT_IMAGE=" + str(GOLDEN) + "/") for x in command), "run from Golden"
    command = [x for x in command if not x.startswith(("BOOT_IMAGE=", "sp11_entry=", "modprobe.blacklist=", "log_buf_len="))]
    command += ["log_buf_len=4M", "sp11_entry=7.1.5-" + ident, marker + "=1",
                "modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0"]
    uuid = sh("findmnt", "-n", "-o", "UUID", "/").strip()
    grub = f"""#!/bin/sh
exec tail -n +3 $0
menuentry '{cfg.get("title", ident)} - one use' --id '{ident}' {{
 load_video
 set gfxpayload=keep
 insmod gzio
 insmod part_gpt
 insmod ext2
 insmod fdt
 search --no-floppy --fs-uuid --set=root {uuid}
 devicetree {BOOT}/{DTB_SRC.name}
 linux {GOLDEN}/{KERNEL} {' '.join(shlex.quote(x) for x in command)}
 initrd {GOLDEN}/{INITRD}
}}
"""
    syntax = D / "grub-syntax.txt"
    syntax.write_text("\n".join(grub.splitlines()[2:]) + "\n")
    sh("grub-script-check", syntax)
    G.write_text(grub)
    G.chmod(0o755)
    ret = f"""#!/usr/bin/env bash
set -Eeuo pipefail
if grep -qw '{marker}=1' /proc/cmdline; then
  rm -f /lib/firmware/qcom/sp11/imx681-2560x1440-nv12-v1.bin
  grub-reboot sp11-audio-fullio-v19c
  if test "${{RUN_WATCHDOG:-0}}" = 1; then
    echo WATCHDOG > {D}/WATCHDOG-FIRED; dmesg > {D}/PRIVATE-WATCHDOG-DMESG.txt; sync
    systemctl reboot --force --force
  else
    printf 'service_result=%s exit_status=%s\\n' "${{SERVICE_RESULT:-?}}" "${{EXIT_STATUS:-?}}" > {D}/SERVICE-RESULT.txt; sync
    systemctl reboot --no-block
  fi
fi
"""
    (D / "return-golden.sh").write_text(ret)
    (D / "return-golden.sh").chmod(0o700)
    S.write_text(f"""[Unit]
Description=SP11 front camera run {ident}, one candidate use
ConditionKernelCommandLine={marker}=1
Before=display-manager.service
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 {D}/run.py
ExecStopPost={D}/return-golden.sh
TimeoutStartSec={cfg["capture_timeout"] + 120}
TimeoutStopSec=15
KillMode=control-group
[Install]
WantedBy=multi-user.target
""")
    WS.write_text(f"""[Unit]
Description=SP11 front run independent Golden-return watchdog
ConditionKernelCommandLine={marker}=1
[Service]
Type=oneshot
Environment=RUN_WATCHDOG=1
ExecStart={D}/return-golden.sh
""")
    WT.write_text(f"""[Unit]
Description=SP11 front run return deadline
ConditionKernelCommandLine={marker}=1
[Timer]
OnBootSec={cfg["watchdog_seconds"]}
Unit={WS.name}
AccuracySec=1
[Install]
WantedBy=timers.target
""")
    sh("systemd-analyze", "verify", S, WS, WT)
    sh("systemctl", "daemon-reload")
    sh("systemctl", "enable", S.name, WT.name)
    sh("update-grub")
    assert f"--id '{ident}'" in Path("/boot/grub/grub.cfg").read_text()
    env = sh("grub-editenv", "/boot/grub/grubenv", "list")
    assert "saved_entry=sp11-audio-fullio-v19c" in env
    print("INSTALLED_NOT_ARMED", ident)


if __name__ == "__main__":
    main()
