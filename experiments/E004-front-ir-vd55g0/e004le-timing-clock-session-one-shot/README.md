# E004le timing-control and C-PHY clock session acceptance

Fresh, single-use identity. Hypothesis: E004ld read-only timing controls and explicit C-PHY bus clock vote preserve real front RAW10 delivery and rear handoff.

Start from the unchanged, fully verified 51-file accepted package and DTB; separately pin/load only the E004ld CAMSS and IMX681 candidate pair. Never alter accepted package manifests or accepted module files. Front controls must read HBLANK2912/PIXEL_RATE719898240 and be read-only. Each camera has one bounded publisher and one independent uid1000 client receiving1800 distinct complete frames. Zero source sequence gaps, native stop/STREAMOFF, durable systemd exit and full neutral graph required. Observe existing debugfs clock summary if accessible; do not mount or change debug controls.

No libcamera activation, QC10C PIX stream, IR emitter, sensor mode expansion or optical file export. Camera nodes remain selectable through existing uaccess. No retry or publisher restart. Auto Golden on any service exit, existing300second service ceiling and source2400frame limits. Failed/partial attempts consume the identity. Retirement only after confirmed Golden return and redacted evidence archive.

Passing RDI at the lower vote does not prove PIX594MHz, libcamera registration, ISP parity or suspend. PIX requires an independently scoped fresh test.

## Result — PASS, consumed and retired
Candidate f6f8c3e2-5a84-45fa-aee8-98bde364aeba from c42bb24 returned automatically to protected Golden d7f4882f-6d75-4f4a-933d-2bf47e3e3a5b. All experimental service/client/boot/private runtime assets retired before this result commit.

Front:1800 distinct1080p app frames at30.0421fps;1803 source frames at30.0049fps, zero sequence gaps. Read-only timing controls matched2912/719898240. Active clock report proves VFE1/CPAS345.6MHz. Rear:1800 distinct4K app frames at30.0058fps;1806 captured,1805 published, source29.9504fps, zero source gaps. Both durable service exits143/success and native STREAMOFF passed. Full119-edge graph returned neutral. Thermal maximum51.2C. No kernel fault or camera error matches;7 unrelated qcom-apm audio error lines were present, so this is not a claim of an entirely error-free kernel log.

Both app streams have one virtual GStreamer offset gap; these offsets are not proven sensor sequences. No source sequence gaps occurred. Distinct complete frame count and cadence remain valid; do not claim perfect end-to-end frame retention.

Historical shell PASS banner still says FRONT120_REAR120; the actual command, validator and numeric evidence prove1800 each. Preserved verbatim for audit. Graph-contract JSON retains source-only labels; live graph files and real independent app evidence establish the physical transition result.

Uncontrolled luma is near black (front mean~16.11; rear~15.98). This prevents quality/low-light/Windows ISP parity claims. Lower clock is demonstrated, power saving is not measured. PIX, live libcamera, sensor/publisher restart, suspend and production default remain open. Never rerun this consumed identity.
