# E004jz — byte-exact 4K NV12 pipe boundary audit (source-only)

2026-09-21. Parent `2b7a30a`. The unique, consumed E004jy physical candidate captured **180 complete normal optical rear Bayer frames**, independently dequeued **69 complete-sized 4K V4L2 buffers**, but E004jx's app received **68 complete 4K frames** and then only **12,439,552 of the next 12,441,600 NV12 bytes** (exactly **2,048 bytes missing**) before an idle timeout. A V4L2 dequeued-buffer record does not prove that the frame's full payload subsequently reached stdout or the application pipe. The source of the final missing bytes, the ~20.54fps physical source rate under load and the downstream subscriber shortfall must not be guessed from the previous evidence.

This new isolated `nv12-4k-pipe-audit.c` is a low-overhead C pass-through instrument for a **future** standard V4L2 reader's stdout immediately before the E004jx app. It reads only from stdin and forwards exactly the same bytes to stdout, in fixed 65,536-byte chunks with robust short-write/EINTR handling; it does **not** change/convert pixels, open a camera or create a raw frame file. It reports only cumulative bytes **read** and **successfully written**, complete NV12 3840×2160 frame boundaries (12,441,600 bytes/frame), incomplete tail byte count and cause (clean EOF, idle, read/write/pipe error or bound violation), and monotonic timing of fully forwarded frame boundaries. It never emits content or frame hashes. It logs progress every ten full frames, rejects more than its fixed **1–120-frame** bound, uses a **100–15,000ms** configurable next-fragment idle limit and exits nonzero for a partial final frame, extra bytes, closed downstream or upstream timeout. A clean exact declared number of complete frames followed by EOF is required for its PASS status.

With the tool inserted *only inside a NEW uniquely named, source-locked, camera-capable, automatically Golden-returning candidate*, independent text evidence can distinguish a truncated `v4l2-ctl --stream-to=-` byte stream from data that was fully written at the pipe boundary but not counted by the GStreamer app. Reader stdout byte totals and app full-frame counts can be compared without saving image payloads. This **does not** itself diagnose kernel scheduling, source frame duplication, v4l2loopback queue/backpressure or deliver native Windows ISP quality; each still requires separate evidence. The old E004jy identity is consumed forever.

**Seven source-only SP11 Golden tests PASS**: byte-exact unchanged one- and two-frame output verified with in-memory SHA-256; exact 2,048-byte synthetic shortfall detected without counting a partial frame; open-but-stalled input exits boundedly; excess bytes/invalid bounds are rejected; the meter does not reference camera/boot/device APIs or create image files; and a separate **actual GStreamer app** accepts two complete offline synthetic NV12 frames through the meter. The standalone C binary compiled on the Golden ABI, source SHA-256 `95986174a00f30095169ecc6bcce9605026c982b046156793fc46a62c091b494`. The binary's offline test rate is **not a physical camera rate** and none of the E004jz tests activated camera or IR.

Source-only reproduction:

```bash
python3 -m unittest discover \
  -s experiments/E004-front-ir-vd55g0/e004jz-rear-4k-pipe-boundary \
  -p 'test_*.py' -v
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```

Next: source-lock and integrate this tool between a real independent V4L2 subscriber and E004jx **only after** a new camera one-shot is built with complete graph checks, isolated boot assets and unconditional Golden return. Independently measure source image-processing/virtual publication bottlenecks and avoid counting loopback repeats or synthetic PTS as native 4K30. Front QC10C displayable-video conversion, ordinary persistent Linux camera lifecycle and Windows OEM image quality matching remain unresolved.
