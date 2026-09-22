# E004le timing-control and C-PHY clock session acceptance

Fresh, single-use identity. Hypothesis: E004ld read-only timing controls and explicit C-PHY bus clock vote preserve real front RAW10 delivery and rear handoff.

Start from the unchanged, fully verified 51-file accepted package and DTB; separately pin/load only the E004ld CAMSS and IMX681 candidate pair. Never alter accepted package manifests or accepted module files. Front controls must read HBLANK2912/PIXEL_RATE719898240 and be read-only. Each camera has one bounded publisher and one independent uid1000 client receiving1800 distinct complete frames. Zero source sequence gaps, native stop/STREAMOFF, durable systemd exit and full neutral graph required. Observe existing debugfs clock summary if accessible; do not mount or change debug controls.

No libcamera activation, QC10C PIX stream, IR emitter, sensor mode expansion or optical file export. Camera nodes remain selectable through existing uaccess. No retry or publisher restart. Auto Golden on any service exit, existing300second service ceiling and source2400frame limits. Failed/partial attempts consume the identity. Retirement only after confirmed Golden return and redacted evidence archive.

Passing RDI at the lower vote does not prove PIX594MHz, libcamera registration, ISP parity or suspend. PIX requires an independently scoped fresh test.
