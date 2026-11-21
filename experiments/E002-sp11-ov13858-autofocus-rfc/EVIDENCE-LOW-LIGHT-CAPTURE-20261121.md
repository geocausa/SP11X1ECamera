# E002 — SP11 dark-room image acquisition and OV13858 synthetic pattern proof

Test date: 2026-11-21, evening UTC. Target: Surface Pro 11 OLED, live test kernel `7.3.0-sp11-camera-rfc1+`, RFC2 Device Tree with `lens-focus = <&rear_vcm>`.

## Results

- **Hardware-verified camera capture:** PASS. libcamera 0.7.0 reports the internal rear OV13858 and captured four RAW `1056×784 SGRBG10_CSI2P` frames of 1,041,152 bytes each, with interframe rates approximately 30 fps. This room was dark, so the first capture buffers were dark-looking and are **not accepted as proof of a synthetic pattern**.
- **Internal colour-bar pattern acquisition:** PASS. With sensor runtime power pinned during setup, V4L2 accepted `test_pattern=1` (Vertical Color Bar Type 1). Direct `/dev/video0` streaming returned three frames (sequence 0, 1, 2) of exactly **1,041,152 bytes** each, 3,123,456 bytes total. Interframe deltas **33.387 ms** and **35.159 ms**. V4L2 streaming exited 0 without a stream error.
- **Actual pattern in captured pixels:** PASS, not just a control readback. All three direct-capture RAW frames had identical SHA256 `a5dcc50c8c634a97dff95352b4363f8c8dec193129e9929c67de00f08ac09ee2`, only five distinct byte values (0x00, 0x10, 0x33, 0xcc, 0xff), and strong repeatable horizontal colour-bar transitions. Interpreting the 10-bit CSI-2 packed data, representative 132-pixel-wide row-sector means on row 300 were approximately `1008.5, 558.0, 1008.5, 543.5, 529.0, 78.5, 529.0, 64.0`. These varied by column and were stable across frame rows, consistent with the requested bars.
- **Power:** During active capture, the Linux regulator summary recorded OV13858's `dovdd` consumer on PM8010 L6M alongside DW9800K's `vddio` consumer (L6M enable count 2), and rear sensor AVDD `vreg_l5m_2p8` count 1. Actuator VDD L16B count 1 during this session because WirePlumber retained the lens file handle. Following the test, the sensor was restored to `test_pattern=0` and its runtime PM `power/control=auto`. L6M returned to count 1 (lens only) and AVDD to count 0.
- **Focus-control hardware path (earlier in session):** VCM appeared as `/dev/v4l-subdev29`; `focus_absolute` commands `128, 512, 896, 256, 0` returned success with matching readback, with no corresponding actuator/CCI error in `dmesg`.

## Boundaries

**Confirmed:** a bootable Linux rear-camera stack, sensor binding, media graph, lens subdevice, successful focus register transactions, RAW frame delivery, and reproducible OV13858 on-chip synthetic colour bars through the memory capture path in darkness.

**Not claimed:** optical lens movement or focus sharpness (requires an illuminated structured scene), the precise physical PM8010 L6M supply parent (the `vreg_s4c_1p8` mapping remains inferred), independent idle power shutdown while all users are closed, or post-camera suspend/resume reliability. Libcamera warns about missing sensor crop rectangles and calibration; streaming works despite those warnings. Avoid attaching a broad `Tested-by` for more than these measured paths.

Raw capture files and the dark scene are **local to SP11** at `/home/geoca/build/sp11-vcm-upstream-rfc-20261121/experiment/synthetic-frames/`. No raw frames, room photos, or other personal imagery are committed publicly.

## Reproduction

```sh
# On kernel 7.3.0-sp11-camera-rfc1+, after the RFC2 DTB boot:
# Ensure the sensor is awake so test_pattern writes reach the hardware.
echo on | sudo tee /sys/bus/i2c/devices/1-0010/power/control
v4l2-ctl -d /dev/v4l-subdev28 --set-ctrl=test_pattern=1
v4l2-ctl -d /dev/v4l-subdev28 --get-ctrl=test_pattern
v4l2-ctl -d /dev/video0 --stream-mmap=3 --stream-count=3 --stream-to=synthetic.raw --verbose
v4l2-ctl -d /dev/v4l-subdev28 --set-ctrl=test_pattern=0
echo auto | sudo tee /sys/bus/i2c/devices/1-0010/power/control
```

Sources, patches, wiring limitations and rollback: [E002 README](README.md).
