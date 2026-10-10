#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build the front camss module 38 = qualified param-queue build 36 plus the
optional measured CST (native_front_cst_q10) and linear colour-correction
(native_front_ccm_q7) overrides. Nothing else changes.
No install, no module load.
"""
import hashlib, json, shutil, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = Path("/home/geoca/Documents/SP11-PROJECT")
BASE = PROJECT / "02-kernel/native-rgb-front-param-queue-20261010-36"
OUT = PROJECT / "02-kernel/native-rgb-front-ae-38"
KSOURCE = PROJECT / "02-kernel/e003i-front-production-src"
KOUTPUT = PROJECT / "02-kernel/build-runtime-v4-headers-20260826"
CST = HERE.parent / "front-pattern/native-front-cst.inc"


def rep(path, a, b):
    t = path.read_text()
    assert t.count(a) == 1, (path.name, a[:60])
    path.write_text(t.replace(a, b, 1))


def main():
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for name in ("camss", "imx681", "ov13858"):
        (OUT / name).mkdir()
        for p in (BASE / name).iterdir():
            if p.is_file() and (p.suffix in (".c", ".h", ".inc") or p.name in ("Makefile", "Kconfig")):
                shutil.copy2(p, OUT / name / p.name)
    shutil.copy2(CST, OUT / "camss/native-front-cst.inc")
    k = OUT / "camss/native-front-profile-kernel.inc"
    rep(k, '#include "native-front-profile.h"\n', '#include "native-front-profile.h"\n#include "native-front-cst.inc"\n')
    rep(k, " if (!ret)\n  ret = native_front_params_profile_store(video, capsule,",
        " if (!ret)\n  ret = native_front_cst_apply(video, capsule, CAMSS_X1E_PIX_CAPSULE_BYTES);\n"
        " if (!ret)\n  ret = native_front_ccm_apply(video, capsule, CAMSS_X1E_PIX_CAPSULE_BYTES);\n"
        " if (!ret)\n  ret = native_front_params_profile_store(video, capsule,")
    result = {"status": "BUILDING", "base": str(BASE)}
    try:
        for name in ("camss", "imx681", "ov13858"):
            with (OUT / (name + "-compile.log")).open("w") as log:
                subprocess.run(["make", "-C", str(KSOURCE), "O=" + str(KOUTPUT), "M=" + str(OUT / name),
                                "CONFIG_VIDEO_QCOM_CAMSS=m", "W=1", "KCFLAGS=-Werror", "-j8", "modules"],
                               stdout=log, stderr=subprocess.STDOUT, check=True)
        mods = {n: OUT / n / f for n, f in (("camss", "qcom-camss.ko"), ("imx681", "imx681.ko"), ("ov13858", "ov13858.ko"))}
        result["vermagic"] = subprocess.check_output(["modinfo", "-F", "vermagic", str(mods["camss"])], text=True).strip()
        params = subprocess.check_output(["modinfo", "-p", str(mods["camss"])], text=True)
        result["cst_param"] = "native_front_cst_q10" in params
        result["ccm_param"] = "native_front_ccm_q7" in params
        result["sha256"] = {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in mods.items()}
        result["status"] = "PASS_BUILD"
    except Exception as exc:
        result["status"] = "FAIL_BUILD"; result["error"] = str(exc); raise
    finally:
        (OUT / "build-result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
