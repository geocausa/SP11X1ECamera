# E003i-J — clean-room GTM

This checkpoint removes proprietary DeviceMFT execution from the validated generation-5 / hardware-`0x60800` / mode-2 GTM transform used by the independent 2026-09-02 front producer capture.

Three native Surface helpers are replaced independently and differential-tested against the SHA-pinned Windows implementation:

- `0x9a4f38` — mode-2 cubic knot mapper: **257/257 float32 exact** for R4/R5/R6;
- `0x9a55c8` — TMC-domain mapper: **257/257 float32 exact** for R4/R5/R6. On this authority both TMC blend scalars are exactly zero and the exponent is exactly `1.0`, so the large tone-domain table is algebraically inactive;
- `0x9aa3a8` — final adaptive mapper: **257/257 float64 exact** for R4/R5/R6. With exact power `1.0`, the active coordinate reduces to `clamp(mode2_domain, 0, 1)` followed by Surface's weighted interpolation and non-increasing enforcement across entries 0..255.

The remaining static Titan x-grid is not an independent table: all 257 entries are reproduced exactly by `max(0, int(float32(float32(domain*16384)+0.5))-1)`. The only fixed GTM table retained is the 257-float mode-2 domain (`1028` bytes, SHA-256 `b33525b102690e0894d55245a0af56e655f10615fe6b144cbfca2cb9e5836325`).

`generate-cleanroom-gtm-wire.py` is a pure Python backend. It does **not** load DeviceMFT and does **not** use Unicorn. From captured internal TMC/module state it reproduces the complete Titan680 0x800-byte GTM payload exactly:

- R4 `656d35c87e95b376f3d6b4eac7624c3387e1857100cf5529f5ae7e2a87ec7f43`
- R5 `9e54b3b16a6a146f9f1f448150a88a929c2ffe3cd4c8aa93e98e5498afb0216e`
- R6 `89bc45b890f6508912bad1b543c7f7ad56e20b6794fdc908455e9f47c967cf95`

Captured `REQ*_GTM_OUT.bin` remains validation only. This live GTM session is deliberately distinct from the historical mixed 0076 compatibility state and must not be spliced into that regression.

The remaining production boundary is **live Linux TMC/ADRC request-state acquisition or construction**. GTM curve transformation and Titan680 LUT packing are no longer proprietary execution dependencies. No Linux camera runtime, module load, STREAMON, sensor operation, or MMIO is performed here.
