// SPDX-License-Identifier: GPL-2.0
/*
 * DMABUF System heap exporter
 *
 * Copyright (C) 2011 Google, Inc.
 * Copyright (C) 2019, 2020 Linaro Ltd.
 *
 * Portions based off of Andrew Davis' SRAM heap:
 * Copyright (C) 2019 Texas Instruments Incorporated - http://www.ti.com/
 *	Andrew F. Davis <afd@ti.com>
 */

#include <linux/cc_platform.h>
#include <linux/dma-buf.h>
#include <linux/dma-mapping.h>
#include <linux/dma-heap.h>
#include <linux/err.h>
#include <linux/highmem.h>
#include <linux/mem_encrypt.h>
#include <linux/mm.h>
#include <linux/set_memory.h>
#include <linux/module.h>
#include <linux/pgtable.h>
#include <linux/scatterlist.h>
#include <linux/slab.h>
#include <linux/vmalloc.h>
#include <linux/firmware/qcom/qcom_scm.h>
#include "sp11-cpz-system-heap.h"
#include "sp11-cpz-dmabuf-query.h"
#include "sp11-cpz-sg-owner.h"

struct system_heap_priv {
	bool cc_shared;
};

enum sp11_cpz_heap_state {
	SP11_CPZ_HEAP_HLOS = 0,
	SP11_CPZ_HEAP_TRANSITION,
	SP11_CPZ_HEAP_LENT,
	SP11_CPZ_HEAP_ACTIVE,
	SP11_CPZ_HEAP_DETACHED,
	SP11_CPZ_HEAP_RECLAIMED,
	SP11_CPZ_HEAP_POISONED,
};

enum sp11_cpz_heap_owner_kind {
	SP11_CPZ_OWNER_NONE = 0,
	SP11_CPZ_OWNER_EXTERNAL,
	SP11_CPZ_OWNER_INTERNAL,
};

struct system_heap_buffer {
	struct dma_heap *heap;
	struct list_head attachments;
	struct mutex lock;
	unsigned long len;
	struct sg_table sg_table;
	int vmap_cnt;
	unsigned int mmap_cnt;
	unsigned int cpu_access_cnt;
	void *vaddr;
	bool cc_shared;
	bool cpz_hold;
	enum sp11_cpz_heap_state cpz_state;
	enum sp11_cpz_heap_owner_kind cpz_owner_kind;
};

struct dma_heap_attachment {
	struct device *dev;
	struct sg_table table;
	struct list_head list;
	bool mapped;
	bool cc_shared;
};

static bool sp11_cpz_hlos_cpu_allowed(const struct system_heap_buffer *buffer)
{
	return buffer->cpz_state == SP11_CPZ_HEAP_HLOS ||
	       buffer->cpz_state == SP11_CPZ_HEAP_RECLAIMED;
}

static bool sp11_cpz_any_mapped_attachment(struct system_heap_buffer *buffer)
{
	struct dma_heap_attachment *a;

	list_for_each_entry(a, &buffer->attachments, list)
		if (a->mapped)
			return true;
	return false;
}

#define LOW_ORDER_GFP (GFP_HIGHUSER | __GFP_ZERO)
#define HIGH_ORDER_GFP  (((GFP_HIGHUSER | __GFP_ZERO | __GFP_NOWARN \
				| __GFP_NORETRY) & ~__GFP_RECLAIM) \
				| __GFP_COMP)
static gfp_t order_flags[] = {HIGH_ORDER_GFP, HIGH_ORDER_GFP, LOW_ORDER_GFP};
/*
 * The selection of the orders used for allocation (1MB, 64K, 4K) is designed
 * to match with the sizes often found in IOMMUs. Using order 4 pages instead
 * of order 0 pages can significantly improve the performance of many IOMMUs
 * by reducing TLB pressure and time spent updating page tables.
 */
static const unsigned int orders[] = {8, 4, 0};
#define NUM_ORDERS ARRAY_SIZE(orders)

