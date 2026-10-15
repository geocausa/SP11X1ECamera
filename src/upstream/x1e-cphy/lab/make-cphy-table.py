#!/usr/bin/env python3
"""Turn our tested CAMSS X1E C-PHY table (built from Qualcomm's GPL-2.0 cam_csiphy_2_1_2_hwreg.h)
into the qcom-mipi-csi2 PHY driver's table format. Drops the Windows-only 0x?94=0x09 extras."""
import re, sys
src = open(sys.argv[1]).read()
body = src[src.index("lane_regs_x1e80100_3ph_gpl[] = {"):]
body = body[body.index("{") + 1:body.index("\n};")]
out = ["""/*
 * 4nm 3PH v2.1.2 C-PHY, 2.5 Gsps, from Qualcomm's GPL-2.0 camera driver
 * (cam_csiphy_2_1_2_hwreg.h: csiphy_3ph_v2_1_2_reg[], datarate_212_2p5Gsps[]
 * and the 3PH reset-exit write), one trio block per lane triplet.
 */
static const struct
mipi_csi2phy_lane_regs lane_regs_x1e80100_cphy[] = {
	/* Power up lanes 3ph mode */
	{.reg_addr = 0x101c, .reg_data = 0x7a, .param_type = CSIPHY_DEFAULT_PARAMS},
	{.reg_addr = 0x1018, .reg_data = 0x01, .param_type = CSIPHY_DEFAULT_PARAMS},
"""]
skip_comment = False
n = 0
for ln in body.splitlines():
    s = ln.strip()
    if not s:
        continue
    if s.startswith("/*"):
        if "not in the GPL table" in s:
            continue
        out.append("\t" + s.replace("datarate_212_2p5Gsps: datarate sensitive, then csiphy_3ph_v2_1_2_reg", "datarate_212_2p5Gsps, then csiphy_3ph_v2_1_2_reg") + "\n")
        continue
    m = re.match(r"\{(0x[0-9a-fA-F]+), (0x[0-9a-fA-F]+), (\d+), (\w+)\},", s)
    assert m, s
    addr, data, delay, param = m.groups()
    if param == "CSIPHY_X1E_LANE_EXTRA":
        continue
    assert param == "CSIPHY_DEFAULT_PARAMS", s
    d = ", .delay_us = %d" % int(delay) if int(delay) else ""
    out.append("\t{.reg_addr = 0x%04x, .reg_data = 0x%02x%s, .param_type = CSIPHY_DEFAULT_PARAMS},\n" % (int(addr, 16), int(data, 16), d))
    n += 1
out.append("};\n")
open(sys.argv[2], "w").write("".join(out))
print("entries", n + 2)
