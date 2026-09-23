/* SPDX-License-Identifier: GPL-2.0-only
 *
 * E004nt: rear 4K FULL Y/C candidate physical buffer layout and strictly
 * bounded Linux DMA address computation. NOT a userspace NV12 image format.
 *
 * Two separate live rear Windows E004nq SP7 KD snapshots proved ONLY these
 * relative Y/C metadata/image register offsets and WM frame increments.
 * This source is included into a fresh isolated CAMSS build; no call sites,
 * no module param, no probe/VB2/sysfs/video-stream path. Runtime denied.
 */
#ifndef VFE680_E004NT_REAR_4K_BUFFER_INC
#define VFE680_E004NT_REAR_4K_BUFFER_INC

#define VFE680_E004NT_REAR_Y_META_OFFSET	0x00000000U
#define VFE680_E004NT_REAR_Y_DATA_OFFSET	0x00011000U
#define VFE680_E004NT_REAR_C_META_OFFSET	0x00a9d000U
#define VFE680_E004NT_REAR_C_DATA_OFFSET	0x00aa6000U
#define VFE680_E004NT_REAR_Y_FRAME_INCR		0x00a9d000U
#define VFE680_E004NT_REAR_C_FRAME_INCR		0x00559000U
#define VFE680_E004NT_REAR_TOTAL_BYTES		0x00ff6000U
#define VFE680_E004NT_REAR_Y_WIDTH		3840U
#define VFE680_E004NT_REAR_Y_ROWS		2160U
#define VFE680_E004NT_REAR_C_WIDTH		3840U
#define VFE680_E004NT_REAR_C_ROWS		1080U
#define VFE680_E004NT_REAR_WM_STRIDE		5120U
#define VFE680_E004NT_REAR_FULL_PACKER_CFG	0x0000000bU
#define VFE680_E004NT_REAR_FULL_META_CFG	0x00000800U

/* Compile-time fit of conservatively bounded physical output image
 * row coverage, INCLUDING the source-derived metadata offsets. This
 * proves only arithmetic and an address span, not actual UBWC quality.
 */
static_assert(VFE680_E004NT_REAR_Y_DATA_OFFSET +
	      VFE680_E004NT_REAR_WM_STRIDE *
	      VFE680_E004NT_REAR_Y_ROWS <=
	      VFE680_E004NT_REAR_C_META_OFFSET);
static_assert(VFE680_E004NT_REAR_C_DATA_OFFSET +
	      VFE680_E004NT_REAR_WM_STRIDE *
	      VFE680_E004NT_REAR_C_ROWS <=
	      VFE680_E004NT_REAR_TOTAL_BYTES);
static_assert(VFE680_E004NT_REAR_Y_FRAME_INCR ==
	      VFE680_E004NT_REAR_C_META_OFFSET);
static_assert(VFE680_E004NT_REAR_Y_FRAME_INCR +
	      VFE680_E004NT_REAR_C_FRAME_INCR ==
	      VFE680_E004NT_REAR_TOTAL_BYTES);
static_assert(VFE680_E004NT_REAR_TOTAL_BYTES % 4096U == 0);

/* This surface is a PRIVATE coherent hardware buffer candidate. Do not
 * advertise it as a V4L2/NV12 userspace output until separate conversion/
 * correct UBWC metadata and ownership are proven on Linux.
 *
 * The DMA IOVA below is allocated on Linux; NO Windows DMA address is
 * copied, stored or inferred. Never free while in-flight.
 */
struct vfe680_e004nt_rear_surface {
	void *cpu;
	dma_addr_t dma;
	size_t size;
	bool in_flight;
};

struct vfe680_e004nt_rear_wm_addrs {
	u32 y_meta;
	u32 y_image;
	u32 c_meta;
	u32 c_image;
};

static bool __used
vfe680_e004nt_rear_4k_target(struct vfe_device *vfe)
{
	return vfe && vfe->camss && vfe->camss->dev &&
	       vfe->camss->res &&
	       vfe->camss->res->version == CAMSS_X1E80100 &&
	       vfe->id == 1 && !vfe_is_lite(vfe);
}

