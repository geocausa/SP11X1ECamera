#!/usr/bin/env python3
"""Add the rear (ov13858) changes to the lab DTB made by make-lab.py: link-frequencies
540/270 MHz (the in-tree driver's two), MCLK assigned 19.2 MHz. Front changes stay."""
import re, subprocess
from pathlib import Path

W = Path("/root/imx681-test")
DST = Path("/boot/sp11-7.1.5-camera-daily2/x1e80100-microsoft-denali-sp11-imx681-lab.dtb")
dts = (W / "lab.dts").read_text()
i = dts.index('compatible = "ovti,ov13858";')
start = dts.rindex("camera@10 {", 0, i)
end = dts.index("\t\t\t\t};\n", dts.index("port {", i))
node = dts[start:end]
clk = re.search(r"clocks = <(0x[0-9a-f]+ 0x[0-9a-f]+)>;", node).group(1)
new = node
if "assigned-clocks" not in new:
    new = new.replace('compatible = "ovti,ov13858";',
                      'compatible = "ovti,ov13858";\n\t\t\t\t\tassigned-clocks = <%s>;\n'
                      '\t\t\t\t\tassigned-clock-rates = <19200000>;' % clk)
new = re.sub(r"link-frequencies = <0x00 0x23556900>;", "link-frequencies = /bits/ 64 <540000000 270000000>;", new)
assert "540000000" in new
dts = dts[:start] + new + dts[end:]
(W / "lab.dts").write_text(dts)
subprocess.run(["dtc", "-q", "-I", "dts", "-O", "dtb", "-o", str(DST), str(W / "lab.dts")], check=True)
print("dtb", DST)
