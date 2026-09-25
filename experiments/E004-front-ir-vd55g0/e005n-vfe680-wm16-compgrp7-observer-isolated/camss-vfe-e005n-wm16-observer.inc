/* SPDX-License-Identifier: GPL-2.0-only */
/*
 * E005n: isolated VFE680 WM16/STATS_BAF comp-group-7 observer.
 *
 * Hardware contract is pinned by E005m:
 *   VFE BUS status0 BIT(7) == composite group 7 done
 *   WM16 == STATS_BAF
 *   WM16 ADDR_STATUS0 == VFE base + 0x1e70
 *
 * This code may acknowledge the dedicated VFE interrupt, but it MUST NOT
 * retire/reuse a software camera buffer, call vfe_buf_done(), touch VB2,
 * unmap DMA, or infer FIFO8 ownership.  Exact consumed addresses are private
 * runtime evidence and must not be exported from SP11.
 */
#define VFE680_E005N_WM16              16
#define VFE680_E005N_COMP_GRP7_DONE    BIT(7)
#define VFE680_E005N_LOG_LIMIT         8

static __maybe_unused void
vfe680_e005n_arm_wm16_compgrp7(struct vfe_device *vfe)
{
	u32 mask;

	if (!vfe680_x1e_bus_target(vfe))
		return;

	mask = readl_relaxed(vfe->base + VFE_BUS_IRQn_MASK(vfe, 0));
	writel_relaxed(mask | VFE680_E005N_COMP_GRP7_DONE,
		       vfe->base + VFE_BUS_IRQn_MASK(vfe, 0));
}

static void vfe680_e005n_observe_wm16(struct vfe_device *vfe, u32 bus0)
{
	u64 count;
	u32 consumed;

	if (!vfe680_x1e_bus_target(vfe) ||
	    !(bus0 & VFE680_E005N_COMP_GRP7_DONE))
		return;

	/* Read the hardware-consumed address before acknowledging BUS status. */
	consumed = readl_relaxed(vfe->base +
				VFE_BUS_ADDR_STATUS0(vfe, VFE680_E005N_WM16));
	WRITE_ONCE(vfe->x1e_e005n_wm16_last_bus0, bus0);
	WRITE_ONCE(vfe->x1e_e005n_wm16_last_consumed, consumed);
	count = atomic64_inc_return(&vfe->x1e_e005n_wm16_comp7_count);

	if (count <= VFE680_E005N_LOG_LIMIT)
		dev_info(vfe->camss->dev,
			 "E005n VFE1 WM16 comp7 hw-done count=%llu bus0=%08x consumed=%08x\n",
			 count, bus0, consumed);
}

static void vfe680_e005n_ack_snapshot(struct vfe_device *vfe,
				      u32 top0, u32 top1,
				      u32 bus0, u32 bus1)
{
	/*
	 * The VFE IRQ is dedicated to this vfe_device.  Clear the exact status
	 * words latched by this handler, then issue each hardware global clear.
	 * IRQ acknowledgement is not software-buffer retirement.
	 */
	writel_relaxed(top0, vfe->base + VFE_TOP_IRQn_CLEAR(vfe, 0));
	writel_relaxed(top1, vfe->base + VFE_TOP_IRQn_CLEAR(vfe, 1));
	writel_relaxed(VFE_TOP_IRQ_CMD_GLOBAL_CLEAR,
		       vfe->base + VFE_TOP_IRQ_CMD(vfe));
	writel_relaxed(bus0, vfe->base + VFE_BUS_IRQn_CLEAR(vfe, 0));
	writel_relaxed(bus1, vfe->base + VFE_BUS_IRQn_CLEAR(vfe, 1));
	writel_relaxed(1, vfe->base + VFE_BUS_IRQ_GLOBAL_CLEAR(vfe));
}
