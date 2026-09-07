# E003i BJ — clean-room AEC log1.03 coordinate

Status: **PASS — target-SP11 Linux clean-room C is bit-exact against the pinned Windows ARM64 math path on 30,566 deterministic cases.**

BI proved that Algorithm001's F−3 baseline is the S1 convergence-derived exposure coordinate. BJ closes the remaining arithmetic precision gate for producing that coordinate on Linux.

## Exact Windows arithmetic

The Windows coordinate producer is:

1. `float ratio = (float)linearExposure / (float)37516`;
2. evaluate the pinned DLL's double **log10** helper at `0x180cc2e98`;
3. multiply by the float32 scale initialized as `1.0f / log10f(1.03f)`;
4. narrow to float32.

Offline Unicorn execution of the pinned DLL recovers:

- `1.03f` bits: `0x3f83d70a`;
- `log10f(1.03f)` bits: `0x3c52532c`;
- reciprocal scale bits: `0x429bcc0c` = `77.89852905273438`.

This also explains the constant already observed in Algorithm001: its luma correction uses the same base-1.03 coordinate scale.

## Clean-room Linux primitive

`native-log103.c` uses only standard `log10(double)` plus the exact proven float32 boundaries and scale. It contains no copied Windows tables or proprietary code.

The verifier compiles it on the SP11 Linux target with:

```sh
gcc -shared -fPIC -O2 -fno-fast-math native-log103.c -lm
```

and differentially checks it against offline Unicorn execution of the exact pinned Windows ARM64 helper sequence.

Corpus: **30,566 / 30,566 bit-exact**, including zero, a dense low range, a dense neighborhood around the T681 base, ±2 around many `1.03^k` boundaries, AB2, large 64-bit values, and 20,000 seeded random `uint64_t` exposures.

The prior AB2 live pair also closes exactly:

`33,312,451 -> 0x4365acdd (229.6752471923828)`.

## Scope

The differential result is for the actual SP11 Linux toolchain/libm and the active T681 base `37,516`. If the target libc/compiler architecture changes, rerun this verifier before treating bit parity as inherited.

No camera stream, sensor, module, MMIO, or Windows boot is used. The proprietary DLL is referenced only as a pinned local oracle and is not committed.
