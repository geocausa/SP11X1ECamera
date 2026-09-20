# E004jn — rear 4K NV12 into an actual GStreamer application (offline)

2026-09-20. Parent: `dba2d7f`. This is a **source-only protected-Golden** experiment, not a native camera boot or a system-discoverable virtual webcam. No camera/IR, GRUB/EFI, reboot, V4L2 camera, installed desktop service, recorded optical/preview data or Windows transition.

## Motivation and exact boundary

The same SP11's Windows WinRT reader delivered **3840×2160 rear NV12 frame buffers** (E004jk). E004jl introduced a strictly offline, uncalibrated rear Bayer10→3840×2160 NV12 C converter and E004jm preserves its full output bytes with faster shared-neighbour processing. These separate tests did **not** establish that a real application can consume their 4K output. E004jn adds a separate bounded **GStreamer appsrc→queue→videoconvert→I420 appsink application** accepting NV12 3840×2160.

The app consumer uses 12,441,600 bytes/frame, bounded queue/backpressure, synthetic 30-fps timestamps and duration, full-buffer size/PTS validation, EOS/error handling and exact frame count. `--require-distinct` optionally SHA-256-computes *consumer-side I420 payload bytes* and rejects repeated payloads; only synthetic distinct-pattern tests use this option. Pixels and hashes are not printed, exported or written to disk. A repeated static scene need not change actual decoded pixels; repeated content alone is not a general live-camera frame-drop test. Every success line explicitly says `SYNTHETIC_PTS_ONLY=YES LIVE_CAMERA_PROVEN=NO VIRTUAL_WEBCAM_CREATED=NO`.

## Physical and synthetic evidence, precisely separated

- A previously archived **rear hardware test-pattern** raw frame (not a new optical scene) was converted into the E004jl/E004jm 3840×2160 NV12 digest `42136b93325c8c7d76dbc25deb64740d3b10c33670f486acb0d81b639753f45d`. The E004jn application consumed one complete 4K frame.
- Two separately generated nonuniform **synthetic** Bayer buffers produced different full 4K NV12 frames, and two distinct I420 frames reached the actual GStreamer appsink. The optional distinctness gate correctly rejects two identical input frames.
- **Six automated tests PASS** for the colourbar→application chain, synthetic distinctness, repeated-frame rejection, truncation/extra-byte rejection, bad counts and nonactivation checks.
- A direct, file-free `8 × archived same hardware colourbar → fused 4K converter → GStreamer appsrc/I420 appsink` pipeline reported **8/8 application frames**, 15.595 ms *average conversion-only* and 198 ms total GStreamer-consumer interval. The source was the **SAME static archived test pattern repeated eight times**, not eight fresh real optical frames. The consumer assigns synthetic timestamps: neither interval establishes physical exposure cadence, sensor-to-screen latency, sustained live 4K30 throughput or application-visible webcam discovery.

No intermediate NV12 or optical files were created; the only image source read was the already archived local rear hardware colourbar. The existing temporary 1080p rear standard V4L2 endpoint (E004jh) and front QC10C capture path are unchanged.

## Replay on SP11 Golden

```bash
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004jm-rear-4k-fused-offline \
  -p test_rear_4k_fused.py -v
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004jn-rear-4k-appsrc-offline \
  -p test_rear_4k_appsrc.py -v
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```

**Next physical gate:** independently establish isolated **3840×2160 NV12 standard virtual-device negotiation** with a synthetic publisher and separate ordinary V4L2 reader, without touching default Golden. Then prepare a new source-locked single-use camera-capable one-shot to connect real rear OV13858 optical capture to this optimized 4K bridge and standard discoverable 4K endpoint under strict timeouts and unconditional Golden return. Measure 4K30 real sustained frame/thermal/latency plus colour/Windows pixel-quality separately. Front needs independent correct QC10C decompression or true safe linear ISP output.
