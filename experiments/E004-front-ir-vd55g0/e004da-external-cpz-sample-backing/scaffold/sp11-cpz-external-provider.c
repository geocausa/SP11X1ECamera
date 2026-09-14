// SPDX-License-Identifier: GPL-2.0
/*
 * E004da compile-only external protected-sample backing/lifetime provider.
 *
 * No registration exists in this file.  No caller exists in production.
 * Ownership-changing functions compile against the E004cz system-heap API but
 * are never invoked by this experiment.
 */
#include <linux/dma-buf.h>
#include <linux/errno.h>
#include <linux/kernel.h>
#include <linux/mutex.h>
#include <linux/string.h>

#include "sp11-cpz-system-heap.h"
#include "sp11-cpz-dmabuf-query.h"
#include "sp11-cpz-external-provider.h"

static bool sp11_cpz_external_extent_valid(struct sp11_cpz_external_runtime *external,
					   size_t extent)
{
	return extent <= external->contract.sample.allocation_extent;
}

int sp11_cpz_external_bind(struct sp11_cpz_external_runtime *external,
			   struct dma_buf *dmabuf, const u8 id[CAMSS_PROTECTED_ID_BYTES],
			   u64 request_id, size_t allocation_extent)
{
	if (!external || !dmabuf || !id || !allocation_extent ||
	    allocation_extent > dmabuf->size)
		return -EINVAL;

	memset(external, 0, sizeof(*external));
	mutex_init(&external->lock);
	get_dma_buf(dmabuf);
	external->dmabuf = dmabuf;
	external->backing_ref_held = true;
	memcpy(external->contract.sample.id, id, CAMSS_PROTECTED_ID_BYTES);
	external->contract.sample.request_id = request_id;
	external->contract.sample.allocation_extent = allocation_extent;
	external->contract.sample.identity_proven = true;
	external->contract.sample.normal_hlos_cpu_visible = true;
	external->contract.sample.phase = CAMSS_EXTERNAL_SAMPLE_IDENTITY_BOUND;
	external->contract.phase = CAMSS_CPZ_EXTERNAL_BACKING_READY;
	external->contract.logical_identity_bound = true;
	external->contract.backing_reference_held = true;
	return 0;
}

int sp11_cpz_external_lend_to_worker(struct sp11_cpz_external_runtime *external)
{
	int ret;

	if (!external)
		return -EINVAL;
	mutex_lock(&external->lock);
	if (!external->dmabuf || !external->backing_ref_held ||
	    external->contract.phase != CAMSS_CPZ_EXTERNAL_BACKING_READY) {
		ret = -EPERM;
		goto out;
	}

	/* camera_target=false is the hard separation from CP_CAMERA ownership. */
	ret = sp11_cpz_system_heap_lend(external->dmabuf, false);
	if (ret) {
		/*
		 * E004cu marks uncertain post-SCM failures POISONED and keeps the
		 * dma-buf held. Mirror that uncertainty instead of claiming HLOS.
		 */
		if (sp11_cpz_dma_buf_is_protected(external->dmabuf)) {
			external->contract.phase = CAMSS_CPZ_EXTERNAL_RECLAIMING;
			external->contract.sample.normal_hlos_cpu_visible = false;
		}
		goto out;
	}

	/* HLOS is no longer trusted immediately after a successful lend. */
	external->contract.worker_owner_active = true;
	external->contract.sample.normal_hlos_cpu_visible = false;
	if (!sp11_cpz_dma_buf_is_protected(external->dmabuf)) {
		/* LENT may reclaim directly.  Failure remains held/fail-closed below. */
		ret = sp11_cpz_system_heap_reclaim(external->dmabuf);
		if (!ret) {
			external->contract.worker_owner_active = false;
			external->contract.sample.normal_hlos_cpu_visible = true;
			ret = -EIO;
		} else {
			external->contract.phase = CAMSS_CPZ_EXTERNAL_RECLAIMING;
		}
		goto out;
	}

	external->contract.phase = CAMSS_CPZ_EXTERNAL_WORKER_OWNED;
	ret = 0;
out:
	mutex_unlock(&external->lock);
	return ret;
}

