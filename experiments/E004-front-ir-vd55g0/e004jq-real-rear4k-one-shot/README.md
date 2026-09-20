# E004jq — bounded real rear optical → standard 4K V4L2 camera → independent app

2026-09-20. New unique one-shot candidate. **Preflight/staging phase only until an actual recorded candidate boot occurs.** E004jp previously proved a *synthetic* standard 3840×2160 NV12 `/dev/video90` V4L2 endpoint, eight independent V4L2 samples and an ordinary GStreamer application, safely returning to Golden. E004jh separately proved a live **optical 1080p** rear webcam and bounded 27-frame front QC10C capture. E004jm/jn proved only offline rear Bayer→4K NV12 conversion/application delivery.

## Goal and boundaries

This distinct experiment uses the exact accepted 51-file source-locked three-sensor camera-capable release, original protected Golden kernel/initrd copied into a NEW non-default boot entry, source-locked derived R4 bootstrap and physically validated front DMA guard, plus a separately rebuilt Golden ABI GPL v4l2loopback module. Only the **rear OV13858 RGB** sensor is intentionally streamed. IR illumination/Hello and front RGB stream are **not started**. All modules and the loopback device exist only in the isolated candidate boot, not Golden. The new identity is consumed on first attempt and cannot be rearmed; the service requests automatic Golden reboot after success, failure or timeout.

The candidate verifies the established hardware rear colourbar then disables test pattern and attempts 27 complete *fresh normal optical* 4076×2806 GRBG10p `pgAA` rear frames. These travel directly (without raw-scene/image files) through the E004jm bit-exact optimized but **uncalibrated** software colour converter to 3840×2160 NV12, to GStreamer `v4l2sink` on standard `/dev/video90`. A separate ordinary V4L2 mmap client must capture eight complete 12,441,600-byte 4K NV12 buffers and feed the exact E004jn GStreamer application. The candidate validates producer hardware sequence/timestamp and independent consumer V4L2 buffer sequences, final route neutral and all sensors suspended. It never asserts 4K exposure cadence from synthetic app PTS. No front displayable video, full OEM ISP, AE/AWB, Windows pixel-quality parity or multi-minute 4K30 is proven even if the bounded result passes.

## Fail-closed safeguards

- Test first on Golden: source-owned clean tracked branch, no physical-camera processes/modules/devices, empty GRUB `next_entry`, original `saved_entry`; source package, private R4, loopback .deb/module, optimized bridge and app are SHA-locked. Before a sensor is enabled the candidate checks both real GRUB writers finished successfully and in accepted E004iy order.
- New `sp11-camera-e004jq-rear4k-one-shot` entry is armed through `grub-reboot` only; original Golden kernel/DTB/initrd and saved default are unchanged. Camera DTB and module are isolated. A new root-owned `ATTEMPT-CONSUMED` marker is written before camera activation. Original E004jg/jh/jp identities must not be reused.
- Hardware-free archived **test-pattern** root-copy offline 4K app and GStreamer publisher preflights must pass before installation/arming. In the candidate no rear optical/raw NV12 intermediate file is created; only root-private logs and the accepted rear sensor colourbar can exist, to be deleted on retirement.
- An independent bounded service exits back to Golden even on normal failure; after verification, deactivate and remove its unique service, entry, boot files, modules and private captured pixels. An unexpected boot or kernel hang requires recovery rather than falsely calling this passed.

## Sources and local preflight

The temporary source build and release package sit in ignored private `/tmp/sp11-e004jq-real-rear4k.zk9Kcz`, not Git. They are not shared or installed persistently; the repository contains only source, source-aware test/one-shot scripts and redacted final metadata if a boot occurs. The package manifest matches the previously accepted 51-file manifest `9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455`; accepted CAMSS candidate SHA `862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7`. Fresh loopback kernel module SHA `e6dbd76cb6437f0d5b492c0bebe5a704cedd83782da1917975add6727bc1700b`, bounded rear 4K converter `ef1250d07cc34a535336be2a3665b3fba3bb23c6590e876649cdfd8155a29c46` and 4K app consumer `813d6ad77f5b936955df178c4b426c3c3844d6d640f4377dd7196b5f1fba96a5` are staged privately after full validation.

```bash
python3 -m unittest discover -s experiments/E004-front-ir-vd55g0/e004jq-real-rear4k-one-shot -p 'test_*.py' -v
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```

**Do not describe an unarmed candidate or earlier synthetic test as a physically validated live 4K rear camera.** Record actual `RESULT.json` and post-Golden evidence only after candidate return and retirement.
