# E007v — rear DSX101 clean provider

Parent Git: `4742df8c` (E007u BPC/ABF411 clean DMI PASS).

Status: **COMPILE-ONLY PASS**.

## Goal

Close the final first-native-frame DMI payload blocker: IFE DSX101 at the exact 4× rear downscale path.

The selected OV13858 DSX1.0 tuning contains one 2,824-byte semantic region (706 float coefficients). For the rear first-frame geometry the DSX NC library takes its fixed 4× branch; that branch bypasses generic runtime filter synthesis and directly packs four coefficient banks from the tuning authority.

## Source lock

Pinned rear tuning:

- module: `com.surface.tuned.rfc_ov13858`;
- SHA-256: `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`;
- root: `0x23`, `dsx10_ife_video_full_dc4_v2`, version 1.0;
- trigger: `0x263`;
- region: `0x265`, 2,824 bytes = 706 float32 values.

Pinned Surface implementation:

- `DSX101Setting::CalculateHWSetting`: `0x1809a5750`;
- `DSX_ProcessNcLib`: `0x180e4a6c0`;
- NC internal: `0x180e4a7b0`;
- fixed-4× luma pack helper: `0x180e47590`;
- fixed-4× chroma pack helper: `0x180e47410`;
- `IFEDSX101Titan680::PackIQRegisterSetting`: `0x180b52b90`;
- `IFEDSX101Titan680::CreateCmdList`: `0x180b52930`.

The common-setting stage converts the tuning floats with truncation toward zero. For exact 4× geometry, the NC core bypasses the generic filter generator and packs:

- 192 luma coefficients → 768-byte DMI table;
- second 192-coefficient luma bank → identical 768-byte table;
- 96 chroma coefficients → 384-byte DMI table;
- second 96-coefficient chroma bank → identical 384-byte table.

Both luma banks are semantically identical in the selected rear tuning; both chroma banks are also identical.

## Wire rule

Each 64-bit DMI entry packs overlapping signed 12-bit coefficient triples:

- bits 0..11: coefficient `2*i`;
- bits 12..23: coefficient `2*i+1`;
- bits 24..35: coefficient `2*i+2`;
- final entry carries only the final two coefficients.

Titan680 emits the contiguous 0x900-byte DSX DMI block as:

- `0xA008`, selector 1: 768 bytes;
- `0xA008`, selector 2: 768 bytes;
- `0xA208`, selector 1: 384 bytes;
- `0xA208`, selector 2: 384 bytes.

## Private validation

The clean tuning-derived generator reproduces **16/16 retained rear DSX payloads byte-for-byte** across startup0, startup1, startup2 and steady_ac8.

No captured DMI bytes are embedded or used as producer inputs.

## Integration

E007v installs the final stable-DMI callback under E007u. All first-frame DMI payload families are then concrete.

After E007v, the only remaining first-native-frame blocker is the upstream derivation of VFE680 `PERIOD_CFG`; its packet-aware materializer boundary was already closed by E007c.

## Build result — PASS

The complete accepted E006/E007 provider chain through E007v compiled in an isolated CAMSS source copy.

- private rear DSX validation: 16/16 exact;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,843,024 bytes;
- SHA-256: `379678934e5224ffd9cc6761198975b105dc48a5a94f09ac3c0e77e1eeebe6aa`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- all first-frame DMI payload families: concrete;
- install/load/camera/DMI/RT-CDM submission: none.

## Safety

Compile-only. No module load, camera access, MMIO, DMI submission or RT-CDM submission.