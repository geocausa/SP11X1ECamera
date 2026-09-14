/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Compile-only external CPZ protected-sample provider contract.
 *
 * E004cq resolves the required ownership/lifetime shape, but this file binds
 * no allocator, ownership service, DSP process, context bank, VMID or runtime
 * transport.  It is deliberately declarations + compile-time assertions only.
 */
#ifndef QC_MSM_CAMSS_PROTECTED_CPZ_EXTERNAL_SAMPLE_H
#define QC_MSM_CAMSS_PROTECTED_CPZ_EXTERNAL_SAMPLE_H

#include "camss-protected-cpz-provider.h"

enum camss_cpz_external_capability {
	CAMSS_CPZ_EXT_CAP_OPAQUE_IDENTITY        = 1U << 0,
	CAMSS_CPZ_EXT_CAP_GENERIC_BACKING        = 1U << 1,
	CAMSS_CPZ_EXT_CAP_WORKER_ONLY_OWNERSHIP  = 1U << 2,
	CAMSS_CPZ_EXT_CAP_HLOS_CPU_EXCLUDED      = 1U << 3,
	CAMSS_CPZ_EXT_CAP_TRUSTED_IMPORT         = 1U << 4,
	CAMSS_CPZ_EXT_CAP_WORKER_REF_HELD        = 1U << 5,
	CAMSS_CPZ_EXT_CAP_DETACH_BEFORE_RECLAIM = 1U << 6,
	CAMSS_CPZ_EXT_CAP_RECLAIM_BEFORE_FREE    = 1U << 7,
	CAMSS_CPZ_EXT_CAP_NO_CAMERA_HW_OWNER     = 1U << 8,
	CAMSS_CPZ_EXT_CAP_NO_HLOS_FALLBACK       = 1U << 9,
};

#define CAMSS_CPZ_EXTERNAL_REQUIRED_CAPS \
	(CAMSS_CPZ_EXT_CAP_OPAQUE_IDENTITY | \
	 CAMSS_CPZ_EXT_CAP_GENERIC_BACKING | \
	 CAMSS_CPZ_EXT_CAP_WORKER_ONLY_OWNERSHIP | \
	 CAMSS_CPZ_EXT_CAP_HLOS_CPU_EXCLUDED | \
	 CAMSS_CPZ_EXT_CAP_TRUSTED_IMPORT | \
	 CAMSS_CPZ_EXT_CAP_WORKER_REF_HELD | \
	 CAMSS_CPZ_EXT_CAP_DETACH_BEFORE_RECLAIM | \
	 CAMSS_CPZ_EXT_CAP_RECLAIM_BEFORE_FREE | \
	 CAMSS_CPZ_EXT_CAP_NO_CAMERA_HW_OWNER | \
	 CAMSS_CPZ_EXT_CAP_NO_HLOS_FALLBACK)

enum camss_cpz_external_phase {
	CAMSS_CPZ_EXTERNAL_DETACHED = 0,
	CAMSS_CPZ_EXTERNAL_IDENTITY_BOUND,
	CAMSS_CPZ_EXTERNAL_BACKING_READY,
	CAMSS_CPZ_EXTERNAL_WORKER_OWNED,
	CAMSS_CPZ_EXTERNAL_WORKER_IMPORTED,
	CAMSS_CPZ_EXTERNAL_PAYLOAD_READY,
	CAMSS_CPZ_EXTERNAL_WORKER_DETACHING,
	CAMSS_CPZ_EXTERNAL_RECLAIMING,
	CAMSS_CPZ_EXTERNAL_RECLAIMED,
	CAMSS_CPZ_EXTERNAL_RELEASING,
};

/*
 * Provider-specific state around the generic external sample representation.
 * No field is a real runtime handle in this compile-only checkpoint.
 */
struct camss_cpz_external_sample_contract {
	struct camss_external_protected_sample sample;
	enum camss_cpz_external_phase phase;
	u32 proven_caps;
	bool logical_identity_bound;
	bool backing_reference_held;
	bool worker_owner_active;
	bool worker_mapping_active;
	bool normal_hlos_cpu_visible;
	bool camera_hw_owner_required;
	bool worker_detached_before_reclaim;
	bool ownership_reclaimed_before_free;
	bool hlos_transfer_fallback_allowed;
};

/*
 * Lifecycle operations are declarations only.  The ordering is explicit:
 * identity -> backing -> protected ownership -> trusted import -> payload ->
 * trusted detach -> ownership reclaim -> backing release.
 */
struct camss_cpz_external_sample_ops {
	int (*bind_identity)(struct device *dev, u64 request_id,
			     struct camss_cpz_external_sample_contract *external);
	int (*prepare_backing)(struct device *dev,
			       struct camss_cpz_external_sample_contract *external);
	int (*activate_worker_ownership)(struct device *dev,
					struct camss_cpz_external_sample_contract *external);
	int (*import_worker_mapping)(struct device *dev,
				     struct camss_cpz_external_sample_contract *external);
	void (*mark_payload_ready)(struct camss_cpz_external_sample_contract *external,
				   size_t captured_extent,
				   size_t serialized_extent,
				   size_t payload_offset);
	void (*detach_worker_mapping)(struct device *dev,
				      struct camss_cpz_external_sample_contract *external);
	int (*reclaim_ownership)(struct device *dev,
				 struct camss_cpz_external_sample_contract *external);
	void (*release_backing)(struct device *dev,
				struct camss_cpz_external_sample_contract *external);
};

static inline void camss_cpz_external_sample_compile_contract(void)
{
	camss_cpz_provider_compile_contract();
	BUILD_BUG_ON(CAMSS_CPZ_EXTERNAL_DETACHED != 0);
	BUILD_BUG_ON(CAMSS_CPZ_EXTERNAL_REQUIRED_CAPS != 0x3ff);
}

#endif /* QC_MSM_CAMSS_PROTECTED_CPZ_EXTERNAL_SAMPLE_H */
