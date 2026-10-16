#!/usr/bin/env python3
"""Test-only debug variant of vd55g1.c (Peter's VD55G0 v2) for SP11.
Module params:
  oif_override: -1 = driver value (default), -2 = do not write OIF_CTRL, >=0 = write this value
  skip_isl:     1 = do not write REG_ISL_ENABLE
Logs OIF_CTRL / ISL before and after, and FSM + 0x030c after stream start."""
import sys
p = sys.argv[1]
s = open(p).read()


def rep(old, new):
    global s
    if s.count(old) != 1:
        sys.exit("edit failed (%d): %r" % (s.count(old), old[:60]))
    s = s.replace(old, new)


rep("""static int vd55g1_enable_streams(struct v4l2_subdev *sd,""",
    """static int oif_override = -1;
module_param(oif_override, int, 0644);
static int skip_isl;
module_param(skip_isl, int, 0644);

static void sp11_dbg_dump(struct vd55g1 *sensor, const char *tag)
{
	u64 oif = 0, isl = 0, fsm = 0, fmt = 0, dt = 0, mipi = 0, ext = 0, lin = 0;

	cci_read(sensor->regmap, CCI_REG16_LE(0x030c), &oif, NULL);
	cci_read(sensor->regmap, CCI_REG8(0x0329), &isl, NULL);
	cci_read(sensor->regmap, CCI_REG8(0x002c), &fsm, NULL);
	cci_read(sensor->regmap, CCI_REG8(0x030a), &fmt, NULL);
	cci_read(sensor->regmap, CCI_REG8(0x030f), &dt, NULL);
	cci_read(sensor->regmap, CCI_REG32_LE(0x0224), &mipi, NULL);
	cci_read(sensor->regmap, CCI_REG32_LE(0x0220), &ext, NULL);
	cci_read(sensor->regmap, CCI_REG16_LE(0x0300), &lin, NULL);
	dev_info(sensor->dev,
		 "SP11DBG %s oif=0x%04llx isl=0x%02llx fsm=%llu fmt=%llu dt=0x%02llx mipi=%llu ext=%llu line=%llu\\n",
		 tag, oif, isl, fsm, fmt, dt, mipi, ext, lin);
}

static int vd55g1_enable_streams(struct v4l2_subdev *sd,""")

rep("""	/* Configure output */
	vd55g1_write(sensor, REG_MIPI_DATA_RATE, sensor->mipi_rate, &ret);
	vd55g1_write(sensor, REG_OIF_CTRL, sensor->oif_ctrl, &ret);
	vd55g1_write(sensor, REG_ISL_ENABLE, 0, &ret);
""", """	sp11_dbg_dump(sensor, "pre");
	/* Configure output */
	vd55g1_write(sensor, REG_MIPI_DATA_RATE, sensor->mipi_rate, &ret);
	if (oif_override == -1)
		vd55g1_write(sensor, REG_OIF_CTRL, sensor->oif_ctrl, &ret);
	else if (oif_override >= 0)
		vd55g1_write(sensor, REG_OIF_CTRL, oif_override, &ret);
	if (!skip_isl)
		vd55g1_write(sensor, REG_ISL_ENABLE, 0, &ret);
	dev_info(sensor->dev, "SP11DBG oif_override=%d skip_isl=%d drv_oif=0x%x\\n",
		 oif_override, skip_isl, sensor->oif_ctrl);
""")

rep("""	vd55g1_wait_state(sensor, VD55G1_SYSTEM_FSM_STREAMING, &ret);
	if (ret)
		goto err_rpm_put;

	vd55g1_grab_ctrls(sensor, true);
""", """	vd55g1_wait_state(sensor, VD55G1_SYSTEM_FSM_STREAMING, &ret);
	sp11_dbg_dump(sensor, "started");
	if (ret)
		goto err_rpm_put;

	vd55g1_grab_ctrls(sensor, true);
""")

open(p, "w").write(s)
print("ok")