static int system_heap_set_page_decrypted(struct page *page)
{
	unsigned long addr = (unsigned long)page_address(page);
	unsigned int nr_pages = 1 << compound_order(page);
	int ret;

	ret = set_memory_decrypted(addr, nr_pages);
	if (ret)
		pr_warn_ratelimited("dma-buf system heap: failed to decrypt page at %p\n",
				    page_address(page));

	return ret;
}

static int system_heap_set_page_encrypted(struct page *page)
{
	unsigned long addr = (unsigned long)page_address(page);
	unsigned int nr_pages = 1 << compound_order(page);
	int ret;

	ret = set_memory_encrypted(addr, nr_pages);
	if (ret)
		pr_warn_ratelimited("dma-buf system heap: failed to re-encrypt page at %p, leaking memory\n",
				    page_address(page));

	return ret;
}

static int dup_sg_table(struct sg_table *from, struct sg_table *to)
{
	struct scatterlist *sg, *new_sg;
	int ret, i;

	ret = sg_alloc_table(to, from->orig_nents, GFP_KERNEL);
	if (ret)
		return ret;

	new_sg = to->sgl;
	for_each_sgtable_sg(from, sg, i) {
		sg_set_page(new_sg, sg_page(sg), sg->length, sg->offset);
		new_sg = sg_next(new_sg);
	}

	return 0;
}

static int system_heap_attach(struct dma_buf *dmabuf,
			      struct dma_buf_attachment *attachment)
{
	struct system_heap_buffer *buffer = dmabuf->priv;
	struct dma_heap_attachment *a;
	int ret;

	a = kzalloc_obj(*a);
	if (!a)
		return -ENOMEM;

	ret = dup_sg_table(&buffer->sg_table, &a->table);
	if (ret) {
		kfree(a);
		return ret;
	}

	a->dev = attachment->dev;
	INIT_LIST_HEAD(&a->list);
	a->mapped = false;
	a->cc_shared = buffer->cc_shared;

	attachment->priv = a;

	mutex_lock(&buffer->lock);
	list_add(&a->list, &buffer->attachments);
	mutex_unlock(&buffer->lock);

	return 0;
}

static void system_heap_detach(struct dma_buf *dmabuf,
			       struct dma_buf_attachment *attachment)
{
	struct system_heap_buffer *buffer = dmabuf->priv;
	struct dma_heap_attachment *a = attachment->priv;

	mutex_lock(&buffer->lock);
	list_del(&a->list);
	mutex_unlock(&buffer->lock);

	sg_free_table(&a->table);
	kfree(a);
}

static struct sg_table *system_heap_map_dma_buf(struct dma_buf_attachment *attachment,
						enum dma_data_direction direction)
{
	struct system_heap_buffer *buffer = attachment->dmabuf->priv;
	struct dma_heap_attachment *a = attachment->priv;
	struct sg_table *table = &a->table;
	unsigned long attrs;
	int ret;

	mutex_lock(&buffer->lock);
	attrs = a->cc_shared ? DMA_ATTR_CC_SHARED : 0;
	if (!sp11_cpz_hlos_cpu_allowed(buffer))
		attrs |= DMA_ATTR_SKIP_CPU_SYNC;
	ret = dma_map_sgtable(attachment->dev, table, direction, attrs);
	if (!ret)
		a->mapped = true;
	mutex_unlock(&buffer->lock);
	if (ret)
		return ERR_PTR(ret);
	return table;
}

static void system_heap_unmap_dma_buf(struct dma_buf_attachment *attachment,
				      struct sg_table *table,
				      enum dma_data_direction direction)
{
	struct system_heap_buffer *buffer = attachment->dmabuf->priv;
	struct dma_heap_attachment *a = attachment->priv;
	unsigned long attrs;

	mutex_lock(&buffer->lock);
	attrs = a->cc_shared ? DMA_ATTR_CC_SHARED : 0;
	if (!sp11_cpz_hlos_cpu_allowed(buffer))
		attrs |= DMA_ATTR_SKIP_CPU_SYNC;
	dma_unmap_sgtable(attachment->dev, table, direction, attrs);
	a->mapped = false;
	mutex_unlock(&buffer->lock);
}

