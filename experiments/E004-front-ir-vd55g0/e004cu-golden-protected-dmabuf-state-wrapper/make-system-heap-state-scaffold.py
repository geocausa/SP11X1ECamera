#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib

SHA = '56b0db19f9e4999ec2144fd3d25bf370e2d15f1602447f8fd5b1c96eb321856d'

def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def one(s, old, new, label):
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: marker count {n}')
    return s.replace(old, new, 1)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('source')
    ap.add_argument('output')
    ns = ap.parse_args()
    src, out = Path(ns.source), Path(ns.output)
    if sha(src) != SHA:
        raise SystemExit('system_heap preimage hash mismatch')
    s = src.read_text()

    inc = '#include <linux/vmalloc.h>\n'
    s = one(s, inc, inc +
            '#include <linux/firmware/qcom/qcom_scm.h>\n'
            '#include "sp11-cpz-system-heap.h"\n'
            '#include "sp11-cpz-sg-owner.h"\n', 'includes')

    old = '''struct system_heap_buffer {
\tstruct dma_heap *heap;
\tstruct list_head attachments;
\tstruct mutex lock;
\tunsigned long len;
\tstruct sg_table sg_table;
\tint vmap_cnt;
\tvoid *vaddr;
\tbool cc_shared;
};
'''
    new = '''enum sp11_cpz_heap_state {
\tSP11_CPZ_HEAP_HLOS = 0,
\tSP11_CPZ_HEAP_TRANSITION,
\tSP11_CPZ_HEAP_LENT,
\tSP11_CPZ_HEAP_ACTIVE,
\tSP11_CPZ_HEAP_DETACHED,
\tSP11_CPZ_HEAP_RECLAIMED,
\tSP11_CPZ_HEAP_POISONED,
};

enum sp11_cpz_heap_owner_kind {
\tSP11_CPZ_OWNER_NONE = 0,
\tSP11_CPZ_OWNER_EXTERNAL,
\tSP11_CPZ_OWNER_INTERNAL,
};

struct system_heap_buffer {
\tstruct dma_heap *heap;
\tstruct list_head attachments;
\tstruct mutex lock;
\tunsigned long len;
\tstruct sg_table sg_table;
\tint vmap_cnt;
\tunsigned int mmap_cnt;
\tunsigned int cpu_access_cnt;
\tvoid *vaddr;
\tbool cc_shared;
\tbool cpz_hold;
\tenum sp11_cpz_heap_state cpz_state;
\tenum sp11_cpz_heap_owner_kind cpz_owner_kind;
};
'''
    s = one(s, old, new, 'buffer state')

    anchor = '''struct dma_heap_attachment {
\tstruct device *dev;
\tstruct sg_table table;
\tstruct list_head list;
\tbool mapped;
\tbool cc_shared;
};
'''
    helper = anchor + '''
static bool sp11_cpz_hlos_cpu_allowed(const struct system_heap_buffer *buffer)
{
\treturn buffer->cpz_state == SP11_CPZ_HEAP_HLOS ||
\t       buffer->cpz_state == SP11_CPZ_HEAP_RECLAIMED;
}

static bool sp11_cpz_any_mapped_attachment(struct system_heap_buffer *buffer)
{
\tstruct dma_heap_attachment *a;

\tlist_for_each_entry(a, &buffer->attachments, list)
\t\tif (a->mapped)
\t\t\treturn true;
\treturn false;
}
'''
    s = one(s, anchor, helper, 'state helpers')

    old = '''static struct sg_table *system_heap_map_dma_buf(struct dma_buf_attachment *attachment,
\t\t\t\t\t\tenum dma_data_direction direction)
{
\tstruct dma_heap_attachment *a = attachment->priv;
\tstruct sg_table *table = &a->table;
\tunsigned long attrs;
\tint ret;

\tattrs = a->cc_shared ? DMA_ATTR_CC_SHARED : 0;
\tret = dma_map_sgtable(attachment->dev, table, direction, attrs);
\tif (ret)
\t\treturn ERR_PTR(ret);

\ta->mapped = true;
\treturn table;
}
'''
    new = '''static struct sg_table *system_heap_map_dma_buf(struct dma_buf_attachment *attachment,
\t\t\t\t\t\tenum dma_data_direction direction)
{
\tstruct system_heap_buffer *buffer = attachment->dmabuf->priv;
\tstruct dma_heap_attachment *a = attachment->priv;
\tstruct sg_table *table = &a->table;
\tunsigned long attrs;
\tint ret;

\tmutex_lock(&buffer->lock);
\tattrs = a->cc_shared ? DMA_ATTR_CC_SHARED : 0;
\tif (!sp11_cpz_hlos_cpu_allowed(buffer))
\t\tattrs |= DMA_ATTR_SKIP_CPU_SYNC;
\tret = dma_map_sgtable(attachment->dev, table, direction, attrs);
\tif (!ret)
\t\ta->mapped = true;
\tmutex_unlock(&buffer->lock);
\tif (ret)
\t\treturn ERR_PTR(ret);
\treturn table;
}
'''
    s = one(s, old, new, 'protected dma map')

    old = '''static void system_heap_unmap_dma_buf(struct dma_buf_attachment *attachment,
\t\t\t\t      struct sg_table *table,
\t\t\t\t      enum dma_data_direction direction)
{
\tstruct dma_heap_attachment *a = attachment->priv;

\ta->mapped = false;
\tdma_unmap_sgtable(attachment->dev, table, direction, 0);
}
'''
    new = '''static void system_heap_unmap_dma_buf(struct dma_buf_attachment *attachment,
\t\t\t\t      struct sg_table *table,
\t\t\t\t      enum dma_data_direction direction)
{
\tstruct system_heap_buffer *buffer = attachment->dmabuf->priv;
\tstruct dma_heap_attachment *a = attachment->priv;
\tunsigned long attrs;

\tmutex_lock(&buffer->lock);
\tattrs = a->cc_shared ? DMA_ATTR_CC_SHARED : 0;
\tif (!sp11_cpz_hlos_cpu_allowed(buffer))
\t\tattrs |= DMA_ATTR_SKIP_CPU_SYNC;
\tdma_unmap_sgtable(attachment->dev, table, direction, attrs);
\ta->mapped = false;
\tmutex_unlock(&buffer->lock);
}
'''
    s = one(s, old, new, 'protected dma unmap')

    old = '''\tmutex_lock(&buffer->lock);

\tif (buffer->vmap_cnt)
\t\tinvalidate_kernel_vmap_range(buffer->vaddr, buffer->len);
'''
    new = '''\tmutex_lock(&buffer->lock);

\tif (!sp11_cpz_hlos_cpu_allowed(buffer)) {
\t\tmutex_unlock(&buffer->lock);
\t\treturn -EPERM;
\t}
\tbuffer->cpu_access_cnt++;

\tif (buffer->vmap_cnt)
\t\tinvalidate_kernel_vmap_range(buffer->vaddr, buffer->len);
'''
    s = one(s, old, new, 'begin cpu access')

    old = '''\tmutex_lock(&buffer->lock);

\tif (buffer->vmap_cnt)
\t\tflush_kernel_vmap_range(buffer->vaddr, buffer->len);
'''
    new = '''\tmutex_lock(&buffer->lock);

\tif (!sp11_cpz_hlos_cpu_allowed(buffer) || !buffer->cpu_access_cnt) {
\t\tmutex_unlock(&buffer->lock);
\t\treturn -EPERM;
\t}

\tif (buffer->vmap_cnt)
\t\tflush_kernel_vmap_range(buffer->vaddr, buffer->len);
'''
    s = one(s, old, new, 'end cpu access guard')

    old = '''\tlist_for_each_entry(a, &buffer->attachments, list) {
\t\tif (!a->mapped)
\t\t\tcontinue;
\t\tdma_sync_sgtable_for_device(a->dev, &a->table, direction);
\t}
\tmutex_unlock(&buffer->lock);

\treturn 0;
}
'''
    new = '''\tlist_for_each_entry(a, &buffer->attachments, list) {
\t\tif (!a->mapped)
\t\t\tcontinue;
\t\tdma_sync_sgtable_for_device(a->dev, &a->table, direction);
\t}
\tbuffer->cpu_access_cnt--;
\tmutex_unlock(&buffer->lock);

\treturn 0;
}
'''
    s = one(s, old, new, 'end cpu access count')

    marker = 'static int system_heap_mmap(struct dma_buf *dmabuf, struct vm_area_struct *vma)\n'
    vmops = '''static void sp11_cpz_heap_vma_open(struct vm_area_struct *vma)
{
\tstruct system_heap_buffer *buffer = vma->vm_private_data;

\tmutex_lock(&buffer->lock);
\tbuffer->mmap_cnt++;
\tmutex_unlock(&buffer->lock);
}

static void sp11_cpz_heap_vma_close(struct vm_area_struct *vma)
{
\tstruct system_heap_buffer *buffer = vma->vm_private_data;

\tmutex_lock(&buffer->lock);
\tif (buffer->mmap_cnt)
\t\tbuffer->mmap_cnt--;
\tmutex_unlock(&buffer->lock);
}

static const struct vm_operations_struct sp11_cpz_heap_vm_ops = {
\t.open = sp11_cpz_heap_vma_open,
\t.close = sp11_cpz_heap_vma_close,
};

''' + marker
    s = one(s, marker, vmops, 'mmap vmops')

    old = '''\tint i, ret;

\tprot = vma->vm_page_prot;
'''
    new = '''\tint i, ret;

\t/* Reserve the mapping before remap_pfn_range so lend cannot race it. */
\tmutex_lock(&buffer->lock);
\tif (!sp11_cpz_hlos_cpu_allowed(buffer)) {
\t\tmutex_unlock(&buffer->lock);
\t\treturn -EPERM;
\t}
\tbuffer->mmap_cnt++;
\tmutex_unlock(&buffer->lock);

\tprot = vma->vm_page_prot;
'''
    s = one(s, old, new, 'mmap reserve')

    old = '''\t\tret = remap_pfn_range(vma, addr, page_to_pfn(page), size, prot);
\t\tif (ret)
\t\t\treturn ret;
'''
    new = '''\t\tret = remap_pfn_range(vma, addr, page_to_pfn(page), size, prot);
\t\tif (ret) {
\t\t\tmutex_lock(&buffer->lock);
\t\t\tbuffer->mmap_cnt--;
\t\t\tmutex_unlock(&buffer->lock);
\t\t\treturn ret;
\t\t}
'''
    s = one(s, old, new, 'mmap failure unwind')

    old = '''\treturn 0;
}

static void *system_heap_do_vmap'''
    new = '''\tvma->vm_private_data = buffer;
\tvma->vm_ops = &sp11_cpz_heap_vm_ops;

\treturn 0;
}

static void *system_heap_do_vmap'''
    s = one(s, old, new, 'mmap tracking')

    old = '''\tmutex_lock(&buffer->lock);
\tif (buffer->vmap_cnt) {
'''
    new = '''\tmutex_lock(&buffer->lock);
\tif (!sp11_cpz_hlos_cpu_allowed(buffer)) {
\t\tret = -EPERM;
\t\tgoto out;
\t}
\tif (buffer->vmap_cnt) {
'''
    s = one(s, old, new, 'vmap guard')

    old = '''\ttable = &buffer->sg_table;
\tfor_each_sgtable_sg(table, sg, i) {
'''
    new = '''\t/* Never recycle backing under remote or ownership-unknown state. */
\tif (!sp11_cpz_hlos_cpu_allowed(buffer) || buffer->cpz_hold) {
\t\tpr_err_ratelimited("sp11-cpz: refusing to free remotely-owned/unknown system-heap backing\\n");
\t\treturn;
\t}

\ttable = &buffer->sg_table;
\tfor_each_sgtable_sg(table, sg, i) {
'''
    s = one(s, old, new, 'release fail closed')

    marker = '''static const struct dma_buf_ops system_heap_buf_ops = {
\t.attach = system_heap_attach,
\t.detach = system_heap_detach,
\t.map_dma_buf = system_heap_map_dma_buf,
\t.unmap_dma_buf = system_heap_unmap_dma_buf,
\t.begin_cpu_access = system_heap_dma_buf_begin_cpu_access,
\t.end_cpu_access = system_heap_dma_buf_end_cpu_access,
\t.mmap = system_heap_mmap,
\t.vmap = system_heap_vmap,
\t.vunmap = system_heap_vunmap,
\t.release = system_heap_dma_buf_release,
};
'''
    transition = marker + '''
static int sp11_cpz_heap_check_quiescent(struct system_heap_buffer *buffer)
{
\tif (buffer->mmap_cnt || buffer->vmap_cnt || buffer->cpu_access_cnt ||
\t    sp11_cpz_any_mapped_attachment(buffer))
\t\treturn -EBUSY;
\treturn 0;
}

int sp11_cpz_system_heap_lend(struct dma_buf *dmabuf, bool camera_target)
{
\tstruct system_heap_buffer *buffer;
\tconst u32 src[] = { QCOM_SCM_VMID_HLOS };
\tstruct qcom_scm_vmperm dst[2];
\tunsigned int nr_dst = 1;
\tint ret;

\tif (!dmabuf || dmabuf->ops != &system_heap_buf_ops)
\t\treturn -EINVAL;
\tbuffer = dmabuf->priv;

\tmutex_lock(&buffer->lock);
\tif (!sp11_cpz_hlos_cpu_allowed(buffer) || buffer->cpz_hold) {
\t\tmutex_unlock(&buffer->lock);
\t\treturn -EPERM;
\t}
\tret = sp11_cpz_heap_check_quiescent(buffer);
\tif (ret) {
\t\tmutex_unlock(&buffer->lock);
\t\treturn ret;
\t}
\tget_dma_buf(dmabuf);
\tbuffer->cpz_hold = true;
\tbuffer->cpz_state = SP11_CPZ_HEAP_TRANSITION;
\tbuffer->cpz_owner_kind = camera_target ? SP11_CPZ_OWNER_INTERNAL :
\t\t\t\t\t       SP11_CPZ_OWNER_EXTERNAL;
\tmutex_unlock(&buffer->lock);

\tdst[0].vmid = QCOM_SCM_VMID_CP_CDSP;
\tdst[0].perm = QCOM_SCM_PERM_RW;
\tif (camera_target) {
\t\tdst[1].vmid = QCOM_SCM_VMID_CP_CAMERA;
\t\tdst[1].perm = QCOM_SCM_PERM_RW;
\t\tnr_dst = 2;
\t}

\tret = sp11_cpz_assign_sg(&buffer->sg_table, src, ARRAY_SIZE(src), dst, nr_dst);
\tmutex_lock(&buffer->lock);
\tbuffer->cpz_state = ret ? SP11_CPZ_HEAP_POISONED : SP11_CPZ_HEAP_LENT;
\tmutex_unlock(&buffer->lock);
\t/* Failure intentionally keeps cpz_hold: physical ownership is uncertain. */
\treturn ret;
}

int sp11_cpz_system_heap_mark_active(struct dma_buf *dmabuf)
{
\tstruct system_heap_buffer *buffer;

\tif (!dmabuf || dmabuf->ops != &system_heap_buf_ops)
\t\treturn -EINVAL;
\tbuffer = dmabuf->priv;
\tmutex_lock(&buffer->lock);
\tif (buffer->cpz_state != SP11_CPZ_HEAP_LENT || !buffer->cpz_hold) {
\t\tmutex_unlock(&buffer->lock);
\t\treturn -EPERM;
\t}
\tbuffer->cpz_state = SP11_CPZ_HEAP_ACTIVE;
\tmutex_unlock(&buffer->lock);
\treturn 0;
}

int sp11_cpz_system_heap_mark_detached(struct dma_buf *dmabuf)
{
\tstruct system_heap_buffer *buffer;

\tif (!dmabuf || dmabuf->ops != &system_heap_buf_ops)
\t\treturn -EINVAL;
\tbuffer = dmabuf->priv;
\tmutex_lock(&buffer->lock);
\tif (buffer->cpz_state != SP11_CPZ_HEAP_ACTIVE || !buffer->cpz_hold) {
\t\tmutex_unlock(&buffer->lock);
\t\treturn -EPERM;
\t}
\tbuffer->cpz_state = SP11_CPZ_HEAP_DETACHED;
\tmutex_unlock(&buffer->lock);
\treturn 0;
}

int sp11_cpz_system_heap_reclaim(struct dma_buf *dmabuf)
{
\tstruct system_heap_buffer *buffer;
\tu32 src[2];
\tconst struct qcom_scm_vmperm dst = {
\t\t.vmid = QCOM_SCM_VMID_HLOS,
\t\t.perm = QCOM_SCM_PERM_RWX,
\t};
\tunsigned int nr_src;
\tint ret;

\tif (!dmabuf || dmabuf->ops != &system_heap_buf_ops)
\t\treturn -EINVAL;
\tbuffer = dmabuf->priv;
\tmutex_lock(&buffer->lock);
\tif (!buffer->cpz_hold ||
\t    (buffer->cpz_state != SP11_CPZ_HEAP_DETACHED &&
\t     buffer->cpz_state != SP11_CPZ_HEAP_LENT)) {
\t\tmutex_unlock(&buffer->lock);
\t\treturn -EPERM;
\t}
\tif (buffer->cpz_owner_kind == SP11_CPZ_OWNER_INTERNAL) {
\t\tsrc[0] = QCOM_SCM_VMID_CP_CDSP;
\t\tsrc[1] = QCOM_SCM_VMID_CP_CAMERA;
\t\tnr_src = 2;
\t} else if (buffer->cpz_owner_kind == SP11_CPZ_OWNER_EXTERNAL) {
\t\tsrc[0] = QCOM_SCM_VMID_CP_CDSP;
\t\tnr_src = 1;
\t} else {
\t\tmutex_unlock(&buffer->lock);
\t\treturn -EINVAL;
\t}
\tbuffer->cpz_state = SP11_CPZ_HEAP_TRANSITION;
\tmutex_unlock(&buffer->lock);

\tret = sp11_cpz_assign_sg(&buffer->sg_table, src, nr_src, &dst, 1);
\tmutex_lock(&buffer->lock);
\tif (ret) {
\t\tbuffer->cpz_state = SP11_CPZ_HEAP_POISONED;
\t\tmutex_unlock(&buffer->lock);
\t\t/* Retain cpz_hold so backing cannot be recycled under uncertainty. */
\t\treturn ret;
\t}
\tbuffer->cpz_state = SP11_CPZ_HEAP_RECLAIMED;
\tbuffer->cpz_owner_kind = SP11_CPZ_OWNER_NONE;
\tbuffer->cpz_hold = false;
\tmutex_unlock(&buffer->lock);
\tdma_buf_put(dmabuf);
\treturn 0;
}
'''
    s = one(s, marker, transition, 'provider transitions')

    old = '''\tbuffer->heap = heap;
\tbuffer->len = len;
\tbuffer->cc_shared = cc_shared;
'''
    new = '''\tbuffer->heap = heap;
\tbuffer->len = len;
\tbuffer->cc_shared = cc_shared;
\tbuffer->cpz_hold = false;
\tbuffer->cpz_state = SP11_CPZ_HEAP_HLOS;
\tbuffer->cpz_owner_kind = SP11_CPZ_OWNER_NONE;
'''
    s = one(s, old, new, 'initial state')

    s = one(s, 'module_init(system_heap_create);\n',
            '/* E004cu compile-only: heap registration deliberately disabled. */\n',
            'disable heap registration')
    s = one(s, 'static int __init system_heap_create(void)',
            'static int __maybe_unused system_heap_create(void)', 'unused heap create')

    out.write_text(s)
    print('E004cu system-heap protected-state scaffold generation: PASS')
    print('base_sha=' + sha(src))
    print('stage_sha=' + sha(out))

if __name__ == '__main__':
    main()
