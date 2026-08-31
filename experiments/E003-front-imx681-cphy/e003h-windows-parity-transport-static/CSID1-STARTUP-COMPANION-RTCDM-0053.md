# E003h 0053 — startup CSID companion RT-CDM transport parity

0052 proved a real X1E CSID clock-selection defect and fixed HBI exactly, but the 3840x2640 completed-frame / `ERROR_LINE_COUNT` crop failure remained unchanged. The follow-on static latch audit closed the obvious register-value theories: Windows/Linux IPP crop coordinates, CFG0/CFG1 crop enable, CTRL, RUP/AUP ordering, BIN-PD ownership and visible LUT-bank programming are already matched or non-causal.

A distinct transport/ownership mismatch remained. Same-machine Windows `0x803` descriptor-1 data is a CSID1 CDM companion list submitted through RT-CDM after `CHANGE_BASE 0x00057000`. The fail-closed 0053 oracle reconstructs those bytes exactly: packet0 is 60 bytes SHA-256 `1872731eaa3eb2233436029c2658682097c61ebf97e3facf46e31224ee25e2a2`; packets1..3 are 16 bytes each SHA-256 `45d059ec64587ea4f55eb8df64704520782801418c4a754f512831c7473fb5c7`. Linux 0052 instead sent only VFE base/main through RT-CDM and then replayed the same CSID companion values with CPU MMIO.

0053 changes transport only. Each startup packet now submits `CHANGE_BASE(VFE1) -> IFE main -> CHANGE_BASE(CSID1) -> exact descriptor-1 companion` through the existing RT-CDM FIFO0 commit path. The four runner calls to `csid680_x1e_front_ipp_companion()` are removed. No new MMIO read/write, register value, crop coordinate, RUP/AUP value, VFE setting, CSIPHY setting or sensor setting is introduced.

The static delta is intentionally not called causal. Correct CPU readback with wrong completed-frame behavior is consistent with an ownership/latch hypothesis, but only a bounded differential can test that.

- transport oracle SHA-256: `4b70a61a2e226b37d9310b4b4dee4d77c7516f975498973ee89dc29d772e2e5c`
- oracle extractor SHA-256: `3dfe96a9b900e98e4ee93168df65eb2db0fbea1d180a85ddc7239a85f6d76d68`
- patch SHA-256: `dba1d21fdc01f4091af89ce051283464661952ce2d1acd1f59afb75c8b52cfd6`
- 0052 baseline `camss.c`: `5a920032e138eee1154c4b9ae1846a445e02fbac3e7626a4245797502e73b793`
- 0053 `camss.c`: `b8cb256514337f1767ba5dab002cc59ff4f0c8f73f9be03f83de77ab8b3507c9`
- qcom-camss.ko: `f04189d766f478083e09fd38b26e73c99c03306ce1f2fb81d68b2ebd0d2be876`
- inspector SHA-256: `ebd637308986670ea6f24a1933aee75ecc7c87ff692f62e87ad92f0ca1afaab2`
- accepted inspection SHA-256: `72ceb0880f673bc1d17698eb228612a88b8bf4683b8f034a9de4f1b784120fea`
- strict checkpatch: 0 errors, 0 warnings, 0 checks
- module vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

**Runtime is not authorized.** Next gate: publish this static checkpoint, then construct and independently inspect a distinct unarmed 0053 one-shot package. Hardware execution requires a separate fresh authorization checkpoint.