/* A single coherent DMA allocation yields one IOMMU-contiguous device
 * aperture rather than incorrectly treating first vb2-dma-sg entry as
 * a complete ~16MB physically contiguous video surface. The memory is
 * allocated with the same real CAMSS device/IOMMU as the existing front
 * auxiliary allocator, and the ENTIRE returned Linux DMA span is checked
 * against the 32-bit VFE register aperture before any address is exposed.
 */
static int __used
vfe680_e004nt_rear_surface_alloc(struct vfe_device *vfe,
				 struct vfe680_e004nt_rear_surface *surface)
{
	struct device *dev;

	if (!vfe680_e004nt_rear_4k_target(vfe) || !surface)
		return -EINVAL;
	if (surface->cpu || surface->in_flight)
		return -EBUSY;

	dev = vfe->camss->dev;
	surface->cpu = dma_alloc_coherent(dev, VFE680_E004NT_REAR_TOTAL_BYTES,
					  &surface->dma, GFP_KERNEL);
	if (!surface->cpu)
		return -ENOMEM;

	if (!IS_ALIGNED(surface->dma, 4096U) ||
	    !vfe680_x1e_dma_span_32bit(surface->dma,
				       VFE680_E004NT_REAR_TOTAL_BYTES)) {
		dma_free_coherent(dev, VFE680_E004NT_REAR_TOTAL_BYTES,
				  surface->cpu, surface->dma);
		memset(surface, 0, sizeof(*surface));
		return -ERANGE;
	}

	surface->size = VFE680_E004NT_REAR_TOTAL_BYTES;
	memset(surface->cpu, 0, surface->size);
	return 0;
}

/* Physical VFE1 WM address words are 32-bit. Verify WHOLE output-buffer
 * aperture before computing individual Linux addresses. No image bytes
 * accessed and NO MMIO written by this function. The result is only an
 * address-formation candidate, not an authorization to start the ISP.
 */
static int __used
vfe680_e004nt_rear_surface_addrs(struct vfe_device *vfe,
				 const struct vfe680_e004nt_rear_surface *surface,
				 struct vfe680_e004nt_rear_wm_addrs *out)
{
	u32 base;

	if (!vfe680_e004nt_rear_4k_target(vfe) || !surface || !out ||
	    !surface->cpu || surface->in_flight ||
	    surface->size != VFE680_E004NT_REAR_TOTAL_BYTES)
		return -EINVAL;
	if (!IS_ALIGNED(surface->dma, 4096U) ||
	    !vfe680_x1e_dma_span_32bit(surface->dma, surface->size))
		return -ERANGE;

	base = (u32)surface->dma;
	out->y_meta = base + VFE680_E004NT_REAR_Y_META_OFFSET;
	out->y_image = base + VFE680_E004NT_REAR_Y_DATA_OFFSET;
	out->c_meta = base + VFE680_E004NT_REAR_C_META_OFFSET;
	out->c_image = base + VFE680_E004NT_REAR_C_DATA_OFFSET;
	return 0;
}

/* Caller must first guarantee bus stop, IRQ retirement and all HW DONE
 * events. This check explicitly rejects free before retirement; no caller
 * or future activation is introduced by the isolated source.
 */
static int __used
vfe680_e004nt_rear_surface_free(struct vfe_device *vfe,
				struct vfe680_e004nt_rear_surface *surface)
{
	if (!vfe680_e004nt_rear_4k_target(vfe) || !surface || !surface->cpu ||
	    surface->size != VFE680_E004NT_REAR_TOTAL_BYTES)
		return -EINVAL;
	if (surface->in_flight)
		return -EBUSY;

	memset(surface->cpu, 0, surface->size);
	dma_free_coherent(vfe->camss->dev, surface->size,
			  surface->cpu, surface->dma);
	memset(surface, 0, sizeof(*surface));
	return 0;
}

/* NO runtime link until rear IQ, metadata format, RT-CDM, 4K output
 * completion, front/rear exclusion and V4L2 client layout are validated.
 */
static int __used
vfe680_e004nt_rear_4k_runtime_authorization(struct vfe_device *vfe)
{
	if (!vfe680_e004nt_rear_4k_target(vfe))
		return -EINVAL;
	return -EOPNOTSUPP;
}
#endif /* VFE680_E004NT_REAR_4K_BUFFER_INC */
