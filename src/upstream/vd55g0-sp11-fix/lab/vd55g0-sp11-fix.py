#!/usr/bin/env python3
"""Fix-up for the VD55G0 support in vd55g1.c (Peter Marshall's v2), found on Surface Pro 11:
 - VD55G0 needs a 1200-pixel minimum line length when the MIPI rate is below 900 Mbps
   (as in ST's reference vd55g0 driver); 1128 stalls the sensor (no frames, stop times out).
 - Writing 0 to 0x0329 (mapped as ISL_ENABLE) stops VD55G0 frame output; ST's driver never
   touches it, so drop it from the VD55G0 map and only write ISL_ENABLE where it exists.
Exact-match edits."""
import sys
p = sys.argv[1]
s = open(p).read()


def rep(old, new):
    global s
    if s.count(old) != 1:
        sys.exit("edit failed (%d): %r" % (s.count(old), old[:60]))
    s = s.replace(old, new)


rep("""	[REG_ISL_ENABLE] = CCI_REG8(0x0329),
""", "")

rep("""#define VD55G0_MIPI_RATE_MAX				(1200 * MEGA)
""", """#define VD55G0_MIPI_RATE_MAX				(1200 * MEGA)
#define VD55G0_LINE_LENGTH_LOW_RATE			1200
#define VD55G0_LOW_MIPI_RATE_LIMIT			(900 * MEGA)
""")

rep("""	u32 mipi_rate_min;
	u32 mipi_rate_max;
	u16 width;""", """	u32 mipi_rate_min;
	u32 mipi_rate_max;
	u32 low_mipi_rate_limit;
	u16 line_length_low_rate;
	u16 width;""")

rep("""	.mipi_rate_min = VD55G0_MIPI_RATE_MIN,
	.mipi_rate_max = VD55G0_MIPI_RATE_MAX,
""", """	.mipi_rate_min = VD55G0_MIPI_RATE_MIN,
	.mipi_rate_max = VD55G0_MIPI_RATE_MAX,
	.low_mipi_rate_limit = VD55G0_LOW_MIPI_RATE_LIMIT,
	.line_length_low_rate = VD55G0_LINE_LENGTH_LOW_RATE,
""")

rep("""	min_line_length = VD55G1_LINE_LENGTH_MIN;
	if (sensor->model->hdr &&""", """	min_line_length = VD55G1_LINE_LENGTH_MIN;
	if (sensor->mipi_rate < sensor->model->low_mipi_rate_limit)
		min_line_length = sensor->model->line_length_low_rate;
	if (sensor->model->hdr &&""")

rep("""	vd55g1_write(sensor, REG_ISL_ENABLE, 0, &ret);
""", """	if (sensor->model->reg_map[REG_ISL_ENABLE])
		vd55g1_write(sensor, REG_ISL_ENABLE, 0, &ret);
""")

open(p, "w").write(s)
print("ok")
