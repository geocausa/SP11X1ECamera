#!/usr/bin/env python3
"""IR-illuminator lab DTB + one-shot GRUB entry 'sp11-ir-flash-lab'.
Starts from lab.dts (old stack, IR sensor as st,vd55g0). Enables the PM8550 flash controller (SID 1, 0xee00)
with one IR LED on sources 1+4 (the pair Windows arms: ee4a/ee4d, enable mask 0x09), hard-capped in DT at
200 mA total (100 mA per channel, under Windows' 700 mA) and a 10 ms per-pulse safety timer; links it to the
sensor with flash-leds. leds_qcom_flash is blacklisted in the entry so only our patched module is loaded."""
import re, subprocess
from pathlib import Path
W = Path("/root/imx681-test")
DST = "/boot/sp11-7.1.5-camera-daily2/x1e80100-microsoft-denali-sp11-ir-flash-lab.dtb"
dts = (W / "lab.dts").read_text()
ph = max(int(x, 16) for x in re.findall(r"phandle = <(0x[0-9a-f]+)>;", dts)) + 1
old = """\t\t\t\t\tled-controller@ee00 {
\t\t\t\t\t\tcompatible = "qcom,pm8550-flash-led", "qcom,spmi-flash-led";
\t\t\t\t\t\treg = <0xee00>;
\t\t\t\t\t\tstatus = "disabled";
\t\t\t\t\t\tphandle = <0x264>;
"""
new = """\t\t\t\t\tled-controller@ee00 {
\t\t\t\t\t\tcompatible = "qcom,pm8550-flash-led", "qcom,spmi-flash-led";
\t\t\t\t\t\treg = <0xee00>;
\t\t\t\t\t\tstatus = "okay";
\t\t\t\t\t\tphandle = <0x264>;

\t\t\t\t\t\tled-0 {
\t\t\t\t\t\t\tfunction = "flash";
\t\t\t\t\t\t\tcolor = <7>;
\t\t\t\t\t\t\tlabel = "sp11-ir-illuminator";
\t\t\t\t\t\t\tled-sources = <1 4>;
\t\t\t\t\t\t\tled-max-microamp = <10000>;
\t\t\t\t\t\t\tflash-max-microamp = <200000>;
\t\t\t\t\t\t\tflash-max-timeout-us = <10000>;
\t\t\t\t\t\t\tphandle = <%#x>;
\t\t\t\t\t\t};
""" % ph
assert dts.count(old) == 1, "flash node"
dts = dts.replace(old, new)
cam = '\t\t\t\t\tcompatible = "st,vd55g0";\n'
assert dts.count(cam) == 1, "camera node"
dts = dts.replace(cam, cam + "\t\t\t\t\tflash-leds = <%#x>;\n" % ph)
(W / "lab-flash.dts").write_text(dts)
subprocess.run(["dtc", "-q", "-I", "dts", "-O", "dtb", "-o", DST, str(W / "lab-flash.dts")], check=True)
print("dtb", DST, "led phandle", hex(ph))

cfg = Path("/boot/grub/custom.cfg")
c = cfg.read_text()
if "--id 'sp11-ir-flash-lab'" not in c:
    m = re.search(r"menuentry '[^']*' --id 'sp11-imx681-lab'.*?\n}\n", c, re.S)
    e = m.group(0)
    e = e.replace("SP11 IMX681 upstream-driver lab (one-shot)", "SP11 IR illuminator lab (one-shot)")
    e = e.replace("--id 'sp11-imx681-lab'", "--id 'sp11-ir-flash-lab'")
    e = e.replace("x1e80100-microsoft-denali-sp11-imx681-lab.dtb", "x1e80100-microsoft-denali-sp11-ir-flash-lab.dtb")
    e = e.replace("sp11_entry=7.1.5-sp11-imx681-lab", "sp11_entry=7.1.5-sp11-imx681-lab sp11_entry=7.1.5-sp11-ir-flash-lab")
    e = e.replace("modprobe.blacklist=qcom_camss,", "modprobe.blacklist=leds_qcom_flash,qcom_camss,")
    assert e.count("ir-flash-lab") == 3 and "leds_qcom_flash" in e
    cfg.write_text(c + e)
    print("grub entry added")
""""""
