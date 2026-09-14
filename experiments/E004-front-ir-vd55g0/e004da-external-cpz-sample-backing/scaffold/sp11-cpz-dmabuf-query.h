/* SPDX-License-Identifier: GPL-2.0 */
#ifndef SP11_CPZ_DMABUF_QUERY_H
#define SP11_CPZ_DMABUF_QUERY_H
#include <linux/dma-buf.h>
/* E004cv compile-only provider authority hook; implementation arrives after integration gate. */
bool sp11_cpz_dma_buf_is_protected(struct dma_buf *dmabuf);
#endif
