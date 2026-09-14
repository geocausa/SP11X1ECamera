/* SPDX-License-Identifier: GPL-2.0 */
#ifndef SP11_CPZ_FASTRPC_HANDOFF_H
#define SP11_CPZ_FASTRPC_HANDOFF_H

#include <linux/types.h>
#include "fastrpc-e004cv-uapi.h"
#include "sp11-cpz-external-provider.h"

enum sp11_cpz_fastrpc_handoff_phase {
	SP11_CPZ_HANDOFF_IDLE = 0,
	SP11_CPZ_HANDOFF_PREPARED,
	SP11_CPZ_HANDOFF_MAP_REQUEST_READY,
	SP11_CPZ_HANDOFF_MAPPED,
	SP11_CPZ_HANDOFF_MAP_COMMIT_FAILED,
	SP11_CPZ_HANDOFF_DETACHED,
	SP11_CPZ_HANDOFF_ABORTED,
};

struct sp11_cpz_fastrpc_handoff {
	struct sp11_cpz_external_runtime *external;
	int dmabuf_fd;
	u64 declared_captured_extent;
	u64 map_length;
	u64 remote_vaddr;
	enum sp11_cpz_fastrpc_handoff_phase phase;
	bool fastrpc_map_succeeded;
};

void sp11_cpz_fastrpc_build_cpz_session_info(
	struct fastrpc_proc_sess_info_e004cv *info);
int sp11_cpz_fastrpc_handoff_prepare(
	struct sp11_cpz_fastrpc_handoff *handoff,
	struct sp11_cpz_external_runtime *external,
	int dmabuf_fd);
int sp11_cpz_fastrpc_declare_captured_extent(
	struct sp11_cpz_fastrpc_handoff *handoff, u64 captured_extent);
int sp11_cpz_fastrpc_build_mem_map(
	struct sp11_cpz_fastrpc_handoff *handoff,
	struct fastrpc_mem_map *req);
int sp11_cpz_fastrpc_complete_mem_map(
	struct sp11_cpz_fastrpc_handoff *handoff,
	int ioctl_ret, const struct fastrpc_mem_map *req);
int sp11_cpz_fastrpc_mark_payload_ready(
	struct sp11_cpz_fastrpc_handoff *handoff,
	u64 captured_extent, u64 serialized_extent, u64 payload_offset);
int sp11_cpz_fastrpc_build_mem_unmap(
	struct sp11_cpz_fastrpc_handoff *handoff,
	struct fastrpc_mem_unmap *req);
int sp11_cpz_fastrpc_complete_mem_unmap(
	struct sp11_cpz_fastrpc_handoff *handoff,
	int ioctl_ret);

#endif
