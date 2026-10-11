#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Daily camera device tree = camera tree + the rear lens actuator supply.

The rear OV13858 module has a DW9800 voice-coil focus actuator on the rear CCI
bus (0x0c) powered from PM8550 LDO16 (2.9 V, the camera VAF rail; the sensor
itself does not use it). The camera tree did not define LDO16, so the lens sat
unpowered at its rest (far) position. This adds LDO16 at 2.9 V and a
regulator-output consumer so userspace (the webcam bridge) can power the
actuator only while the rear camera streams.
Usage: make-daily-dtb.py <in.dtb> <out.dtb>
"""
import subprocess, sys, tempfile
from pathlib import Path

PH = 0x2f0


def main():
    src, dst = sys.argv[1], sys.argv[2]
    dts = subprocess.run(["dtc", "-q", "-s", "-I", "dtb", "-O", "dts", src], check=True, capture_output=True, text=True).stdout
    assert f"<{hex(PH)}>" not in dts and "vreg_l16b" not in dts
    anchor = 'regulator-name = "vreg_l15b_1p8";\n\t\t\t\t};\n'
    assert dts.count(anchor) == 1
    ldo16 = ("\n\t\t\t\tldo16 {\n\t\t\t\t\tphandle = <%s>;\n\t\t\t\t\tregulator-initial-mode = <0x03>;\n"
             "\t\t\t\t\tregulator-max-microvolt = <2900000>;\n\t\t\t\t\tregulator-min-microvolt = <2900000>;\n"
             "\t\t\t\t\tregulator-name = \"vreg_l16b_2p9\";\n\t\t\t\t};\n") % hex(PH)
    dts = dts.replace(anchor, anchor + ldo16)
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
