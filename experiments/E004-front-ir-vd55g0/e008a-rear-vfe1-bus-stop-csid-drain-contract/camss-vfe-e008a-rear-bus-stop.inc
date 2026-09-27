/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008a build-only rear VFE1 ten-WM BUS stop helper.
 * Unreachable: no call site is installed by this checkpoint.
 */
#ifndef CAMSS_VFE_E008A_REAR_BUS_STOP_INC
#define CAMSS_VFE_E008A_REAR_BUS_STOP_INC

#define E008A_REAR_WM_COUNT 10U

static const u8 e008a_rear_wms[E008A_REAR_WM_COUNT] = {
	0, 1, 2, 3, 11, 12, 13, 14, 16, 18,
};

/*
 * Qualcomm BUS-v3 stop_wm writes zero to each client CFG. Use that stronger
 * postcondition rather than merely clearing the enable bit. VFE680 completion
 * ownership is external-CSID-driven on this SP11 tree, but mask VFE TOP/BUS
 * IRQ banks and synchronize its Linux IRQ as teardown hygiene.
 */
int vfe680_e008a_rear_bus_stop(struct vfe_device *vfe,
				 bool exact_rear_owner);

int __used
vfe680_e008a_rear_bus_stop(struct vfe_device *vfe, bool exact_rear_owner)
{
	unsigned int i;

	if (!vfe || !exact_rear_owner || vfe->id != 1 || vfe_is_lite(vfe) ||
	    !vfe->irq)
		return -EINVAL;

	writel(0, vfe->base + VFE_TOP_IRQn_MASK(vfe, 0));
	writel(0, vfe->base + VFE_TOP_IRQn_MASK(vfe, 1));
	writel(0, vfe->base + VFE_BUS_IRQn_MASK(vfe, 0));
	writel(0, vfe->base + VFE_BUS_IRQn_MASK(vfe, 1));

	for (i = 0; i < E008A_REAR_WM_COUNT; i++)
		writel(0, vfe->base +
		       VFE_BUS_WRITE_CLIENT_CFG(vfe, e008a_rear_wms[i]));

	/* Order posted MMIO writes before the readback/synchronization fence. */
	wmb();
	synchronize_irq(vfe->irq);

	for (i = 0; i < E008A_REAR_WM_COUNT; i++)
		if (readl(vfe->base +
			  VFE_BUS_WRITE_CLIENT_CFG(vfe, e008a_rear_wms[i])) != 0)
			return -EBUSY;

	if (readl(vfe->base + VFE_TOP_IRQn_MASK(vfe, 0)) ||
	    readl(vfe->base + VFE_TOP_IRQn_MASK(vfe, 1)) ||
	    readl(vfe->base + VFE_BUS_IRQn_MASK(vfe, 0)) ||
	    readl(vfe->base + VFE_BUS_IRQn_MASK(vfe, 1)))
		return -EBUSY;

	return 0;
}

#endif /* CAMSS_VFE_E008A_REAR_BUS_STOP_INC */
