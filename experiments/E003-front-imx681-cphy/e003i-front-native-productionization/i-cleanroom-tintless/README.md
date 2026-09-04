# E003i-I — clean-room Tintless substitution

This checkpoint starts replacing the embedded Surface Tintless implementation itself rather than merely replaying it.

The proof runs the accepted sequential front R4→R5→R6 Tintless replay, but hooks exact ARM64 helper entrypoints and returns from them after executing independent Python implementations. The native helper bodies therefore do not execute. Final descriptor-addressed output and LSC0/LSC1/GIC must remain byte-for-byte identical to the accepted Windows authority.

Closed clean-room stages:

- raw 32×24 Tintless BG statistics preprocessing (`0xc9f438`);
- edge-replicated 3×3 integer smoothing (`0xc9bb48`);
- 32×24 float accumulation (`0xc9f078`);
- natural-log float field transform (`0xc9ebc8`), using the platform `logf` primitive; synthetic differential testing was bit-exact against Surface;
- float→Q16 integer quantizer (`0xc97f40`), independently differential-tested;
- linear-extrapolation mesh padding (`0xc9c4b0`);
- Catmull–Rom row kernel (`0xc9e398`);
- complete active mesh→32×24 interpolation parent (`0xc9e590`);
- radix-2 complex FFT and matrix-transpose leaves (`0xca1d98`, `0xca1ed0`);
- complete 64×32 forward and inverse 2-D FFT parents (`0xca1fb0`, `0xca2310`), including exact inverse `1/2048` scaling;
- exponential Q16 postprocess (`0xc9ed88`);
- correction-map→mesh stage (`0xc9c868`), including exact 29×37 persistent core-state writeback and Surface corner extrapolation;
- solver state re-layout (`0xc9a288`);
- periodic forward gradients (`0xc98270`);
- active mode-2 complex spectral threshold (`0xc989d0`);
- periodic zero-mean projection (`0xc998b8`), including Surface's mixed NEON-reciprocal/scalar-FDIV row rounding;
- periodic divergence / gradient adjoint (`0xc99130`).

Once the interpolation and 2-D FFT parents are substituted, their native pad/bicubic/FFT/transpose leaves are no longer reached on the validated front path. The `0xc9c868` substitution is differential-exact for both all 221 output floats and every persistent core-state byte it mutates. `ACTIVE-PATH.json` records the remaining native solver/state boundary and observed call counts.

This remains an **offline differential proof**. DeviceMFT is still required for the unported solver/final-application stages. No Linux camera runtime, module load, STREAMON, sensor operation, or MMIO is performed by this checkpoint.
