/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008n: consumed single-use wrapper around E008l command ownership + E008k
 * complete unreachable rear transaction. Still no runtime entry point.
 */
#ifndef VFE680_E008N_REAR_SINGLE_USE_WRAPPER_INC
#define VFE680_E008N_REAR_SINGLE_USE_WRAPPER_INC

struct e008n_rear_request {
	struct v4l2_subdev *sensor;
	struct e007d_rear_register_state *regs;
	struct e007v_rear_dmi_state *dmi_state;
	u64 packet_request_id[E007Y_STARTUP_PACKETS];
	u64 first_request_generation;
	unsigned long epoch_timeout_us;
	unsigned long done_timeout_us;
};

struct e008n_rear_result {
	struct e008k_rear_result transaction;
	bool identity_consumed;
	bool command_arena_allocated;
	bool preflight_materialized;
	bool command_arena_released;
	bool reboot_required;
};

static atomic_t e008n_rear_consumed = ATOMIC_INIT(0);

static void
e008n_rear_fill_kreq(struct e008k_rear_request *dst,
		     struct e008n_rear_request *src,
		     struct e008l_rear_command_set *commands)
{
	unsigned int p;

	memset(dst, 0, sizeof(*dst));
	dst->sensor = src->sensor;
	dst->regs = src->regs;
	dst->dmi_state = src->dmi_state;
	dst->first_request_generation = src->first_request_generation;
	dst->epoch_timeout_us = src->epoch_timeout_us;
	dst->done_timeout_us = src->done_timeout_us;
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		struct e007y_rear_startup_output *out =
			e008l_rear_command_output(commands, p);

		dst->packet_request_id[p] = src->packet_request_id[p];
		if (out)
			dst->packet[p] = *out;
	}
}

/*
 * This wrapper consumes its in-module identity on the first call, even if
 * preflight fails. That makes a future wired candidate disposable by
 * construction and prevents a retry against uncertain shared hardware state.
 */
static int __used
e008n_rear_run_once_unreachable(struct vfe_device *vfe,
				 struct e008n_rear_request *req,
				 struct e008n_rear_result *result)
{
	struct e008l_rear_command_set *commands;
	struct e008k_rear_request kreq;
	unsigned int p;
	int ret;

	if (!vfe || !req || !result)
		return -EINVAL;
	memset(result, 0, sizeof(*result));

	if (atomic_cmpxchg(&e008n_rear_consumed, 0, 1))
		return -EALREADY;
	result->identity_consumed = true;

	commands = kzalloc(sizeof(*commands), GFP_KERNEL);
	if (!commands)
		return -ENOMEM;

	ret = e008l_rear_command_alloc(vfe, commands);
	if (ret)
		goto out_free_wrapper;
	result->command_arena_allocated = true;

	e008n_rear_fill_kreq(&kreq, req, commands);

	/*
	 * Preflight while every command allocation is still known unsubmitted.
	 * E008k repeats these checks; that duplication is intentional so the
	 * accepted E008k contract remains self-contained.
	 */
	ret = e008k_rear_validate_route(vfe->camss, req->sensor);
	if (ret)
		goto out_release_clean;
	ret = e008k_rear_materialize_all(&kreq);
	if (ret)
		goto out_release_clean;
	result->preflight_materialized = true;

	/*
	 * Before E008k can submit its first BL, conservatively mark the complete
	 * command set hardware-exposed. This means any failure after this point
	 * pins all command DMA rather than risking a partial-FIFO-fetch UAF.
	 */
	for (p = 0; p < E007Y_STARTUP_PACKETS; p++) {
		ret = e008l_rear_command_mark_submitted(commands, p);
		if (ret)
			goto out_pin;
	}
	result->reboot_required = true;

	ret = e008k_rear_run_unreachable(vfe, &kreq, &result->transaction);
	if (ret)
		goto out_pin;

	if (!result->transaction.rtcdm_stopped ||
	    !result->transaction.owner_released ||
	    !result->transaction.both_frames_complete) {
		ret = -EIO;
		goto out_pin;
	}

	/*
	 * E008k successful teardown proves RT-CDM stopped, so command DMA may
	 * finally be released. Output DMA remains intentionally pinned by E008k;
	 * the one-shot still requires reboot before any second camera attempt.
	 */
	ret = e008l_rear_command_release(vfe, commands, true);
	if (ret)
		goto out_pin;
	result->command_arena_released = true;
	kfree(commands);
	return 0;

out_release_clean:
	(void)e008l_rear_command_release(vfe, commands, false);
out_free_wrapper:
	kfree(commands);
	return ret;

out_pin:
	/*
	 * Deliberately leak/pin coherent command memory until reboot. The future
	 * runtime package must treat reboot as mandatory on every post-preflight
	 * return, success or failure.
	 */
	return ret ? ret : -EIO;
}

struct e008n_rear_single_use_ops {
	int (*run_once_unreachable)(struct vfe_device *,
				    struct e008n_rear_request *,
				    struct e008n_rear_result *);
};

static const struct e008n_rear_single_use_ops
e008n_rear_single_use_recipe __used = {
	.run_once_unreachable = e008n_rear_run_once_unreachable,
};

static int __used e008n_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

#endif
