# E003h RT-CDM startup dynamic ownership — static/unreachable

Date: 2026-08-29

## Correction to the 0019 boundary

`0019` deliberately treated 20 command words as caller-supplied because five VFE1 register identities were known to be live-volatile and `period_cfg +0x8c` differed between independent Windows startup captures. The new same-machine oracle separates **startup command ownership** from **post-start live register behavior**.

The result is narrower:

- 46 DMI address words remain Linux-rewritten holes;
- only four `period_cfg +0x8c` words remain start-dependent caller inputs, one per startup packet;
- the other 16 words (`+0x3b70` and `+0x3d78/+0x3d7c/+0x3d80/+0x3d84` where present) remain exact caller-provided startup-template data.

This is not permission to freeze the latter as live-state constants. `+0x3d78..+0x3d84` visibly mutate while Windows is streaming; `+0x3b70` stayed stable only during the bounded samples.

## Windows proof

The hash-pinned `E003H_VFE1_DYNFIELD_KMD_PASS_20260829.log` proves all captured fields are byte-for-byte unchanged across `qccamisp8380+0x26838` for packets 0..3. They therefore arrive at that KMD processor already populated.

The bounded live cadence proves:

- live `+0x8c` reads `0` in all three samples after startup;
- live `+0x3b70` remains `0x04270427` in those samples;
- live `+0x3d78..+0x3d84` change between samples.

Independent startup command captures, however, carry identical values for all 16 non-period words. After zeroing only the 46 DMI addresses and four period words, the independent command streams are byte-identical. Refined normalized packet SHA-256 values are:

- packet 0: `8c9ee558869a05fa6a5fe36f8c6266af8e7b7ce12db135ef4747c0b606124e6b`;
- packet 1: `59ff6ba89a82963cea5384c012764f1dec3e56f7a93f7eb4f4fac9ad6be2e963`;
- packet 2: `05bec5f3b39d953f19fd55a6a826973e74a312bf6ac6b1afd359b67b00dc8da8`;
- packet 3: `807d3cdb8053a7d56b0bf78effa01f42947572b385643e0866473712990980f8`.

Extractor SHA-256: `4309c598eed431cb6d0e83461ce4cf917195ec90a6fd1c9123487a3d76f113e3`.
Oracle SHA-256: `402510679bae860f801166bd7ff36834ca8284650aa29d64f1c08d7c6afda856`.

## Refined static materialization

`materialize_rtcdm_startup_owned.py` reconstructs both independent Windows variants using Linux-owned synthetic DMI addresses. It patches only 46 DMI addresses and four period values while retaining the 16 invariant startup words directly from the normalized templates. Both variants decode to exactly 278 commands, 2,131 ordinary register writes and 46 DMI commands.

Static materializer SHA-256: `e01c89af6b0c7c02b18a1c64f2e4caaa3ba30a59518d0400de05d09866953b4e`.
Static proof SHA-256: `65f614dd40ede7dd96136f9a926c5dce960039d24983b5b559b93c7d09099043`.

## Linux `0020`

`0020-x1e-rtcdm-startup-dynamic-ownership-unreachable.patch` is a refinement on top of `0019`; it does not rewrite project history. The private materializer now requires `CAMSS_RTCDM1_CORPUS_DYNAMIC_COUNT=4` and `dynamic_valid=GENMASK(3,0)`. Its dynamic table contains only the four packet-local `+0x8c` value fields.

The 16 invariant startup words are neither embedded by `0020` nor patched by the kernel helper; they must already be present in the exact caller-provided normalized template. The patch introduces no MMIO, IRQ, FIFO commit, VFE op or stream call and leaves VFE1 PIX rejected before stream setup.

Patch SHA-256: `147b89961803f3812c10dfd6f89cc00a4273d077514fc39756e5eb78f2d2d86e`.
Inspector SHA-256: `2733ca50e2d396c796f2e2d356bd87830ae71eaa337a81e8ac2004e83d32d427`.
Inspection JSON SHA-256: `a589a5546342bb9ad127bc6b5b880071cb1be35bdc8327524b7e521eb48f4add`.
Built module SHA-256: `ccafdf9e94ec6e5e1609bb5e36ec8c1f6bb97055d8e6a4ce80a09c3cecd73d2f` with exact Golden vermagic and zero compiler diagnostics.

Forward/reverse patch reconstruction passes. Strict checkpatch reports zero code/style checks; only raw-mail-patch metadata is absent. The module was not loaded and no camera runtime occurred.

## Remaining boundary

`period_cfg +0x8c` remains genuinely start-dependent and upstream-owned. Fresh Windows starts produce different values, with packets 1/2/3 sharing one value within a start while packet 0 uses another; its exact producer/value rule is not yet closed. Separately, the post-start meaning/update ownership of `+0x3b70/+0x3d78..+0x3d84` remains a runtime-orchestration question, not a command-materializer input question.

Do not submit RT-CDM FIFO0, enable VFE1 PIX, transmit IMX681 or attempt a Linux front frame yet.
