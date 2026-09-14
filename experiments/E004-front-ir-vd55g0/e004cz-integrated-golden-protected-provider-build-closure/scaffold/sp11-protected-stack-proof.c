// SPDX-License-Identifier: GPL-2.0
/* E004cz compile/link closure only. No initcall, no runtime registration. */
#include <linux/compiler_attributes.h>
#include <linux/dma-buf.h>
#include <linux/types.h>
#include "sp11-cpz-system-heap.h"
#include "sp11-cpz-dmabuf-query.h"
#include "camss-protected-cpz-external-sample.h"

static __used void sp11_e004cz_camss_contract_compile_proof(void)
{
	camss_cpz_external_sample_compile_contract();
}

struct sp11_e004cz_provider_link_contract {
	int (*lend)(struct dma_buf *dmabuf, bool camera_target);
	int (*mark_active)(struct dma_buf *dmabuf);
	int (*mark_detached)(struct dma_buf *dmabuf);
	int (*reclaim)(struct dma_buf *dmabuf);
	bool (*is_protected)(struct dma_buf *dmabuf);
};

static const struct sp11_e004cz_provider_link_contract __used sp11_e004cz_provider_links = {
	.lend = sp11_cpz_system_heap_lend,
	.mark_active = sp11_cpz_system_heap_mark_active,
	.mark_detached = sp11_cpz_system_heap_mark_detached,
	.reclaim = sp11_cpz_system_heap_reclaim,
	.is_protected = sp11_cpz_dma_buf_is_protected,
};
