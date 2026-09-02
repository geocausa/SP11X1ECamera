# E003h 0073 — exact live LSC staging → Titan680 wire target

Status: **accepted live-capture/offline-packing checkpoint**. The source staging bytes were captured read-only from the native Windows producer session. All packing and validation here are offline. No Linux camera runtime or Linux request6 is performed or authorized.

## What is closed

The Windows 2026-09-02 producer session already captured `IFELSC411`'s exact **0x18a0-byte post-calculation staging object** at `module+0xac` for requests 4, 5 and 6. The remaining question between that object and the DMI wire payload does not require another Windows run: the exact SHA-pinned Surface `QcDeviceMFT8380.dll` contains `IFELSC411Titan680::PackIQRegisterSetting` at RVA **`0xb3d8a0`**.

The exact ARM64 loop reads the active bank from staging `+0x08`, adds two to the stored mesh dimensions at `+0x14/+0x18`, and emits 13×17 = **221 dwords** to each of three LSC DMI destinations. The proof asserts the raw ARM64 instruction bytes for the loop rather than relying on decompiler pointer types.

For LSC0 and LSC1, the packer combines two 14-bit fields into each dword. LSC2 uses a 12-bit low field plus an 18-bit high field; importantly, the high source is a **32-bit scaled-by-4 load**. Keeping that address expression literal avoids a mixed-pointer-unit error that would be easy to introduce from decompiled pseudocode.

## Same-stream wire targets

The resulting 0x374-byte targets are deterministic from the captured staging:

| Request | bank | LSC0 SHA256 | LSC1 SHA256 | LSC2 |
|---|---:|---|---|---|
| 4 | 1 | `d4a4a75ffe930e2af7186ab17a083e37de40e520b69db29cb798587774ced6f5` | `f8d98429561f31e6fbbe351d320589192563673fae7c22d5646da723e0abeb43` | all zero |
| 5 | 0 | `e058fb6950db8b0f352c0feca2f38431f2d64ac51534a1703ee53b20707de6a2` | `dc91ab40eca8ebe115341cd7b3bd2150251675f0ce23997484b47a42bb40f4af` | all zero |
| 6 | 1 | `db9f60b5ffc8945c2b4772a3b0c0c7cad685408c2c3ee5c56f2f6e64f7421420` | `52e3c4f0eb5c3cff0b45d097a5bede4f6c58fc03e446d8c4a3ea5ecaea545c27` | all zero |

LSC2 is byte-identical zero for all three requests, with SHA256 `6ca83adefc47fc9ab71637c150b95b33083e61e507dff2ee5f2692aa27e1453e`.

The previously proven Surface GIC wire anomaly follows automatically. GIC reads source bytes `0x62e..0x82e`, which relative to `LSC0 || LSC1` are `[0x22e:0x42e]`. The derived 512-byte GIC alias hashes are:

- request4: `a0eafa31899484f9f584e9432ab3188407d4f4f6f53f6cd85c1331e1fd57caaa`
- request5: `5309035131e7d2e0c1622ddbd2c506ab4bf81db9702a56a827c786b84730d31e`
- request6: `04c5a085d18362fc0b0dae0c6d2b62fb64447ff6242b2926f65ad0ac4be6c028`

These are targets for this **independent live producer stream**, not the older matched-trigger request5/6 oracle. They must not be mixed with producer state from another stream.

## Remaining LSC gate

This closes **post-calculation staging → LSC0/LSC1/LSC2 → wire GIC alias**. It does not claim that the upstream LSC producer has been reconstructed yet.

The remaining hard transform is now earlier and narrower:

`same-device calibration/config + exact 4048×3152/(104,496)→3840×2160 geometry + sequential validated Tintless config/stats/state → captured 0x18a0 LSC staging`.

Once an offline producer reproduces that staging byte-for-byte for one atomic Windows stream, LSC0/LSC1 and wire GIC parity follow deterministically from this closed packer. GTM is already independently byte-exact. Linux request6 remains blocked until the full atomic offline producer comparison passes.

Proof artifacts: `prove-lsc-live-staging-pack.py` and `lsc-live-staging-pack-oracle.json`. Raw Windows capture bytes remain local/untracked.
