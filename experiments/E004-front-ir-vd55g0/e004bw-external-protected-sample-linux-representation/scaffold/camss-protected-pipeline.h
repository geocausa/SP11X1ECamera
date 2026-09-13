/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Compile-only protected-camera pipeline contract.
 *
 * No allocator, heap, backend, runtime selector, ioctl, SCM call, VMID,
 * QTEE/QSEE service, HLOS mapping or transfer implementation exists here.
 *
 * E004bt/E004bu model the internal CP_CAMERA target as a separate backing
 * with simultaneous camera-hardware + trusted-worker visibility.
 * E004bv proves the external Windows sample separately carries opaque identity,
 * allocation/captured extents, request association and trusted payload layout.
 */
#ifndef QC_MSM_CAMSS_PROTECTED_PIPELINE_H
#define QC_MSM_CAMSS_PROTECTED_PIPELINE_H

#include <linux/build_bug.h>
#include <linux/types.h>

struct device;
struct vb2_buffer;

#define CAMSS_PROTECTED_ID_BYTES 16
#define CAMSS_PROTECTED_MAX_PLANES 3

/* Queue exposure/fallback policy is separate from secure ownership/lifetime. */
struct camss_protected_queue_contract {
	bool cpu_mappable;
	bool ordinary_sg_fallback;
	bool read_io_allowed;
	bool mmap_io_allowed;
	bool dmabuf_import_requires_protected_proof;
};

/* Internal target owner/visibility state.  Concrete owner IDs stay unresolved. */
struct camss_protected_owner_set_contract {
	unsigned int owner_count;
	bool camera_hw_visible;
	bool trusted_worker_visible;
	bool normal_hlos_cpu_visible;
	bool concrete_owner_ids_resolved;
	bool concrete_permissions_resolved;
};

enum camss_secure_target_phase {
	CAMSS_SECURE_TARGET_UNPREPARED = 0,
	CAMSS_SECURE_TARGET_BACKING_READY,
	CAMSS_SECURE_TARGET_ACTIVE_VISIBILITY,
	CAMSS_SECURE_TARGET_REVOKING_VISIBILITY,
};

struct camss_secure_capture_target {
	u8 id[CAMSS_PROTECTED_ID_BYTES];
	phys_addr_t ownership_phys;
	size_t ownership_size;
	dma_addr_t camss_iova[CAMSS_PROTECTED_MAX_PLANES];
	size_t plane_size[CAMSS_PROTECTED_MAX_PLANES];
	unsigned int num_planes;
	struct camss_protected_owner_set_contract owners;
	enum camss_secure_target_phase phase;
	void *backend_handle;
};

/*
 * External protected consumer sample.
 *
 * This deliberately has no CAMSS IOVA or physical-ownership range: Windows
 * programs the distinct internal CP_CAMERA target into IFE, then transfers
 * into the external sample from a trusted worker.
 *
 * E004bv proves that identity, allocation extent, captured extent, serialized
 * extent and pixel payload offset are independent concepts.  A Linux provider
 * must preserve that distinction rather than flattening them to vb2 length.
 */
enum camss_external_sample_phase {
	CAMSS_EXTERNAL_SAMPLE_DETACHED = 0,
	CAMSS_EXTERNAL_SAMPLE_IDENTITY_BOUND,
	CAMSS_EXTERNAL_SAMPLE_TRUSTED_VISIBLE,
	CAMSS_EXTERNAL_SAMPLE_PAYLOAD_READY,
	CAMSS_EXTERNAL_SAMPLE_RELEASING,
};

struct camss_external_protected_sample {
	u8 id[CAMSS_PROTECTED_ID_BYTES];
	u64 request_id;
	size_t allocation_extent;
	size_t captured_extent;
	size_t serialized_extent;
	size_t payload_offset;
	size_t plane_size[CAMSS_PROTECTED_MAX_PLANES];
	unsigned int num_planes;
	enum camss_external_sample_phase phase;
	void *backend_handle;
	bool identity_proven;
	bool trusted_worker_visible;
	bool normal_hlos_cpu_visible;
};

/* Internal target lifecycle: backing lifetime and active visibility are split. */
struct camss_secure_capture_target_ops {
	int (*prepare_backing)(struct device *dev, struct vb2_buffer *vb,
			       struct camss_secure_capture_target *target);
	int (*activate_visibility)(struct device *dev,
				   struct camss_secure_capture_target *target);
	void (*deactivate_visibility)(struct device *dev,
				      struct camss_secure_capture_target *target);
	void (*release_backing)(struct device *dev,
				struct camss_secure_capture_target *target);
};

/*
 * External lifetime is separately bracketed.  These callbacks are declarations
 * only; E004bw defines no provider and invokes none of them.
 */
struct camss_external_protected_sample_ops {
	int (*bind_identity)(struct device *dev, struct vb2_buffer *vb, u64 request_id,
			     struct camss_external_protected_sample *sample);
	int (*activate_trusted_visibility)(struct device *dev,
					 struct camss_external_protected_sample *sample);
	void (*deactivate_trusted_visibility)(struct device *dev,
					     struct camss_external_protected_sample *sample);
	void (*release_identity)(struct device *dev,
				 struct camss_external_protected_sample *sample);
};

/* Trusted internal -> external processing/transfer remains an independent role. */
struct camss_protected_transfer_ops {
	int (*transfer)(struct device *dev,
			struct camss_secure_capture_target *source,
			struct camss_external_protected_sample *destination);
};

/* Secure CSI/lane ownership remains independent from both sample lifetimes. */
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

/* Compile-time only: no contract instance and no callback invocation. */
static inline void camss_protected_pipeline_compile_contract(void)
{
	BUILD_BUG_ON(CAMSS_PROTECTED_ID_BYTES != 16);
	BUILD_BUG_ON(CAMSS_PROTECTED_MAX_PLANES != 3);
	BUILD_BUG_ON(CAMSS_SECURE_TARGET_UNPREPARED != 0);
	BUILD_BUG_ON(CAMSS_EXTERNAL_SAMPLE_DETACHED != 0);
}

#endif /* QC_MSM_CAMSS_PROTECTED_PIPELINE_H */
