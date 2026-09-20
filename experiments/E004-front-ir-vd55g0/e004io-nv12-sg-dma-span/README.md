# E004io — reject fragmented DMA for the proposed linear-NV12 frame

Date: 2026-09-20. Parent: `c350103`. SP11 Linux Golden v4.

## New concrete issue discovered

The accepted CAMSS `video_buf_init` calls
`vb2_dma_sg_plane_desc(vb, 0)` and assigns only
`sg_dma_address(sgt->sgl)` to `buffer->addr[0]`. The prior uninstalled
E004ik NV12 planner checked the vb2 allocation length, starting DMA
address and 32-bit end address. These checks **cannot establish** that
the 5,529,600-byte linear Y+UV allocation maps as one uninterrupted
**device-visible DMA span**. The running kernel's
`include/linux/scatterlist.h` explicitly distinguishes the number
of mapped DMA segments `sgt->nents` from physical `orig_nents`
and defines `sg_dma_len(sg)` as each mapped segment's DMA length.

**Critical distinction:** a large enough V4L2 buffer may contain
multiple mapped DMA segments. Computing UV as Y DMA base + 3,686,400
would then cross an unverified IOVA boundary. A 32-bit end-address
check does not validate that the intervening DMA addresses are mapped.

## New scratch-only implementation

E004io builds on the combined, offline-only E004in kernel source tree.
Its `make_dma_span.py` reproduces the exact upstream scratch tree,
verifies prior source hashes and safety checks, then inserts a guard
*only inside the unreferenced NV12 planning function* in a disposable
copy of `camss-vfe-680.c`:

- require a present, mapped `sg_table` for exactly video plane 0;
- require exactly **one mapped DMA segment**, `sgt->nents == 1`
  (not `orig_nents == 1`, which would incorrectly reject physically
  scattered but IOMMU-coalesced buffers);
- require `sg_dma_len(sgt->sgl) >= 5529600` and the same base as
  `buffer->addr[0]`;
- after the original alignment/32-bit length checks, verify the
  existing V4L2 NV12 `buffer->addr[1]` exactly matches the computed
  interleaved UV address.

This is deliberately conservative: a valid *multi*-segment mapping
may be rejected. A future driver could instead allocate one
DMA-contiguous/IOMMU-contiguous surface or implement a separate
correctly validated scatter/gather-aware mapping strategy; do not
remove this guard merely to make a capture pass.

The scratch VFE680 copy adds the exact kernel header
`media/videobuf2-dma-sg.h`. Every accepted camera source file and
the E004ik/E004im/E004in source hashes remain unchanged. There are
**no new camera MMIO operations, new live callers, new V4L2 format
paths or changed active QC10C code**.

## Actual validation on SP11

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004io-nv12-sg-dma-span \
  -p 'test_dma_span.py' -v
bash experiments/E004-front-ir-vd55g0/e004io-nv12-sg-dma-span/build-offline.sh
```

Eight positive/negative source-contract tests PASS, including
rejection of a changed mapped-segment count, truncated first-segment
length, stale base, wrong chroma offset, removed SG-table access,
premature hardware authorization and unrelated live-source edits.
The **entire ARM64 qcom-camss.ko** then built successfully against
SP11's actual running Golden-v4 ABI. SHA-256 of the **uninstalled,
disposable** module:

`8b373ef68a8edf8414a56a5f61020a3536bee4a174242ccd518d49e4e777bfa5`

An initial compilation attempt exposed the missing
`videobuf2-dma-sg.h` declaration in the VFE680 source file; the
header was added only to the scratch overlay, and the subsequent
complete build and eight tests passed. No actual vb2 buffer mapping
or real NV12 image has yet been tested, so this validates the code
and its fail-closed source contract, **not runtime DMA behaviour**.

## Remaining gates

NV12 STREAMON remains rejected at two independent stages before
media-pipeline power or pipeline allocation. The new DMA planner
remains without a live call site and its private hardware
authorization always returns `-EOPNOTSUPP`.

The exact SP11 VFE1 RAW10-to-8-bit linear NV12 ISP output,
compression-mode initialisation/verification and one-shot stream/
IRQ/auxiliary/AEC lifecycle remain unproven. The archived Windows
1920x1080 app NV12 result does not itself prove linear VFE1
2560x1440 output, and the established QC10C surface must never be
passed to the E004ij linear-NV12 desktop converter.

No camera opened, no module installed, no experimental boot,
no Golden changes, no IR illumination, no PMIC/firmware or
protected-signing work. A hardware test cannot be justified
only by passing these DMA memory checks.