int sp11_cpz_external_begin_worker_import(struct sp11_cpz_external_runtime *external,
					 struct dma_buf **dmabuf)
{
	int ret = 0;

	if (!external || !dmabuf)
		return -EINVAL;
	mutex_lock(&external->lock);
	if (!external->dmabuf || !external->contract.worker_owner_active ||
	    external->contract.phase != CAMSS_CPZ_EXTERNAL_WORKER_OWNED ||
	    !sp11_cpz_dma_buf_is_protected(external->dmabuf) ||
	    external->worker_ref_held) {
		ret = -EPERM;
		goto out;
	}

	/*
	 * Provider-held reference spans the future FastRPC import and payload life.
	 * The actual FastRPC map also takes its own dma-buf reference.
	 */
	get_dma_buf(external->dmabuf);
	external->worker_ref_held = true;
	*dmabuf = external->dmabuf;
out:
	mutex_unlock(&external->lock);
	return ret;
}

int sp11_cpz_external_commit_worker_import(struct sp11_cpz_external_runtime *external)
{
	int ret;

	if (!external)
		return -EINVAL;
	mutex_lock(&external->lock);
	if (!external->worker_ref_held ||
	    external->contract.phase != CAMSS_CPZ_EXTERNAL_WORKER_OWNED) {
		ret = -EPERM;
		goto out;
	}
	ret = sp11_cpz_system_heap_mark_active(external->dmabuf);
	if (ret)
		goto out;
	external->contract.phase = CAMSS_CPZ_EXTERNAL_WORKER_IMPORTED;
	external->contract.worker_mapping_active = true;
	external->contract.sample.trusted_worker_visible = true;
	external->contract.sample.phase = CAMSS_EXTERNAL_SAMPLE_TRUSTED_VISIBLE;
out:
	mutex_unlock(&external->lock);
	return ret;
}

void sp11_cpz_external_abort_worker_import(struct sp11_cpz_external_runtime *external)
{
	struct dma_buf *put = NULL;

	if (!external)
		return;
	mutex_lock(&external->lock);
	if (external->worker_ref_held &&
	    external->contract.phase == CAMSS_CPZ_EXTERNAL_WORKER_OWNED) {
		external->worker_ref_held = false;
		put = external->dmabuf;
	}
	mutex_unlock(&external->lock);
	if (put)
		dma_buf_put(put);
}

int sp11_cpz_external_mark_payload_ready(struct sp11_cpz_external_runtime *external,
					 size_t captured_extent,
					 size_t serialized_extent,
					 size_t payload_offset)
{
	int ret = 0;

	if (!external)
		return -EINVAL;
	mutex_lock(&external->lock);
	if (external->contract.phase != CAMSS_CPZ_EXTERNAL_WORKER_IMPORTED ||
	    !external->contract.worker_mapping_active || !external->worker_ref_held ||
	    !sp11_cpz_external_extent_valid(external, captured_extent) ||
	    !sp11_cpz_external_extent_valid(external, serialized_extent) ||
	    serialized_extent > captured_extent ||
	    payload_offset > captured_extent || payload_offset > serialized_extent) {
		ret = -EINVAL;
		goto out;
	}
	external->contract.sample.captured_extent = captured_extent;
	external->contract.sample.serialized_extent = serialized_extent;
	external->contract.sample.payload_offset = payload_offset;
	external->contract.sample.phase = CAMSS_EXTERNAL_SAMPLE_PAYLOAD_READY;
	external->contract.phase = CAMSS_CPZ_EXTERNAL_PAYLOAD_READY;
out:
	mutex_unlock(&external->lock);
	return ret;
}

