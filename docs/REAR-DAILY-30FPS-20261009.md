# Rear daily boot entry and 30 fps (2026-10-09)

## Daily entry (identity 64)

`src/native-rgb/rear-daily/`: GRUB entry `sp11-camera-daily` = Golden kernel and
initrd + camera device tree; `sp11-camera-daily.service` loads and routes the
camera stack at boot (`setup-camera.py`), no capture and no reboot. Golden stays
the GRUB default. Kernel module = run-63 measured tone/colour build with the
per-boot session limit raised from 3 to 1,000,000 (an unclean session still
poisons the gate until reboot). libcamera lib20 = lib19 with private statistics
recording optional. Verified: 4 back-to-back clean 300-frame sessions in one boot.

## 15 -> 30 fps (identity 65)

Kernel cadence counters showed epoch_delta=9000 for 4,500 handoffs: every second
sensor frame was missed. The per-frame loop is program -> collect -> retire; retire
averaged 21 ms with zero proof retries. The time was the statistics transport
copying all six statistics planes (~2.4 MB) from uncached coherent DMA memory
before AUX release. The IPA decodes only plane 0's normal AEC grid (32x32 x 80 B).
Daily 65 copies just that 80 KB prefix and zero-fills the remaining planes.

| | daily 64 | daily 65 |
| --- | --- | --- |
| sensor epochs per delivered frame | 2.0 | 1.0 (600/600) |
| retire per frame | ~21 ms | ~2.4 ms |
| measured fps (600-frame sessions) | ~14.7 | 29.4 |
| clean repeat sessions | yes | yes |

## Incident

Unloading the sensor modules while PipeWire/WirePlumber (desktop session, stock
libcamera) held the camera subdevices open caused a use-after-free oops in
`subdev_close` during the following shutdown; the reboot hung and the pending
one-shot entry was consumed by the next power-on. Rule: never rmmod camera
modules on a running desktop; keep WirePlumber off the raw camss nodes.
