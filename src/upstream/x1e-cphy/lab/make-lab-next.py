#!/usr/bin/env python3
"""Lab DTB for the upstream (linux-next) camera stack: CAMSS in PHY-API mode with separate
qcom,x1e80100-csi2-phy nodes, following Bryan O'Donoghue's x1e80100 camera DT v7.
Usage: make-lab-next.py rear|front|both
  rear : CSIPHY1 D-PHY (ov13858, 4 lanes, 540/270 MHz)
  front: CSIPHY2 C-PHY (imx681, 1 trio, 1.2 GHz)  -- needs C-PHY support in PHY+CAMSS
The IR camera (CSIPHY0) is left unconnected. A one-shot GRUB entry 'sp11-next-lab' is written.
"""
import re, subprocess, sys
from pathlib import Path

mode = sys.argv[1]
SRC = Path("/boot/sp11-7.1.5-camera-daily2/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb")
DST = SRC.with_name("x1e80100-microsoft-denali-sp11-next-lab.dtb")
W = Path("/root/imx681-test")
dts = subprocess.run(["dtc", "-q", "-I", "dtb", "-O", "dts", str(SRC)], capture_output=True, text=True, check=True).stdout

CAMCC, RPMHPD, OPP56, OPP64 = 0x2b8, 0x3c, 0x100, 0x2f
VDDA_1P2, VDDA_0P9 = 0x28b, 0x28c
PH = {"opp": 0x7f000001, "phy1_in": 0x7f000011, "phy1_out": 0x7f000012,
      "phy2_in": 0x7f000021, "phy2_out": 0x7f000022}


def sub1(pat, rep, text, flags=re.S):
    new, n = re.subn(pat, rep, text, count=1, flags=flags)
    assert n == 1, pat
    return new


# 1. CSIPHY OPP table at the root (MXC variant from the v7 dtsi).
opp = """
\tcsiphy-mxc-opp-table {
\t\tcompatible = "operating-points-v2";
\t\tphandle = <0x%x>;
\t\topp-300000000 {
\t\t\topp-hz = /bits/ 64 <300000000>;
\t\t\trequired-opps = <0x%x 0x%x>;
\t\t};
\t\topp-400000000 {
\t\t\topp-hz = /bits/ 64 <400000000>;
\t\t\trequired-opps = <0x%x 0x%x>;
\t\t};
\t\topp-480000000 {
\t\t\topp-hz = /bits/ 64 <480000000>;
\t\t\trequired-opps = <0x%x 0x%x>;
\t\t};
\t};
""" % (PH["opp"], OPP56, OPP56, OPP64, OPP64, OPP64, OPP64)
dts = sub1(r"(\n\tsoc@0 \{)", lambda m: opp + m.group(1), dts)


def phy_node(n, addr, core, timer, irq, ep_in, ep_out, sensor_ep, camss_ep, lanes, cphy):
    bt = "\t\t\t\t\t\tbus-type = <0x01>;\n" if cphy else ""
    return """
\t\tphy@%x {
\t\t\tcompatible = "qcom,x1e80100-csi2-phy";
\t\t\treg = <0x00 0x%x 0x00 0x2000>;
\t\t\tclocks = <0x%x %d 0x%x %d 0x%x 13>;
\t\t\tclock-names = "core", "timer", "ahb";
\t\t\toperating-points-v2 = <0x%x>;
\t\t\tinterrupts = <0x00 %d 0x01>;
\t\t\tpower-domains = <0x%x 5 0x%x 6 0x%x 10>;
\t\t\tpower-domain-names = "top", "mmcx", "mx";
\t\t\tvdda-0p9-supply = <0x%x>;
\t\t\tvdda-1p2-supply = <0x%x>;
\t\t\tports {
\t\t\t\t#address-cells = <0x01>;
\t\t\t\t#size-cells = <0x00>;
\t\t\t\tport@0 {
\t\t\t\t\treg = <0x00>;
\t\t\t\t\tendpoint {
%s\t\t\t\t\t\tdata-lanes = <%s>;
\t\t\t\t\t\tremote-endpoint = <0x%x>;
\t\t\t\t\t\tphandle = <0x%x>;
\t\t\t\t\t};
\t\t\t\t};
\t\t\t\tport@1 {
\t\t\t\t\treg = <0x01>;
\t\t\t\t\tendpoint {
\t\t\t\t\t\tremote-endpoint = <0x%x>;
\t\t\t\t\t\tphandle = <0x%x>;
\t\t\t\t\t};
\t\t\t\t};
\t\t\t};
\t\t};
""" % (addr, addr, CAMCC, core, CAMCC, timer, CAMCC, PH["opp"], irq, CAMCC, RPMHPD, RPMHPD,
       VDDA_0P9, VDDA_1P2, bt, lanes, sensor_ep, ep_in, camss_ep, ep_out)


# Existing phandles: camss port endpoints and sensor endpoints.
CAMSS_EP = {0: 0x2d2, 1: 0x2cc, 2: 0x2ca}
SENSOR_EP = {0: 0x2d3, 1: 0x2cd, 2: 0x2cb}
nodes = ""
use_rear = mode in ("rear", "both")
use_front = mode in ("front", "both")
if use_rear:
    nodes += phy_node(1, 0xace6000, 39, 25, 478, PH["phy1_in"], PH["phy1_out"], SENSOR_EP[1], CAMSS_EP[1], "0x01 0x02 0x03 0x04", False)
