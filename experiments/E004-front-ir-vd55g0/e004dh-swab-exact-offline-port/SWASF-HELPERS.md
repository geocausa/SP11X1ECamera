# E004dh — Windows-authoritative SWASF helper kernels

The shipping Windows `QcISPTrustlet8380.dll` remains the authority.  This note records two internal SWASF kernels that have now been called directly in Windows with deterministic inputs and then transcribed to scalar C.  Ghidra/NEON decompilation is used only to explain the arithmetic that reproduces those Windows outputs.

## `FUN_18001b848` — local positive/negative extrema

The helper consumes five rows of eight signed 16-bit samples and emits four positive and four negative values.  For output lane `i=0..3`, Windows uses `row2[i+2]` as the center and scans the 5×5 neighborhood spanning rows `0..4`, columns `i..i+4`.

Let:

- `max_pos = max(max(sample-center,0))`
- `max_neg = max(max(center-sample,0))`

over that 5×5 window.  Windows then applies its `0x99/256` rounded gain:

`out = (max * 0x99 + 0x80) >> 8`.

The scalar implementation reproduces every direct Windows helper-oracle vector exactly.

## `FUN_18001c078` — 5×5 symmetric activity/curvature metric

A dedicated Windows basis oracle perturbed each input position by `+64` and `-64` around a constant center.  The exact response matrix is:

```
1   4   6   4   1
4  16  24  16   4
6  24  36  24   6
4  16  24  16   4
1   4   6   4   1
```

and columns 5..7 do not contribute.  This is the outer product `[1 4 6 4 1]^T [1 4 6 4 1]` after Windows' symmetric pair construction.

For center `C`, scale `S`, `cap=((S<<3)&0x7f8)`, and horizontal weights `h=[1,4,6,4,1]`, the exact scalar form matching the shipping helper is:

```
d0 = min(abs(row0[c] + row4[4-c] - 2*C), cap)
d1 = min(abs(row1[c] + row3[4-c] - 2*C), cap)
d2 = min(abs(row2[c] + row2[4-c] - 2*C), cap)
sum += h[c] * (2*d0 + 8*d1 + 6*d2)
output = min(255, (sum + 0x40) >> 7)
```

The direct Windows cases produce `0x0d`, `0x3d`, `0xff`, and `0x41`; the scalar code reproduces all four and every basis response exactly.

## Offline build

`scaffold/sp11-swasf-helpers.c` passes all Windows-derived vectors and builds freestanding for Hexagon v73:

- `.text = 896` bytes
- zero undefined symbols
- SHA-256 `5a66752efdbef37105d87c0e1fbc32a546fb9523d752c83b1e41921dc267b08d`

This closes two internal SWASF primitives, not the whole pixel transform.  `FUN_18001c3e8` and the final `FUN_18001cd90` combine remain outstanding.  `SP11_WORKER_ESWAB_PENDING` therefore remains fail-closed.
