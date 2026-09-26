# E007l — rear TMC141 solver-input Windows oracle

Parent Git: `120bc0bc` (E007k TMC141 static producer contract PASS).

Status: **PREPARED / NOT YET CONSUMED**.

## Goal

Capture one bounded original-Windows rear 4K sequence at the exact entry/return boundary of the source-locked TMC141 anchor solver `QcDeviceMFT8380.dll+0x9255F0`.

E007k proved that GTM consumes TMC141 family #2 and that its 15-float coefficient block is fully derived from the two seven-knot vectors. The remaining unknown is therefore the live producer of those source/destination knots, especially the histogram-driven settling seen from R7 through R10.

This oracle captures the already-preprocessed solver inputs, not another broad GTM/TMC state dump.

## Hook

Entry breakpoint:

- `QcDeviceMFT8380+0x9255F0`;
- accepted only when LR is one of the two direct calls from `0x180923B90`: `+0x9241C4` or `+0x92425C`;
- request ID is the established CamX field `qwo(x1+0x1FF8)`;
- request range R4..R18;
- branch is additionally gated by `dwo(x1+8) == 0x60800`.

Return breakpoints at the two call-return addresses capture only the contemporaneous family-2 SRC/DST/COEF result.

## Private per-request capture

At solver entry:

- `TUNE`: x0, 0x170 bytes;
- `RUNTIME`: x1, 0x498 bytes;
- `DESC`: x2, 0x88 bytes;
- `HIST`: `poi(x2+0x10)`, 0x1000 bytes, the 1024-float preprocessed histogram;
- family-2 pre-state through descriptor pointers: `PRE_SRC` 28 bytes, `PRE_DST` 28 bytes, `PRE_COEF` 60 bytes;
- optional pointed input slices: `COMMON` 0x80 bytes, `CTRL` 0x40 bytes, and `FACE` 0x40 bytes when non-null.

At solver return:

- `POST_SRC`: 28 bytes;
- `POST_DST`: 28 bytes;
- `POST_COEF`: 60 bytes.

Raw values remain private and are excluded by `.gitignore`.

## Streaming discipline

`holder.ps1` is mechanically inherited from the accepted E007j rear 4K holder, renamed to E007L. It initializes the unique Surface Camera Rear / Color / VideoRecord / NV12 3840x2160 source, creates the reader, then waits at `E007L-READY` for `E007L-START.GO`. No optical pixel buffer is copied.

The experiment is single-use through `SCRIPT-ENTRY-CONSUMED.marker`.

## Acceptance intent

After return to Golden Linux, mount Windows read-only and port/emulate only the TMC141 family-2 solver path. Acceptance requires exact reproduction of `POST_SRC`, `POST_DST`, and the already-source-locked derived `POST_COEF` across R4..R18.

Captured-state/request-number replay is not an acceptable producer.
