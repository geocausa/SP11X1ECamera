/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008h: build-only rear two-slot ten-WM prime/ownership scaffold.
 *
 * No runtime call site is installed. This source allocates two complete
 * Linux-owned E008d DMA sets, binds two independent E007z exact-consumed-IOVA
 * ledgers, and models the Windows-proven initial BUS sequence without
 * submitting RT-CDM, starting CSID/PHY/sensor, or exposing a V4L2 buffer.
 */
#ifndef VFE680_E008H_REAR_TWO_SLOT_PRIME_INC
#define VFE680_E008H_REAR_TWO_SLOT_PRIME_INC

#define E008H_REAR_SLOTS 2U

/*
 * Resource order source-locked by E008f:
 * FULL(0x3000: WM0 then WM1), DS4, DS16, AEC_BE, RS, BHIST, AWB_BG,
 * TL_BG, BAF. The WM mapping for the first nine is the accepted front BUS
 * contract; WM16/0x300d is the rear-only E008f/E004oj BAF resource.
 */
static const u8 e008h_rear_program_wms[E007Z_REAR_WMS] = {
	0, 1, 2, 3, 11, 18, 12, 14, 13, 16,
};
static_assert(ARRAY_SIZE(e008h_rear_program_wms) == E007Z_REAR_WMS);

struct e008h_rear_prime_pair {
	struct e008d_rear_dma_set dma[E008H_REAR_SLOTS];
	struct e008d_rear_addresses addr[E008H_REAR_SLOTS];
	struct e007z_rear_frame frame[E008H_REAR_SLOTS];
	bool allocated;
	bool slot0_preloaded_disabled;
	bool ledgers_bound;
	bool enabled;
	bool programmed[E008H_REAR_SLOTS];
	bool faulted;
};

static int
e008h_rear_addr_index(const struct e008d_rear_addresses *addr, u8 wm)
{
	unsigned int i;

	if (!addr)
		return -EINVAL;
	for (i = 0; i < VFE680_E004NU_REAR_CLIENTS; i++)
		if (addr->wm[i] == wm)
			return i;
	return -ENOENT;
}

static int
e008h_rear_build_binding(struct e008h_rear_prime_pair *pair,
			 unsigned int slot,
			 struct e007z_rear_binding out[E007Z_REAR_WMS])
{
	struct e008d_rear_dma_set *set;
	struct e008d_rear_addresses *addr;
	unsigned int i;

	if (!pair || !out || slot >= E008H_REAR_SLOTS)
		return -EINVAL;
	set = &pair->dma[slot];
	addr = &pair->addr[slot];
	if (!set->allocated)
		return -EINVAL;

	for (i = 0; i < E007Z_REAR_WMS; i++) {
		const struct e007z_rear_wm_desc *desc = &e007z_rear_wm_descs[i];
		struct e008d_rear_aux_buffer *aux;
		u64 owned_base;
		u32 owned_bytes;
		int ai;
		int ret;

		ai = e008h_rear_addr_index(addr, desc->wm);
		if (ai < 0)
			return ai;

		switch (desc->wm) {
		case 0:
			owned_base = (u64)set->full.dma;
			owned_bytes = VFE680_E004NT_REAR_Y_FRAME_INCR;
			break;
		case 1:
			owned_base = (u64)set->full.dma +
				     VFE680_E004NT_REAR_C_META_OFFSET;
			owned_bytes = VFE680_E004NT_REAR_C_FRAME_INCR;
			break;
		default:
			aux = e008d_rear_aux_for_wm(set, desc->wm);
			if (!aux || !aux->cpu || !aux->size)
				return -EINVAL;
			owned_base = (u64)aux->dma;
			owned_bytes = aux->size;
			break;
		}

		if (!owned_base || owned_base > U32_MAX)
			return -ERANGE;
		out[i].wm = desc->wm;
		out[i].owned_base_iova = (u32)owned_base;
		out[i].owned_bytes = owned_bytes;
		out[i].programmed_image_iova = addr->image[ai];

		ret = e007z_rear_validate_binding(desc, &out[i]);
		if (ret)
			return ret;
	}

	return 0;
}

static int
e008h_rear_validate_pair_disjoint(struct e008h_rear_prime_pair *pair)
{
	struct e007z_rear_binding b[E008H_REAR_SLOTS][E007Z_REAR_WMS];
	unsigned int i, j;
	int ret;

	ret = e008h_rear_build_binding(pair, 0, b[0]);
	if (ret)
		return ret;
	ret = e008h_rear_build_binding(pair, 1, b[1]);
	if (ret)
		return ret;

	for (i = 0; i < E007Z_REAR_WMS; i++)
		for (j = 0; j < E007Z_REAR_WMS; j++)
			if (e007z_rear_spans_overlap(b[0][i].owned_base_iova,
						     b[0][i].owned_bytes,
						     b[1][j].owned_base_iova,
						     b[1][j].owned_bytes))
				return -EADDRINUSE;

	return 0;
}

