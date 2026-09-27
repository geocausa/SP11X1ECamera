/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E008i VFE1 read-only ADDR_STATUS0 sampler for the ten rear write masters.
 * This helper performs no write and has no caller in the repository baseline.
 */
#ifndef CAMSS_VFE_E008I_REAR_STATUS_INC
#define CAMSS_VFE_E008I_REAR_STATUS_INC

static const u8 e008i_rear_wm[E008I_REAR_WMS] = {
	0, 1, 2, 3, 11, 12, 13, 14, 16, 18,
};

static const u8 e008i_rear_group[E008I_REAR_WMS] = {
	0, 0, 0, 0, 4, 4, 5, 6, 7, 9,
};

static_assert(ARRAY_SIZE(e008i_rear_wm) == E008I_REAR_WMS);
static_assert(ARRAY_SIZE(e008i_rear_group) == E008I_REAR_WMS);

int vfe680_e008i_rear_snapshot_addr_status0(struct vfe_device *vfe,
					    u32 buf_done_status,
					    u16 *wm_mask,
					    u32 addr_status0[E008I_REAR_WMS])
{
	unsigned int i;

	if (!vfe || !vfe->camss || !vfe->camss->res || !wm_mask ||
	    !addr_status0 || vfe->camss->res->version != CAMSS_X1E80100 ||
	    vfe->id != 1 || vfe_is_lite(vfe))
		return -EINVAL;

	*wm_mask = 0;
	for (i = 0; i < E008I_REAR_WMS; i++)
		addr_status0[i] = 0;

	for (i = 0; i < E008I_REAR_WMS; i++) {
		u8 wm = e008i_rear_wm[i];

		if (!(buf_done_status & BIT(e008i_rear_group[i])))
			continue;

		addr_status0[i] = readl_relaxed(vfe->base +
			VFE680_X1E_BUS_CLIENT_BASE +
			wm * VFE680_X1E_BUS_CLIENT_STRIDE +
			VFE680_X1E_BUS_ADDR_STATUS0);
		*wm_mask |= BIT(i);
	}

	return *wm_mask ? 0 : -ENODATA;
}

#endif /* CAMSS_VFE_E008I_REAR_STATUS_INC */
