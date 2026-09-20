#!/usr/bin/env python3
"""E004ip: patch only an uninstalled CAMSS scratch copy. QC10C DMA safety.

The accepted source, default capture and previously staged NV12 format do
not change. Do NOT deploy this patch until an isolated QC10C mapping/stream
regression has run with rollback on the exact SP11.
"""
import hashlib
import json
from pathlib import Path
import runpy
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
PARENT=ROOT/"experiments/E004-front-ir-vd55g0/e004io-nv12-sg-dma-span"
MAKE_PARENT=runpy.run_path(str(PARENT/"make_dma_span.py"))
EXPECTED_CAMSS_SHA="117136b2c624de5ef3f4c081cdcf9c363cda9f6db5c752b7ade5f5e11b1b3e95"
# Unique source-locked capture validation anchor: only QC10C front PIX.
ANCHOR="\tif (!buffer->addr[0] || !IS_ALIGNED(buffer->addr[0], PAGE_SIZE))\n\t\treturn -EINVAL;\n\tend = (u64)buffer->addr[0] + CAMSS_X1E_PIX_GATE_QC10C_BYTES - 1;\n\tif (end > U32_MAX)\n\t\treturn -ERANGE;\n\n\treturn 0;\n}"
PATCH="\tif (!buffer->addr[0] || !IS_ALIGNED(buffer->addr[0], PAGE_SIZE))\n\t\treturn -EINVAL;\n\tend = (u64)buffer->addr[0] + CAMSS_X1E_PIX_GATE_QC10C_BYTES - 1;\n\tif (end > U32_MAX)\n\t\treturn -ERANGE;\n\n\t/*\n\t * A vb2_dma_sg allocation length does NOT guarantee that DMA may\n\t * advance through a single device-visible IOVA range. The accepted\n\t * compressed output uses one Y_META->Y_DATA->C_META->C_DATA\n\t * allocation and the camera cannot scatter DMA across a gap.\n\t *\n\t * Validate the mapped DMA segments (nents, NOT orig_nents).\n\t * Adjacent mapped segments are fine; every gap or short mapping\n\t * is rejected before the first camera DMA programming for buffer.\n\t */\n\t{\n\t\tstruct sg_table *sgt = vb2_dma_sg_plane_desc(vb, 0);\n\t\tstruct scatterlist *sg;\n\t\tu64 cursor = (u64)buffer->addr[0];\n\t\tu64 remaining = CAMSS_X1E_PIX_GATE_QC10C_BYTES;\n\t\tunsigned int i;\n\n\t\tif (!sgt || !sgt->sgl || sgt->nents == 0 ||\n\t\t    sg_dma_address(sgt->sgl) != buffer->addr[0])\n\t\t\treturn -EINVAL;\n\t\tfor_each_sgtable_dma_sg(sgt, sg, i) {\n\t\t\tu64 length;\n\t\t\tu64 take;\n\n\t\t\tif (!remaining)\n\t\t\t\tbreak;\n\t\t\tif (sg_dma_address(sg) != cursor)\n\t\t\t\treturn -EINVAL;\n\t\t\tlength = sg_dma_len(sg);\n\t\t\tif (!length)\n\t\t\t\treturn -EINVAL;\n\t\t\ttake = min_t(u64, remaining, length);\n\t\t\tcursor += take;\n\t\t\tremaining -= take;\n\t\t}\n\t\tif (remaining)\n\t\t\treturn -EINVAL;\n\t}\n\n\treturn 0;\n}"

def make(source:Path,scratch:Path):
    if hashlib.sha256((source/"camss.c").read_bytes()).hexdigest()!=EXPECTED_CAMSS_SHA:
        raise ValueError("accepted QC10C source changed")
    parent=MAKE_PARENT["make"](source,scratch)
    if parent["new_mmio_calls"]!=0 or parent["experimental_nv12_streaming"]!="-EOPNOTSUPP before media pipeline PM":
        raise ValueError("prior NV12 gates changed")
    file=scratch/"camss.c"
    text=file.read_text()
    if text.count(ANCHOR)!=1:
        raise ValueError("accepted QC10C validation anchor is missing/not unique")
    text=text.replace(ANCHOR,PATCH,1)
    file.write_text(text)
    return audit(scratch)

def audit(scratch:Path):
    accepted=ROOT/"src/front-imx681/kernel/camss/camss.c"
    if hashlib.sha256(accepted.read_bytes()).hexdigest()!=EXPECTED_CAMSS_SHA:
        raise ValueError("accepted QC10C source changed")
    code=(scratch/"camss.c").read_text()
    original=accepted.read_text()
    if original.count(ANCHOR)!=1 or code!=original.replace(ANCHOR,PATCH,1):
        raise ValueError("unexpected CAMSS core source edits")
    if "static int camss_x1e_pix_v4l2_buffer(" not in code:
        raise ValueError("missing QC10C buffer validator")
    segment=code.split("static int camss_x1e_pix_v4l2_buffer(",1)[1].split(
        "static void camss_x1e_pix_v4l2_error_buffer(",1)[0]
    required=(
        "fmt->pixelformat != V4L2_PIX_FMT_QC10C",
        "vb2_plane_size(vb, 0) < CAMSS_X1E_PIX_GATE_QC10C_BYTES",
        "vb2_dma_sg_plane_desc(vb, 0)",
        "sgt->nents == 0",
        "sg_dma_address(sgt->sgl) != buffer->addr[0]",
        "for_each_sgtable_dma_sg(sgt, sg, i)",
        "sg_dma_address(sg) != cursor",
        "sg_dma_len(sg)",
        "min_t(u64, remaining, length)",
        "if (remaining)",
        "return -EINVAL;",
    )
    if any(x not in segment for x in required):
        raise ValueError("QC10C contiguous DMA-map validation missing")
    if not (segment.index("fmt->pixelformat != V4L2_PIX_FMT_QC10C") <
            segment.index("vb2_dma_sg_plane_desc(vb, 0)") <
            segment.index("for_each_sgtable_dma_sg(sgt, sg, i)") <
            segment.rindex("return 0;")):
        raise ValueError("DMA validation no longer follows format gate before success")
    if any(name in PATCH for name in ("writel(","readl(","ioremap(","pm_runtime_get(")):
        raise ValueError("new hardware/power operations forbidden")
    return {"status":"PASS_E004IP_UNINSTALLED_QC10C_CONTIGUOUS_MAPPED_SG_PREFIX_GUARD",
      "accepted_source_changed":False,
      "scratch_non_qc10c_source_changes":0,
      "requires_qc10c_mapped_iova_coverage_bytes":7778304,
      "supports_multiple_mapped_segments_if_adjacent":True,
      "rejects_mapped_iova_gaps_zero_length_short_span_and_stale_base":True,
      "v4l2_nv12_streaming_still_forbidden":True,
      "live_qc10c_regression_run":False,
      "module_installed":False}

if __name__=="__main__":
    if len(sys.argv)!=3:
        raise SystemExit("usage: make_qc10c_span.py ACCEPTED_CAMSS SCRATCH_CAMSS")
    print(json.dumps(make(Path(sys.argv[1]),Path(sys.argv[2])),sort_keys=True,indent=2))
