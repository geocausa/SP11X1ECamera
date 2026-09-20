# E004ip — fail-closed QC10C mapped-DMA coverage (offline build)

Date: 2026-09-20. Parent: `0910a49`. SP11 Golden-v4 ARM64.

## Why this matters

The established front QC10C capture accepts a single V4L2 memory plane
holding the Windows-matched `Y_META -> Y_DATA -> C_META -> C_DATA`
surface (7,778,304 bytes). The accepted `video_buf_init` stores the
first mapped scatter-gather DMA address in `buffer->addr[0]`;
`camss_x1e_pix_v4l2_buffer` checks total allocation size and that
the calculated end lies inside the 32-bit DMA window. Those checks do
not establish that the *whole interval* is actually mapped as an
uninterrupted device-visible DMA range. No past observed capture
proves that every later DMABUF or vb2 mapping will have this property.

## New code (uninstalled scratch driver only)

`make_qc10c_span.py` first constructs the exact prior E004io
scratch source, then inserts **one bounded validation block** into
the existing QC10C-only V4L2 frame validator in the temporary
`camss.c`. Its initial source SHA-256 and single insertion point
are exact-pinned. It iterates `for_each_sgtable_dma_sg` over the
**mapped** `sgt->nents` entries (not physical `orig_nents`), ensuring
each successive DMA segment starts exactly where the previous ends
until the entire 7,778,304-byte QC10C surface is covered. Missing
maps, a mismatched cached base, gaps, overlaps, zero-length entries
and insufficient mapped bytes fail with `-EINVAL` before bus DMA
programming. The original 32-bit address-window check runs first,
bounding cursor arithmetic. Multi-segment mappings with truly
adjacent device DMA addresses are accepted, avoiding the overly
strict single-segment-only requirement used in the unproven NV12
planner.

The accepted production QC10C driver is **unchanged**. This change
is a candidate safety guard only; it cannot be deployed until an
isolated bounded QC10C regression establishes that actual SP11
vb2 DMA mappings pass, and confirms correct recovery if a mapping
is rejected. No new MMIO operations, format declarations,
camera-mode changes, IR enablement or unsafe NV12 authorization.

## Actual tests and limitations

```sh
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004ip-qc10c-mapped-dma-coverage \
  -p 'test_qc10c_span.py' -v
bash experiments/E004-front-ir-vd55g0/e004ip-qc10c-mapped-dma-coverage/build-offline.sh
```

On SP11: six tests PASS, including exact source-integrity and
deliberately corrupted checks. Two of those tests compile and
execute the **actual inserted C validation block** under both GCC
and Clang with AddressSanitizer/UBSan against ten synthetic DMA
mapping cases apiece: adjacent/single span accepted; gap,
overlap, short/zero segment, stale base, empty/missing mapped
table and 32-bit overflow rejected. This is a userspace mock of
kernel SG iteration, not proof of a real DMA API or kernel
camera session.

A full, **uninstalled** ARM64 `qcom-camss.ko` module builds
against the running SP11 Golden-v4 headers and kernel output.
Disposable module SHA-256:

`f7765ca9c672113781f72017c54e7b24916c6ce101bfb06676d8ef039cf5d188`

The scratch module is deleted after the build; nothing was
installed or activated. The earlier alternate NV12 V4L2 mode
remains blocked before media power and the separate ISP and UBWC
linear-output authority remains unproven. Existing observed
QC10C frames are not invalidated by this source-level finding;
the new guard addresses future mapped-buffer safety.

## Next checkpoints

For this QC10C safety patch: preserve the original production
driver and perform a *separately authorized*, one-shot candidate
regression only after verifying the exact deployment/rollback
procedure, the current DMA mapping characteristics and absence
of competing camera sessions. Do not mistake a scratch build for
a successful live capture.

For ordinary Linux front RGB: the unchanged blocker is the
exact X1E80100 linear-NV12 ISP output, safe compression-mode
initialization/verification and frame/auxiliary completion;
neither this patch nor the archived Windows app-facing NV12
resolution proves that path.

Golden, original camera module, Windows, KD, PMIC/firmware, IR
emitter and login/production protected trust are unchanged.
