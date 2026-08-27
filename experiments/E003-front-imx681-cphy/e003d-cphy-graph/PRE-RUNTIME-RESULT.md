# E003d pre-runtime result

Status: **READY FOR ONE-SHOT / runtime not yet performed**.

## Windows-derived electrical table

- Exact Windows X1E C-PHY table boundary: 121 ordered records from local `qccammipicsi8380.sys` raw offset `0xf650`.
- 118 unique final register offsets match both independent KD live snapshots exactly.
- Linux translation preserves ordered writes, zero writes, duplicate writes and the three proven delays (10 ms / 1 ms / 10 ms).
- One-trio lane mask is `0x02`, matching Windows live common CTRL5.
- Windows live/common CTRL7 is `0x7a`; X1E C-PHY Linux path carries `0x7a` while D-PHY retains the accepted `0x02` behavior.

## Build and ABI gates

The broad exact-Golden `make modules` pass completed successfully. The wrapper's final exit status 2 came only from an initially misspelled DT target (`x1e...dtb` instead of `qcom/x1e...dtb`); there were no CAMSS/compiler/MODPOST errors. The corrected DT target then built successfully.

- candidate `qcom-camss.ko` SHA-256: `04e92a3ea8b9075f6d5ffa43856276595b0bb2b47877ce43b3987c08c4a41e91`;
- candidate CAMSS srcversion: `446A14F6FC085EC7F4C542F`;
- exact Golden vermagic: PASS;
- imported symbol CRCs: 140 checked / 0 mismatches;
- `E003D_CAMSS_ABI=PASS`.

## DT gate

Baseline is accepted E003c DTB SHA-256 `a698603969880be9ac986e543fe0c772a75551cfd0d1d27422fd84375e48da9b`.

Candidate E003d DTB SHA-256:
`9e5eab025ed4dc0d23983f0e0ab0b84ca6095826f5a9b4f57fb1c6b9b3e50d79`

Phandle-aware semantic verification reports:
- exactly 4 intended new graph nodes;
- 415 changed properties in the raw decompile;
- 404 are phandle-renumber-only;
- 0 unexpected nodes;
- 0 unexpected properties;
- reciprocal IMX681 ↔ CSIPHY2 C-PHY endpoints;
- exactly one zero-based trio (`data-lanes = <0>`);
- no `link-frequencies` property introduced;
- `E003D_DT_SCOPE=PASS`.

## Reproducible initrd gate

Base is accepted R3 initrd SHA-256:
`dfcc8a0d53391b80ef418ff7b3c40df2ccbc0d8aeb43ffe6a8e7abb5aabf7e15`

Two independent E003d builds are byte-identical:
`f44bda2c835985cae5ca77a50bc986567c606b08a4e225bff96c6bcfa07b2bdd`

The semantic initrd delta is exactly 10 entries: the E003d module directory, candidate `qcom-camss`, accepted bind-only `imx681`, `v4l2-cci`, four videobuf2 dependency modules, the E003d init-top hook and `ORDER` update.

`E003D_INITRD_REPRODUCIBLE=PASS`.

## Runtime safety boundary

E003d adds only the idle graph/receiver capability. The accepted IMX681 driver still contains no sensor write path and `.s_stream(1)` remains hard-blocked with `-EOPNOTSUPP`. No link-frequency is asserted. The C-PHY electrical table is therefore present in CAMSS but must remain unexecuted during this gate.

No E003d boot had been installed or armed when this pre-runtime checkpoint was written.
