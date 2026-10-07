/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * Internal sleepable startup handoff. Caller supplies typed semantic inputs,
 * never register commands, DMA addresses or a userspace pointer. This is not
 * a UAPI or a registered V4L2 callback. Production authorization stays denied.
 */
struct native_rear_startup_request {
 struct v4l2_subdev *sensor;
 const struct native_rear_startup_input *input;
 u64 first_request_generation;
 unsigned long epoch_timeout_us, done_timeout_us;
};
struct native_rear_startup_result {
 struct e008n_rear_result once;
 bool composed;
};
static int
native_rear_startup_run_once_unreachable(struct vfe_device *vfe,
                                        const struct native_rear_startup_request *request,
                                        struct native_rear_startup_result *result)
{
 struct e008o_rear_semantic_set *semantics;
 struct e008n_rear_request run = {};
 int ret;

 if (!vfe || !vfe->camss || !request || !result ||
     !request->sensor || !request->input ||
     !request->first_request_generation ||
     request->first_request_generation == U64_MAX)
  return -EINVAL;
 memset(result, 0, sizeof(*result));
 semantics = kzalloc(sizeof(*semantics), GFP_KERNEL);
 if (!semantics)
  return -ENOMEM;
 ret = native_rear_compose_startup(semantics, request->input);
 if (ret)
  goto out;
 result->composed = true;
 run.sensor = request->sensor;
 run.semantics = semantics;
 run.first_request_generation = request->first_request_generation;
 run.epoch_timeout_us = request->epoch_timeout_us;
 run.done_timeout_us = request->done_timeout_us;
 ret = e008n_rear_run_once_unreachable(vfe, &run, &result->once);
out:
 /*
  * The synchronous wrapper copies every command/DMI byte into its owned arena
  * before exposure. It retains no semantic/provider pointer after returning.
  * An uncertain arena remains pinned by that wrapper, independently of these
  * input-only semantics. Never clear/free the arena from this handoff.
  */
 memzero_explicit(semantics, sizeof(*semantics));
 kfree(semantics);
 return ret;
}
static typeof(&native_rear_startup_run_once_unreachable)
native_rear_startup_entry_recipe __used = native_rear_startup_run_once_unreachable;
