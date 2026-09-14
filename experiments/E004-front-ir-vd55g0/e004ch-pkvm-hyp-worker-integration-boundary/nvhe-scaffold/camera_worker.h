/* SPDX-License-Identifier: GPL-2.0-only */
#ifndef __KVM_NVHE_CAMERA_WORKER__
#define __KVM_NVHE_CAMERA_WORKER__

#include <linux/types.h>

/*
 * Compile-only E004ch substrate proof.
 * Both pages must already be HYP-owned/mapped. This function establishes no
 * ownership, Qualcomm VMID, DMA, camera, or secure-world policy.
 */
int __pkvm_camera_worker_copy_mapped(u64 src_pfn, u64 dst_pfn, size_t len);

#endif /* __KVM_NVHE_CAMERA_WORKER__ */
