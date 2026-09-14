/* SPDX-License-Identifier: GPL-2.0 */
#ifndef SP11_CPZ_SG_OWNER_H
#define SP11_CPZ_SG_OWNER_H
#include <linux/scatterlist.h>
#include <linux/firmware/qcom/qcom_scm.h>
int sp11_cpz_assign_sg(struct sg_table *sgt,
		       const u32 *src_vmids, unsigned int nr_src,
		       const struct qcom_scm_vmperm *dst, unsigned int nr_dst);
#endif
