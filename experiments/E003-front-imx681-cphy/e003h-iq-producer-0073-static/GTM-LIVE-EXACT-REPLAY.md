# E003h 0073 — exact live GTM producer replay

Status: **accepted live-capture/offline-replay checkpoint**. The Windows capture was read-only producer observation; the replay itself runs entirely offline on SP11 Linux. No Linux camera runtime, MMIO, sensor operation, or Linux request6 submission is performed or authorized by this checkpoint.

## Result

The generation-5 Surface GTM producer transform is now reproduced byte-for-byte for an independent Windows request4/5/6 producer session. The proof maps the SHA-pinned ARM64 `QcDeviceMFT8380.dll` into Unicorn and executes the exact Surface mode-2 cubic mapper (`0x9a4f38`), TMC-domain mapper (`0x9a55c8`) and final adaptive mapper (`0x9aa3a8`). It then reproduces the hardware-version-specific GTM131 setting loop and Titan680 64-bit LUT packing.

| request | exact GTM qwords | replay/oracle SHA-256 |
|---|---:|---|
| 4 | **256/256** | `656d35c87e95b376f3d6b4eac7624c3387e1857100cf5529f5ae7e2a87ec7f43` |
| 5 | **256/256** | `9e54b3b16a6a146f9f1f448150a88a929c2ffe3cd4c8aa93e98e5498afb0216e` |
| 6 | **256/256** | `89bc45b890f6508912bad1b543c7f7ad56e20b6794fdc908455e9f47c967cf95` |

All three replays are exact 0x800-byte equality, not a metric/curve approximation.

## Exact target branch

- internal TMC generation: **5**;
- hardware version: **`0x60800`**;
- TMC valid: **1**;
- curve mode: **2**;
- GTM common strength: exact float **0.8500000238418579**;
- GTM common power: exact float **1.0**.

Within the previously bounded generation-5 TMC reads, request4→6 changes are confined to the source knots at `+0x5104`, target knots at `+0x5120`, and cubic coefficients at `+0x51b0`. The generation/hardware/valid header, mode and the two blend scalars remain invariant. Only the first `0x100` bytes of the large `+0x6228` tone-domain were captured; that prefix is zero. The uncaptured tail is **not required** for this replay because both blend scalars at `+0x109c/+0x10a0` are exactly zero. The proof deliberately fills the uncaptured tail with finite non-zero sentinel values and still obtains byte-for-byte Windows output, so it does not silently assume an all-zero tail.

## Geometry captured atomically

The same live requests close the LSC request-local geometry that was previously unresolved:

- sensor/full domain: **4048×3152**;
- output: **3840×2160**;
- crop offset: **x=104, y=496**;
- scale: **1**.

These values are invariant across requests 4, 5 and 6 and come from the exact LSC common input capture, not from a guessed sensor-mode rectangle.

## Stream identity guard

This 2026-09-02 producer capture is **not** the earlier matched-trigger request4/5/6 stream. Its trigger bytes differ, and `prove-gtm-live-exact-replay.py` fails closed if the sessions unexpectedly alias. Therefore this result closes the Surface **TMC→GTM wire transformation** and validates the capture/replay method, but it does not invent the missing internal TMC state for the older matched request6 oracle.

## Revised gate

The GTM transform itself is no longer an unresolved algorithm. For a fully atomic request6 parity capsule, use one Windows stream in which dynamic producer state and wire outputs are captured together. The remaining harder independent wire transform is LSC: same-device EEPROM calibration + exact geometry + sequential Tintless/ALSC/AWB-BG state must reproduce LSC0/LSC1; wire GIC then follows automatically from the proven LSC alias. Linux request6 remains forbidden until the chosen atomic Windows oracle is reproduced offline.

Proof artifacts: `prove-gtm-live-exact-replay.py` and `gtm-live-exact-replay-oracle.json`. Raw Windows `.bin` captures remain local/untracked.