static int system_heap_dma_buf_begin_cpu_access(struct dma_buf *dmabuf,
						enum dma_data_direction direction)
{
	struct system_heap_buffer *buffer = dmabuf->priv;
	struct dma_heap_attachment *a;

	mutex_lock(&buffer->lock);

	if (!sp11_cpz_hlos_cpu_allowed(buffer)) {
		mutex_unlock(&buffer->lock);
		return -EPERM;
	}
	buffer->cpu_access_cnt++;

	if (buffer->vmap_cnt)
		invalidate_kernel_vmap_range(buffer->vaddr, buffer->len);

	list_for_each_entry(a, &buffer->attachments, list) {
		if (!a->mapped)
			continue;
		dma_sync_sgtable_for_cpu(a->dev, &a->table, direction);
	}
	mutex_unlock(&buffer->lock);

	return 0;
}

static int system_heap_dma_buf_end_cpu_access(struct dma_buf *dmabuf,
					      enum dma_data_direction direction)
{
	struct system_heap_buffer *buffer = dmabuf->priv;
	struct dma_heap_attachment *a;

	mutex_lock(&buffer->lock);

	if (!sp11_cpz_hlos_cpu_allowed(buffer) || !buffer->cpu_access_cnt) {
		mutex_unlock(&buffer->lock);
		return -EPERM;
	}

	if (buffer->vmap_cnt)
		flush_kernel_vmap_range(buffer->vaddr, buffer->len);

	list_for_each_entry(a, &buffer->attachments, list) {
		if (!a->mapped)
			continue;
		dma_sync_sgtable_for_device(a->dev, &a->table, direction);
	}
	buffer->cpu_access_cnt--;
	mutex_unlock(&buffer->lock);

	return 0;
}

static void sp11_cpz_heap_vma_open(struct vm_area_struct *vma)
{
	struct system_heap_buffer *buffer = vma->vm_private_data;

	mutex_lock(&buffer->lock);
	buffer->mmap_cnt++;
	mutex_unlock(&buffer->lock);
}

static void sp11_cpz_heap_vma_close(struct vm_area_struct *vma)
{
	struct system_heap_buffer *buffer = vma->vm_private_data;

	mutex_lock(&buffer->lock);
	if (buffer->mmap_cnt)
		buffer->mmap_cnt--;
	mutex_unlock(&buffer->lock);
}

static const struct vm_operations_struct sp11_cpz_heap_vm_ops = {
	.open = sp11_cpz_heap_vma_open,
	.close = sp11_cpz_heap_vma_close,
};

static int system_heap_mmap(struct dma_buf *dmabuf, struct vm_area_struct *vma)
{
	struct system_heap_buffer *buffer = dmabuf->priv;
	struct sg_table *table = &buffer->sg_table;
	unsigned long addr = vma->vm_start;
	unsigned long pgoff = vma->vm_pgoff;
	struct scatterlist *sg;
	pgprot_t prot;
	int i, ret;

	/* Reserve the mapping before remap_pfn_range so lend cannot race it. */
	mutex_lock(&buffer->lock);
	if (!sp11_cpz_hlos_cpu_allowed(buffer)) {
		mutex_unlock(&buffer->lock);
		return -EPERM;
	}
	buffer->mmap_cnt++;
	mutex_unlock(&buffer->lock);

	prot = vma->vm_page_prot;
	if (buffer->cc_shared)
		prot = pgprot_decrypted(prot);

	for_each_sgtable_sg(table, sg, i) {
		unsigned long n = sg->length >> PAGE_SHIFT;

		if (pgoff < n)
			break;
		pgoff -= n;
	}

	for (; sg && addr < vma->vm_end; sg = sg_next(sg)) {
		unsigned long n = (sg->length >> PAGE_SHIFT) - pgoff;
		struct page *page = sg_page(sg) + pgoff;
		unsigned long size = n << PAGE_SHIFT;

		if (addr + size > vma->vm_end)
			size = vma->vm_end - addr;

		ret = remap_pfn_range(vma, addr, page_to_pfn(page), size, prot);
		if (ret) {
			mutex_lock(&buffer->lock);
			buffer->mmap_cnt--;
			mutex_unlock(&buffer->lock);
			return ret;
		}

		addr += size;
		pgoff = 0;
	}

	vma->vm_private_data = buffer;
	vma->vm_ops = &sp11_cpz_heap_vm_ops;

	return 0;
}

