/* SPDX-License-Identifier: GPL-2.0 */
#ifndef SP11_CPZ_EXTERNAL_PROVIDER_H
#define SP11_CPZ_EXTERNAL_PROVIDER_H

#include <linux/dma-buf.h>
#include <linux/mutex.h>
#include "camss-protected-cpz-external-sample.h"

struct sp11_cpz_external_runtime {
	struct camss_cpz_external_sample_contract contract;
	struct dma_buf *dmabuf;
	struct mutex lock;
	bool backing_ref_held;
	bool worker_ref_held;
};

int sp11_cpz_external_bind(struct sp11_cpz_external_runtime *external,
			   struct dma_buf *dmabuf, const u8 id[CAMSS_PROTECTED_ID_BYTES],
			   u64 request_id, size_t allocation_extent);
int sp11_cpz_external_lend_to_worker(struct sp11_cpz_external_runtime *external);
int sp11_cpz_external_begin_worker_import(struct sp11_cpz_external_runtime *external,
					 struct dma_buf **dmabuf);
int sp11_cpz_external_commit_worker_import(struct sp11_cpz_external_runtime *external);
void sp11_cpz_external_abort_worker_import(struct sp11_cpz_external_runtime *external);
int sp11_cpz_external_mark_payload_ready(struct sp11_cpz_external_runtime *external,
					 size_t captured_extent,
					 size_t serialized_extent,
					 size_t payload_offset);
int sp11_cpz_external_worker_detached(struct sp11_cpz_external_runtime *external);
int sp11_cpz_external_reclaim(struct sp11_cpz_external_runtime *external);
int sp11_cpz_external_release(struct sp11_cpz_external_runtime *external);

#endif
