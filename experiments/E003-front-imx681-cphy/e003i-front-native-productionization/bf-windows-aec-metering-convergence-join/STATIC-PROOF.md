# BF static proof anchors

Pinned `QcDeviceMFT8380.dll` SHA-256:
`c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

## Metering output

- `0x180374714`: x2 = `controller+0x14b38` for external metering postprocess callback `+0x30`.
- Postprocess seven-output layout is x2 `+0x38..+0x68`.
- Arithmetic: `0x14b38 + 0x38 = 0x14b70`; seventh qword = `0x14ba0`.

## True `CAECXControl::runConvergence`

Entry: `0x180374ab8`.

Normal setup:

- `0x180374ee8`: x24 = `controller+0x14b70`.
- `0x180374ef8`: x1 = x24.
- `0x180374efc`: call pre-convergence bridge `0x180389dd0`.
- `0x180374f04`: store returned pointer at `controller+0x14ca8`.
- `0x180374f0c`: load current FrameID from controller `+0x165d0`.
- `0x180374f10`: store FrameID at `controller+0x14ca0`.
- `0x180374f18..0x180374f38`: copy exactly seven qwords from `+0x14b70..+0x14ba0` to `+0x14cb0..+0x14ce0`.
- `0x180375150`: x1 = `controller+0x14ca0`.
- `0x180375154`: x2 = `controller+0x14cf8`.
- `0x180375158`: external callback slot `+0xb0`, already mapped by AR to `RunConvProcesss`.

Therefore convergence input layout is:

```text
+0x00 FrameID
+0x08 pre-arbitrated target-record pointer
+0x10 target[0]
+0x18 target[1]
+0x20 target[2]
+0x28 target[3]
+0x30 target[4]
+0x38 target[5]
+0x40 target[6]
```

## Pre-convergence bridge `0x180389dd0`

- `0x180389de0`: w4=1.
- `0x180389dec`: call `RunControlArbitration`.
- returned rich records are copied into seven 0x50 records rooted at child `+0x688`.
- `0x180389efc`: return `child+0x688`.

## Core convergence

`RunConvProcesss` at `0x1803b38c0`:

- `0x1803b3904`: preserves output x2.
- `0x1803b3908`: preserves input x1 in x23.
- later dereferences x23 members, mechanically proving x1 is a structure pointer.

## Post-convergence arbitration

- `0x1803723c0`: w4=0.
- `0x1803723c8`: x1 = `controller+0x14cf8`.
- `0x1803723d0`: call `RunControlArbitration`.
- returned 0x3c0 block copied to `controller+0x14da8`.

AR/AQ then close:

`RunArbitrationInput+0x198 = child+0x268` (T681 base exposure), while input `+0x138/+0x160` carry the log1.03 exposure-coordinate candidates. AQ's normal table path converts coordinate + base to desired exposure and applies T681.

Fresh verifier joins: BD, BE, AX, AR, AQ, BC, AW, AP.
