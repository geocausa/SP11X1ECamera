#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build the rear camss module with the measured tone curve and colour matrix (run 63).

Starts from the rear60 staged sources (build73) and changes only:
 * the IFE Gamma1.5 LUT values -> fitted curve from fit-tone-ccm.py;
 * the CST12 3x3 matrix in every startup packet -> BT.601 x fitted CCM.
No other register, DMI or lifecycle behaviour changes.
"""
import json, re, shutil, subprocess, sys
from pathlib import Path
PROJECT = Path("/home/geoca/Documents/SP11-PROJECT")
BASE = PROJECT / "02-kernel/native-rgb-rear-generation-20261007-73"
OUT = PROJECT / "02-kernel/native-rgb-rear-tone-63"
KSOURCE = PROJECT / "02-kernel/e003i-front-production-src"
KOUTPUT = PROJECT / "02-kernel/build-runtime-v4-headers-20260826"


def replace(path, a, b):
    t = path.read_text()
    assert t.count(a) == 1, a[:60]
    path.write_text(t.replace(a, b, 1))


def main():
    fit = json.loads(Path(sys.argv[1]).read_text())
    curve = fit["tone_curve_12bit"]; q = fit["cst_q10_GBR"]
    assert len(curve) == 257 and curve[0] == 0 and curve[-1] == 4095 and all(b >= a for a, b in zip(curve, curve[1:]))
    assert all(abs(v) <= 4095 for row in q for v in row)
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    for name in ["camss", "imx681", "ov13858"]:
        d = OUT / name; d.mkdir()
        for p in (BASE / name).iterdir():
            if p.is_file() and p.suffix in (".c", ".h", ".inc") or p.name in ("Makefile", "Kconfig"):
                shutil.copy2(p, d / p.name)
    g = OUT / "camss/camss-e007t-gamma151.inc"
    t = g.read_text()
    start = t.index("e007t_gamma_curve[E007T_GAMMA_SAMPLES] = {")
    a = t.index("{", start) + 1; b = t.index("};", a)
    rows = [", ".join(str(v) for v in curve[i:i + 12]) for i in range(0, 257, 12)]
    t = t[:a] + "\n\t" + ",\n\t".join(rows) + ",\n" + t[b:]
    t = t.replace("Semantic authority: 257 integral 12-bit samples derived from the selected\n * OV13858 Gamma1.5 tuning region. These are tuning semantics, not captured\n * Windows DMI words.",
                  "257 integral 12-bit samples of an independently measured tone curve\n * (SP7 pattern runs 61/62, fit-tone-ccm.py). No OEM tuning table.")
    g.write_text(t)
    iq = OUT / "camss/native-rear-startup-iq.inc"
    m = "".join(f"c->m{r}{c}={q[r][c]};" for r in range(3) for c in range(3))
    replace(iq, "\twork->input = *input;\n",
            "\twork->input = *input;\n\t{ /* Measured colour matrix (BT.601 x fitted CCM, Q10, cols G,B,R). */\n\t\tunsigned int q;\n\t\tfor (q = 0; q < E007Y_STARTUP_PACKETS; q++) {\n\t\t\tstruct e006r_cst12_state *c = &work->input.packet[q].cst;\n\t\t\t" + m + "\n\t\t}\n\t}\n")
    replace(OUT / "camss/native-rear-generation-hook.inc", "NATIVE_REAR_GENERATION_ATTEMPT identity=60", "NATIVE_REAR_GENERATION_ATTEMPT identity=63tone")
    result = dict(status="BUILDING", cst_q10_GBR=q, curve_points=257)
    try:
        for name in ["camss", "imx681", "ov13858"]:
            with (OUT / (name + "-compile.log")).open("w") as log:
                subprocess.run(["make", "-C", str(KSOURCE), "O=" + str(KOUTPUT), "M=" + str(OUT / name),
                                "CONFIG_VIDEO_QCOM_CAMSS=m", "W=1", "KCFLAGS=-Werror", "-j8", "modules"],
                               stdout=log, stderr=subprocess.STDOUT, check=True)
        result["vermagic"] = subprocess.check_output(["modinfo", "-F", "vermagic", str(OUT / "camss/qcom-camss.ko")], text=True).strip()
        result["status"] = "PASS_BUILD"
    except Exception as e:
        result["status"] = "FAIL_BUILD"; result["error"] = str(e); raise
    finally:
        (OUT / "build-result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
