/* SPDX-License-Identifier: GPL-2.0-only */
/* E011AR: packet-isolated one-shot wrapper; no runtime caller. */
#ifndef VFE680_E011AR_REAR_SINGLE_USE_INC
#define VFE680_E011AR_REAR_SINGLE_USE_INC

struct e011ar_rear_once_request {
	struct v4l2_subdev *sensor;
	struct e008o_rear_semantic_set *semantics;
	u64 first_request_generation;
	unsigned long epoch_timeout_us;
	unsigned long done_timeout_us;
};

struct e011ar_rear_once_result {
	struct e011ar_rear_result transaction;
	bool identity_consumed;
	bool command_arena_allocated;
	bool command_arena_released;
	bool reboot_required;
};

static atomic_t e011ar_rear_consumed = ATOMIC_INIT(0);

static int __used
e011ar_rear_run_once_unreachable(struct vfe_device *vfe,
				  struct e011ar_rear_once_request *req,
				  struct e011ar_rear_once_result *result)
{
	struct e008l_rear_command_set *commands;
	struct e011ar_rear_request run = { };
	int ret;

	if (!vfe || !vfe->camss || !req || !result)
		return -EINVAL;
	memset(result, 0, sizeof(*result));
	if (atomic_cmpxchg(&e011ar_rear_consumed, 0, 1))
		return -EALREADY;
	result->identity_consumed = true;

	/* Reject incomplete semantics before allocating any command arena. */
	ret = e008o_rear_validate_semantic_set(req->semantics);
	if (ret)
		return ret;
	if (!req->sensor || !req->first_request_generation ||
	    req->first_request_generation == U64_MAX)
		return -EINVAL;
	ret = e008k_rear_validate_route(vfe->camss, req->sensor);
	if (ret)
		return ret;

	commands = kzalloc(sizeof(*commands), GFP_KERNEL);
	if (!commands)
		return -ENOMEM;
	ret = e008l_rear_command_alloc(vfe, commands);
	if (ret)
		goto out_free;
	result->command_arena_allocated = true;

	run.sensor = req->sensor;
	run.semantics = req->semantics;
	run.commands = commands;
	run.first_request_generation = req->first_request_generation;
	run.epoch_timeout_us = req->epoch_timeout_us;
	run.done_timeout_us = req->done_timeout_us;

	/* Runner materializes once, before owner acquire or hardware exposure. */
	ret = e011ar_rear_run_unreachable(vfe, &run, &result->transaction);
	result->reboot_required = commands->hardware_exposed;
	if (ret) {
		if (commands->hardware_exposed)
			goto out_pin;
		goto out_release_clean;
	}
	if (!commands->hardware_exposed ||
	    !result->transaction.rtcdm_stopped ||
	    !result->transaction.both_frames_complete ||
	    !result->transaction.owner_released ||
	    !result->transaction.dma_intentionally_pinned) {
		ret = -EIO;
		goto out_pin;
	}

	/* Exposed commands may free only after the accepted stop proof. */
	ret = e008l_rear_command_release(vfe, commands, true);
	if (ret)
		goto out_pin;
	result->command_arena_released = true;
	kfree(commands);
	return 0;

out_release_clean:
	if (e008l_rear_command_release(vfe, commands, false))
		goto out_pin;
	result->command_arena_released = true;
out_free:
	kfree(commands);
	return ret;

out_pin:
	/* Never free uncertain command/output DMA; never retry this identity. */
	result->reboot_required = true;
	return ret ? ret : -EIO;
}

struct e011ar_rear_single_use_ops {
	int (*run_once_unreachable)(struct vfe_device *,
				    struct e011ar_rear_once_request *,
				    struct e011ar_rear_once_result *);
};
static const struct e011ar_rear_single_use_ops
e011ar_rear_single_use_recipe __used = {
	.run_once_unreachable = e011ar_rear_run_once_unreachable,
};
static int __used e011ar_rear_once_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}
#endif
