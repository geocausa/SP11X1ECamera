#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Daily camera device tree = camera tree + the rear lens actuator supply.

The rear OV13858 module has a DW9800 voice-coil focus actuator on the rear CCI
bus (0x0c) powered from PM8550 LDO16 (2.9 V, the camera VAF rail; the sensor
itself does not use it). The camera tree does not define LDO16.

v1 added LDO16 to the Golden PM8550 provider with fixed constraints and an
initial mode: the regulator core then programs the rail at boot, and that boot
hung (2026-10-11, twice). v2 instead adds a separate camera-only provider node
under the RPMh RSC (compatible microsoft,sp11-camera-rpmh-regulators, driver
vaf/sp11_camera_rpmh_regulator.c, the provider that powered LDO16 at 2.9 V in
the E002b rear bring-up). No in-kernel driver binds it, so boot is unchanged;
the camera boot loads the provider, which sends no vote until the rail is
enabled. A regulator-output consumer lets the webcam bridge power the actuator
only while the rear camera streams.
Usage: make-daily-dtb.py <in.dtb> <out.dtb>
"""
import re, subprocess, sys, tempfile

PH = 0x2f0


def main():
    src, dst = sys.argv[1], sys.argv[2]
    dts = subprocess.run(["dtc", "-q", "-I", "dtb", "-O", "dts", src], check=True, capture_output=True, text=True).stdout
    assert f"<{hex(PH)}>" not in dts and "ldob16" not in dts and "sp11-rear-vaf" not in dts
    m = re.search(r"\n(\t+)rsc@17500000 \{\n", dts)
    assert m and dts.count("rsc@17500000 {") == 1
    ind = m.group(1) + "\t"
    node = (f"{ind}camera-vaf-regulators {{\n"
            f"{ind}\tcompatible = \"microsoft,sp11-camera-rpmh-regulators\";\n\n"
            f"{ind}\tldo16b {{\n"
            f"{ind}\t\tphandle = <{hex(PH)}>;\n"
            f"{ind}\t\tregulator-name = \"vreg_l16b_rear_vaf\";\n"
            f"{ind}\t\tmicrosoft,rpmh-resource = \"ldob16\";\n"
            f"{ind}\t\tmicrosoft,target-microvolt = <2900000>;\n"
            f"{ind}\t\tmicrosoft,vrm-mode = <7>;\n"
            f"{ind}\t}};\n"
            f"{ind}}};\n\n")
    # append as the last child of the RSC node (properties must precede subnodes)
    depth, i = 1, m.end()
    while depth:
        c = dts[i]
        depth += (c == "{") - (c == "}")
        i += 1
    at = dts.rfind("\n", 0, i - 1) + 1
    dts = dts[:at] + "\n" + node.rstrip("\n") + "\n" + dts[at:]
    assert dts.rstrip().endswith("};")
    body = dts.rstrip()[:-2]
    dts = body + ("\n\tsp11-rear-vaf {\n\t\tcompatible = \"regulator-output\";\n"
                  "\t\tvout-supply = <%s>;\n\t};\n};\n") % hex(PH)
    with tempfile.NamedTemporaryFile("w", suffix=".dts") as f:
        f.write(dts)
        f.flush()
        subprocess.run(["dtc", "-q", "-I", "dts", "-O", "dtb", "-o", dst, f.name], check=True)
    print("WROTE", dst)


if __name__ == "__main__":
    main()