static void *system_heap_do_vmap(struct system_heap_buffer *buffer)
{
	struct sg_table *table = &buffer->sg_table;
	int npages = PAGE_ALIGN(buffer->len) / PAGE_SIZE;
	struct page **pages = vmalloc(sizeof(struct page *) * npages);
	struct page **tmp = pages;
	struct sg_page_iter piter;
	pgprot_t prot;
	void *vaddr;

	if (!pages)
		return ERR_PTR(-ENOMEM);

	for_each_sgtable_page(table, &piter, 0) {
		WARN_ON(tmp - pages >= npages);
		*tmp++ = sg_page_iter_page(&piter);
	}

	prot = PAGE_KERNEL;
	if (buffer->cc_shared)
		prot = pgprot_decrypted(prot);
	vaddr = vmap(pages, npages, VM_MAP, prot);
	vfree(pages);

	if (!vaddr)
		return ERR_PTR(-ENOMEM);

	return vaddr;
}

static int system_heap_vmap(struct dma_buf *dmabuf, struct iosys_map *map)
{
	struct system_heap_buffer *buffer = dmabuf->priv;
	void *vaddr;
	int ret = 0;

	mutex_lock(&buffer->lock);
	if (!sp11_cpz_hlos_cpu_allowed(buffer)) {
		ret = -EPERM;
		goto out;
	}
	if (buffer->vmap_cnt) {
		buffer->vmap_cnt++;
		iosys_map_set_vaddr(map, buffer->vaddr);
		goto out;
	}

	vaddr = system_heap_do_vmap(buffer);
	if (IS_ERR(vaddr)) {
		ret = PTR_ERR(vaddr);
		goto out;
	}

	buffer->vaddr = vaddr;
	buffer->vmap_cnt++;
	iosys_map_set_vaddr(map, buffer->vaddr);
out:
	mutex_unlock(&buffer->lock);

	return ret;
}

static void system_heap_vunmap(struct dma_buf *dmabuf, struct iosys_map *map)
{
	struct system_heap_buffer *buffer = dmabuf->priv;

	mutex_lock(&buffer->lock);
	if (!--buffer->vmap_cnt) {
		vunmap(buffer->vaddr);
		buffer->vaddr = NULL;
	}
	mutex_unlock(&buffer->lock);
	iosys_map_clear(map);
}

static void system_heap_dma_buf_release(struct dma_buf *dmabuf)
{
	struct system_heap_buffer *buffer = dmabuf->priv;
	struct sg_table *table;
	struct scatterlist *sg;
	int i;

	/* Never recycle backing under remote or ownership-unknown state. */
	if (!sp11_cpz_hlos_cpu_allowed(buffer) || buffer->cpz_hold) {
		pr_err_ratelimited("sp11-cpz: refusing to free remotely-owned/unknown system-heap backing\n");
		return;
	}

	table = &buffer->sg_table;
	for_each_sgtable_sg(table, sg, i) {
		struct page *page = sg_page(sg);

		/*
		 * Intentionally leak pages that cannot be re-encrypted
		 * to prevent shared memory from being reused.
		 */
		if (buffer->cc_shared &&
		    system_heap_set_page_encrypted(page))
			continue;

		__free_pages(page, compound_order(page));
	}
	sg_free_table(table);
	kfree(buffer);
}

static const struct dma_buf_ops system_heap_buf_ops = {
	.attach = system_heap_attach,
	.detach = system_heap_detach,
	.map_dma_buf = system_heap_map_dma_buf,
	.unmap_dma_buf = system_heap_unmap_dma_buf,
	.begin_cpu_access = system_heap_dma_buf_begin_cpu_access,
	.end_cpu_access = system_heap_dma_buf_end_cpu_access,
	.mmap = system_heap_mmap,
	.vmap = system_heap_vmap,
	.vunmap = system_heap_vunmap,
	.release = system_heap_dma_buf_release,
};

