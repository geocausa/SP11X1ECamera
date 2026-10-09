/* SPDX-License-Identifier: GPL-2.0-only */
/* Candidate-only readback after normal control setup, before STREAMING.
 * Reads only the documented sensor control registers; no control writes.
 */
static int native_rear_sensor_controls_readback(struct ov13858 *ov13858)
{
 struct v4l2_ctrl *ec = v4l2_ctrl_find(ov13858->sd.ctrl_handler, V4L2_CID_EXPOSURE);
 struct v4l2_ctrl *ac = v4l2_ctrl_find(ov13858->sd.ctrl_handler, V4L2_CID_ANALOGUE_GAIN);
 struct v4l2_ctrl *dc = v4l2_ctrl_find(ov13858->sd.ctrl_handler, V4L2_CID_DIGITAL_GAIN);
 struct v4l2_ctrl *tc = v4l2_ctrl_find(ov13858->sd.ctrl_handler, V4L2_CID_TEST_PATTERN);
 u32 exposure, analog, blue, green, red, pattern, expected_pattern;
 int ret;
 if (!ec || !ac || !dc || !tc)
  return -EPROTO;
 ret = ov13858_read_reg(ov13858, 0x3500, 3, &exposure);
 if (ret) return ret;
 ret = ov13858_read_reg(ov13858, 0x3508, 2, &analog);
 if (ret) return ret;
 ret = ov13858_read_reg(ov13858, 0x5100, 2, &blue);
 if (ret) return ret;
 ret = ov13858_read_reg(ov13858, 0x5102, 2, &green);
 if (ret) return ret;
 ret = ov13858_read_reg(ov13858, 0x5104, 2, &red);
 if (ret) return ret;
 ret = ov13858_read_reg(ov13858, 0x4503, 1, &pattern);
 if (ret) return ret;
 expected_pattern = tc->val ? 0x80U | (tc->val - 1) : 0U;
 if (exposure != (u32)ec->val << 4 || analog != (u32)ac->val ||
     blue != (u32)dc->val || green != (u32)dc->val ||
     red != (u32)dc->val || (pattern & (tc->val ? 0x83U : 0x80U)) != expected_pattern)
  return -EPROTO;
 dev_info(ov13858->dev, "NATIVE_REAR_SENSOR_CONTROLS exposure_reg=%u exposure_lines=%u analog=%u digital_b=%u digital_g=%u digital_r=%u pattern_reg=%u pattern_control=%u\n",
          exposure, (u32)ec->val, analog, blue, green, red, pattern, (u32)tc->val);
 return 0;
}
