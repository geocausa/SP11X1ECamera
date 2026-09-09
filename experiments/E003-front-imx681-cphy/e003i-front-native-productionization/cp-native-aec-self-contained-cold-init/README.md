# E003i CP — self-contained ordinary cold AEC initialization

Status: **PASS (Windows static + bounded live oracle + native/offline)**.

CP closes CO's final two ordinary front-preview initialization seams. The native request loop no longer accepts caller-supplied initial Lux or Algorithm001 blend alpha: `e003i_request_loop_init()` now takes only the state pointer and installs the complete fixed ordinary cold-preview state internally.

A fresh same-machine Windows oracle was gated before `StartAsync`, with CDB attached to FrameServer before streaming. At `CAECXControl::QueryControlStartExposure`'s common Lux join, the direct startup-Lux override was invalid/zero, so the `CalculateStartLuxIndex` path was taken. The published initial Lux and its controller input were both exactly `0x4365b24a` = `229.69644165039062f`. The startup-exposure operand at this call was 33,333,333; this is deliberately kept distinct from CN's synthetic retained-history lanes, which are 33,333,332.

The same run stopped immediately after `CAnalyzerAlgorithm001::RunAlgorithm` loaded object `+0x70`: both memory and `s18` proved exact `+0.0f` (`0x00000000`) alpha. This independently confirms the earlier AB2 live observation.

CP therefore owns three startup contracts:

- CN synthetic retained exposure history: frame 0, Short/Long/Safe/S1 = 33,333,332;
- ordinary cold initial Lux: exact float32 bits `0x4365b24a`;
- ordinary fixed-profile Algorithm001 alpha: exact float32 bits `0x00000000`.

The public initialization API is now `e003i_request_loop_init(state)`. The verifier fresh-runs CO, pins the Windows DLL and oracle hashes, rechecks the exact disassembly sites, compiles CP with strict FP flags, and compares 192 deterministic cold-start sequences / 2,304 requests against an independent CN history selector + FrameSA + CF + CG + CH composition. All outputs are byte-exact.

The Windows oracle performed one normal front-camera Start/Stop cycle with read-only debugger breakpoints. SP11 returned to the exact Golden Linux kernel; persistent BootOrder/GRUB default were unchanged. CP performs no Linux camera module load, STREAMON, sensor write, or MMIO runtime.
