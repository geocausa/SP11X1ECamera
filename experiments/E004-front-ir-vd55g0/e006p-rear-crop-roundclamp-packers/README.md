# E006p — Titan680 Crop12 + RoundClamp12 clean packers

Parent Git: `f0d28457` (E006o 468-register singleton provider PASS).

Status: **STAGED / COMPILE-ONLY**.

## Goal

Implement 78 of the 184 startup-only register values from semantic Linux-owned state instead of captured Windows words:

- Crop12: 12 registers
- RoundClamp12: 66 registers

These cover the Video Full, DS4 and DS16 luma/chroma paths.

## Source-lock

Pinned Surface DeviceMFT source strings/decompilation identify:

- `IFECrop12Titan680::CreateCmdList`
  - Full: 0x9C68/6C + 0x9E68/6C
  - DS4: 0xA468/6C + 0xA668/6C
  - DS16: 0xAC68/6C + 0xAE68/6C
- `IFERoundClamp12Titan680::CreateCmdList`
  - corresponding 0x..60 config + ten-word 0x..70..94 blocks.

The older CamX reference tree supplies the semantic state names (`CropInfo`, output dimensions/format), while the pinned Titan680 binary supplies the exact current-generation bit packing.

Crop12 packs:
- firstLine/lastLine into the first register;
- firstPixel/lastPixel into the second;
- each coordinate is 14-bit.

RoundClamp12 depends on:
- output bit width (8/10/14);
- per-path enable state;
and deterministically emits clamp max, round-off count, rounding pattern and luma/chroma interleave state.

## Private validation

The retained E006a startup packets were decoded **locally on SP7**. Only safe semantic facts were exported.

Both startup0 and startup1 agree:

- Full luma 3840x2160, chroma 1920x1080, origin 0,0
- DS4 luma 960x540, chroma 480x270, origin 0,0
- DS16 luma 240x136, chroma 120x68, origin 0,0
- each RoundClamp block has exactly one matching source-defined candidate:
  - bit width = 10
  - path enabled = true

Startup2/3 omit these modules entirely.

No raw register values or command bytes are committed.

## Contract

The C implementation accepts semantic crop rectangles plus bit-width/enable inputs. It does **not** hardcode captured Windows register words. The functions are retained only for compiler/type checking against E006m's callback signature.

Passing compilation closes packing/implementation for these 78 register addresses; upstream production of the semantic geometry state remains a separate Linux integration task.

Native rear Linux processed ISP remains **DENIED**.

## Build result — PASS

The single isolated E006p build passed after re-verifying E006g/j/l/m/o/p.

- implemented startup-only addresses: 78
  - Crop12: 12
  - RoundClamp12: 66
- private semantic validation: startup0/startup1 exact
- W=1: zero warnings/errors
- qcom-camss.ko: 13,586,400 bytes
- SHA-256: 875e3bc64e67f5d508e7488a92d28162daabe7c56457fc672fbbdcc4ec386472
- vermagic: exact Golden
- Crop12 and RoundClamp12 provider symbols retained

No install/load/camera/RT-CDM/MMIO/boot action occurred.

Status: **COMPILE-ONLY PASS**.
