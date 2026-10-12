/* SPDX-License-Identifier: GPL-2.0-only */
/* Independent FULL two-plane NV12 bus setup, with both clients disabled.
 * Public Qualcomm GPL layout/format definitions; see NV12-BUS-PROVENANCE.md.
 * No firmware, MMIO, allocation, submission or enable command. Declared DMA
 * extents are arithmetic inputs, not proof of kernel ownership or retirement.
 */
#ifndef SP11_OPEN_VFE680_NV12_H
#define SP11_OPEN_VFE680_NV12_H
#include "sp11-cdm.h"

#define SP11_VFE680_NV12_SETUP_BYTES 232U

struct sp11_vfe680_nv12_plane {
	u64 dma_base, allocation_bytes, offset;
	u32 stride;
};

/* Single stripe, origin zero, uncompressed FULL Y/C clients 0/1 only.
 * The provider must already own a stopped full VFE and both live mappings.
 */
struct sp11_vfe680_nv12 {
	u32 width, height;
	struct sp11_vfe680_nv12_plane plane[2];
};

static inline int sp11_vfe680_nv12_validate(const struct sp11_vfe680_nv12 *s)
{
	u64 begin[2], bytes[2];
	unsigned int i;

	if (!s || !s->width || !s->height || ((s->width | s->height) & 1U))
		return -EINVAL;
	if (s->width > 16384 || s->height > 16384)
		return -ERANGE;
	for (i = 0; i < 2; i++) {
		const struct sp11_vfe680_nv12_plane *p = &s->plane[i];

		if (p->stride < s->width || (p->stride & 15U) ||
		    !p->allocation_bytes || (p->dma_base & 15U) ||
		    (p->offset & 15U) || p->dma_base > 0xffffffffULL ||
		    p->allocation_bytes > 0x100000000ULL - p->dma_base ||
		    p->offset > p->allocation_bytes)
			return -ERANGE;
		bytes[i] = (u64)p->stride * (s->height >> i);
		if (bytes[i] > 0xffffffffULL ||
		    bytes[i] > p->allocation_bytes - p->offset)
			return -ERANGE;
		begin[i] = p->dma_base + p->offset;
	}
	if (begin[0] < begin[1] + bytes[1] && begin[1] < begin[0] + bytes[0])
		return -EINVAL;
	return 0;
}

/* Produces no WM enable. First disable both clients, then configure them.
 * Disable writes do not prove physical halt, IRQ synchronization or retirement.
 * Numeric non-overlap cannot detect aliases in different IOMMU mappings.
 */
static inline int sp11_vfe680_nv12_setup_disabled(u8 *out, size_t capacity,
					       const struct sp11_vfe680_nv12 *s)
{
	u8 tmp[SP11_VFE680_NV12_SETUP_BYTES];
	const u32 zero = 0;
	const u32 header[3] = {0, 0, 0};
	const u32 every_frame[4] = {0, 1, 0, 1};
	const u32 prefetch_off[2] = {0, 0};
	u32 image[6];
	unsigned int i;
	size_t pos = 0;
	int ret;

	if (!out || !s)
		return -EINVAL;
	if (capacity < sizeof(tmp))
		return -ENOSPC;
	if (sp11_cdm_overlap(out, sizeof(tmp), s, sizeof(*s)))
		return -EINVAL;
	ret = sp11_vfe680_nv12_validate(s);
	if (ret)
		return ret;
	for (i = 0; i < 2; i++) {
		ret = sp11_cdm_reg_cont(tmp + pos, sizeof(tmp) - pos,
				       0xe00U + i * 0x100U, &zero, 1);
		if (ret)
			return ret;
		pos += 12;
	}
	for (i = 0; i < 2; i++) {
		const struct sp11_vfe680_nv12_plane *p = &s->plane[i];
		u32 base = 0xe00U + i * 0x100U;
		u32 height = s->height >> i;

		image[0] = (u32)(p->dma_base + p->offset);
		image[1] = p->stride * height;
		/* FULL uses sample width; the RDI stride/16 rule does not apply. */
		image[2] = height << 16 | s->width;
		image[3] = 0; /* origin-zero horizontal initialization */
		image[4] = p->stride;
		/* Public PACKER_FMT_VER3_PLAIN_8_LSB_MSB_10 for two-plane NV12. */
		image[5] = 3;
		ret = sp11_cdm_reg_cont(tmp + pos, sizeof(tmp) - pos,
				       base + 4, image, 6);
		if (ret)
			return ret;
		pos += 32;
		ret = sp11_cdm_reg_cont(tmp + pos, sizeof(tmp) - pos,
				       base + 0x20, header, 3);
		if (ret)
			return ret;
		pos += 20;
		ret = sp11_cdm_reg_cont(tmp + pos, sizeof(tmp) - pos,
				       base + 0x30, every_frame, 4);
		if (ret)
			return ret;
		pos += 24;
		ret = sp11_cdm_reg_cont(tmp + pos, sizeof(tmp) - pos,
				       base + 0x48, &zero, 1); /* UBWC off */
		if (ret)
			return ret;
		pos += 12;
		ret = sp11_cdm_reg_cont(tmp + pos, sizeof(tmp) - pos,
				       base + 0x60, prefetch_off, 2);
		if (ret)
			return ret;
		pos += 16;
	}
	if (pos != sizeof(tmp))
		return -EINVAL;
	memcpy(out, tmp, sizeof(tmp));
	return 0;
}
#endif