bool sp11_cpz_dma_buf_is_protected(struct dma_buf *dmabuf)
{
	struct system_heap_buffer *buffer;
	bool protected;

	if (!dmabuf || dmabuf->ops != &system_heap_buf_ops)
		return false;
	buffer = dmabuf->priv;

	mutex_lock(&buffer->lock);
	protected = buffer->cpz_state == SP11_CPZ_HEAP_TRANSITION ||
		    buffer->cpz_state == SP11_CPZ_HEAP_LENT ||
		    buffer->cpz_state == SP11_CPZ_HEAP_ACTIVE ||
		    buffer->cpz_state == SP11_CPZ_HEAP_DETACHED ||
		    buffer->cpz_state == SP11_CPZ_HEAP_POISONED;
	mutex_unlock(&buffer->lock);

	return protected;
}

static int sp11_cpz_heap_check_quiescent(struct system_heap_buffer *buffer)
{
	if (buffer->mmap_cnt || buffer->vmap_cnt || buffer->cpu_access_cnt ||
	    sp11_cpz_any_mapped_attachment(buffer))
		return -EBUSY;
	return 0;
}

int sp11_cpz_system_heap_lend(struct dma_buf *dmabuf, bool camera_target)
{
	struct system_heap_buffer *buffer;
	const u32 src[] = { QCOM_SCM_VMID_HLOS };
	struct qcom_scm_vmperm dst[2];
	unsigned int nr_dst = 1;
	int ret;

	if (!dmabuf || dmabuf->ops != &system_heap_buf_ops)
		return -EINVAL;
	buffer = dmabuf->priv;

	mutex_lock(&buffer->lock);
	if (!sp11_cpz_hlos_cpu_allowed(buffer) || buffer->cpz_hold) {
		mutex_unlock(&buffer->lock);
		return -EPERM;
	}
	ret = sp11_cpz_heap_check_quiescent(buffer);
	if (ret) {
		mutex_unlock(&buffer->lock);
		return ret;
	}
	get_dma_buf(dmabuf);
	buffer->cpz_hold = true;
	buffer->cpz_state = SP11_CPZ_HEAP_TRANSITION;
	buffer->cpz_owner_kind = camera_target ? SP11_CPZ_OWNER_INTERNAL :
					       SP11_CPZ_OWNER_EXTERNAL;
	mutex_unlock(&buffer->lock);

	dst[0].vmid = QCOM_SCM_VMID_CP_CDSP;
	dst[0].perm = QCOM_SCM_PERM_RW;
	if (camera_target) {
		dst[1].vmid = QCOM_SCM_VMID_CP_CAMERA;
		dst[1].perm = QCOM_SCM_PERM_RW;
		nr_dst = 2;
	}

	ret = sp11_cpz_assign_sg(&buffer->sg_table, src, ARRAY_SIZE(src), dst, nr_dst);
	mutex_lock(&buffer->lock);
	buffer->cpz_state = ret ? SP11_CPZ_HEAP_POISONED : SP11_CPZ_HEAP_LENT;
	mutex_unlock(&buffer->lock);
	/* Failure intentionally keeps cpz_hold: physical ownership is uncertain. */
	return ret;
}

int sp11_cpz_system_heap_mark_active(struct dma_buf *dmabuf)
{
	struct system_heap_buffer *buffer;

	if (!dmabuf || dmabuf->ops != &system_heap_buf_ops)
		return -EINVAL;
	buffer = dmabuf->priv;
	mutex_lock(&buffer->lock);
	if (buffer->cpz_state != SP11_CPZ_HEAP_LENT || !buffer->cpz_hold) {
		mutex_unlock(&buffer->lock);
		return -EPERM;
	}
	buffer->cpz_state = SP11_CPZ_HEAP_ACTIVE;
	mutex_unlock(&buffer->lock);
	return 0;
}

