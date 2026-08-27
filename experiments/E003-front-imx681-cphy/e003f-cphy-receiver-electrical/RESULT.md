# E003f result — ACCEPTED: host-powered CSIPHY2 C-PHY receiver electrical gate

Date: 2026-08-27

## Conclusion

E003f is accepted. The R3 retry proved the front IMX681 receiver-side X1E C-PHY programming exactly against the same-machine Windows live oracle while the sensor remained electrically idle and non-transmitting.

R2 had already proven the corrected 8 KiB CSIPHY2 aperture and local PHY power-on, but without normal host pipeline power it read 78 expected non-zero Windows values as zero. R3 changed only the missing host-side prerequisite: VFE0 `s_power(1/0)` around the same receiver-only CSIPHY2 power/start/compare/stop sequence. No CSID stream, sensor callback, CCI/I2C transaction, MODE_SELECT write, or sensor-power action exists in the R3 verifier.

## Exact candidate identity

- boot entry: `sp11-camera-e003f-r3-cphy-receiver`
- Golden Image SHA-256: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`
- R3 initrd SHA-256: `082f9aebc0ba19ed2279856c6e7a55b8f9a29c6733586b7430a51c91578fa587`
- corrected 8 KiB DTB SHA-256: `e9fd13a29b6580955d2662c27377dbd1caba14f7f89613510b5e23bd6c266293`
- patched CAMSS SHA-256 at build/package boundary: `e1c8dcb099ee872ffd8bac263576b8f2db85cef104077df80d29a2916f47f308`
- loaded patched CAMSS srcversion: `1D2912B8FF127D1F3D94704`
- R3 verifier SHA-256: `20c60fa0d6fd5650a1cca51adb78b6697b8b0dbdb70edb692d7c1b2ba105a1f6`
- verifier srcversion: `ADBC641834EB18909E697EA`
- verifier ABI: 13 imports, zero Golden CRC mismatches

The R3 initrd was independently reproduced twice and the two images were byte-identical.

## Runtime proof

Before the verifier load:

- one-shot marker was exact and `next_entry` had already been consumed;
- Golden remained the permanent saved GRUB default;
- live CSIPHY2 resource was `0x0ace8000-0x0ace9fff` (8 KiB);
- the dynamically discovered IMX681 client was runtime-suspended with usage 0;
- GPIO237 was reset-low;
- MCLK4, CSIPHY2/timer and IFE0/CPAS clocks had zero enable/prepare counts;
- L3M 1.8 V and L7B 2.8 V front rails had zero active users.

The SHA-checked verifier was loaded exactly once. It reported:

- `E003F_MMIO_PREFLIGHT_PASS`: CSIPHY2 size `0x2000`;
- `E003F_PREFLIGHT_PASS`: C-PHY, one trio, zero-based trio position, 121 expected registers;
- `E003F_HOST_POWER_ON_PASS`: VFE0 power_count 1;
- `E003F_POWER_ON_PASS`: PHY timer 400 MHz;
- `E003F_LIVE_COMPARE`: **121 expected, 0 mismatches**;
- common receiver controls matched Windows exactly while active: CTRL5 `0x02`, CTRL6 `0x01`, CTRL7 `0x7a`;
- `E003F_STREAM_OFF_PASS`: CTRL5/CTRL6 both returned to zero;
- `E003F_HOST_POWER_OFF`: VFE0 power_count returned to 0;
- `E003F_RECEIVER_ONLY_PASS`: receiver stopped and powered off cleanly.

After verifier removal, IMX681 was still runtime-suspended with usage 0, MCLK4/front rails/reset remained inactive, and the R3 time window contained no IMX681/CCI/I2C/sensor kernel activity. This independently supports the source-level guarantee that the sensor did not transmit.

## Regression and rollback proof

On the candidate after R3:

- rear OV13858 dynamically bound and remained suspended/usage 0 with its immutable CSIPHY1 link intact;
- Wi-Fi remained associated;
- FullIO `MultiMedia1 Playback` and `MultiMedia3 Capture` remained present;
- `Microsoft Surface G6 Touch` remained present;
- no serious kernel Oops/panic/SError/lockup signature was found.

A normal reboot then returned to FullIO v19c Golden with saved entry `sp11-audio-fullio-v19c` and empty `next_entry`. The canonical Golden artifacts were mechanically reverified byte-for-byte:

- Image: `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a`
- initrd: `ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`
- DTB: `2fcfa738c229b32764ff2722847cf4056b3153c64a12f8490429309f29df6d00`

Golden Wi-Fi, FullIO playback/capture and G6 touch were healthy after return; Golden again exposed no camera media/video nodes, as expected.

## What E003f proves

The corrected X1E CSIPHY2 8 KiB resource plus the Windows-derived C-PHY table are electrically correct on this SP11 **when executed under the normal VFE0/IFE/CAMNOC/CPAS host-power context**. The remaining front-camera unknown is no longer receiver electrical programming; it is the bounded end-to-end sensor/CSID/VFE transport lifecycle.

## Next smallest experiment

E003g begins static-only. Derive the exact front CSID/VFE/RDI route and the smallest safe sensor-stream lifecycle from the accepted E003d/e/f graph, the native IMX681 driver and same-machine Windows evidence. Keep Golden untouched and do not enable MODE_SELECT or attempt a frame until that route, teardown, timeout and rollback plan are mechanically prepared as a separate one-shot candidate.
