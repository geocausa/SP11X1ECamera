# E002e result — ACCEPTED

## Result

**PASS.** The accepted rear native sensor/graph now carries Windows-proven transport metadata end-to-end without programming a Surface mode or invoking stream.

Automatic probe validation logged:

`SP11 E002e PASS: four-lane D-PHY endpoint at 592800000 Hz validated`

Read-only V4L2 control ioctls on the native rear subdevice returned:

- `V4L2_CID_LINK_FREQ`: index 0 = **592800000 Hz**;
- `V4L2_CID_PIXEL_RATE`: **474240000 pixels/s**.

The driver's unchanged RAW10/four-lane relation gives `592.8 MHz * 2 * 4 / 10 = 474.24 MHz`, exactly matching the installed Windows QTI sensor metadata.

Read-only `MEDIA_IOC_G_TOPOLOGY` still proves:

`ov13858 1-0010 pad0 -> msm_csiphy1 pad0`, flags `0x3` = ENABLED + IMMUTABLE, data link.

## Electrical idle

After probe and all read-only ioctls:

- sensor runtime PM = `suspended`;
- usage count = 0;
- GPIO97 = `0x00000244`;
- GPIO110 = `0x00000200` (reset asserted low);
- MCLK1 enable count = 0;
- CSIPHY1 enable count = 0;
- CSI1 PHY timer enable count = 0;
- no camera rail activity occurred after the normal native identity cycle.

Wi-Fi, playback and capture remained healthy.

## Isolation

E002e did **not** change any sensor PLL or mode register array. Mechanical SHA-256 comparison of all upstream PLL/mode arrays against E002c showed byte identity. The only functional driver additions were endpoint validation, 592.8 MHz control metadata, and a DT-selected stream guard placed before runtime-PM power-up.

The no-stream guard was not deliberately exercised because all acceptance criteria were satisfied without a stream-capable operation.

Payload hashes:

- kernel: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`;
- initrd: `4851777632c621d336391ef0f865ea3608b2ea5d986584c8d74e249c5bbca4a5`;
- DTB: `0e25c28f604b12e05b1db61a9e3c177dce77845b42361ef84cc10d7714c12428`;
- E002e OV13858 module: `68369e6496382a0aa31fbbddc63c92742fd82d39c339c831cd2c663c19a99ee9`, srcversion `F8251C8C28A8AB99D09BD40`.

**E002e 592.8 MHz transport-metadata gate: ACCEPTED.**

Next smallest gate: E002f programs the Windows-derived Surface mode-0 PLL plus only the focused register delta relative to the upstream full-resolution table, while retaining the hard no-stream guard. Validate key registers in sensor standby and keep CSIPHY completely idle.