int sp11_cpz_system_heap_mark_detached(struct dma_buf *dmabuf)
{
	struct system_heap_buffer *buffer;

	if (!dmabuf || dmabuf->ops != &system_heap_buf_ops)
		return -EINVAL;
	buffer = dmabuf->priv;
	mutex_lock(&buffer->lock);
	if (buffer->cpz_state != SP11_CPZ_HEAP_ACTIVE || !buffer->cpz_hold) {
		mutex_unlock(&buffer->lock);
		return -EPERM;
	}
	buffer->cpz_state = SP11_CPZ_HEAP_DETACHED;
	mutex_unlock(&buffer->lock);
	return 0;
}

int sp11_cpz_system_heap_reclaim(struct dma_buf *dmabuf)
{
	struct system_heap_buffer *buffer;
	u32 src[2];
	const struct qcom_scm_vmperm dst = {
		.vmid = QCOM_SCM_VMID_HLOS,
		.perm = QCOM_SCM_PERM_RWX,
	};
	unsigned int nr_src;
	int ret;

	if (!dmabuf || dmabuf->ops != &system_heap_buf_ops)
		return -EINVAL;
	buffer = dmabuf->priv;
	mutex_lock(&buffer->lock);
	if (!buffer->cpz_hold ||
	    (buffer->cpz_state != SP11_CPZ_HEAP_DETACHED &&
	     buffer->cpz_state != SP11_CPZ_HEAP_LENT)) {
		mutex_unlock(&buffer->lock);
		return -EPERM;
	}
	if (buffer->cpz_owner_kind == SP11_CPZ_OWNER_INTERNAL) {
		src[0] = QCOM_SCM_VMID_CP_CDSP;
		src[1] = QCOM_SCM_VMID_CP_CAMERA;
		nr_src = 2;
	} else if (buffer->cpz_owner_kind == SP11_CPZ_OWNER_EXTERNAL) {
		src[0] = QCOM_SCM_VMID_CP_CDSP;
		nr_src = 1;
	} else {
		mutex_unlock(&buffer->lock);
		return -EINVAL;
	}
	buffer->cpz_state = SP11_CPZ_HEAP_TRANSITION;
	mutex_unlock(&buffer->lock);

	ret = sp11_cpz_assign_sg(&buffer->sg_table, src, nr_src, &dst, 1);
	mutex_lock(&buffer->lock);
	if (ret) {
		buffer->cpz_state = SP11_CPZ_HEAP_POISONED;
		mutex_unlock(&buffer->lock);
		/* Retain cpz_hold so backing cannot be recycled under uncertainty. */
		return ret;
	}
	buffer->cpz_state = SP11_CPZ_HEAP_RECLAIMED;
	buffer->cpz_owner_kind = SP11_CPZ_OWNER_NONE;
	buffer->cpz_hold = false;
	mutex_unlock(&buffer->lock);
	dma_buf_put(dmabuf);
	return 0;
}

static struct page *alloc_largest_available(unsigned long size,
					    unsigned int max_order)
{
	struct page *page;
	int i;
	gfp_t flags;

	for (i = 0; i < NUM_ORDERS; i++) {
		if (size <  (PAGE_SIZE << orders[i]))
			continue;
		if (max_order < orders[i])
			continue;
		flags = order_flags[i];
		if (mem_accounting)
			flags |= __GFP_ACCOUNT;
		page = alloc_pages(flags, orders[i]);
		if (!page)
			continue;
		return page;
	}
	return NULL;
}

