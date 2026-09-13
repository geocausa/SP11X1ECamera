#!/usr/bin/env python3
from pathlib import Path
import json,sys

d=Path(__file__).resolve().parent
def need(v,m):
    if not v:
        print("E004bl VERIFY: FAIL - "+m); sys.exit(1)

r=json.loads((d/"RESULT.json").read_text())
need(r["status"]=="PASS_STATIC_LINUX_PROTECTED_SAMPLE_BOUNDARY_MAPPED","status")

src=(d/"evidence/LINUX-SOURCE-IDENTITY.txt").read_text(errors="replace")
for x in (
 "2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4",
 "69fdbb6364a772d5b9fe50114878bbc7a1a1ffc61e62af1e71c79fd16e94c982",
 "98474729d5036a4e1770e3ab7d275ccaaba143b22202468e4ad8b93c0cbec2cb",
 "7d268c6204f1d85fe6047af5204693a428dc396667ee68ec12785462540cff03",
):
    need(x in src,"source identity missing "+x)

vb=(d/"evidence/CAMSS-VB2-LIFETIME.txt").read_text(errors="replace")
for x in (
 "q->mem_ops = &vb2_dma_sg_memops;",
 "q->io_modes = VB2_DMABUF | VB2_MMAP | VB2_READ;",
 "sgt = vb2_dma_sg_plane_desc(vb, i);",
 "buffer->addr[i] = sg_dma_address(sgt->sgl);",
 "static int video_start_streaming",
 "static void video_stop_streaming",
 ".buf_init        = video_buf_init,",
):
    need(x in vb,"VB2 boundary missing "+x)
need(".buf_cleanup" not in vb,"current queue unexpectedly already has buf_cleanup")

vfe=(d/"evidence/CAMSS-VFE-BUFFER-OWNERSHIP.txt").read_text(errors="replace")
for x in (
 "ops->vfe_wm_update(vfe, output->wm_idx[0],",
 "buf->addr[0]",
 "vb2_buffer_done(&output->buf[0]->vb.vb2_buf, state);",
 "vb2_buffer_done(&output->buf[1]->vb.vb2_buf, state);",
):
    need(x in vfe,"VFE ownership evidence missing "+x)

sensor=(d/"evidence/VD55G0-SENSOR-BOUNDARY.txt").read_text(errors="replace")
need("SECURE_BUFFER_VOCABULARY_ABSENT=1" in sensor,"sensor boundary")
need("static int vd55g0_s_stream" in sensor,"sensor stream callback")

win=(d/"evidence/WINDOWS-CONTRACT-INPUT.txt").read_text(errors="replace")
for x in (
 "PASS_MFCORE_OWNS_SECURE_SURFACE_AND_REQUESTS_SECURE_ALLOCATOR",
 "PASS_MFPLAT_SECURE_BUFFER_OWNER_IS_FSISO_RPC",
 "PASS_FSISO_SERVER_CREATES_SECURE_CAMERA_IUM_SECTION",
):
    need(x in win,"Windows prerequisite missing "+x)

need(r["current_path"]["buffer_cleanup_callback_present"] is False,"buf_cleanup mapping")
need(r["sensor_boundary"]["protected_memory_owner"] is False,"sensor ownership")
need(r["invariants"]["normal_path_unchanged"] is True,"normal path")
need(r["invariants"]["protected_path_no_mmap_read"] is True,"protected mmap/read")
need(r["invariants"]["protected_path_no_ordinary_sg_fallback"] is True,"SG fallback")
need(r["invariants"]["external_sample_separate_from_secureisp_internal_buffer"] is True,"sample/internal split")
need(r["invariants"]["sample_lifetime_separate_from_lane_ownership"] is True,"sample/lane split")
need(r["source_code_modified"] is False,"source modification")
need(r["linux_secure_runtime_executed"] is False,"Linux secure runtime")
need(r["linux_memory_reassignment"] is False,"memory reassignment")
need(r["protected_mmio_access_linux"] is False,"protected MMIO")
need(r["qcomtee_loaded"] is False,"QCOMTEE")

print("E004bl VERIFY: PASS")
print(" - ordinary CAMSS buffer path is anchored from VB2 SG allocation through VFE completion")
print(" - protected policy belongs at CAMSS video/VB2, not in the VD55G0 sensor driver")
print(" - future protected backing needs its own identity/address/lifetime and fail-closed queue policy")
print(" - protected sample lifetime remains separate from SecureISP internal memory and secure-lane ownership")
print(" - no source/runtime/security state was changed")