static void
e008h_rear_release_before_mmio(struct vfe_device *vfe,
			       struct e008h_rear_prime_pair *pair)
{
	if (!vfe || !pair)
		return;
	e008d_rear_release_partial(vfe, &pair->dma[1]);
	e008d_rear_release_partial(vfe, &pair->dma[0]);
	memset(pair, 0, sizeof(*pair));
}

/*
 * Allocate two complete, distinct rear output sets. Slot0 is then preloaded
 * while every WM is still disabled. This preload is a Linux safety measure:
 * when a later checkpoint enables the WMs there is never an enabled interval
 * containing an unowned/stale address. The post-enable helper rewrites slot0
 * again, preserving the Windows-observed enable -> initial-address sequence.
 */
static int __used
e008h_rear_alloc_prime_pair(struct vfe_device *vfe,
			    struct e008h_rear_prime_pair *pair)
{
	int ret;

	if (!vfe680_e004nt_rear_4k_target(vfe) || !pair)
		return -EINVAL;
	if (pair->allocated || pair->faulted ||
	    pair->dma[0].allocated || pair->dma[1].allocated)
		return -EBUSY;

	ret = e008d_rear_dma_alloc(vfe, &pair->dma[0]);
	if (ret)
		return ret;
	ret = e008d_rear_dma_alloc(vfe, &pair->dma[1]);
	if (ret) {
		e008h_rear_release_before_mmio(vfe, pair);
		return ret;
	}

	ret = e008d_rear_build_addresses(vfe, &pair->dma[0], &pair->addr[0]);
	if (ret)
		goto fail_before_mmio;
	ret = e008d_rear_build_addresses(vfe, &pair->dma[1], &pair->addr[1]);
	if (ret)
		goto fail_before_mmio;
	ret = e008h_rear_validate_pair_disjoint(pair);
	if (ret)
		goto fail_before_mmio;

	/*
	 * From this call onward, a failure is conservatively pinned: the helper
	 * may have touched VFE registers. Never free/reuse either DMA set on the
	 * error path merely because no stream was intentionally started.
	 */
	ret = e008d_rear_prepare_addresses_disabled(vfe, &pair->dma[0],
						    &pair->addr[0]);
	if (ret) {
		pair->allocated = true;
		pair->faulted = true;
		return ret;
	}

	pair->allocated = true;
	pair->slot0_preloaded_disabled = true;
	return 0;

fail_before_mmio:
	e008h_rear_release_before_mmio(vfe, pair);
	return ret;
}

