// SPDX-License-Identifier: GPL-2.0
/* Compile-only SG ownership batching proof for E004ct. No runtime caller. */
#include <linux/errno.h>
#include <linux/kernel.h>
#include <linux/scatterlist.h>
#include <linux/slab.h>
#include <linux/firmware/qcom/qcom_scm.h>
#include "sp11-cpz-sg-owner.h"

#define SP11_CPZ_BATCH_SECTIONS 32
#define SP11_CPZ_BATCH_BYTES SZ_2M

int sp11_cpz_assign_sg(struct sg_table *sgt,
		       const u32 *src_vmids, unsigned int nr_src,
		       const struct qcom_scm_vmperm *dst, unsigned int nr_dst)
{
	struct qcom_scm_mem_map_info *regions;
	struct qcom_scm_current_perm_info *newvms;
	struct scatterlist *sg;
	u32 *src;
	size_t src_sz, dst_sz, regions_sz;
	unsigned int i, idx = 0, n;
	int ret = 0;

	if (!sgt || !sgt->sgl || !sgt->nents || !src_vmids || !nr_src ||
	    !dst || !nr_dst)
		return -EINVAL;

	/* Validate the complete SG shape before the first ownership transition. */
	for_each_sg(sgt->sgl, sg, sgt->nents, i) {
		if (!sg->length || sg->length >= SP11_CPZ_BATCH_BYTES)
			return -E2BIG;
	}

	src_sz = nr_src * sizeof(*src);
	dst_sz = nr_dst * sizeof(*newvms);
	src = kmemdup(src_vmids, src_sz, GFP_KERNEL);
	newvms = kcalloc(nr_dst, sizeof(*newvms), GFP_KERNEL);
	regions = kcalloc(SP11_CPZ_BATCH_SECTIONS, sizeof(*regions), GFP_KERNEL);
	if (!src || !newvms || !regions) {
		ret = -ENOMEM;
		goto out_free;
	}

	for (i = 0; i < nr_dst; i++)
		qcom_scm_populate_vmperm_info(&newvms[i], dst[i].vmid, dst[i].perm);

	sg = sgt->sgl;
	while (idx < sgt->nents) {
		size_t batch_bytes = 0;

		for (n = 0; idx < sgt->nents && n < SP11_CPZ_BATCH_SECTIONS; n++, idx++) {
			if (n && batch_bytes + sg->length >= SP11_CPZ_BATCH_BYTES)
				break;
			qcom_scm_populate_mem_map_info(&regions[n], sg_phys(sg), sg->length);
			batch_bytes += sg->length;
			sg = sg_next(sg);
		}

		regions_sz = n * sizeof(*regions);
		ret = qcom_scm_assign_mem_regions(regions, regions_sz,
						 src, src_sz, newvms, dst_sz);
		if (ret) {
			/* Earlier batches may already have changed owner: poison/retain. */
			ret = -EADDRNOTAVAIL;
			break;
		}
	}

out_free:
	kfree(regions);
	kfree(newvms);
	kfree(src);
	return ret;
}