if use_front:
    nodes += phy_node(2, 0xace8000, 40, 27, 479, PH["phy2_in"], PH["phy2_out"], SENSOR_EP[2], CAMSS_EP[2], "0x01", True)
dts = sub1(r"(\n\t\tisp@acb7000 \{)", lambda m: nodes + m.group(1), dts)

# 2. CAMSS port endpoints -> PHY output endpoints (1-based lanes); unused ports lose their remote.
i = dts.index("\t\tisp@acb7000 {")
j = dts.index("\n\t\t};\n", dts.index("ports {", i))
cam = dts[i:j]


def set_ep(cam, ph, remote, lanes, cphy):
    blk = re.search(r"endpoint \{[^}]*phandle = <0x%x>;[^}]*\}" % ph, cam, re.S).group(0)
    new = blk
    if remote is None:
        new = re.sub(r"\n\t*remote-endpoint = <0x[0-9a-f]+>;", "", new)
    else:
        new = re.sub(r"remote-endpoint = <0x[0-9a-f]+>;", "remote-endpoint = <0x%x>;" % remote, new)
        new = re.sub(r"data-lanes = <[^>]*>;", "data-lanes = <%s>;" % lanes, new)
        new = re.sub(r"bus-type = <0x0[14]>;", "bus-type = <0x0%d>;" % (1 if cphy else 4), new)
    return cam.replace(blk, new)


cam = set_ep(cam, CAMSS_EP[0], None, None, False)
cam = set_ep(cam, CAMSS_EP[1], PH["phy1_out"] if use_rear else None, "0x01 0x02 0x03 0x04", False)
cam = set_ep(cam, CAMSS_EP[2], PH["phy2_out"] if use_front else None, "0x01", True)
dts = dts[:i] + cam + dts[j:]

# 3. Sensor endpoints -> PHY input endpoints; rear link frequencies and MCLK as the in-tree driver needs.


def sensor(dts, compat, ph, remote, extra):
    k = dts.index('compatible = "%s";' % compat)
    s = dts.rindex("camera@", 0, k)
    e = dts.index("\t\t\t\t};\n", dts.index("port {", k))
    node = dts[s:e]
    if remote is None:
        node = re.sub(r"\n\t*remote-endpoint = <0x[0-9a-f]+>;", "", node)
    else:
        node = re.sub(r"remote-endpoint = <0x[0-9a-f]+>;", "remote-endpoint = <0x%x>;" % remote, node)
    for a, b in extra:
        node = re.sub(a, b, node)
    return dts[:s] + node + dts[e:]


clk_rear = "0x2b8 0x49"
dts = sensor(dts, "ovti,ov13858", SENSOR_EP[1], PH["phy1_in"] if use_rear else None,
             [(r"link-frequencies = <0x00 0x23556900>;", "link-frequencies = /bits/ 64 <540000000 270000000>;"),
              (r'compatible = "ovti,ov13858";', 'compatible = "ovti,ov13858";\n\t\t\t\t\tassigned-clocks = <%s>;\n\t\t\t\t\tassigned-clock-rates = <19200000>;' % clk_rear)])
dts = sensor(dts, "sony,imx681", SENSOR_EP[2], PH["phy2_in"] if use_front else None,
             [(r"data-lanes = <0x00>;", "data-lanes = <0x01>;\n\t\t\t\t\t\t\tlink-frequencies = /bits/ 64 <1200000000>;"),
              (r'compatible = "sony,imx681";', 'compatible = "sony,imx681";\n\t\t\t\t\tdvdd-supply = <0x2c5>;\n\t\t\t\t\tassigned-clocks = <0x2b8 0x4f>;\n\t\t\t\t\tassigned-clock-rates = <19200000>;')])
dts = sensor(dts, "microsoft,sp11-vd55g0", SENSOR_EP[0], None, [])

(W / ("next-lab-%s.dts" % mode)).write_text(dts)
subprocess.run(["dtc", "-q", "-I", "dts", "-O", "dtb", "-o", str(DST), str(W / ("next-lab-%s.dts" % mode))], check=True)
print("dtb", DST)

cfg = Path("/boot/grub/custom.cfg").read_text()
if "sp11-next-lab" not in cfg:
    m = re.search(r"menuentry 'SP11 IMX681 upstream-driver lab \(one-shot\)' --id 'sp11-imx681-lab'.*?\n\}\n", cfg, re.S)
    entry = m.group(0).replace("'SP11 IMX681 upstream-driver lab (one-shot)' --id 'sp11-imx681-lab'",
                               "'SP11 upstream camera stack lab (one-shot)' --id 'sp11-next-lab'")
    entry = entry.replace("sp11-imx681-lab.dtb", "sp11-next-lab.dtb").replace("sp11_entry=7.1.5-sp11-imx681-lab", "sp11_entry=7.1.5-sp11-next-lab")
    Path("/boot/grub/custom.cfg").write_text(cfg + entry)
    print("grub entry added")
