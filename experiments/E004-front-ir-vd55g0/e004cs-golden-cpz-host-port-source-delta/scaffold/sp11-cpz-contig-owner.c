// SPDX-License-Identifier: GPL-2.0
/* Compile-only concrete ownership primitive proof. Never loaded in E004cs. */
#include <linux/module.h>
#include <linux/bitops.h>
#include <linux/firmware/qcom/qcom_scm.h>
#include <dt-bindings/firmware/qcom,scm.h>

struct sp11_cpz_owner_range {
	phys_addr_t phys;
	size_t size;
	u64 owners;
};

static int sp11_cpz_assign(struct sp11_cpz_owner_range *r,
			   const struct qcom_scm_vmperm *dst,
			   unsigned int nr_dst)
{
	u64 src;
	int ret;

	if (!r || !r->phys || !r->size || !r->owners || !dst || !nr_dst)
		return -EINVAL;

	src = r->owners;
	ret = qcom_scm_assign_mem(r->phys, r->size, &src, dst, nr_dst);
	if (!ret)
		r->owners = src;

	return ret;
}

int
sp11_cpz_lend_external(struct sp11_cpz_owner_range *r)
{
	const struct qcom_scm_vmperm dst[] = {
		{ .vmid = QCOM_SCM_VMID_CP_CDSP, .perm = QCOM_SCM_PERM_RW },
	};

	return sp11_cpz_assign(r, dst, ARRAY_SIZE(dst));
}

int
sp11_cpz_lend_internal(struct sp11_cpz_owner_range *r)
{
	const struct qcom_scm_vmperm dst[] = {
		{ .vmid = QCOM_SCM_VMID_CP_CAMERA, .perm = QCOM_SCM_PERM_RW },
		{ .vmid = QCOM_SCM_VMID_CP_CDSP, .perm = QCOM_SCM_PERM_RW },
	};

	return sp11_cpz_assign(r, dst, ARRAY_SIZE(dst));
}

int
sp11_cpz_reclaim_hlos(struct sp11_cpz_owner_range *r)
{
	const struct qcom_scm_vmperm dst[] = {
		{ .vmid = QCOM_SCM_VMID_HLOS, .perm = QCOM_SCM_PERM_RWX },
	};

	return sp11_cpz_assign(r, dst, ARRAY_SIZE(dst));
}

EXPORT_SYMBOL_GPL(sp11_cpz_lend_external);
EXPORT_SYMBOL_GPL(sp11_cpz_lend_internal);
EXPORT_SYMBOL_GPL(sp11_cpz_reclaim_hlos);

static int __init sp11_cpz_owner_compile_init(void)
{
	/* Deliberately no allocation, ownership or secure operation. */
	return 0;
}
module_init(sp11_cpz_owner_compile_init);
MODULE_DESCRIPTION("SP11 CPZ contiguous ownership compile proof only");
MODULE_LICENSE("GPL");
