// SPDX-License-Identifier: GPL-2.0
/*
 * E004db compile-only coordinator for the real fd/ioctl FastRPC handoff.
 *
 * This object issues no ioctl and registers no device.  A future trusted
 * userspace control process owns the actual /dev/fastrpc-cdsp-secure file and
 * executes the requests constructed here.  These helpers only prove the
 * dma-buf-fd identity and bind ioctl results to the E004da backing lifetime.
 */
#include <linux/dma-buf.h>
#include <linux/err.h>
#include <linux/errno.h>
#include <linux/string.h>

#include "sp11-cpz-dmabuf-query.h"
#include "sp11-cpz-fastrpc-handoff.h"

#define SP11_FASTRPC_CDSP_DOMAIN_ID 3

void sp11_cpz_fastrpc_build_cpz_session_info(
	struct fastrpc_proc_sess_info_e004cv *info)
{
	memset(info, 0, sizeof(*info));
	info->domain_id = SP11_FASTRPC_CDSP_DOMAIN_ID;
	info->pd_type = FASTRPC_REMOTE_PD_CPZ_USER;
	info->sharedcb = 0;
}

int sp11_cpz_fastrpc_handoff_prepare(
	struct sp11_cpz_fastrpc_handoff *handoff,
	struct sp11_cpz_external_runtime *external,
	int dmabuf_fd)
{
	struct dma_buf *fd_buf;
	struct dma_buf *worker_buf = NULL;
	int ret;

	if (!handoff || !external || dmabuf_fd < 0)
		return -EINVAL;
	if (handoff->phase != SP11_CPZ_HANDOFF_IDLE)
		return -EBUSY;

	/*
	 * fd lookup only takes a dma-buf/file reference.  It does not CPU-map the
	 * backing.  The protected system heap remains the CPU-access authority.
	 */
	fd_buf = dma_buf_get(dmabuf_fd);
	if (IS_ERR(fd_buf))
		return PTR_ERR(fd_buf);
	if (fd_buf != external->dmabuf ||
	    !sp11_cpz_dma_buf_is_protected(fd_buf)) {
		ret = -EACCES;
		goto out_put_fd;
	}

	ret = sp11_cpz_external_begin_worker_import(external, &worker_buf);
	if (ret)
		goto out_put_fd;
	if (worker_buf != fd_buf) {
		/* No FastRPC map exists yet, so the provider worker ref may be aborted. */
		sp11_cpz_external_abort_worker_import(external);
		ret = -EXDEV;
		goto out_put_fd;
	}

	handoff->external = external;
	handoff->dmabuf_fd = dmabuf_fd;
	handoff->phase = SP11_CPZ_HANDOFF_PREPARED;
	ret = 0;

out_put_fd:
	dma_buf_put(fd_buf);
	return ret;
}

int sp11_cpz_fastrpc_declare_captured_extent(
	struct sp11_cpz_fastrpc_handoff *handoff, u64 captured_extent)
{
	if (!handoff || !handoff->external || !captured_extent)
		return -EINVAL;
	if (handoff->phase != SP11_CPZ_HANDOFF_PREPARED)
		return -EPERM;
	if (captured_extent > handoff->external->contract.sample.allocation_extent)
		return -E2BIG;

	/*
	 * Windows forwards cbCaptured before the trustlet opens/maps the external
	 * section.  Preserve that timing without mutating E004da's later payload
	 * completion record: this handoff-local value is the exact map extent.
	 */
	handoff->declared_captured_extent = captured_extent;
	return 0;
}

int sp11_cpz_fastrpc_build_mem_map(
	struct sp11_cpz_fastrpc_handoff *handoff,
	struct fastrpc_mem_map *req)
{
	u64 length;

	if (!handoff || !req || !handoff->external)
		return -EINVAL;
	if (handoff->phase != SP11_CPZ_HANDOFF_PREPARED)
		return -EPERM;
	length = handoff->declared_captured_extent;
	if (!length || length > handoff->external->contract.sample.allocation_extent)
		return -EINVAL;

	memset(req, 0, sizeof(*req));
	req->version = 0;
	req->fd = handoff->dmabuf_fd;
	req->offset = 0;
	/* Same-machine CDSP dispatches FastRPC map flag 2 through fd_mmap_create. */
	req->flags = FASTRPC_MAP_FD;
	req->vaddrin = 0;
	/* Windows parity: external mapping length is cbCaptured, not capacity. */
	req->length = length;
	req->attrs = 0;
	handoff->map_length = length;
	handoff->phase = SP11_CPZ_HANDOFF_MAP_REQUEST_READY;
	return 0;
}

