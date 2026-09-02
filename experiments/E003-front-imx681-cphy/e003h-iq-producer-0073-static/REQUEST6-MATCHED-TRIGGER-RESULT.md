# E003h 0073 — matched Windows request6 trigger oracle

Status: **accepted offline/oracle checkpoint**. No Linux request6 runtime has been executed or authorized.

## Closed in one Windows camera stream

The initial/precompute FrameServer phase was traced from DeviceMFT IQ trigger production through qccamisp steady packet emission. Requests 4, 5 and 6 each emitted the 0x958 / 14-DMI steady shape.

The matched request6 artifacts are:

- main 0x958 SHA256 `2277aebae7559227b0ce745b7d73b464b57b4b5e62baf8033940ee7f7180e4b4`
- DMI slot SHA256 `ff5f0f04bee8491c76451838743a28e3793ee5d2a0ecbff8f6589dca5c92f955`
- producer log SHA256 `a6fab1472792828c00144b372d69f1a10386cc278ff2aa1e04808520c6b25522`

The exact matched request6 trigger vector is:

- exposureTime = 1.0
- exposureGainRatio = 1.0
- AECSensitivity = 1.0
- realGain = 43.2984619140625
- luxIndex = 374.19293212890625
- AWB green = 1.0
- AWB blue = 1.936495065689087
- AWB red = 1.7811671495437622
- CCT = 4999.0
- DRC gain = 1.0
- lensPosition = 0.0
- blackLevel = 6528

From request5 to request6, only `realGain` and `luxIndex` changed in the captured common trigger vector. AWB B/R gains had changed from request4 to request5 and then remained stable through request6.

## Producer boundary

`IQSetupTriggerData` is at DeviceMFT RVA `0x88a4e8`. Four stable callers repeat per steady request at return RVAs `0x7f441c`, `0x7befc8`, `0x746e70`, `0x7580d0`; calls 3 and 4 operate on the same IFE moduleInput object. The completed trigger block is `moduleInput + 0x2080`.

## Offline Linux capsule

The matched request6 Windows bytes can be normalized/materialized by the existing Linux capsule builder. The local/untracked matched capsule is 41,088 bytes with SHA256 `68495ceb22b1bc5c9e2a69a685d733c8671413c08bd355b594f969884999ddb0`. Its hash-only manifest is committed; proprietary oracle bytes and capsule remain local/untracked.

## Adaptive producer boundary

Subsequent exact-binary work closes an important ambiguity: the remaining LSC/GTM problem is **not** just missing AEC/AWB trigger labels. LSC41 and GTM13 stay in the same relevant Chromatix trigger zones across the matched request5/request6 trigger vectors, while the exact Surface implementation has additional adaptive producer state after base interpolation. LSC411 can consume sensor calibration plus Tintless/ALSC state; GTM131 can consume dynamic TMC state. See `ADAPTIVE-IQ-STATE-BOUNDARY.md` and `adaptive-iq-state-boundary-oracle.json`.

The static LSC calibration descriptor is now reduced further to one 221-point table sourced from exactly 0x6e8 physical EEPROM bytes at `0x103d..0x1724`; the exact runtime OTP table layout is also pinned. The adaptive LSC implementation is no longer opaque either: exact IFELSC411 constructs embedded Tintless/ALSC interfaces in DeviceMFT, Tintless retains a `0xdf0` previous-mesh history, and the 64x48 ALSC AWB-BG read is bounded to at most `0x54020` bytes. A separate output proof rejects all pure-Chromatix LSC channel orderings and proves the dynamic GTM path materially changes the flat base curve.

The exact GTM/TMC read boundary is now reduced too. The published TMC/ADRC state is a `0x8278`-byte object, but IFE GTM converts it to the internal layout and generation-5 GTM131 reads only bounded internal state. A later independent 2026-09-02 producer session goes further: exact Surface ARM64 replay reproduces all **256/256 GTM0 qwords** for requests4/5/6 on generation 5 / hardware `0x60800` / mode 2. That session is **not** this older matched-trigger stream, so it closes the transform without manufacturing the old stream's missing TMC state. See `GTM-LIVE-EXACT-REPLAY.md`.

## Next gate

Do not combine this older matched-trigger output with producer state captured from the independent 2026-09-02 stream. The new stream closes GTM transform behavior and exact LSC geometry, and proves its own active LSC branch is Tintless-only with a conditional **0x961e/0x12bec** request-local stats bound. The next clean parity target is one atomic Windows producer/output stream: preserve same-device calibration/config and sequential Tintless state/stats, reproduce LSC0/LSC1 byte-for-byte, reproduce GTM0 from that same stream (the transform is now independently validated), then derive wire GIC from the proven LSC alias. Linux request6 remains forbidden until that atomic offline comparison passes and a separate runtime authorization review succeeds.
