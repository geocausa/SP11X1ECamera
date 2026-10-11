#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build the front camss module 46 = module 45 plus the robust front queue
(native_front_queue_robust, native_front_queue_wait_us): frames without a
consumer buffer go to a driver-owned scratch buffer and are dropped, frames
without a new IQ packet reuse the newest parameters, stale IQ packets are
skipped. Off by default; the serialized queue is unchanged when off.
Sources: front-robust/native-front-queue.inc, front-robust/robust-iq.c.
No install, no module load.
"""
import hashlib, json, shutil, subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROBUST = HERE.parent / "front-robust"
PROJECT = Path("/home/geoca/Documents/SP11-PROJECT")
BASE = PROJECT / "02-kernel/native-rgb-front-ae-45"
OUT = PROJECT / "02-kernel/native-rgb-front-ae-46"
KSOURCE = PROJECT / "02-kernel/e003i-front-production-src"
KOUTPUT = PROJECT / "02-kernel/build-runtime-v4-headers-20260826"


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
    shutil.copy2(ROBUST / "native-front-queue.inc", OUT / "camss/native-front-queue.inc")
    c = OUT / "camss/camss.c"
    decl = ("static int camss_x1e_pix_iq_provider_next_steady(\n"
            "\tstruct camss *camss, struct camss_video *video, u64 expected_request_id,\n"
            "\tstruct camss_x1e_epoch0_materialized *steady);\n")
    rep(c, decl, decl + "static void camss_x1e_pix_iq_robust_reset(void);\n"
        "static int camss_x1e_pix_iq_provider_next_robust(\n"
        "\tstruct camss *camss, struct camss_video *video, u64 frame,\n"
        "\tstruct camss_x1e_epoch0_materialized *steady, bool *reused);\n")
    anchor = "struct camss_x1e_pix_iq_provider_static_ops {\n"
    rep(c, anchor, (ROBUST / "robust-iq.c").read_text().lstrip("\n") + anchor)
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
        result["robust_param"] = "native_front_queue_robust" in params
        result["abf_param"] = "native_front_abf" in params
        result["sha256"] = {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in mods.items()}
        result["status"] = "PASS_BUILD"
    except Exception as exc:
        result["status"] = "FAIL_BUILD"; result["error"] = str(exc); raise
    finally:
        (OUT / "build-result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
