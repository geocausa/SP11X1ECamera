/* SPDX-License-Identifier: GPL-2.0-only */
/* Existing sensor mutex held; reads only the control just written.
 * Never call public v4l2_ctrl_find or acquire the same mutex again.
 */
static int native_rear_live_control_readback(struct ov13858 *ov13858,
                                             struct v4l2_ctrl *ctrl)
{
 u32 value,reg,length,expected;
 u64 begin,end;
 int ret;
 lockdep_assert_held(&ov13858->mutex);
 if (!ov13858->native_control_streaming)
  return -EPROTO;
 if (ctrl->id == V4L2_CID_EXPOSURE) {
  reg=0x3500;length=3;expected=(u32)ctrl->val << 4;
 } else if (ctrl->id == V4L2_CID_ANALOGUE_GAIN) {
  reg=0x3508;length=2;expected=(u32)ctrl->val;
 } else {
  return -EOPNOTSUPP;
 }
 begin=ktime_get_ns();
 ret=ov13858_read_reg(ov13858,reg,length,&value);
 end=ktime_get_ns();
 if (ret) return ret;
 if (value!=expected || end<begin) return -EPROTO;
 dev_info(ov13858->dev,
  "NATIVE_REAR_LIVE_CONTROL id=%u value=%d reg=%u readback=%u before_ns=%llu after_ns=%llu\n",
  ctrl->id,ctrl->val,reg,value,(unsigned long long)begin,(unsigned long long)end);
 return 0;
}
