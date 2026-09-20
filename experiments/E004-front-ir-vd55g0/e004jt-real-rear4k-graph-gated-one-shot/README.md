# E004jt — first graph-gated live rear 4K virtual-camera candidate

## Actual E004jt one-shot result — fail closed before sensor capture

One-use camera-capable candidate `e1bb0532-83e8-4697-8e3b-5449c784325c` passed package/GRUB/source guards and the improved current-boot graph diagnostic on its **first** try: complete 44-entity media graph, no stderr, 19,279 bytes of topology, and successful independent unified parser. The next command was the pre-stream route-state checker. The system journal reports `run-once.sh: line 190: .../route-state.py: Permission denied`, with service exit code **126**: the committed `route-state.py` was mode **0644** and the runner mistakenly executed it directly instead of invoking Python. Thus the rear test pattern, normal optical capture, 4K converter, standard virtual webcam and app **never ran** in this candidate; the kernel did not report an Oops/panic or IR-illumination-on marker. The service automatically returned to Golden boot `5033a749-f6da-4eb3-b7d0-155835a2ef4b`, original saved entry with empty next_entry and no experimental camera modules/nodes. The unique candidate service, boot entry, copied modules, private logs and stage were retired, and `evidence/PRE-CAMERA-ABORT.json` marks the **E004jt identity consumed; never rearm it**. See `RESULT.json`.

The failure is a launch-script executable-permission defect, **not** a sensor, media graph, 4K algorithm or 4K delivery finding. A NEW uniquely identified candidate must explicitly call `/usr/bin/python3 route-state.py` everywhere, include an offline static check for the route helper's non-executable mode, pass the same graph-first checks and use its own fresh single-use Golden-returning boot. It still must not claim live 4K optical video until independent app buffers are observed.

2026-09-20. New single-use identity distinct from E004jq (consumed fail-closed) and E004js (consumed diagnostic pass). Source parent `0c9b2c5`. Goal: only after verified *current-boot* complete 44-role media graph gate, connect actual OV13858 optical RAW10 4076×2806 to the bounded E004jm 3840×2160 NV12 converter, standard 4K /dev/video90, independent V4L2 subscriber and GStreamer application.

## What is already physically demonstrated vs not

E004jh proved real optical **1080p** selectable Linux rear webcam. E004jp separately proved a synthetic **4K** selectable Linux webcam and eight consumer buffers. E004js separately proved same exact accepted three-sensor package boot can provide a complete 44-entity media graph on first attempt, with all sensors suspended and no streaming. E004jm/jn proved archived rear colourbar→4K NV12→GStreamer app **offline**. These are distinct observations, not proof of a native 4K optical Linux webcam, Windows ISP-quality processing, sustained 4K30 or front QC10C display.

## Candidate source and isolation

The exact 51-file accepted camera stack (CAMERA-STACK-MANIFEST.sha256 `9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455`), known Golden-v4 ABI module hashes, Windows-derived R4 bootstrap, isolated copied kernel/initrd and camera DTB are hash checked. Source-only bounded rear C converter binary SHA `adb7925376f61ebf81e30b07f05cabcccde41b400676a9a5b24e7c24903af3c4` preserves earlier offline output and admits up to 27 frames. Rebuilt disposable GPL v4l2loopback SHA `52ca41e7a6dd510f1034458969255dfd1f55c244c50830ab12ea1f18795f0379` matches current kernel `vermagic`. The separate E004jn GStreamer app SHA and original rear physical archived colourbar fixture are checked before arming. None of these binaries or modules is installed into Golden.

**New critical safety gate:** root-owned E004jr diagnostic source SHA `4435c52d364e4030285c3e74372446eb452fa5722c355301201812a6d2341348` is root-copied to candidate stage. The candidate captures bounded real `media-ctl -p` device inventory, error text and graph role verdict *before* any sensor pattern, route change or optical capture. It proceeds only when that current boot's complete graph and original `discover-unified.py --from-file` both succeed. Otherwise it fails closed and records non-image diagnostics. Previously E004jq swallowed discovery stderr; E004jt does not.

The source-locked single-use GRUB entry preserves the original saved Golden default and returns automatically after success, failure or timeout. Only the rear RGB sensor is deliberately streamed. The front camera is only probed in standby; IR illumination/Hello are never requested. The original 1080p endpoint stays untouched in protected Golden.

## Acceptance is deliberately narrow

The candidate first validates archived *hardware colourbar* from the real rear sensor with exact expected SHA, then disables the test pattern and requires 27 normal optical rear Bayer source frames into transient private pipes. The optimized but **uncalibrated** converter publishes 4K NV12 to /dev/video90. An independent ordinary V4L2 subscriber must read eight correctly sized 4K NV12 buffers and pass them into E004jn's GStreamer I420 application. Source capture sequences/timestamps, virtual buffer sequences, reader count and app format are independently validated. No normal optical pixel payload is stored in a file. Timing is bounded, and the disposable endpoint is removed and rear route neutralized before return.

Even successful finite streaming would NOT establish multi-minute 4K30 camera reliability, Windows colour/exposure/focus/sharpness parity, native OEM ISP processing, native camera module default, or front QC10C conversion. No synthetic result should be described as real optical. If any source format, timing, media graph, colourbar or consumer condition fails, report the actual failure, DO NOT rearm this identity, inspect the precise private logs and return to Golden.

## Offline verification

```bash
python3 -m unittest discover -s experiments/E004-front-ir-vd55g0/e004jt-real-rear4k-graph-gated-one-shot -p 'test_*.py' -v
python3 -m unittest discover -s experiments/E004-front-ir-vd55g0/e004jr-media-graph-diagnostic -p test_media_graph_diagnostic.py -v
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```
