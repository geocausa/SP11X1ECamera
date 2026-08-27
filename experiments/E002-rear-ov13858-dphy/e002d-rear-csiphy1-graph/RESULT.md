# E002d result — ACCEPTED

## Result

**PASS.** The rear OV13858 native V4L2 subdevice completed asynchronous media-graph binding to X1E CAMSS **CSIPHY1** with no streaming and no PHY power-up.

A read-only `MEDIA_IOC_G_TOPOLOGY` query on `/dev/media0` returned:

- entity `ov13858 1-0010`;
- entity `msm_csiphy1`;
- link `ov13858 1-0010` pad 0 -> `msm_csiphy1` pad 0;
- link flags `0x00000003` = `MEDIA_LNK_FL_ENABLED | MEDIA_LNK_FL_IMMUTABLE`;
- data-link type.

This closes the only acceptance item that was missing when `media-ctl` was unavailable. The checked-in `read-media-topology.c` helper performs only `MEDIA_IOC_G_TOPOLOGY`; it never issues `MEDIA_IOC_SETUP_LINK`, a format ioctl, power ioctl, or stream ioctl.

## Electrical safety confirmation

After graph enumeration:

- OV13858 runtime PM: `suspended`;
- runtime usage count: `0`;
- GPIO97: `0x00000244`, MCLK1 pinmux retained;
- GPIO110: `0x00000200`, reset physically low/asserted;
- `cam_cc_mclk1_clk` enable count: 0;
- `cam_cc_csiphy1_clk` enable count: 0;
- `cam_cc_csi1phytimer_clk` enable count: 0;
- no camera-rail activity occurred after the one native identity cycle at boot.

Wi-Fi, `MultiMedia1 Playback`, and `MultiMedia3 Capture` remained healthy.

## Mechanical isolation

E002d reused the accepted E002c-r1 kernel and initrd byte-for-byte. Only the DTB changed, adding reciprocal graph endpoints:

- sensor side: explicit D-PHY, `data-lanes = <1 2 3 4>`;
- CAMSS `port@1` / CSIPHY1 side: explicit D-PHY, `data-lanes = <0 1 2 3>`.

No `link-frequencies`, mode-table, CSID/VFE routing, format, or streaming change was introduced.

Payload hashes:

- kernel: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`;
- initrd: `d1e56f66b742e33f980748a66e4184e92ba1b7e0cb4f7a1844471b5fb7ffe344`;
- E002d DTB: `ea55cafdc4b35197e4d839a8435c7514c351ef4cfd2933d81458db0bea10472d`.

## Conclusion

The rear-sensor graph is proven: native OV13858 -> X1E CSIPHY1, four-lane D-PHY, immutable enabled media link, electrically idle after enumeration.

**E002d rear CSIPHY1 graph gate: ACCEPTED.**

Next smallest gate: derive and validate the first rear mode's exact Linux-visible link frequency/timing relationship from the Windows oracle and the native OV13858 mode table before invoking any stream operation. Keep physical rails/reset/MCLK/CCI and the accepted CSIPHY1 graph unchanged.