static struct dma_buf *system_heap_allocate(struct dma_heap *heap,
					    unsigned long len,
					    u32 fd_flags,
					    u64 heap_flags)
{
	struct system_heap_buffer *buffer;
	DEFINE_DMA_BUF_EXPORT_INFO(exp_info);
	unsigned long size_remaining = len;
	unsigned int max_order = orders[0];
	struct system_heap_priv *priv = dma_heap_get_drvdata(heap);
	bool cc_shared = priv->cc_shared;
	struct dma_buf *dmabuf;
	struct sg_table *table;
	struct scatterlist *sg;
	struct list_head pages;
	struct page *page, *tmp_page;
	int i, ret = -ENOMEM;

	buffer = kzalloc_obj(*buffer);
	if (!buffer)
		return ERR_PTR(-ENOMEM);

	INIT_LIST_HEAD(&buffer->attachments);
	mutex_init(&buffer->lock);
	buffer->heap = heap;
	buffer->len = len;
	buffer->cc_shared = cc_shared;
	buffer->cpz_hold = false;
	buffer->cpz_state = SP11_CPZ_HEAP_HLOS;
	buffer->cpz_owner_kind = SP11_CPZ_OWNER_NONE;

	INIT_LIST_HEAD(&pages);
	i = 0;
	while (size_remaining > 0) {
		/*
		 * Avoid trying to allocate memory if the process
		 * has been killed by SIGKILL
		 */
		if (fatal_signal_pending(current)) {
			ret = -EINTR;
			goto free_buffer;
		}

		page = alloc_largest_available(size_remaining, max_order);
		if (!page)
			goto free_buffer;

		list_add_tail(&page->lru, &pages);
		size_remaining -= page_size(page);
		max_order = compound_order(page);
		i++;
	}

	table = &buffer->sg_table;
	if (sg_alloc_table(table, i, GFP_KERNEL))
		goto free_buffer;

	sg = table->sgl;
	list_for_each_entry_safe(page, tmp_page, &pages, lru) {
		sg_set_page(sg, page, page_size(page), 0);
		sg = sg_next(sg);
		list_del(&page->lru);
	}

	if (cc_shared) {
		for_each_sgtable_sg(table, sg, i) {
			ret = system_heap_set_page_decrypted(sg_page(sg));
			if (ret)
				goto free_pages;
		}
	}

	/* create the dmabuf */
	exp_info.exp_name = dma_heap_get_name(heap);
	exp_info.ops = &system_heap_buf_ops;
	exp_info.size = buffer->len;
	exp_info.flags = fd_flags;
	exp_info.priv = buffer;
	dmabuf = dma_buf_export(&exp_info);
	if (IS_ERR(dmabuf)) {
		ret = PTR_ERR(dmabuf);
		goto free_pages;
	}
	return dmabuf;

free_pages:
	for_each_sgtable_sg(table, sg, i) {
		struct page *p = sg_page(sg);

		/*
		 * Intentionally leak pages that cannot be re-encrypted
		 * to prevent shared memory from being reused.
		 */
		if (buffer->cc_shared &&
		    system_heap_set_page_encrypted(p))
			continue;
		__free_pages(p, compound_order(p));
	}
	sg_free_table(table);
free_buffer:
	list_for_each_entry_safe(page, tmp_page, &pages, lru)
		__free_pages(page, compound_order(page));
	kfree(buffer);

	return ERR_PTR(ret);
}

static const struct dma_heap_ops system_heap_ops = {
	.allocate = system_heap_allocate,
};

static struct system_heap_priv system_heap_priv = {
	.cc_shared = false,
};

static struct system_heap_priv system_heap_cc_shared_priv = {
	.cc_shared = true,
};

static int __maybe_unused system_heap_create(void)
{
	struct dma_heap_export_info exp_info;
	struct dma_heap *sys_heap;

	exp_info.name = "system";
	exp_info.ops = &system_heap_ops;
	exp_info.priv = &system_heap_priv;

	sys_heap = dma_heap_add(&exp_info);
	if (IS_ERR(sys_heap))
		return PTR_ERR(sys_heap);

	if (IS_ENABLED(CONFIG_HIGHMEM) ||
	    !cc_platform_has(CC_ATTR_MEM_ENCRYPT))
		return 0;

	exp_info.name = "system_cc_shared";
	exp_info.priv = &system_heap_cc_shared_priv;
	sys_heap = dma_heap_add(&exp_info);
	if (IS_ERR(sys_heap))
		return PTR_ERR(sys_heap);

	return 0;
}
/* E004cu compile-only: heap registration deliberately disabled. */
