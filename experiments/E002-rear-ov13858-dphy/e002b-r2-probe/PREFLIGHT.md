# E002b-r2 preflight — rear OV13858 identity probe only

## Scope

r2 starts from the accepted E002b-r1 isolation architecture. It adds only the rear control path required to reproduce the Windows identity probe:

- CCI0 master1 pinmux: TLMM GPIO103/104, `cci_i2c`;
- CCI0 master1 bus rate: 400 kHz (Windows/QTI FAST);
- rear I2C client at Linux 7-bit address `0x10`;
- reset GPIO110, active low;
- MCLK1 @ 19.2 MHz;
- four supplies referencing the **isolated** camera-only RPMh provider handles from r1;
- candidate-initrd-only `sp11_ov13858_probe.ko`.

There is no CAMSS sensor endpoint, no CSIPHY link, no stream code and no image pipeline operation in r2.

## Probe lifecycle

The probe-only driver reproduces the Windows D0 ordering:

1. acquire reset asserted (GPIO110 physical low);
2. cache/request LDO6_M = 1.8 V;
3. cache/request LDO1_M = 1.2 V;
4. cache/request LDO5_M = 2.8 V;
5. cache/request LDO16_B = 2.9 V;
6. enable LDO6_M -> LDO1_M -> LDO5_M;
7. delay 1 ms;
8. enable LDO16_B;
9. set/enable MCLK1 at 19.2 MHz;
10. release reset;
11. delay 10 ms;
12. read three ID bytes beginning at register `0x300a`;
13. require `0x00d855`;
14. assert reset and tear MCLK/rails down in reverse order.

No V4L2/media sensor registration is performed by this shim.

## DT mechanical proof

- literal deployed FullIO v19c DTB SHA256: `2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`;
- r2 overlay DTBO SHA256: `9824ff5bcd4e9850e261514ec11a07f1de89358031d6ddb80946eb72683bcfe0`;
- r2 merged DTB SHA256: `637d42574e74a22d41dfe6de065b753e5f9e78a8975b773d66b46bc3aad7fa23`;
- normalized Golden -> r2 tree has **0 removed Golden lines**;
- no experimental child is added to existing Golden `regulators-0`;
- r1 -> r2 functional delta is only CCI pinctrl/rate + one rear client.

## Module proof

- `sp11_ov13858_probe.ko` SHA256: `c945eb7e3f8aa4c142d4bf2f86c996fcd1b858764855d09518654b414de698be`;
- vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- live no-device insmod/rmmod on accepted r1: PASS, all four isolated rails remained 0 users / 0 mV.

The module is **not installed in the shared Golden `/lib/modules` tree**.

## Candidate initrd proof

The candidate initrd is built by `build-candidate-initrd.py` from the exact Golden v19c initrd. The script:

- decompresses Golden;
- parses its `newc` archive and preserves every byte before the original `TRAILER!!!`;
- inserts one deterministic cpio layer before that trailer;
- recompresses as one zstd stream;
- validates the final semantic file map.

Golden initrd SHA256:
`ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`

Golden uncompressed prefix SHA256 (209,664,148 bytes):
`d9a694f9b3dcb0784cd497688a53e490b5aee0ad58e0b008dfe2598ad5a7a0b4`

Deterministic r2 initrd SHA256 (two independent builds matched):
`314547e3b5d0403e9a8539b4f6d39d5936a2b1a6ee6311b1c8f508abc71377a1`

Semantic delta is exactly:

1. add `usr/lib/modules/7.1.5-sp11-render-parity-v4+/extra/`;
2. add `sp11_ov13858_probe.ko` there;
3. add `scripts/init-top/zz-sp11-camera-r2-probe`;
4. override `scripts/init-top/ORDER` by appending one invocation of that loader.

The extracted loader passes `dash -n`, and the extracted module SHA is identical to the vetted build.

## Acceptance

PASS requires all of the following:

1. userspace reached and one-shot GRUB consumed;
2. Wi-Fi UP/associated;
3. Golden playback and capture enumerate;
4. existing Golden PM8550-B provider remains bound;
5. isolated r1 camera providers remain bound;
6. initrd log proves the probe module loaded;
7. exactly one rear identity probe succeeds with `0x00d855` at address `0x10`;
8. probe logs prove teardown completed;
9. four camera rails return to 0 users and MCLK1 returns to enable count 0;
10. no CSI endpoint/stream is attempted.
