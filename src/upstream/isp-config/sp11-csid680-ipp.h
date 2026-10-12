/* SPDX-License-Identifier: GPL-2.0-only */
/* Independent single-VC RAW10 IPP input setup from public Qualcomm GPL
 * definitions. This is a CSID register plan, never a VFE CDM command stream.
 * No firmware, MMIO, path-enable, CTRL, reset, IRQ mask or register-update.
 * See CSID680-IPP-PROVENANCE.md for exact reference and integration limits.
 */
#ifndef SP11_OPEN_CSID680_IPP_H
#define SP11_OPEN_CSID680_IPP_H
#include "sp11-cdm.h"

#define SP11_CSID680_IPP_WRITES 7U
#define SP11_CSID680_IPP_TARGET 1U

struct sp11_csid680_ipp_input {
	u32 virtual_channel, dt_id, input_bits;
};

struct sp11_csid680_ipp_write {
	u32 offset, value;
};

/* Internal host-endian plan. The target tag identifies CSID680, not VFE.
 * No public ABI or serialized size is assigned to this structure.
 */
struct sp11_csid680_ipp_plan {
	u32 target, count;
	struct sp11_csid680_ipp_write writes[SP11_CSID680_IPP_WRITES];
};

/* Full-frame pass-through: no crop, binning, HDR, multiple VC/DT, frame-ID
 * packet decoding or VFR. CFA order and processing precision belong to VFE.
 * Caller must own an already stopped CSID/IPP and its reserved CID routing.
 */
static inline int sp11_csid680_ipp_prepare(struct sp11_csid680_ipp_plan *out,
					 const struct sp11_csid680_ipp_input *s)
{
	struct sp11_csid680_ipp_plan tmp = {
		.target = SP11_CSID680_IPP_TARGET,
		.count = SP11_CSID680_IPP_WRITES,
		.writes = {
			{0x300, 0},
			{0x30c, 0},
			{0x310, 0},
			{0x374, 1},
			{0x378, 0},
			{0x37c, 1},
			{0x380, 0},
		},
	};

	if (!out || !s || sp11_cdm_overlap(out, sizeof(*out), s, sizeof(*s)))
		return -EINVAL;
	if (s->input_bits != 10)
		return -EOPNOTSUPP;
	if (s->virtual_channel > 31 || s->dt_id > 3)
		return -ERANGE;
	/* RAW10 CSI-2 type 0x2b; public IPP decoder 2. Bit31 stays clear. */
	tmp.writes[0].value = s->virtual_channel << 22 | s->dt_id << 27 |
			      0x2bU << 16 | 2U << 12;
	/* Pixel store and timestamps, using the exact IPP strobe selection.
	 * RDI plain-format bits must not be transplanted into this register.
	 */
	tmp.writes[2].value = 1U << 14 | 1U << 9 | 2U;
	memcpy(out, &tmp, sizeof(tmp));
	return 0;
}
#endif
