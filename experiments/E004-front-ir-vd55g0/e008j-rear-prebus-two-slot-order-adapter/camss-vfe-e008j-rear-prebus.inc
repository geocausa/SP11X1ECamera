/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008j: build-only adapter which splits E008h allocation from its slot0
 * disabled MMIO preload. E008g proves rear startup packet0 is consumed
 * before BUS configuration, so a final runner must be able to allocate/bind
 * both Linux-owned slots without touching VFE registers, submit packet0, then
 * prepare+enable slot0.
 *
 * No runtime call site exists.
 */
#ifndef VFE680_E008J_REAR_PREBUS_ADAPTER_INC
#define VFE680_E008J_REAR_PREBUS_ADAPTER_INC

static int __used
e008j_rear_alloc_pair_no_mmio(struct vfe_device *vfe,
			      struct e008h_rear_prime_pair *pair)
{
	int ret;

	if (!vfe680_e004nt_rear_4k_target(vfe) || !pair)
		return -EINVAL;
	if (pair->allocated || pair->faulted ||
	    pair->dma[0].allocated || pair->dma[1].allocated ||
	    pair->slot0_preloaded_disabled || pair->ledgers_bound ||
	    pair->enabled || pair->programmed[0] || pair->programmed[1])
		return -EBUSY;

	ret = e008d_rear_dma_alloc(vfe, &pair->dma[0]);
	if (ret)
		return ret;
	ret = e008d_rear_dma_alloc(vfe, &pair->dma[1]);
	if (ret)
		goto fail;

	ret = e008d_rear_build_addresses(vfe, &pair->dma[0], &pair->addr[0]);
	if (ret)
		goto fail;
	ret = e008d_rear_build_addresses(vfe, &pair->dma[1], &pair->addr[1]);
	if (ret)
		goto fail;
	ret = e008h_rear_validate_pair_disjoint(pair);
	if (ret)
		goto fail;

	pair->allocated = true;
	return 0;

fail:
	e008h_rear_release_before_mmio(vfe, pair);
	return ret;
}

static int __used
e008j_rear_bind_pair_no_mmio(struct e008h_rear_prime_pair *pair,
			     u64 owner_epoch, u64 first_request_generation)
{
	struct e007z_rear_binding binding[E008H_REAR_SLOTS][E007Z_REAR_WMS];
	struct e007z_rear_frame tmp[E008H_REAR_SLOTS] = {};
	unsigned int s;
	int ret;

	if (!pair || !pair->allocated || pair->slot0_preloaded_disabled ||
	    pair->ledgers_bound || pair->enabled || pair->faulted ||
	    !owner_epoch || !first_request_generation ||
	    first_request_generation == U64_MAX)
		return -EINVAL;

	ret = e008h_rear_validate_pair_disjoint(pair);
	if (ret)
		return ret;
	for (s = 0; s < E008H_REAR_SLOTS; s++) {
		ret = e008h_rear_build_binding(pair, s, binding[s]);
		if (ret)
			return ret;
		ret = e007z_rear_bind(&tmp[s], owner_epoch,
				      first_request_generation + s,
				      binding[s]);
		if (ret)
			return ret;
	}

	memcpy(pair->frame, tmp, sizeof(tmp));
	pair->ledgers_bound = true;
	return 0;
}

/*
 * First VFE/BUS MMIO point for the future rear runner.
 * Caller ordering contract:
 *
 *   alloc_pair_no_mmio -> bind_pair_no_mmio -> E007y packet0 submit
 *   -> prepare_slot0_after_packet0 -> E008h enable_slot0 -> E007y packet1
 *
 * E008d keeps every WM disabled while installing static config and owned
 * slot0 addresses. E008h then enables in E008f live resource order and
 * rewrites/readbacks the same owned addresses after enable.
 */
static int __used
e008j_rear_prepare_slot0_after_packet0(struct vfe_device *vfe,
				       struct e008h_rear_prime_pair *pair)
{
	int ret;

	if (!vfe680_e004nt_rear_4k_target(vfe) || !pair ||
	    !pair->allocated || !pair->ledgers_bound ||
	    pair->slot0_preloaded_disabled || pair->enabled ||
	    pair->programmed[0] || pair->programmed[1] || pair->faulted)
		return -EINVAL;

	ret = e008d_rear_prepare_addresses_disabled(vfe, &pair->dma[0],
						    &pair->addr[0]);
	if (ret) {
		pair->faulted = true;
		e008h_rear_fault_ledgers(pair, pair->frame[0].owner_epoch);
		return ret;
	}

	pair->slot0_preloaded_disabled = true;
	return 0;
}

struct e008j_rear_prebus_ops {
	int (*alloc_no_mmio)(struct vfe_device *, struct e008h_rear_prime_pair *);
	int (*bind_no_mmio)(struct e008h_rear_prime_pair *, u64, u64);
	int (*prepare_slot0_after_packet0)(struct vfe_device *,
					  struct e008h_rear_prime_pair *);
};

static const struct e008j_rear_prebus_ops
e008j_rear_prebus_recipe __used = {
	.alloc_no_mmio = e008j_rear_alloc_pair_no_mmio,
	.bind_no_mmio = e008j_rear_bind_pair_no_mmio,
	.prepare_slot0_after_packet0 = e008j_rear_prepare_slot0_after_packet0,
};

static int __used e008j_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

#endif