int sp11_cpz_external_worker_detached(struct sp11_cpz_external_runtime *external)
{
	struct dma_buf *put = NULL;
	int ret;

	if (!external)
		return -EINVAL;
	mutex_lock(&external->lock);
	if (!external->worker_ref_held || !external->contract.worker_mapping_active ||
	    (external->contract.phase != CAMSS_CPZ_EXTERNAL_WORKER_IMPORTED &&
	     external->contract.phase != CAMSS_CPZ_EXTERNAL_PAYLOAD_READY)) {
		ret = -EPERM;
		goto out;
	}

	/* Called only after the real FastRPC map has been detached. */
	ret = sp11_cpz_system_heap_mark_detached(external->dmabuf);
	if (ret)
		goto out;
	external->contract.phase = CAMSS_CPZ_EXTERNAL_WORKER_DETACHING;
	external->contract.worker_mapping_active = false;
	external->contract.sample.trusted_worker_visible = false;
	external->contract.worker_detached_before_reclaim = true;
	external->worker_ref_held = false;
	put = external->dmabuf;
out:
	mutex_unlock(&external->lock);
	if (put)
		dma_buf_put(put);
	return ret;
}

int sp11_cpz_external_reclaim(struct sp11_cpz_external_runtime *external)
{
	int ret;

	if (!external)
		return -EINVAL;
	mutex_lock(&external->lock);
	if (external->contract.worker_mapping_active || external->worker_ref_held) {
		ret = -EPERM;
		goto out;
	}
	if (external->contract.phase == CAMSS_CPZ_EXTERNAL_WORKER_DETACHING) {
		if (!external->contract.worker_detached_before_reclaim) {
			ret = -EPERM;
			goto out;
		}
	} else if (external->contract.phase != CAMSS_CPZ_EXTERNAL_WORKER_OWNED) {
		/* WORKER_OWNED with no mapping/ref is the failed-import rollback path. */
		ret = -EPERM;
		goto out;
	}
	external->contract.phase = CAMSS_CPZ_EXTERNAL_RECLAIMING;
	ret = sp11_cpz_system_heap_reclaim(external->dmabuf);
	if (ret)
		goto out_fail_closed;
	external->contract.phase = CAMSS_CPZ_EXTERNAL_RECLAIMED;
	external->contract.worker_owner_active = false;
	external->contract.ownership_reclaimed_before_free = true;
	external->contract.sample.normal_hlos_cpu_visible = true;
	goto out;

out_fail_closed:
	/* Keep backing_ref_held and the dma-buf pointer under unknown ownership. */
	external->contract.phase = CAMSS_CPZ_EXTERNAL_RECLAIMING;
out:
	mutex_unlock(&external->lock);
	return ret;
}

int sp11_cpz_external_release(struct sp11_cpz_external_runtime *external)
{
	struct dma_buf *put;
	int ret = 0;

	if (!external)
		return -EINVAL;
	mutex_lock(&external->lock);
	if (!external->backing_ref_held || !external->dmabuf || external->worker_ref_held ||
	    (external->contract.phase != CAMSS_CPZ_EXTERNAL_RECLAIMED &&
	     external->contract.phase != CAMSS_CPZ_EXTERNAL_BACKING_READY)) {
		ret = -EBUSY;
		goto out;
	}
	if (external->contract.phase == CAMSS_CPZ_EXTERNAL_RECLAIMED &&
	    !external->contract.ownership_reclaimed_before_free) {
		ret = -EPERM;
		goto out;
	}
	put = external->dmabuf;
	external->dmabuf = NULL;
	external->backing_ref_held = false;
	external->contract.backing_reference_held = false;
	external->contract.sample.phase = CAMSS_EXTERNAL_SAMPLE_RELEASING;
	external->contract.phase = CAMSS_CPZ_EXTERNAL_RELEASING;
	mutex_unlock(&external->lock);
	dma_buf_put(put);
	return 0;
out:
	mutex_unlock(&external->lock);
	return ret;
}
