# E003b result — ACCEPTED

E003b electrically identified the Surface Pro 11 front Sony IMX681 on Linux without exposing the sensor to CSI/C-PHY or V4L2 streaming.

## Identity

The one-shot E003b boot loaded the probe-only shim on CCI1/master1 at Linux address `0x10` and logged:

`SP11 E003b PASS: IMX681 chip ID 0x0aff at 0x10`

This exactly matches the same-machine Windows oracle (`0x0004 -> 0x0aff`). The loaded probe module srcversion was `3881AD933BB056C941626AB` with exact Golden vermagic and 24/24 imported symbol CRCs matching Golden.

## Teardown / isolation

Immediately after the two-byte identity read, the probe logged that its power sequence was torn down. Runtime mechanical state then showed:

- `cam_cc_mclk4_clk`: prepare/enable/protect counts `0/0/0`;
- `cam_cc_csiphy2_clk`: `0/0/0`;
- `cam_cc_csi2phytimer_clk`: `0/0/0`;
- `vreg_l3m_camera` / `3-0010-ldo3m`: enable count `0`;
- `vreg_l7b_2p8` / `3-0010-ldo7b`: enable count `0`;
- GPIO237: output low (reset asserted);
- media graph: no IMX681/front sensor entity or link; CSIPHY2 has no sensor sink link;
- no `Missing lane_regs` or C-PHY programming path was entered.

Rear OV13858 remained bound on CSIPHY1. Wi-Fi, MultiMedia1 playback, MultiMedia3 capture and Microsoft Surface G6 Touch remained healthy. No serious kernel fault was found.

## Recovery

The E003b one-shot was consumed while `saved_entry` remained `sp11-audio-fullio-v19c`. The machine was explicitly rebooted back to Golden. Post-return hashes are exact:

- Image: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`
- DTB: `2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`
- initrd: `ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`

Golden Wi-Fi/audio/touch are healthy, the E003b probe module is absent, and `next_entry` is empty.

## Conclusion

**E003b ACCEPTED.** The front IMX681 electrical/control path is no longer speculative: Linux can reproduce Windows' rails/reset/MCLK4/CCI1-master1 lifecycle and read the exact chip identity. Next gate is E003c: a native IMX681 V4L2 sensor bind while still withholding the front CSI endpoint/stream path.
