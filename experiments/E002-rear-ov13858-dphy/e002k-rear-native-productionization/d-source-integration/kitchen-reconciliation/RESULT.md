# E002k-D Kitchen reconciliation result

Date: 2026-08-27

Status: **PASS — source/DT reconciliation only; no runtime mutation**

## Portable replay

The maintained series was replayed from the exact Golden replay filesystem source, not from the already-modified camera tree.

All five source patches now use portable `a/...` / `b/...` paths and apply with GNU `patch --fuzz=0 -p1`:

1. `0001-media-ov13858-surface-profile.patch`
2. `0002-arm64-dts-qcom-hamoa-add-x1e-camera-infrastructure.patch`
3. `0003-arm64-dts-qcom-denali-add-rear-ov13858.patch`
4. `0004-sp11-preserve-phase91-touch-transport.patch`
5. `0005-sp11-preserve-fullio-v19c-tx-dmic.patch`

After 0001..0003, the three touched files are byte-identical to the existing isolated camera source. This proves the portable replay did not silently reconstruct a different camera implementation.

## Reconciled DT compile

Source replay:

`/home/geoca/Documents/SP11-PROJECT/02-kernel/sp11-camera-e002k-d-kitchen-src`

DT-only build:

`/home/geoca/Documents/SP11-PROJECT/02-kernel/e002k-d-kitchen-dtb-build`

Target:

`qcom/x1e80100-microsoft-denali-oled.dtb`

Result: **PASS**, with no warning/error emitted by the kernel DT make invocation.

Reconciled DTB SHA-256:

`8cb5783fed2711758763aa81dc2f28c9f348259830ad6f57ffa18a6c5fd0d553`

Pre-Kitchen camera-only maintained DTB SHA-256:

`a8efe69044a8860ac4dc50d4a01b612f2925dc7648ec2e699b1412fa74f3c2f2`

Deployed Golden FullIO v19c DTB SHA-256:

`2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`

## Mechanical semantic oracle

`verify-v19c-kitchen.py` first re-checks the historical maintained-Golden-source → deployed-v19c gap:

- changed nodes: 6
- changed properties: 26
- unexpected nodes: 0
- unexpected properties: 0
- changed sorted-DTS lines: exactly 44

It then compares camera-before-Kitchen → camera-after-Kitchen. Adding the labelled QSPI pin state changes FDT phandle allocation, so the raw decompile contains 1,235 downstream property-number changes. The verifier resolves changed phandle cells back to their target node paths before judging semantics:

- changed nodes: 6
- raw changed properties: 1261
- phandle-renumber-only properties: 1235
- unexpected nodes after canonicalization: 0
- unexpected properties after canonicalization: 0

Finally it resolves the post-Kitchen phandles from `__symbols__` and requires the actual compiled DTB to reproduce the deployed v19c semantics for:

- GPI DMA1 enabled;
- QSPI GSI-DMA + BIOSREF mode;
- QSPI DMA tuples and three-state pinctrl tuple;
- GPIO49/50 QSPI data lanes;
- MSHW0485 transport/IRQ/power/reset properties;
- FullIO v19c sound-card model;
- TX DMIC0/1 routes;
- `TX DMIC Capture` codec/CPU/platform DAI chain using maintained labels.

Result:

`NONCAMERA_V19C_RECONCILIATION=PASS`

## Safety

Nothing in this reconciliation was copied to `/boot`, no GRUB entry was changed, and Golden was not rebooted. The independent full kernel/modules build must still complete and pass Image/Module.symvers/module-ABI inspection before an integrated one-shot candidate may be packaged.
