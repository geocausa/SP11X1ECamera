/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Compile-only two-buffer protected-camera contract.
 *
 * No backend, runtime selector, control, ioctl, SCM call, VMID choice,
 * protected-memory operation or transfer implementation exists here.
 *
 * E004bp proved that Windows uses:
 *   camera HW -> internal CP_CAMERA target -> protected worker
 *             -> external protected sample
 * with secure-lane ownership as another independent lifetime.
 */
#ifndef QC_MSM_CAMSS_PROTECTED_PIPELINE_H
#define QC_MSM_CAMSS_PROTECTED_PIPELINE_H

#include <linux/build_bug.h>
#include <linux/types.h>

struct device;
struct vb2_buffer;

#define CAMSS_PROTECTED_ID_BYTES 16
#define CAMSS_PROTECTED_MAX_PLANES 3

/* Queue exposure/fallback policy is separate from memory ownership. */
struct camss_protected_queue_contract {
	bool cpu_mappable;
	bool ordinary_sg_fallback;
	bool read_io_allowed;
	bool mmap_io_allowed;
	bool dmabuf_import_requires_protected_proof;
};

/*
 * Internal camera HW target.
 *
 * The physical ownership range and camera-visible DMA/IOVA are deliberately
 * separate fields: E004bo proved that CAMSS is SMMU-attached and that the
 * ordinary sg_dma_address() result is not proof of physical identity.
 *
 * No VMID or permission value is encoded here.
 */
struct camss_secure_capture_target {
	u8 id[CAMSS_PROTECTED_ID_BYTES];
	phys_addr_t ownership_phys;
	size_t ownership_size;
	dma_addr_t camss_iova[CAMSS_PROTECTED_MAX_PLANES];
	size_t plane_size[CAMSS_PROTECTED_MAX_PLANES];
	unsigned int num_planes;
	void *backend_handle;
	bool prepared;
};

/*
 * External consumer-facing protected sample.
 *
 * It intentionally has no CAMSS IOVA field: E004bp proved the external
 * VTL1 sample is not the direct IFE HW target on Windows.
 */
struct camss_external_protected_sample {
	u8 id[CAMSS_PROTECTED_ID_BYTES];
	size_t plane_size[CAMSS_PROTECTED_MAX_PLANES];
	unsigned int num_planes;
	void *backend_handle;
	bool prepared;
};

/* Lifetime of the internal camera HW target. */
struct camss_secure_capture_target_ops {
	int (*prepare)(struct device *dev, struct vb2_buffer *vb,
		       struct camss_secure_capture_target *target);
	void (*release)(struct device *dev,
			struct camss_secure_capture_target *target);
};

/* Lifetime of the separate external protected sample. */
struct camss_external_protected_sample_ops {
	int (*attach)(struct device *dev, struct vb2_buffer *vb,
		      struct camss_external_protected_sample *sample);
	void (*release)(struct device *dev,
			struct camss_external_protected_sample *sample);
};

/*
 * Protected execution/transfer boundary.
 * This is separate from both buffer lifetimes and from secure-lane ownership.
 */
struct camss_protected_transfer_ops {
	int (*transfer)(struct device *dev,
			struct camss_secure_capture_target *source,
			struct camss_external_protected_sample *destination);
};

/* Secure CSI/worker lane ownership brackets streaming, not buffer lifetime. */
struct camss_secure_lane_ops {
	int (*acquire)(struct device *dev);
	void (*release)(struct device *dev);
};

struct camss_protected_pipeline_contract {
	struct camss_protected_queue_contract queue;
	const struct camss_secure_capture_target_ops *capture_target_ops;
	const struct camss_external_protected_sample_ops *external_sample_ops;
	const struct camss_protected_transfer_ops *transfer_ops;
	const struct camss_secure_lane_ops *lane_ops;
};

/*
 * Compile-time only.  E004bq defines no contract instance and invokes none
 * of the operation callbacks above.
 */
static inline void camss_protected_pipeline_compile_contract(void)
{
	BUILD_BUG_ON(CAMSS_PROTECTED_ID_BYTES != 16);
	BUILD_BUG_ON(CAMSS_PROTECTED_MAX_PLANES != 3);
}

#endif /* QC_MSM_CAMSS_PROTECTED_PIPELINE_H */
