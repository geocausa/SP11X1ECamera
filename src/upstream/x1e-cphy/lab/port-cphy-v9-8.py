#!/usr/bin/env python3
"""Port David Heidelberg's C-PHY v9 8/9 (link frequency for C-PHY) onto linux-next CAMSS by hand."""
import re, sys
from pathlib import Path
D = Path(sys.argv[1])


def edit(name, pairs):
    p = D / name
    s = p.read_text()
    for old, new in pairs:
        if s.count(old) < 1:
            sys.exit("%s: no match for %r" % (name, old[:60]))
        s = s.replace(old, new)
    p.write_text(s)


c = (D / "camss.c").read_text()
m = re.search(r"s64 camss_get_link_freq\(struct media_entity \*entity, unsigned int bpp,\n\t\t\tunsigned int lanes\)\n\{.*?\n\}\n", c, re.S)
body = m.group(0)
new = """s64 camss_get_link_freq(struct media_entity *entity, unsigned int bpp,
			unsigned int lanes, const bool cphy)
{
	struct media_pad *sensor_pad;
	unsigned int div = lanes * 2 * (cphy ? CAMSS_CPHY_DIVISOR :
					       CAMSS_DPHY_DIVISOR);

	sensor_pad = camss_find_sensor_pad(entity);
	if (!sensor_pad)
		return -ENODEV;

	return v4l2_get_link_freq(sensor_pad, CAMSS_COMMON_PHY_DIVIDENT * bpp, div);
}
"""
c = c.replace(body, new)
c = c.replace(" * @lanes: Number of lanes in the link to the sensor\n *\n * Return link frequency",
              " * @lanes: Number of lanes in the link to the sensor\n * @cphy: If C-PHY encoding is used.\n *\n * Return link frequency", 1)
if "CAMSS_CPHY_DIVISOR 7" not in c:
    c = c.replace("#define CAMSS_CLOCK_MARGIN_DENOMINATOR 100\n",
                  "#define CAMSS_CLOCK_MARGIN_DENOMINATOR 100\n\n/*\n * C-PHY encodes data by 16/7 ~ 2.28 bits/symbol\n * D-PHY doesn't encode data, thus 16/16 = 1 b/s\n */\n#define CAMSS_COMMON_PHY_DIVIDENT 16\n#define CAMSS_CPHY_DIVISOR 7\n#define CAMSS_DPHY_DIVISOR 16\n", 1)
(D / "camss.c").write_text(c)

edit("camss.h", [("s64 camss_get_link_freq(struct media_entity *entity, unsigned int bpp,\n\t\t\tunsigned int lanes);",
                  "s64 camss_get_link_freq(struct media_entity *entity, unsigned int bpp,\n\t\t\tunsigned int lanes, const bool cphy);")])

s = (D / "camss-csid.c").read_text()
s = re.sub(r"link_freq = camss_get_link_freq\(&csid->subdev.entity, fmt->bpp,\s*csid->phy.lane_cnt\);",
           "link_freq = camss_get_link_freq(&csid->subdev.entity, fmt->bpp, csid->phy.lane_cnt,\n\t\t\t\t\tcsid->phy.phy_sel == CSID_PHY_SEL_CPHY);", s)
(D / "camss-csid.c").write_text(s)

s = (D / "camss-csiphy.c").read_text()
n = 0
for pat in (r"camss_get_link_freq\(&csiphy->subdev.entity, bpp, num_lanes\)",):
    s, n = re.subn(pat, "camss_get_link_freq(&csiphy->subdev.entity, bpp, num_lanes,\n\t\t\t\t\tcsiphy->cfg.csi2->lane_cfg.phy_cfg == V4L2_MBUS_CSI2_CPHY)", s)
(D / "camss-csiphy.c").write_text(s)
print("csiphy call sites:", n)
for f in D.glob("*.c"):
    for ln in f.read_text().splitlines():
        if "camss_get_link_freq(" in ln and "cphy" not in ln and "CPHY" not in ln and "s64 camss_get_link_freq" not in ln:
            print("check:", f.name, ln.strip())
