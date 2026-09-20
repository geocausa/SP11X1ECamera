# E004ju — unique real rear 4K candidate with interpreter-locked route checks

2026-09-20. Parent `bd4205c`; NEW identity, never reuse consumed E004jq/E004jt or nonstreaming E004js. E004jt independently **proved complete media graph** (44 nodes) at its first attempt, but failed closed *before optical capture* because its route-state.py source was mode 0644 and the runner invoked it as an executable. E004ju preserves accepted hardware components and graph-gated 4K pipeline, fixing **all four route checks** to use `/usr/bin/python3 "$H/route-state.py"` rather than assuming an executable bit. A new automated regression checks four exact interpreter invocations, non-executable helper mode, archived graph parse, complete media gate **before** test-pattern/optical capture and matching isolated boot paths.

This unique candidate source, reboot/one-shot, install/arm/retire and 27-frame bounded 4K bridge are separate from the consumed E004jt program. An accepted rebuilt 51-file package has manifest SHA `9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455`. Its new private same-kernel GPL loopback SHA `cd98e3ddc76bd3e8b794876e84f38e9316777f362e050780eafa0add0fd08f9b`; new C bridge SHA `694fb2673b785cbed706469d5e64e3df808f75bf35df8c82dd579c04f49c9fd4`. The separate bounded E004jr media diagnostic and E004jn app are source SHA-locked and copied privately in the candidate. No default Golden kernel/DTB/initrd, boot saved entry, front Linux webcam, IR illumination/Hello or camera service is modified.

A passed *current-boot* bounded non-image media graph (all required roles and preserved stderr/return code) and explicit interpreter-run unified graph parser are mandatory **before** test-pattern and optical streaming. After exact archived rear hardware colourbar acceptance, the physical OV13858 would produce 27 normal 4076×2806 Bayer frames, converted via transient pipes to 3840×2160 NV12 to standard /dev/video90, with a separate V4L2 app reader checking eight 4K samples and GStreamer appsink. No normal optical pixels are written to disk. Even if this finite physical test succeeds, neither long-duration 4K30, OEM Windows image-processing parity, native hardware ISP nor front QC10C decoding is claimed. Any failure consumes E004ju permanently, records redacted evidence and unconditionally returns to protected Golden before retiring unique temporary assets.

Replay source-only gates:

```bash
python3 -m unittest discover -s experiments/E004-front-ir-vd55g0/e004ju-real-rear4k-python-route-one-shot -p 'test_*.py' -v
python3 -m unittest discover -s experiments/E004-front-ir-vd55g0/e004jr-media-graph-diagnostic -p 'test_*.py' -v
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```
