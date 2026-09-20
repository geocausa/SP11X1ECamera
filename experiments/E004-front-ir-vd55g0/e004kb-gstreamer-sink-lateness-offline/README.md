# E004kb — camera-free GStreamer 30fps PTS versus slower source lateness experiment

2026-09-21. Parent `453d8c8`. The physical E004ka test captured 180 real rear optical OV13858 Bayer frames in 8.18028 seconds (**21.8819 delivered source fps** under full 4K software converter + loopback/GStreamer load), converted all 180 to 4K NV12, but the independent standard V4L2 reader and the true app consumed only **40 complete 4K buffers**. An exact-byte meter between the V4L2 stdout and GStreamer app measured 40 complete NV12 frames with **no pipe loss**; the shortage occurred at or before reader stdout. The publisher pipeline assigned `rawvideoparse framerate=30/1` and ended in `v4l2sink sync=true`, although the real source was materially slower than 30fps. A concrete, testable possible explanation is *GStreamer sink lateness-based buffer dropping*, not necessarily a kernel camera/CAMSS fault.

## What E004kb measured on the same SP11 Golden GStreamer installation

The actual installed `v4l2sink` factory was **instantiated but never opened or set to PLAYING**, so no video device, sensor, experimental boot, module or IR was activated. GStreamer **1.28.2** advertises defaults `sync=true`, `qos=true`, `max-lateness=5,000,000 ns` (**5 ms**) and processing deadline 15 ms. A real `fdsrc→rawvideoparse framerate=30/1→identity` timestamp probe, on an unmounted pipe with three tiny synthetic NV12 frames, produced PTS **0, 33,333,333, 66,666,666 ns**: those timestamps represent a nominal 30fps caps clock, not actual sensor delivery times.

Then, a controlled **camera-free** paced synthetic stream of **35 tiny 320×180 NV12 frames supplied at 22fps** was fed through a real GStreamer `fdsrc→rawvideoparse framerate=30/1→queue→fakesink` pipeline. `fakesink` was deliberately configured with the actual v4l2sink default clock/lateness/QoS parameters, while its handoff callback counted buffers that *reached the rendering boundary*. In one bounded run, that default-clock model rendered **4 of 35** buffers and dropped **31 as late**. Changing only the sink to `sync=true qos=true max-lateness=-1` rendered **35/35**. Changing to `sync=false qos=false max-lateness=-1` also rendered **35/35**. A separately timed synthetic `appsrc` model corroborated: default-clock model 5/35; no-lateness and unsynced models 35/35. The exact drop count varies with scheduling and is **not** the physical camera's 40/180 measurement. Four offline automated tests passed, including real installed factory defaults and fdsrc/rawvideoparse timestamp assignment, bounded paced frame delivery under three sink configurations and nonactivation checks. No synthetic raw video/image file was written.

**Interpretation and limits:** the normal 5-ms lateness drop on installed GStreamer has a directly reproduced mechanism for discarding many buffers when source delivery (~22fps) lags synthetic 30fps PTS. This is a **plausible, measurable candidate contributor** to the E004ka physical virtual-camera underdelivery, **NOT proof** that this particular setting caused E004ka's observed 40/180 buffers or that changing it alone will ensure continuous application 4K30. The model used small 320×180 synthetic data and a fakesink, not the physical 4K camera or real v4l2loopback queue. Independent source/loopback reader scheduling, thermal/backpressure and Windows ISP colour/exposure/detail parity remain unresolved.

## Next guarded physical gate

Use a **NEW uniquely identified**, source-locked, single-use camera-capable candidate (do not reuse consumed E004ka/E004jy) with the exact same bounded 180 real optical source → 4K NV12 → /dev/video90 → independent V4L2 stdout byte meter → E004jx app setup. Change the virtual output pipeline's sink explicitly to `v4l2sink sync=true qos=false max-lateness=-1` to test whether avoiding late-buffer drop improves the counted **publisher→independent reader** path. Keep real hardware timestamps, full output byte totals, app callback arrival cadence and fail-closed partial telemetry. An improved buffer count would not establish long-run 4K30 or Windows visual parity, and front QC10C decoding remains a separate task.

Reproduce the source-only probe without camera activation:

```bash
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004kb-gstreamer-sink-lateness-offline \
  -p 'test_*.py' -v
/usr/bin/python3 experiments/E004-front-ir-vd55g0/e004kb-gstreamer-sink-lateness-offline/gst_sink_lateness_probe.py --frames 35 --source-fps 22
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```
