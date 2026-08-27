# E002b-r3f — Windows-exact OV13858 identity transaction

Status: PREPARED / NOT YET BOOTED

## Question

Does the rear OV13858 acknowledge and identify when the already-validated SP11 power/MCLK/CCI route is left unchanged and only the identity transfer is changed from r3e's generic three-byte `0x300a` read to the exact Windows/QTI 16-bit `0x300b -> 0xd855` transaction?

## Fixed inputs

No DT or electrical change from accepted r3d / r3e:

- Golden kernel release: `7.1.5-sp11-render-parity-v4+`
- DTB: exact accepted r3d bytes, SHA-256 `4eca2b3fb7f6793d780cc7d9e3642bf9f3a4703b7db011a6650f4857a2b12233`
- isolated camera RPMh provider SHA-256 `ac9269cd4be0842cb5dd3eeef9ccc2dc95100c86b59e57d83b3d86c8f5178ace`
- CCI route: CCI0/master1
- CCI rate: FAST / 400 kHz
- Linux 7-bit sensor address: `0x10`
- MCLK1: 19.2 MHz
- reset: GPIO110, active-low logical description / Windows D0 release high
- rails: LDO6_M 1.8 V -> LDO1_M 1.2 V -> LDO5_M 2.8 V -> LDO16_B 2.9 V
- no CSI endpoint and no streaming

## Single intended code delta

r3e:

- register `0x300a`
- read 3 bytes
- compare `0x00d855`

r3f:

- register `0x300b`
- read 2 bytes
- combine big-endian as `0xd855`

This matches the exact installed QTI sensor-module data (`reg_addr_type=16-bit`, `reg_data_type=16-bit`, ID register `0x300b`, ID `0xd855`).

## Reproducibility / hashes

- r3f source SHA-256: `d3bde89ec24774625ef8d1a92003434b44fa96d38a009713dae4b8015dd46198`
- r3f module SHA-256, clean build A/B: `939cc97d40e33eaec82f28c219b71cfe7a03a9bfc91c9871b481e0d5ef16d0ac`
- vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`
- Golden initrd SHA-256: `ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`
- candidate initrd SHA-256, independent build A/B: `0ed680055bdf5359478a29451e167679f2cba2b7c4f8b0ba30841046a453dbb2`
- candidate semantic initrd delta count: 5 exactly

## Runtime acceptance

First boot is permissive, retaining Golden's `clk_ignore_unused pd_ignore_unused` for isolation from unrelated missing ownership. Success requires:

1. candidate boots and provider binds;
2. rear power/MCLK/reset sequence reaches CCI without regression;
3. identity read returns `0xd855` at address `0x10`;
4. probe tears down every camera rail and MCLK cleanly;
5. Golden audio/Wi-Fi/touch remain healthy;
6. saved GRUB default remains `sp11-audio-fullio-v19c`.

If permissive r3f passes, repeat an otherwise-identical strict boot with only `clk_ignore_unused pd_ignore_unused` removed before calling the rear identity gate accepted.

## Rollback

Golden FullIO v19c remains the saved GRUB default. r3f is one-shot only and has a separate `/boot` payload and GRUB ID.
