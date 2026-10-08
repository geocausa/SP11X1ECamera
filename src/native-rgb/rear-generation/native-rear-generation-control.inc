/* SPDX-License-Identifier: GPL-2.0-only */
/* Candidate-only trigger: userspace supplies no configuration or commands. */
#define V4L2_CID_QCOM_CAMSS_REAR_GENERATION (V4L2_CID_USER_BASE + 0x1244)
static int video_rear_generation_s_ctrl(struct v4l2_ctrl *ctrl)
{
 struct camss_video *video = container_of(ctrl->handler, struct camss_video, ctrl_handler);
 if (ctrl->id != V4L2_CID_QCOM_CAMSS_REAR_GENERATION || !video_is_x1e_front_pix(video))
  return -EINVAL;
 if (!ctrl->val)
  return 0;
 return camss_x1e_rear_generation_once(video);
}
static const struct v4l2_ctrl_ops video_rear_generation_ops = {
 .s_ctrl = video_rear_generation_s_ctrl,
};
static const struct v4l2_ctrl_config video_rear_generation_ctrl = {
 .ops = &video_rear_generation_ops,
 .id = V4L2_CID_QCOM_CAMSS_REAR_GENERATION,
 .name = "Rear generation one use",
 .type = V4L2_CTRL_TYPE_BOOLEAN,
 .min = 0, .max = 1, .step = 1, .def = 0,
 .flags = V4L2_CTRL_FLAG_WRITE_ONLY | V4L2_CTRL_FLAG_EXECUTE_ON_WRITE,
};
