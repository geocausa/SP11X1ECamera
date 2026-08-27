# E003e pre-runtime result

Status: **READY FOR ONE-SHOT / runtime not yet performed**.

## Oracle extraction

Exact same-machine QTI sensor package SHA-256:
`f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c`

The reproducible parser resolves QTI references rather than hard-coding file offsets:

- init regSetting id 1859: 364 ordered 16-bit-address / 8-bit-data writes;
- mode0 regSetting id 38: 68 ordered writes;
- combined: 432 writes / 430 unique final registers;
- MODE_SELECT writes: 0;
- group-hold writes: 0;
- orientation writes: 0;
- all operations are simple writes; no per-record delay or slave override.

Mode0 metadata cross-check: VC0, RAW10 (`0x2b`), crop start 104/256, output 3840x2640, line length 6752, frame length 3554, QTI output pixel clock 548.570 MHz, nominal 30 fps.

PLL2 is 19.2 MHz × 375 / 3 = 2.400 GHz C-PHY symbol rate. Per the local kernel CSI-2 C-PHY formula and fixed-link reporting rule, E003e returns fixed V4L2 link frequency 1.200 GHz through `.get_mbus_config()`.

## Sensor module

- module SHA-256: `6a1939aae15fea062bd893ae6d5c60f6a8f7985c391ea289ddb82195e3d8233c`;
- srcversion: `9E78852E65A2AA230272FB0`;
- exact Golden vermagic;
- 38 imported symbol CRCs / 0 mismatches;
- `E003E_MODULE_ABI=PASS`.

The module advertises only mode0. Probe powers/identifies the sensor, requires MODE_SELECT=0, writes Windows init+mode0, reads back the C-PHY/RAW10/timing/crop/output/PLL registers, requires MODE_SELECT=0 again, then registers the subdevice and lets runtime-PM power it down. `.s_stream(1)` remains `-EOPNOTSUPP`.

## Host side

E003e reuses the already-accepted E003d host side unchanged:

- qcom-camss SHA-256 `04e92a3ea8b9075f6d5ffa43856276595b0bb2b47877ce43b3987c08c4a41e91`;
- E003d DTB SHA-256 `9e5eab025ed4dc0d23983f0e0ab0b84ca6095826f5a9b4f57fb1c6b9b3e50d79`;
- immutable one-trio IMX681 → CSIPHY2 graph.

No DT change is required.

## Reproducible initrd

Base accepted R3 initrd SHA-256:
`dfcc8a0d53391b80ef418ff7b3c40df2ccbc0d8aeb43ffe6a8e7abb5aabf7e15`

Independent A/B E003e initrds are byte-identical:
`8299ff53e31f40782bd58ea12b52bb6c52ffb848b22ad92abd406dbd217e8b36`

Semantic delta remains exactly 10 isolated entries: E003e module directory, accepted E003d CAMSS, E003e IMX681, v4l2-cci, four videobuf2 dependencies, E003e init-top hook and ORDER update.

`E003E_INITRD_REPRODUCIBLE=PASS`.
