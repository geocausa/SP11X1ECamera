#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Build the front camss module 43 = module 42 plus an optional C-PHY receive table
expressed from Qualcomm's published GPL CSIPHY v2.1.2 tables instead of the
Windows-captured sequence.

  csiphy_x1e_cphy_gpl=1     use the GPL-derived table (default 0 = Windows-exact table)
  csiphy_x1e_cphy_lane09=0  drop the one Windows-only per-lane write (0x?94 = 0x09)

GPL source: cam_csiphy_2_1_2_hwreg.h (Qualcomm Innovation Center, GPL-2.0-only),
csiphy_3ph_v2_1_2_reg[] + datarate_212_2p5Gsps[] + csiphy_reset_exit_reg_2_1_2[] (3PH).
With the GPL table the IRQ mask registers are zeroed as for every other target
(no Windows mask values). No install, no module load.
"""
import hashlib, json, shutil, subprocess
from pathlib import Path

PROJECT = Path("/home/geoca/Documents/SP11-PROJECT")
BASE = PROJECT / "02-kernel/native-rgb-front-ae-42"
OUT = PROJECT / "02-kernel/native-rgb-front-ae-43"
KSOURCE = PROJECT / "02-kernel/e003i-front-production-src"
KOUTPUT = PROJECT / "02-kernel/build-runtime-v4-headers-20260826"

LANES = (0x000, 0x400, 0x800)
# datarate_212_2p5Gsps[] AFE settings, per lane, GPL order (0x?78 is CDR_LN_SETTINGS there)
AFE = [(0x268, 0xF1), (0x294, 0x01), (0x288, 0x20), (0x278, 0x20),
       (0x26C, 0x3D), (0x28C, 0x30), (0x270, 0x00), (0x274, 0x03)]
# csiphy_3ph_v2_1_2_reg[] leading per-lane block
PRE = [(0x2F4, 0x00), (0x2F8, 0x00), (0x2FC, 0x00), (0x2F0, 0xEF)]
# datarate_212_2p5Gsps[] datarate-sensitive per lane (0x?0C settle low byte default 0x22)
DR = [(0x20C, 0x22), (0x208, 0x00), (0x210, 0x00), (0x214, 0x00)]
# csiphy_3ph_v2_1_2_reg[] main per-lane block
MAIN = [(0x204, 0x00), (0x2E4, 0x00), (0x2E8, 0x7F), (0x2EC, 0x7F), (0x218, 0x3E),
        (0x21C, 0x41), (0x220, 0x41), (0x224, 0x7F), (0x228, 0x00), (0x22C, 0x00),
        (0x264, 0x01), (0x244, 0xB2), (0x310, 0x35), (0x2BC, 0xD0), (0x254, 0x00),
        (0x240, 0x00), (0x260, 0xA8), (0x284, 0x00), (0x290, 0x02)]


def table():
    rows = []
    def add(reg, val, delay=0, kind="CSIPHY_DEFAULT_PARAMS"):
        rows.append(f"\t{{0x{reg:04x}, 0x{val:02x}, {delay}, {kind}}},")
    rows.append("\t/* datarate_212_2p5Gsps: AFE settings */")
    for li, lo in enumerate(LANES):
        for i, (r, v) in enumerate(AFE):
            add(lo + r, v, 10 if (li == 2 and i == len(AFE) - 1) else 0)
    rows.append("\t/* not in the GPL table: final per-lane AFE value used by the Windows driver */")
    for lo in LANES:
        add(lo + 0x294, 0x09, 0, "CSIPHY_X1E_LANE_EXTRA")
    rows.append("\t/* csiphy_3ph_v2_1_2_reg */")
    for lo in LANES:
        for r, v in PRE:
            add(lo + r, v, 3 if r == 0x2F0 else 0)
    for lo in LANES:
        rows.append("\t/* datarate_212_2p5Gsps: datarate sensitive, then csiphy_3ph_v2_1_2_reg */")
        for r, v in DR + MAIN:
            add(lo + r, v)
    rows.append("\t/* csiphy_reset_exit_reg_2_1_2, 3PH */")
    add(0x1000, 0x0E, 3048)
    return rows


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
    c = OUT / "camss/camss-csiphy-3ph-1-0.c"
    rep(c, "#define CSIPHY_SKEW_CAL\t\t\t7\n",
        "#define CSIPHY_SKEW_CAL\t\t\t7\n#define CSIPHY_X1E_LANE_EXTRA\t\t8\n")
    rows = table()
    gpl = (
        "static bool csiphy_x1e_cphy_gpl;\n"
        "module_param(csiphy_x1e_cphy_gpl, bool, 0400);\n"
        "MODULE_PARM_DESC(csiphy_x1e_cphy_gpl,\n"
        "\t\t \"X1E80100 C-PHY: use the table built from the Qualcomm GPL v2.1.2 tables\");\n\n"
        "static bool csiphy_x1e_cphy_lane09 = true;\n"
        "module_param(csiphy_x1e_cphy_lane09, bool, 0400);\n"
        "MODULE_PARM_DESC(csiphy_x1e_cphy_lane09,\n"
        "\t\t \"X1E80100 C-PHY GPL table: keep the final per-lane 0x?94=0x09 write\");\n\n"
        "/*\n"
        " * 4nm X1E80100 C-PHY (CSIPHY v2.1.2) at 2.5 Gsps, from Qualcomm's GPL-2.0\n"
        " * cam_csiphy_2_1_2_hwreg.h: csiphy_3ph_v2_1_2_reg[], datarate_212_2p5Gsps[]\n"
        " * and the 3PH reset-exit write. Settle count kept at the table default.\n"
        " */\n"
        "static const struct\ncsiphy_lane_regs lane_regs_x1e80100_3ph_gpl[] = {\n"
        + "\n".join(rows) + "\n};\n\n"
        "/* 4nm 2PH v 2.1.2 2p5Gbps 4 lane DPHY mode */\n")
    rep(c, "/* 4nm 2PH v 2.1.2 2p5Gbps 4 lane DPHY mode */\n", gpl)
    rep(c, "\t\tcase CSIPHY_DNP_PARAMS:\n\t\t\tcontinue;\n",
        "\t\tcase CSIPHY_DNP_PARAMS:\n\t\t\tcontinue;\n"
        "\t\tcase CSIPHY_X1E_LANE_EXTRA:\n"
        "\t\t\tif (!csiphy_x1e_cphy_lane09)\n\t\t\t\tcontinue;\n"
        "\t\t\tval = r->reg_data;\n\t\t\tbreak;\n")
    rep(c, "\t\t\tregs->lane_regs = lane_regs_x1e80100_3ph;\n"
           "\t\t\tregs->lane_array_size = ARRAY_SIZE(lane_regs_x1e80100_3ph);\n",
        "\t\t\tif (csiphy_x1e_cphy_gpl) {\n"
        "\t\t\t\tregs->lane_regs = lane_regs_x1e80100_3ph_gpl;\n"
        "\t\t\t\tregs->lane_array_size = ARRAY_SIZE(lane_regs_x1e80100_3ph_gpl);\n"
        "\t\t\t\tdev_info(csiphy->camss->dev,\n"
        "\t\t\t\t\t \"CSIPHY_X1E_CPHY_GPL_TABLE writes=%zu lane09=%d\\n\",\n"
        "\t\t\t\t\t ARRAY_SIZE(lane_regs_x1e80100_3ph_gpl), csiphy_x1e_cphy_lane09);\n"
        "\t\t\t} else {\n"
        "\t\t\t\tregs->lane_regs = lane_regs_x1e80100_3ph;\n"
        "\t\t\t\tregs->lane_array_size = ARRAY_SIZE(lane_regs_x1e80100_3ph);\n"
        "\t\t\t}\n")
    rep(c, "\t} else if (!x1e_cphy) {\n", "\t} else if (!x1e_cphy || csiphy_x1e_cphy_gpl) {\n")
    result = {"status": "BUILDING", "base": str(BASE), "gpl_writes": sum(1 for r in rows if r.startswith("\t{"))}
    try:
        for name in ("camss", "imx681", "ov13858"):
            with (OUT / (name + "-compile.log")).open("w") as log:
                subprocess.run(["make", "-C", str(KSOURCE), "O=" + str(KOUTPUT), "M=" + str(OUT / name),
                                "CONFIG_VIDEO_QCOM_CAMSS=m", "W=1", "KCFLAGS=-Werror", "-j8", "modules"],
                               stdout=log, stderr=subprocess.STDOUT, check=True)
        mods = {n: OUT / n / f for n, f in (("camss", "qcom-camss.ko"), ("imx681", "imx681.ko"), ("ov13858", "ov13858.ko"))}
        result["vermagic"] = subprocess.check_output(["modinfo", "-F", "vermagic", str(mods["camss"])], text=True).strip()
        params = subprocess.check_output(["modinfo", "-p", str(mods["camss"])], text=True)
        result["gpl_param"] = "csiphy_x1e_cphy_gpl" in params
        result["lane09_param"] = "csiphy_x1e_cphy_lane09" in params
        result["lsc_param"] = "native_front_lsc" in params
        result["sha256"] = {n: hashlib.sha256(p.read_bytes()).hexdigest() for n, p in mods.items()}
        result["status"] = "PASS_BUILD"
    except Exception as exc:
        result["status"] = "FAIL_BUILD"; result["error"] = str(exc); raise
    finally:
        (OUT / "build-result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