static int __used
e008h_rear_bind_pair(struct e008h_rear_prime_pair *pair,
		     u64 owner_epoch, u64 first_request_generation)
{
	struct e007z_rear_binding binding[E008H_REAR_SLOTS][E007Z_REAR_WMS];
	struct e007z_rear_frame tmp[E008H_REAR_SLOTS] = {};
	unsigned int s;
	int ret;

	if (!pair || !pair->allocated || !pair->slot0_preloaded_disabled ||
	    pair->ledgers_bound || pair->faulted || !owner_epoch ||
	    !first_request_generation || first_request_generation == U64_MAX)
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

static int
e008h_rear_check_slot_addresses(struct vfe_device *vfe,
				const struct e008h_rear_prime_pair *pair,
				unsigned int slot, bool must_be_enabled)
{
	unsigned int i;

	if (!vfe || !pair || slot >= E008H_REAR_SLOTS)
		return -EINVAL;

	for (i = 0; i < E007Z_REAR_WMS; i++) {
		const struct vfe680_e004nu_rear_wm_static *c;
		void __iomem *cfg;
		u32 cfg_now;
		int ai;

		c = e008d_rear_contract_for_wm(e008h_rear_program_wms[i]);
		if (!c)
			return -EINVAL;
		ai = e008h_rear_addr_index(&pair->addr[slot], c->wm);
		if (ai < 0)
			return ai;
		cfg = vfe680_x1e_bus_reg(vfe, c->wm, 0);
		cfg_now = readl_relaxed(cfg + VFE680_X1E_BUS_CFG);
		if (!!(cfg_now & VFE_BUS_WRITE_CLIENT_CFG_EN) != must_be_enabled)
			return -EIO;
		if ((cfg_now & ~VFE_BUS_WRITE_CLIENT_CFG_EN) !=
		    (c->cfg & ~VFE_BUS_WRITE_CLIENT_CFG_EN))
			return -EIO;
		if (readl_relaxed(cfg + VFE680_X1E_BUS_IMAGE_ADDR) !=
		    pair->addr[slot].image[ai])
			return -EIO;
		if (c->wm == 0 &&
		    readl_relaxed(cfg + VFE680_X1E_BUS_META_ADDR) !=
		    pair->addr[slot].full_meta[0])
			return -EIO;
		if (c->wm == 1 &&
		    readl_relaxed(cfg + VFE680_X1E_BUS_META_ADDR) !=
		    pair->addr[slot].full_meta[1])
			return -EIO;
	}
	return 0;
}

static int
e008h_rear_write_slot_addresses(struct vfe_device *vfe,
				struct e008h_rear_prime_pair *pair,
				unsigned int slot)
{
	unsigned int i;

	for (i = 0; i < E007Z_REAR_WMS; i++) {
		const struct vfe680_e004nu_rear_wm_static *c;
		void __iomem *cfg;
		int ai;

		c = e008d_rear_contract_for_wm(e008h_rear_program_wms[i]);
		if (!c)
			return -EINVAL;
		ai = e008h_rear_addr_index(&pair->addr[slot], c->wm);
		if (ai < 0)
			return ai;
		cfg = vfe680_x1e_bus_reg(vfe, c->wm, 0);
		writel_relaxed(pair->addr[slot].image[ai],
			       cfg + VFE680_X1E_BUS_IMAGE_ADDR);
		if (c->wm == 0)
			writel_relaxed(pair->addr[slot].full_meta[0],
				       cfg + VFE680_X1E_BUS_META_ADDR);
		else if (c->wm == 1)
			writel_relaxed(pair->addr[slot].full_meta[1],
				       cfg + VFE680_X1E_BUS_META_ADDR);
	}
	wmb();
	return 0;
}

/*
 * Build-only activation primitive. No caller exists. It verifies slot0 is
 * already a valid disabled target, enables WMs in the source-locked resource
 * order, then rewrites/readbacks slot0 addresses after enable. Any partial
 * enable/readback failure permanently faults the pair; no rollback/free is
 * attempted here.
 */
static int __used
e008h_rear_enable_slot0(struct vfe_device *vfe,
			struct e008h_rear_prime_pair *pair)
{
	unsigned int i;
	int ret;

	if (!vfe680_e004nt_rear_4k_target(vfe) || !pair || !pair->allocated ||
	    !pair->slot0_preloaded_disabled || !pair->ledgers_bound ||
	    pair->enabled || pair->faulted)
		return -EINVAL;

	ret = e008h_rear_check_slot_addresses(vfe, pair, 0, false);
	if (ret)
		return ret;

	for (i = 0; i < E007Z_REAR_WMS; i++) {
		const struct vfe680_e004nu_rear_wm_static *c;
		void __iomem *cfg;
		u32 cfg_now;

		c = e008d_rear_contract_for_wm(e008h_rear_program_wms[i]);
		if (!c) {
			pair->faulted = true;
			return -EINVAL;
		}
		cfg = vfe680_x1e_bus_reg(vfe, c->wm, 0);
		cfg_now = readl_relaxed(cfg + VFE680_X1E_BUS_CFG);
		if (cfg_now & VFE_BUS_WRITE_CLIENT_CFG_EN) {
			pair->faulted = true;
			return -EBUSY;
		}
		writel_relaxed(cfg_now | VFE_BUS_WRITE_CLIENT_CFG_EN,
			       cfg + VFE680_X1E_BUS_CFG);
	}
	wmb();

	ret = e008h_rear_write_slot_addresses(vfe, pair, 0);
	if (ret) {
		pair->faulted = true;
		return ret;
	}
	ret = e008h_rear_check_slot_addresses(vfe, pair, 0, true);
	if (ret) {
		pair->faulted = true;
		return ret;
	}

	pair->enabled = true;
	pair->programmed[0] = true;
	pair->dma[0].full.in_flight = true;
	return 0;
}

/*
 * First Epoch0 address phase. The future runner must call this before E007y
 * packet2 / E008g BATCH2. It never submits RT-CDM itself.
 */
static int __used
e008h_rear_epoch0_retarget_slot1(struct vfe_device *vfe,
				 struct e008h_rear_prime_pair *pair)
{
	int ret;

	if (!vfe680_e004nt_rear_4k_target(vfe) || !pair || !pair->enabled ||
	    !pair->programmed[0] || pair->programmed[1] ||
	    !pair->ledgers_bound || pair->faulted)
		return -EINVAL;

	ret = e008h_rear_write_slot_addresses(vfe, pair, 1);
	if (ret) {
		pair->faulted = true;
		return ret;
	}
	ret = e008h_rear_check_slot_addresses(vfe, pair, 1, true);
	if (ret) {
		pair->faulted = true;
		return ret;
	}

	pair->programmed[1] = true;
	pair->dma[1].full.in_flight = true;
	return 0;
}

static void
e008h_rear_fault_ledgers(struct e008h_rear_prime_pair *pair, u64 owner_epoch)
{
	unsigned int s;

	if (!pair)
		return;
	pair->faulted = true;
	for (s = 0; s < E008H_REAR_SLOTS; s++)
		if (pair->frame[s].active &&
		    pair->frame[s].owner_epoch == owner_epoch)
			(void)e007z_rear_mark_fault(&pair->frame[s], owner_epoch,
						   pair->frame[s].request_generation);
}

/*
 * Route one already-latched/ACKed WM completion to the unique pending ledger
 * whose exact programmed image IOVA matches last_consumed_iova. A stale
 * duplicate matching an already-cleared slot is ignored as -EALREADY rather
 * than being misattributed to the other frame.
 */
static int __used
e008h_rear_observe_consumed(struct e008h_rear_prime_pair *pair,
			    u64 owner_epoch, u32 csid_buf_done_status,
			    u8 wm, u32 last_consumed_iova)
{
	int idx;
	int pending_match = -1;
	bool stale_match = false;
	unsigned int s;

	if (!pair || !pair->ledgers_bound || pair->faulted || !owner_epoch ||
	    !last_consumed_iova)
		return -EINVAL;
	idx = e007z_rear_index(wm);
	if (idx < 0)
		return idx;

	for (s = 0; s < E008H_REAR_SLOTS; s++) {
		struct e007z_rear_frame *f = &pair->frame[s];

		if (!f->active || f->faulted || f->owner_epoch != owner_epoch)
			continue;
		if (f->slot[idx].programmed_image_iova != last_consumed_iova)
			continue;
		if (!pair->programmed[s]) {
			e008h_rear_fault_ledgers(pair, owner_epoch);
			return -EPROTO;
		}
		if (f->pending & BIT(idx)) {
			if (pending_match >= 0) {
				e008h_rear_fault_ledgers(pair, owner_epoch);
				return -EADDRINUSE;
			}
			pending_match = s;
		} else {
			stale_match = true;
		}
	}

	if (pending_match < 0) {
		if (stale_match)
			return -EALREADY;
		e008h_rear_fault_ledgers(pair, owner_epoch);
		return -EIO;
	}

	if (e007z_rear_observe(&pair->frame[pending_match], owner_epoch,
			       pair->frame[pending_match].request_generation,
			       csid_buf_done_status, wm,
			       last_consumed_iova)) {
		e008h_rear_fault_ledgers(pair, owner_epoch);
		return -EIO;
	}
	return 0;
}

static bool __used
e008h_rear_both_complete(const struct e008h_rear_prime_pair *pair,
			 u64 owner_epoch)
{
	unsigned int s;

	if (!pair || !pair->ledgers_bound || pair->faulted || !owner_epoch ||
	    !pair->programmed[0] || !pair->programmed[1])
		return false;
	for (s = 0; s < E008H_REAR_SLOTS; s++) {
		const struct e007z_rear_frame *f = &pair->frame[s];

		if (!f->active || f->faulted || f->owner_epoch != owner_epoch ||
		    f->pending)
			return false;
	}
	return true;
}

static int __used e008h_rear_runtime_authorization(void)
{
	return -EOPNOTSUPP;
}

struct e008h_rear_prime_ops {
	int (*alloc_pair)(struct vfe_device *, struct e008h_rear_prime_pair *);
	int (*bind_pair)(struct e008h_rear_prime_pair *, u64, u64);
	int (*enable_slot0)(struct vfe_device *, struct e008h_rear_prime_pair *);
	int (*retarget_slot1)(struct vfe_device *, struct e008h_rear_prime_pair *);
	int (*observe_consumed)(struct e008h_rear_prime_pair *, u64, u32, u8, u32);
	bool (*both_complete)(const struct e008h_rear_prime_pair *, u64);
};

static const struct e008h_rear_prime_ops e008h_rear_prime_recipe __used = {
	.alloc_pair = e008h_rear_alloc_prime_pair,
	.bind_pair = e008h_rear_bind_pair,
	.enable_slot0 = e008h_rear_enable_slot0,
	.retarget_slot1 = e008h_rear_epoch0_retarget_slot1,
	.observe_consumed = e008h_rear_observe_consumed,
	.both_complete = e008h_rear_both_complete,
};

#endif /* VFE680_E008H_REAR_TWO_SLOT_PRIME_INC */
