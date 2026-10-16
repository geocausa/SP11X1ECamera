#!/usr/bin/env python3
"""Test-only: isl_mode param for the VD55G0 0x0329 question (Sergey).
0 = never write (our fix), 1 = write 0 at every stream start (Peter v2), 2 = write 0 once per power-on
after boot, in software standby (Sergey's driver). Logs 0x0329 and FSM before START and once streaming."""
import sys
p = sys.argv[1]
s = open(p).read()
def rep(old, new):
    global s
    assert s.count(old) == 1, old[:60]
    s = s.replace(old, new)
rep("static int vd55g1_enable_streams(struct v4l2_subdev *sd,", """static int isl_mode;
module_param(isl_mode, int, 0644);

static void sp11_isl_dump(struct vd55g1 *sensor, const char *tag)
{
	u64 isl = 0, fsm = 0;

	cci_read(sensor->regmap, CCI_REG8(0x0329), &isl, NULL);
	cci_read(sensor->regmap, CCI_REG8(0x002c), &fsm, NULL);
	dev_info(sensor->dev, "SP11ISL %s mode=%d isl=0x%02llx fsm=%llu\\n", tag, isl_mode, isl, fsm);
}

static int vd55g1_enable_streams(struct v4l2_subdev *sd,""")
rep("""	if (sensor->model->reg_map[REG_ISL_ENABLE])
		vd55g1_write(sensor, REG_ISL_ENABLE, 0, &ret);
	if (ret)
		goto err_rpm_put;
""", """	if (sensor->model->reg_map[REG_ISL_ENABLE])
		vd55g1_write(sensor, REG_ISL_ENABLE, 0, &ret);
	if (isl_mode == 1)
		cci_write(sensor->regmap, CCI_REG8(0x0329), 0, &ret);
	if (ret)
		goto err_rpm_put;
""")
rep("""	/* Start streaming */
	vd55g1_write(sensor, REG_STBY, VD55G1_STBY_START_STREAM, &ret);
	vd55g1_poll_reg(sensor, REG_STBY, 0, &ret);
	vd55g1_wait_state(sensor, VD55G1_SYSTEM_FSM_STREAMING, &ret);
""", """	sp11_isl_dump(sensor, "prestart");
	/* Start streaming */
	vd55g1_write(sensor, REG_STBY, VD55G1_STBY_START_STREAM, &ret);
	vd55g1_poll_reg(sensor, REG_STBY, 0, &ret);
	vd55g1_wait_state(sensor, VD55G1_SYSTEM_FSM_STREAMING, &ret);
	sp11_isl_dump(sensor, "streaming");
""")
rep("""	ret = vd55g1_patch(sensor);
	if (ret)
		goto disable_clock;

	return 0;
""", """	ret = vd55g1_patch(sensor);
	if (ret)
		goto disable_clock;

	if (isl_mode == 2) {
		sp11_isl_dump(sensor, "poweron-before");
		cci_write(sensor->regmap, CCI_REG8(0x0329), 0, &ret);
		sp11_isl_dump(sensor, "poweron-after");
		if (ret)
			goto disable_clock;
	}

	return 0;
""")
# forward declaration needed: power_on is after enable_streams, fine; dump defined before both.
open(p, "w").write(s)
print("ok")
