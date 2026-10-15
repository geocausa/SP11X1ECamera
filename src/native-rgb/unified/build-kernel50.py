#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build camss module 50 = module 49 with the open rear start-up path.

Changes (rear only; the front path is untouched):
 * e006o steady singletons: PDPC, GIC and the GTM tone mapper switched off
   (enable bit 0 cleared, every other configuration register of those modules
   0, the 262 GTM curve registers included); BPC_ABF registers set to the open
   values measured on the front IFE (front-ae/tuning/imx681-front-isp-regs.txt).
 * e007u BPC_ABF noise LUT: 65 points generated from our rear noise model
   (front-ae/tuning/ov13858-rear-abf-v1.json, open-profile/gen-abf-lut.py).
 * The rear loader reads qcom/sp11/ov13858-rear-open-v1.bin (gen-rear-open-input.py)
   and admits only that file's SHA-256.
Usage: build-kernel50.py <rear-open-input.bin> <ov13858-rear-abf-v1.json> [out-dir]. No install.
"""
import hashlib, json, re, shutil, subprocess, sys
from pathlib import Path

PROJECT = Path("/home/geoca/Documents/SP11-PROJECT")
BASE = PROJECT / "02-kernel/native-rgb-unified-49"
OUT = Path(sys.argv[3]) if len(sys.argv) > 3 else PROJECT / "02-kernel/native-rgb-unified-50"
KSOURCE = PROJECT / "02-kernel/e003i-front-production-src"
KOUTPUT = PROJECT / "02-kernel/build-runtime-v4-headers-20260826"

OFF = [(0x3D60, 0x3E00), (0x4760, 0x4800), (0x5A60, 0x5F00)]  # PDPC, GIC, GTM
ABF = {0x4960: 0x101, 0x4968: 0x4, 0x496C: 0x0, 0x4980: 0x0, 0x4984: 0x0, 0x4988: 0x3C0044, 0x498C: 0x0,
       0x49A0: 0x0, 0x49A4: 0x0, 0x49A8: 0x0, 0x49AC: 0x0, 0x49B0: 0x0, 0x49B4: 0x0, 0x49C8: 0x0, 0x49CC: 0x0,
       0x49E4: 0x0, 0x49E8: 0x0}


def singleton(reg, value):
    for en, end in OFF:
        if reg == en:
            return value & ~1
        if en < reg < end:
            return 0
    return ABF.get(reg, value)


def main():
    rear = Path(sys.argv[1]).read_bytes()
    assert len(rear) == 16672
    digest = hashlib.sha256(rear).digest()
    points = json.load(open(sys.argv[2]))["points"]
    assert len(points) == 65 and all(1 <= p <= 8192 for p in points)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    (OUT / "camss").mkdir()
    for p in (BASE / "camss").iterdir():
        if p.is_file() and (p.suffix in (".c", ".h", ".inc") or p.name in ("Makefile", "Kconfig")) \
                and not p.name.endswith(".mod.c"):
            shutil.copy2(p, OUT / "camss" / p.name)
    for name in ("imx681", "ov13858"):
        shutil.copytree(BASE / name, OUT / name)
    s = OUT / "camss/camss-e006o-rear-steady-singletons.inc"
    t = s.read_text()
    changed = 0

    def sub(m):
        nonlocal changed
        reg, val = int(m.group(1), 16), int(m.group(2), 16)
        new = singleton(reg, val)
        changed += new != val
        return "{ .reg = 0x%04x, .value = 0x%08x }" % (reg, new)
    t = re.sub(r"\{ \.reg = 0x([0-9a-f]{4}), \.value = 0x([0-9a-f]{8}) \}", sub, t)
    t = t.replace(" * hardware-register observations; no private Windows buffer is read here.\n",
                  " * hardware-register observations; no private Windows buffer is read here.\n"
                  " * camss 50: PDPC, GIC and GTM switched off (configuration zero), BPC_ABF set\n"
                  " * to the open values measured on the front IFE.\n")
    s.write_text(t)
    u = OUT / "camss/camss-e007u-bpcabf411.inc"
    t = u.read_text()
    a = t.index("e007u_bpcabf_points[E007U_BPCABF_POINTS] = {")
    b = t.index("};", a)
    rows = ", ".join(str(p) for p in points)
    t = t[:a] + "e007u_bpcabf_points[E007U_BPCABF_POINTS] = {\n\t/* our rear noise model, ov13858-rear-abf-v1.json */\n\t" + rows + ",\n" + t[b:]
    u.write_text(t)
    i = OUT / "camss/native-rear-generation-identity.h"
    t = i.read_text()
    t = t.replace('"qcom/sp11/rear-generation-20261007-60.bin"', '"qcom/sp11/ov13858-rear-open-v1.bin"')
    t = re.sub(r"native_rear_generation_input_sha256\[32\]=\{[0-9,]+\}",
               "native_rear_generation_input_sha256[32]={" + ",".join(str(x) for x in digest) + "}", t)
    i.write_text(t)
    result = {"status": "BUILDING", "base": str(BASE), "rear_input_sha256": digest.hex(),
              "singletons_changed": changed,
              "profile_sha256": json.load(open(BASE / "build-result.json"))["profile_sha256"]}
    try:
        with (OUT / "camss-compile.log").open("w") as log:
            subprocess.run(["make", "-C", str(KSOURCE), "O=" + str(KOUTPUT), "M=" + str(OUT / "camss"),
                            "CONFIG_VIDEO_QCOM_CAMSS=m", "W=1", "KCFLAGS=-Werror", "-j8", "modules"],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        ko = OUT / "camss/qcom-camss.ko"
        fw = subprocess.check_output(["modinfo", "-F", "firmware", str(ko)], text=True).split()
        result["firmware"] = fw
        assert "qcom/sp11/ov13858-rear-open-v1.bin" in fw and not any("rear-generation" in f for f in fw)
        result["sha256"] = hashlib.sha256(ko.read_bytes()).hexdigest()
        result["status"] = "PASS_BUILD"
    except Exception as exc:
        result["status"] = "FAIL_BUILD"; result["error"] = str(exc); raise
    finally:
        (OUT / "build-result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
