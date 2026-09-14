# E004dh — Windows `FUN_18001c3e8` tile structure

The root SWASF worker calls `FUN_18001c3e8` in **8-pixel horizontal tiles**.  Treating it as a whole-row function was the source of the earlier 17-row-looking scratch overrun; direct left/right tile oracles close the actual contract.

For each pixel in the tile Windows first computes a five-point cross median over the raw 16-bit image:

```
               U
F(x,y) = median(L, C, R, U, D)
               D
```

with coordinate clamping at image boundaries.  `verify_c3e8_cross5.py` compares this formula against the shipping Windows function for both 8-pixel tiles of a 16×16 image across constant, positive/negative impulse, horizontal/vertical step, checkerboard and deterministic random inputs.  The result is **1792/1792 exact filtered pixels**, covering left/right/top/bottom edge handling.

The Ghidra min/max network at `FUN_18001c3e8` lines corresponding to `NEON_uminp/umaxp` is therefore a vectorized median-of-five cross, not a 3×3 median.  The checkerboard oracle is particularly discriminating: a 3×3 median and the cross median return opposite answers, and Windows follows the cross median exactly.

The cross-median value becomes the two `tail` samples consumed by the already-closed `FUN_18001c230`.  The remaining C3E8 arithmetic is therefore:

1. build a clamped 7×8 raw neighborhood for each two output pixels;
2. use `F(x,y), F(x+1,y)` as the C230 tail pair;
3. emit two signed 32-bit high-pass/intermediate values and two byte low-pass/control values.

`scaffold/sp11-swasf-c3e8.c` encodes that scalar form.  Together with the exact C230 implementation it builds as a freestanding Hexagon-v73 relocatable with zero unresolved symbols (`1776` bytes `.text`).  A direct Windows whole-tile random differential is staged next; until that passes, `c3e8_intermediate_filter_exact` remains false.
