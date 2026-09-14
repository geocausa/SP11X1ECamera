/* SPDX-License-Identifier: GPL-2.0 */
#ifndef SP11_CPZ_SYSTEM_HEAP_H
#define SP11_CPZ_SYSTEM_HEAP_H
#include <linux/dma-buf.h>
int sp11_cpz_system_heap_lend(struct dma_buf *dmabuf, bool camera_target);
int sp11_cpz_system_heap_mark_active(struct dma_buf *dmabuf);
int sp11_cpz_system_heap_mark_detached(struct dma_buf *dmabuf);
int sp11_cpz_system_heap_reclaim(struct dma_buf *dmabuf);
#endif
