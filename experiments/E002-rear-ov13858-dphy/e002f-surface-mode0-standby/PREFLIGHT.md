# E002f preflight — Surface OV13858 mode0 programming in standby

## Question

Can Linux program and read back the Windows-derived Surface rear mode-0 PLL/crop/timing configuration while the real OV13858 remains in standby, with CSIPHY completely idle and the E002e no-stream guard still enforced?

## One major unknown

Sensor register programming only. No receiver programming and no streaming.

## Proven base retained

- Golden kernel bytes unchanged: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`.
- E002e accepted 592.8 MHz transport metadata retained.
- E002d accepted OV13858 -> CSIPHY1 graph retained.
- E002c accepted rails/reset/MCLK/CCI ownership retained.
- E002e pre-power `.s_stream(1)` guard retained mechanically before `pm_runtime_resume_and_get()`.

## Clean-room Surface mode0 program

The installed Windows QTI sensor package is used only as a local oracle; no proprietary blob/table is committed.

Instead of copying its 207-register mode table, E002f composes:

1. a 12-register Windows-derived Surface PLL profile for 592.8 MHz;
2. the existing upstream `mode_4224x3136_regs` common table unchanged;
3. a compact 24-register Surface mode0 delta.

All pre-existing upstream PLL/mode arrays are byte-identical to E002e.

Expected static readback before the frame-length control-stage correction:

- MODE_SELECT `0x0100` = `0x00` standby;
- PLL `0x0300=0x05`, `0x0301=0x00`, `0x0302=0xf7`;
- output width `0x3808/09 = 0x0fec` = 4076;
- output height `0x380a/0b = 0x0af6` = 2806;
- line length `0x380c/0d = 0x0462` = 1122;
- static VTS `0x380e/0f = 0x0c88` = 3208;
- MIPI timing `0x4837=0x0d`.

Then E002f writes the QTI mode metadata frame length through the same VTS register as Linux VBLANK control:

- final VTS `0x380e/0f = 0x0c8e` = 3214;
- MODE_SELECT must still read `0x00`.

The validator never writes MODE_SELECT=1.

## Artifacts

E002f OV13858 module:

- SHA-256 `d70cd7708ceeca024de65582950e3d7b4a8beaae3b085fa0dead728a1cdbb6ae`;
- srcversion `231AFB553F518F668097FEB`;
- exact Golden v4 vermagic.

Candidate DTB:

- SHA-256 `b669db40f44a108560aeca23e9f0d52b312246452d0771c93daf8765fc8d0692`;
- only delta from E002e: `microsoft,e002f-validate-mode0` on the rear sensor node;
- DTC warnings unchanged 30 -> 30.

Golden-based initrd independent A/B builds:

- SHA-256 `b23b757b390da6c906b72812552f5e2c249a0f7e85580e7a2d7492cb7a142d27`;
- byte-identical.

## Runtime sequence

At native probe:

1. accepted Windows-derived power sequence;
2. native silicon identity;
3. software reset;
4. explicitly select standby;
5. Surface PLL;
6. unchanged upstream common full-res table;
7. compact Surface mode0 delta;
8. key readbacks including static VTS 3208;
9. VTS control-stage write to 3214;
10. final MODE_SELECT readback = standby;
11. normal reverse power teardown.

No CAMSS/CSIPHY stream or power operation is requested.

## Acceptance

- `SP11 E002f PASS: Surface mode0 standby 4076x2806, VTS 3214, PLL 592.8 MHz profile`;
- E002c identity and E002e endpoint validation still pass;
- sensor returns runtime-suspended usage 0 after probe;
- MCLK1, CSIPHY1 and CSI1 timer enable counts are 0 after teardown;
- immutable OV13858 -> CSIPHY1 graph remains intact;
- LINK_FREQ=592800000 and PIXEL_RATE=474240000 remain unchanged;
- Wi-Fi/audio healthy;
- no stream call.

## Rollback

Golden `sp11-audio-fullio-v19c` remains saved GRUB default. Candidate is separate one-shot only.
