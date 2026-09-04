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
- complete active mesh→32×24 interpolation parent (`0xc9e590`).

Once `0xc9e590` is substituted, the native `0xc9c4b0` and `0xc9e398` bodies are no longer reached on the validated front path. `ACTIVE-PATH.json` records the remaining native solver/state boundary and observed call counts.

This remains an **offline differential proof**. DeviceMFT is still required for the unported solver/final-application stages. No Linux camera runtime, module load, STREAMON, sensor operation, or MMIO is performed by this checkpoint.
