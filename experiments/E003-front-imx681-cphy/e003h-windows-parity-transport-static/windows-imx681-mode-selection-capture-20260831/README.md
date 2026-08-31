# E003h same-machine Windows IMX681 selected-resolution capture — 2026-08-31

This checkpoint resolves the six-mode ambiguity introduced by the corrected current Windows IMX681 firmware parse. It is a Windows-only observation on the same Surface Pro 11; it authorizes no Linux camera runtime by itself.

## Capture

The SP11 was returned to protected FullIO v19c Golden after consumed 0053, then booted once through the existing direct Microsoft firmware entry (`BootNext=0006`) while the persistent boot order remained unchanged. SP7 KD used the exact installed `surfacecamfrontsensor8380.sys` (SHA-256 `80a8e4a1ef8f0dacfbc2e8c6919cb269993057ffd3133c2ef7016ff742e46f03`).

Static reversal had already established that the normal selected-resolution executor receives an archived packet descriptor and that each register pair is encoded as an 8-byte record. A breakpoint at `surfacecamfrontsensor8380.sys +0x54c4`, immediately before the selected resolution packet is applied, dumped that descriptor and packet during one stock Windows Camera start. SensorCrop-only callsites at `+0x5520/+0x57a0/+0x68c4` were also armed but did not fire in this start.

Raw KD log: `E003H_IMX681_MODE_SELECTION_20260831.log`, 16,162 bytes, UTF-16LE, SHA-256 `341df7c5cf0d80456d9d74242878bb4561911a37d76d288e74b2a489ae2ed0ec`. The log was closed with `.logclose` before Windows rebooted normally back to Golden Linux.

## Result

The one real selected-resolution event has descriptor length `0x228` (552 bytes): an 8-byte packet header plus exactly 68 8-byte address/value entries. The deterministic extractor reconstructs all 68 pairs and compares the sequence against all six resolution records in the exact current Windows sensor blob SHA-256 `f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c`.

There is exactly one full-sequence match: **resolution index 2, 3840x2160 @ 30 fps**. In particular, both `0x034c..0x034f` and `0x040c..0x040f` are `0f 00 08 70`, so the sensor output/digital-crop size is 3840x2160 before CSID.

Therefore the earlier Linux diagnosis "a 3840x2640 input reaches CSID and Windows must crop it vertically to 2160" is superseded. Linux's bounded runs programmed firmware resolution index 0 (3840x2640@30), while Windows selected index 2. The Linux 3840x2640 completed-frame measurement is now explained first by the sensor-mode mismatch; no additional CSID crop-register write is justified.

## Next gate

Derive Linux's exact mode2 register table from the same firmware record and inspect the delta against current mode0. Only after a static, hash-pinned mode2 parity candidate is public should a distinct bounded one-shot runtime be considered.
