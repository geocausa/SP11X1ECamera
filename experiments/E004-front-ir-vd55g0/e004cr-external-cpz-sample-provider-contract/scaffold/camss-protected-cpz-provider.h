/* SPDX-License-Identifier: GPL-2.0 */
/*
 * Compile-only CPZ protected-camera provider port contract.
 *
 * This file selects no runtime backend and performs no ownership, FastRPC,
 * DSP, SMMU, DT, allocator or secure-world operation.  It only records the
 * authority that a future provider must prove before binding is allowed.
 */
#ifndef QC_MSM_CAMSS_PROTECTED_CPZ_PROVIDER_H
#define QC_MSM_CAMSS_PROTECTED_CPZ_PROVIDER_H

#include "camss-protected-pipeline.h"

/*
 * E004co proved the vendor architecture can compose these properties, but
 * Golden does not implement the host binding yet.  Runtime readiness requires
 * every capability, including the still-unresolved external-sample import.
 */
enum camss_cpz_provider_capability {
	CAMSS_CPZ_CAP_CAMERA_CDSP_COOWNED_TARGET = 1U << 0,
	CAMSS_CPZ_CAP_HLOS_EXCLUDED_TARGET       = 1U << 1,
	CAMSS_CPZ_CAP_PRIVILEGED_PROCESS_TYPE    = 1U << 2,
	CAMSS_CPZ_CAP_SECURE_CONTEXT_IMPORT      = 1U << 3,
	CAMSS_CPZ_CAP_EXTERNAL_SAMPLE_IMPORT     = 1U << 4,
	CAMSS_CPZ_CAP_RECLAIM_ORDER_RESOLVED     = 1U << 5,
	CAMSS_CPZ_CAP_NO_HLOS_FALLBACK           = 1U << 6,
};

#define CAMSS_CPZ_PROVIDER_REQUIRED_CAPS \
	(CAMSS_CPZ_CAP_CAMERA_CDSP_COOWNED_TARGET | \
	 CAMSS_CPZ_CAP_HLOS_EXCLUDED_TARGET | \
	 CAMSS_CPZ_CAP_PRIVILEGED_PROCESS_TYPE | \
	 CAMSS_CPZ_CAP_SECURE_CONTEXT_IMPORT | \
	 CAMSS_CPZ_CAP_EXTERNAL_SAMPLE_IMPORT | \
	 CAMSS_CPZ_CAP_RECLAIM_ORDER_RESOLVED | \
	 CAMSS_CPZ_CAP_NO_HLOS_FALLBACK)

enum camss_cpz_provider_phase {
	CAMSS_CPZ_PROVIDER_UNAVAILABLE = 0,
	CAMSS_CPZ_PROVIDER_HOST_BINDING_MISSING,
	CAMSS_CPZ_PROVIDER_EXTERNAL_SAMPLE_MISSING,
	CAMSS_CPZ_PROVIDER_PARITY_READY,
};

struct camss_cpz_provider_port_contract {
	u32 proven_caps;
	enum camss_cpz_provider_phase phase;

	/* Authority gates.  No field below is itself an implementation. */
	bool runtime_binding_authorized;
	bool host_process_type_binding_present;
	bool secure_context_bank_policy_present;
	bool internal_target_hlos_excluded;
	bool internal_target_camera_and_worker_visible;
	bool external_sample_provider_resolved;
	bool external_sample_hlos_excluded;
	bool ownership_reclaim_before_backing_release;
	bool hlos_transfer_fallback_allowed;
};

static inline void camss_cpz_provider_compile_contract(void)
{
	camss_protected_pipeline_compile_contract();
	BUILD_BUG_ON(CAMSS_CPZ_PROVIDER_UNAVAILABLE != 0);
	BUILD_BUG_ON(CAMSS_CPZ_PROVIDER_REQUIRED_CAPS != 0x7f);
}

#endif /* QC_MSM_CAMSS_PROTECTED_CPZ_PROVIDER_H */