int sp11_cpz_fastrpc_complete_mem_map(
	struct sp11_cpz_fastrpc_handoff *handoff,
	int ioctl_ret, const struct fastrpc_mem_map *req)
{
	int ret;

	if (!handoff || !req || !handoff->external)
		return -EINVAL;
	if (handoff->phase != SP11_CPZ_HANDOFF_MAP_REQUEST_READY ||
	    req->fd != handoff->dmabuf_fd || req->length != handoff->map_length)
		return -EPERM;

	if (ioctl_ret) {
		/* MEM_MAP failed: no successful DSP map to detach. */
		sp11_cpz_external_abort_worker_import(handoff->external);
		handoff->phase = SP11_CPZ_HANDOFF_ABORTED;
		return ioctl_ret;
	}

	/*
	 * A zero ioctl return is the authority that FastRPC owns a map/reference.
	 * From this point onward we must unmap before dropping the provider worker
	 * reference, even if the provider-side ACTIVE commit unexpectedly fails.
	 */
	handoff->fastrpc_map_succeeded = true;
	handoff->remote_vaddr = req->vaddrout;
	ret = sp11_cpz_external_commit_worker_import(handoff->external);
	if (ret) {
		handoff->phase = SP11_CPZ_HANDOFF_MAP_COMMIT_FAILED;
		return ret;
	}
	handoff->phase = SP11_CPZ_HANDOFF_MAPPED;
	return 0;
}

int sp11_cpz_fastrpc_mark_payload_ready(
	struct sp11_cpz_fastrpc_handoff *handoff,
	u64 captured_extent, u64 serialized_extent, u64 payload_offset)
{
	if (!handoff || !handoff->external ||
	    handoff->phase != SP11_CPZ_HANDOFF_MAPPED)
		return -EPERM;
	if (!handoff->declared_captured_extent ||
	    captured_extent != handoff->declared_captured_extent)
		return -EINVAL;
	if (serialized_extent > captured_extent ||
	    payload_offset > serialized_extent)
		return -EINVAL;

	return sp11_cpz_external_mark_payload_ready(handoff->external,
					 captured_extent, serialized_extent,
					 payload_offset);
}

int sp11_cpz_fastrpc_build_mem_unmap(
	struct sp11_cpz_fastrpc_handoff *handoff,
	struct fastrpc_mem_unmap *req)
{
	if (!handoff || !req || !handoff->external ||
	    !handoff->fastrpc_map_succeeded)
		return -EINVAL;
	if (handoff->phase != SP11_CPZ_HANDOFF_MAPPED &&
	    handoff->phase != SP11_CPZ_HANDOFF_MAP_COMMIT_FAILED)
		return -EPERM;

	memset(req, 0, sizeof(*req));
	req->vesion = 0;
	req->fd = handoff->dmabuf_fd;
	req->vaddr = handoff->remote_vaddr;
	req->length = handoff->map_length;
	return 0;
}

int sp11_cpz_fastrpc_complete_mem_unmap(
	struct sp11_cpz_fastrpc_handoff *handoff,
	int ioctl_ret)
{
	int ret;

	if (!handoff || !handoff->external || !handoff->fastrpc_map_succeeded)
		return -EINVAL;
	if (handoff->phase != SP11_CPZ_HANDOFF_MAPPED &&
	    handoff->phase != SP11_CPZ_HANDOFF_MAP_COMMIT_FAILED)
		return -EPERM;

	/* An unmap failure keeps the worker reference/ownership pinned. */
	if (ioctl_ret)
		return ioctl_ret;

	if (handoff->phase == SP11_CPZ_HANDOFF_MAP_COMMIT_FAILED) {
		/* FastRPC map is gone; E004da never reached ACTIVE, so abort the worker ref. */
		sp11_cpz_external_abort_worker_import(handoff->external);
		handoff->fastrpc_map_succeeded = false;
		handoff->phase = SP11_CPZ_HANDOFF_ABORTED;
		return 0;
	}

	ret = sp11_cpz_external_worker_detached(handoff->external);
	if (ret)
		return ret;
	handoff->fastrpc_map_succeeded = false;
	handoff->phase = SP11_CPZ_HANDOFF_DETACHED;
	return 0;
}
