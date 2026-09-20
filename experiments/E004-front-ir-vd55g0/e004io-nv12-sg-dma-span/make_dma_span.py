#!/usr/bin/env python3
"""E004io: harden ONLY the disposable NV12 sidecar against noncontiguous SG DMA.

Compiles with the parent E004in overlay. Never edits accepted CAMSS files;
no MMIO, hardware activation, boot, firmware or new capture.
"""
import hashlib
import json
from pathlib import Path
import runpy
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PARENT=ROOT/"experiments/E004-front-ir-vd55g0/e004in-linear-full-wm-dryrun"
P=runpy.run_path(str(PARENT/"make_full_dryrun.py"))
BEFORE="\tif (buffer->vb.vb2_buf.num_planes != 1 ||\n\t    buffer->vb.vb2_buf.state != VB2_BUF_STATE_ACTIVE ||\n\t    vb2_plane_size(&buffer->vb.vb2_buf, 0) <\n\t\tVFE680_X1E_LINEAR_NV12_ALLOCATION)\n\t\treturn -EINVAL;\n\n\tbase = buffer->addr[0];\n\tif (!base || !IS_ALIGNED(base, PAGE_SIZE))\n\t\treturn -EINVAL;\n\tchroma = (u64)base + VFE680_X1E_LINEAR_NV12_Y_BYTES;\n\tend = (u64)base + VFE680_X1E_LINEAR_NV12_ALLOCATION;\n\tif (base > U32_MAX || chroma > U32_MAX || end <= base ||\n\t    end - 1 > U32_MAX)\n\t\treturn -ERANGE;"
AFTER="\tif (buffer->vb.vb2_buf.num_planes != 1 ||\n\t    buffer->vb.vb2_buf.state != VB2_BUF_STATE_ACTIVE ||\n\t    vb2_plane_size(&buffer->vb.vb2_buf, 0) <\n\t\tVFE680_X1E_LINEAR_NV12_ALLOCATION)\n\t\treturn -EINVAL;\n\n\t/*\n\t * vb2_dma_sg does NOT guarantee that a sufficiently large V4L2\n\t * allocation maps to ONE contiguous DMA span. A base address from\n\t * sg_dma_address(sgl) cannot authorize access past the first mapped\n\t * segment. Fail closed until a proper IOVA/SG-aware allocator exists.\n\t * nents is the mapped DMA segment count (not orig_nents/pages).\n\t */\n\t{\n\t\tstruct sg_table *sgt =\n\t\t\tvb2_dma_sg_plane_desc(&buffer->vb.vb2_buf, 0);\n\n\t\tif (!sgt || !sgt->sgl || sgt->nents != 1 ||\n\t\t    sg_dma_len(sgt->sgl) < VFE680_X1E_LINEAR_NV12_ALLOCATION ||\n\t\t    sg_dma_address(sgt->sgl) != buffer->addr[0])\n\t\t\treturn -EINVAL;\n\t}\n\n\tbase = buffer->addr[0];\n\tif (!base || !IS_ALIGNED(base, PAGE_SIZE))\n\t\treturn -EINVAL;\n\tchroma = (u64)base + VFE680_X1E_LINEAR_NV12_Y_BYTES;\n\tend = (u64)base + VFE680_X1E_LINEAR_NV12_ALLOCATION;\n\tif (base > U32_MAX || chroma > U32_MAX || end <= base ||\n\t    end - 1 > U32_MAX)\n\t\treturn -ERANGE;\n\t/* vb2 front NV12 computes C from Y+stride*height at buf_init. */\n\tif (buffer->addr[1] != (dma_addr_t)chroma)\n\t\treturn -EINVAL;"

