/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Compile-only protected-camera pipeline contract.
 *
 * No allocator, heap, ownership API, secure transport, service identity,
 * runtime selector or callback invocation exists here.
 */
#ifndef QC_MSM_CAMSS_PROTECTED_PIPELINE_H
#define QC_MSM_CAMSS_PROTECTED_PIPELINE_H

#include <linux/build_bug.h>
#include <linux/types.h>

struct device;
struct vb2_buffer;

#define CAMSS_PROTECTED_ID_BYTES 16
#define CAMSS_PROTECTED_MAX_PLANES 3

struct camss_protected_queue_contract {
	bool cpu_mappable;
	bool ordinary_sg_fallback;
	bool read_io_allowed;
	bool mmap_io_allowed;
	bool dmabuf_import_requires_protected_proof;
};

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

/*
 * Provider readiness is a conjunction, not a name or a single primitive.
 * Every bit below must be proven by authority before runtime binding exists.
 */
enum camss_protected_provider_capability {
	CAMSS_PROTECTED_CAP_HLOS_ACCESS_REVOKED       = 1U << 0,
	CAMSS_PROTECTED_CAP_TRUSTED_OWNER_RESOLVED    = 1U << 1,
	CAMSS_PROTECTED_CAP_TRUSTED_WORKER_VISIBLE    = 1U << 2,
	CAMSS_PROTECTED_CAP_RELEASE_PATH_RESOLVED     = 1U << 3,
	CAMSS_PROTECTED_CAP_NO_HLOS_TRANSFER_FALLBACK = 1U << 4,
	CAMSS_PROTECTED_CAP_EXTERNAL_TARGET_DISTINCT  = 1U << 5,
	CAMSS_PROTECTED_CAP_HW_WORKER_OVERLAP_PROVEN   = 1U << 6,
};

#define CAMSS_PROTECTED_PROVIDER_REQUIRED_CAPS \
	(CAMSS_PROTECTED_CAP_HLOS_ACCESS_REVOKED | \
	 CAMSS_PROTECTED_CAP_TRUSTED_OWNER_RESOLVED | \
	 CAMSS_PROTECTED_CAP_TRUSTED_WORKER_VISIBLE | \
	 CAMSS_PROTECTED_CAP_RELEASE_PATH_RESOLVED | \
	 CAMSS_PROTECTED_CAP_NO_HLOS_TRANSFER_FALLBACK | \
	 CAMSS_PROTECTED_CAP_EXTERNAL_TARGET_DISTINCT | \
	 CAMSS_PROTECTED_CAP_HW_WORKER_OVERLAP_PROVEN)

enum camss_protected_provider_phase {
	CAMSS_PROTECTED_PROVIDER_UNBOUND = 0,
	CAMSS_PROTECTED_PROVIDER_AUTHORITY_INCOMPLETE,
	CAMSS_PROTECTED_PROVIDER_PARITY_READY,
};

struct camss_protected_provider_capability_contract {
	u32 proven_caps;
	enum camss_protected_provider_phase phase;
	bool runtime_binding_authorized;
	bool concrete_trusted_owner_resolved;
	bool concrete_release_authority_resolved;
	bool external_reuses_internal_target;
	bool hlos_transfer_fallback_allowed;
	bool hardware_worker_overlap_proven;
	bool time_multiplex_visibility_allowed;
};

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

struct camss_protected_transfer_ops {
	int (*transfer)(struct device *dev,
			struct camss_secure_capture_target *source,
			struct camss_external_protected_sample *destination);
};

struct camss_secure_lane_ops {
	int (*acquire)(struct device *dev);
	void (*release)(struct device *dev);
};

struct camss_protected_pipeline_contract {
	struct camss_protected_queue_contract queue;
	struct camss_protected_provider_capability_contract provider;
	const struct camss_secure_capture_target_ops *capture_target_ops;
	const struct camss_external_protected_sample_ops *external_sample_ops;
	const struct camss_protected_transfer_ops *transfer_ops;
	const struct camss_secure_lane_ops *lane_ops;
};

static inline void camss_protected_pipeline_compile_contract(void)
{
	BUILD_BUG_ON(CAMSS_PROTECTED_ID_BYTES != 16);
	BUILD_BUG_ON(CAMSS_PROTECTED_MAX_PLANES != 3);
	BUILD_BUG_ON(CAMSS_SECURE_TARGET_UNPREPARED != 0);
	BUILD_BUG_ON(CAMSS_EXTERNAL_SAMPLE_DETACHED != 0);
	BUILD_BUG_ON(CAMSS_PROTECTED_PROVIDER_UNBOUND != 0);
	BUILD_BUG_ON(CAMSS_PROTECTED_PROVIDER_REQUIRED_CAPS != 0x7f);
}

#endif /* QC_MSM_CAMSS_PROTECTED_PIPELINE_H */
