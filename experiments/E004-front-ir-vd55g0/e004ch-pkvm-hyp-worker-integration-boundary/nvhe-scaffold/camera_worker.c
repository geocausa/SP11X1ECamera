// SPDX-License-Identifier: GPL-2.0-only
/* E004ch compile-only nVHE worker substrate proof. */

#include <linux/errno.h>
#include <linux/string.h>

#include <nvhe/camera_worker.h>
#include <nvhe/memory.h>

int __pkvm_camera_worker_copy_mapped(u64 src_pfn, u64 dst_pfn, size_t len)
{
	phys_addr_t src_phys = hyp_pfn_to_phys(src_pfn);
	phys_addr_t dst_phys = hyp_pfn_to_phys(dst_pfn);
	struct hyp_page *src_page;
	struct hyp_page *dst_page;
	void *src;
	void *dst;

	if (!len || len > PAGE_SIZE)
		return -EINVAL;

	src_page = hyp_phys_to_page(src_phys);
	dst_page = hyp_phys_to_page(dst_phys);
	if (get_hyp_state(src_page) != PKVM_PAGE_OWNED ||
	    get_hyp_state(dst_page) != PKVM_PAGE_OWNED)
		return -EPERM;

	src = hyp_phys_to_virt(src_phys);
	dst = hyp_phys_to_virt(dst_phys);
	memcpy(dst, src, len);

	return 0;
}