def make(source: Path, scratch: Path):
    original=P["make"](source,scratch)
    if original["hardware_access_authorized"] or original["actual_register_writes"]:
        raise ValueError("parent changed to hardware-accessible code")
    vfe=scratch/"camss-vfe-680.c"
    before=vfe.read_text()
    if before.count(BEFORE)!=1:
        raise ValueError("expected unique unmodified planner block missing")
    changed=before.replace(BEFORE, AFTER, 1)
    if changed.count('#include "camss.h"') != 1:
        raise ValueError("missing unique CAMSS include anchor")
    changed=changed.replace('#include "camss.h"',
        '#include <media/videobuf2-dma-sg.h>\n#include "camss.h"', 1)
    if changed.count("vfe680_x1e_linear_nv12_buffer_plan(")!=2:
        # one definition and one pure dry-run caller, never live callers
        raise ValueError("unexpected planner cross-stage call count")
    vfe.write_text(changed)
    return audit(scratch, expected=changed)

def audit(scratch: Path, expected=None):
    vfe=(scratch/"camss-vfe-680.c").read_text()
    if expected is None:
        # Deterministically reconstruct the exact parent overlay without
        # touching production source, then compare ONLY the planned hardening.
        import shutil
        import tempfile
        with tempfile.TemporaryDirectory(prefix="sp11-e004io-audit-") as td:
            ref=Path(td)
            src=ROOT/"src/front-imx681/kernel/camss"
            shutil.copytree(src,ref/"camss")
            P["make"](src,ref/"camss")
            b=(ref/"camss"/"camss-vfe-680.c").read_text()
            if b.count(BEFORE)!=1:
                raise ValueError("upstream NV12 planner drift")
            expected=b.replace(BEFORE,AFTER,1).replace('#include "camss.h"',
                '#include <media/videobuf2-dma-sg.h>\n#include "camss.h"', 1)
            for name in ("camss.c","camss-vfe.c","camss-video.c"):
                if (scratch/name).read_bytes()!=(ref/"camss"/name).read_bytes():
                    raise ValueError("non-VFE680 scratch source drift: "+name)
    if vfe!=expected:
        raise ValueError("unreviewed source added to scratch VFE680")
    # Assertions cover the *actual* full source, not untrusted narrative.
    for token in ('#include <media/videobuf2-dma-sg.h>',
                  "vb2_dma_sg_plane_desc(&buffer->vb.vb2_buf, 0);",
                  "!sgt || !sgt->sgl || sgt->nents != 1",
                  "sg_dma_len(sgt->sgl) < VFE680_X1E_LINEAR_NV12_ALLOCATION",
                  "sg_dma_address(sgt->sgl) != buffer->addr[0]",
                  "buffer->addr[1] != (dma_addr_t)chroma",
                  "out->approved_for_hardware = false;",
                  "return -EOPNOTSUPP;"):
        if token not in vfe:
            raise ValueError("new SG check or existing stream safety gate missing")
    for file in ("camss.c","camss-video.c"):
        if "vfe680_x1e_linear_nv12_buffer_plan(" in (scratch/file).read_text():
            raise ValueError("DMA planner connected to active camera runtime")
    return {"status":"PASS_E004IO_OFFLINE_SINGLE_DMA_SEGMENT_SPAN_VALIDATED",
      "required_mapped_dma_segments":1,
      "required_first_mapped_segment_bytes":5529600,
      "required_single_segment_base_matches_cached_dma":True,
      "required_chroma_dma_matches_computed_offset":True,
      "non_contiguous_mapped_vb2_buffer_rejected":True,
      "accepted_qc10c_source_modified":False,
      "experimental_nv12_streaming":"-EOPNOTSUPP before media pipeline PM",
      "new_mmio_calls":0,"module_installed":False,"live_capture":False,
      "sp11_linear_isp_output_proven":False,
      "sp11_ubwc_reset_proven":False}

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: make_dma_span.py ACCEPTED_CAMSS SCRATCH_CAMSS")
    print(json.dumps(make(Path(sys.argv[1]),Path(sys.argv[2])),indent=2,sort_keys=True))
