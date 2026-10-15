#!/usr/bin/env python3
"""Lab DTB + one-shot GRUB entry for testing the upstream-candidate imx681 driver.

Front sensor node changed to what the upstream binding expects:
  data-lanes = <1> (one trio), link-frequencies = 1.2 GHz, MCLK4 assigned 19.2 MHz,
  dvdd on the avdd rail (the module regulates its own core supply, as on other X1E laptops).
The lab entry boots the camera DTB variant WITHOUT sp11_camera_daily2=1, so nothing
loads by itself; camera modules stay blacklisted and are loaded by hand for the test.
"""
import re, subprocess
from pathlib import Path

SRC = Path("/boot/sp11-7.1.5-camera-daily2/x1e80100-microsoft-denali-sp11-unified-rgb-ir.dtb")
DST = SRC.with_name("x1e80100-microsoft-denali-sp11-imx681-lab.dtb")
W = Path("/root/imx681-test")

dts = subprocess.run(["dtc", "-q", "-I", "dtb", "-O", "dts", str(SRC)], capture_output=True, text=True, check=True).stdout
i = dts.index('compatible = "sony,imx681";')
start = dts.rindex("camera@10 {", 0, i)
end = dts.index("\t\t\t\t};\n", dts.index("port {", i))
node = dts[start:end]
avdd = re.search(r"avdd-supply = <(0x[0-9a-f]+)>;", node).group(1)
clk = re.search(r"clocks = <(0x[0-9a-f]+ 0x[0-9a-f]+)>;", node).group(1)
new = node.replace('compatible = "sony,imx681";',
                   'compatible = "sony,imx681";\n\t\t\t\t\tdvdd-supply = <%s>;\n'
                   '\t\t\t\t\tassigned-clocks = <%s>;\n\t\t\t\t\tassigned-clock-rates = <19200000>;' % (avdd, clk))
new = re.sub(r"(endpoint \{[^}]*?)data-lanes = <0x00>;", r"\1data-lanes = <0x01>;\n\t\t\t\t\t\t\tlink-frequencies = /bits/ 64 <1200000000>;", new, flags=re.S)
assert new.count("link-frequencies") == 1 and "dvdd-supply" in new
dts = dts[:start] + new + dts[end:]
(W / "lab.dts").write_text(dts)
subprocess.run(["dtc", "-q", "-I", "dts", "-O", "dtb", "-o", str(DST), str(W / "lab.dts")], check=True)
print("dtb", DST)

cfg = Path("/boot/grub/grub.cfg").read_text()
m = re.search(r"menuentry 'SP11 Golden \+ Cameras' --id 'sp11-camera-daily2'.*?\n\}\n", cfg, re.S)
entry = m.group(0)
entry = entry.replace("'SP11 Golden + Cameras' --id 'sp11-camera-daily2'", "'SP11 IMX681 upstream-driver lab (one-shot)' --id 'sp11-imx681-lab'")
entry = entry.replace(str(SRC), str(DST))
entry = entry.replace(" sp11_camera_daily2=1 sp11_entry=7.1.5-sp11-camera-daily2", " sp11_entry=7.1.5-sp11-imx681-lab")
assert "sp11_camera_daily2=1" not in entry and str(DST) in entry
Path("/boot/grub/custom.cfg").write_text("# SP11 lab entries (one-shot via grub-reboot); not a default.\n" + entry)
print("custom.cfg written")
