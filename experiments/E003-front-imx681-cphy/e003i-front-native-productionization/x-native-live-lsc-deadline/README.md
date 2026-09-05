# E003i-X — native live-LSC producer deadline closure

Status: **PASS (offline scheduling/ABI proof; no camera runtime).**

W dynamically proved the request/statistics law by exact pointer identity: `request_frame = source_generation + 3`. Therefore request4 consumes G1, request5 consumes G2 and request6 consumes G3. Static inspection of the existing Linux runner shows G2 is already published before the request5 IQ-provider dequeue and G3 is already published before request6, so hardware availability is not the scheduling blocker.

## Current front tuning authority

This checkpoint deliberately keeps the repaired 2026-09-04 **front IMX681** authority used by stages G/K/M. It does **not** substitute the older independent Windows stream whose resolved LSC object used the rear/default tuning tree.

The current front tree is decoded directly from SHA-pinned `com.surface.tuned.ffc_imx681.bin`:

- LSC control vector `[8,2,5,100,0,6]`;
- AEC selector is the generic trigger vector's index 0, already proved to be `ISPIQTriggerData.AECLuxIndex`;
- lower AEC branch is `1..390`, upper branch begins at `490`;
- in the lower AEC branch, CCT `3400..4500` resolves front leaf `0x4bd`, CCT `5000..10000` resolves front leaf `0x4bf`, with only the gaps interpolating.

W request4/5/6 have lux `358.0217 / 358.097046 / 357.9939` and CCT `5096 / 5082 / 5098`, so all three W requests select **front leaf `0x4bf` directly**. The resulting calibrated/resampled pre-Tintless mesh SHA256 is `ec60c6de7557b24493fdeaa8cefe464601e8c383e111985b1ebf99a434b88201`.

## Why a native hot path is necessary

The existing clean-room Python implementation is the correctness oracle but is too slow for live 30-fps production. On SP11 it took about 423 ms/frame; PyPy reduced the same algorithm to roughly 113–136 ms/frame, still above the 33.33 ms frame budget. Profiling showed the cost was Python call/SparseMemory overhead in the already-closed mode-2 Tintless numerical core and fixed 17×13 geometry resampler, not a missing algorithm.

`native-tintless-core.c` is an independent C translation of only those two proven hot primitives:

1. active front mode-2 Tintless core;
2. fixed front 17×13 calibrated-mesh geometry resampler.

It is built with `-fno-fast-math -ffp-contract=off` and strict warnings. No DeviceMFT code or Windows binary is linked or executed.

## Differential acceptance

`prove-native-live-lsc-deadline.py` requires:

- native resampler byte-exact against the Python clean-room reference over ratios `0`, `0.001`, `0.1234567`, `0.212`, `0.342`, `0.5`, `0.6770310998`, `0.999`, and `1`;
- G1→G2→G3 hybrid sequence output byte-exact to the original Python wrapper;
- complete `0x1090` wrapper history byte-exact;
- complete `0x126e8` core state byte-exact;
- W +3 mapping and front-tree selector assertions remain true.

Accepted G1/G2/G3 LSC0 hashes are:

- G1 `74b0ce6529fcab7036a071c1aa2c38e3898f9db4f9bf05a799c0e463fdca6c8a`
- G2 `f1ef5dbeb14c77b22ea623c3e41beb09453b8d65e443d4b3f63eba844e61d484`
- G3 `d033b4f75a0f82ff4fe311ea79ef2f58af320a2bb51007d74b9c12e6bf5ead78`

These are **not** claimed as Windows parity outputs: W trigger state and U Linux TL_BG are independent streams. They prove ABI/state continuity and scheduling capacity only.

## Deadline result

100-iteration accepted SP11 benchmark, conservative sum of independent p95 components:

- current W direct-leaf/cached path: **5.387 ms**;
- arbitrary changing interpolation ratio path: **7.131 ms**;
- frame budget at 30 fps: **33.333 ms**.

Thus producer compute time is no longer the R5/R6 blocker, even if the front tree enters an interpolation gap on another scene.

## Remaining gate

Dynamic Linux R5/R6 substitution remains **unauthorized**. The next gate is to acquire Linux request-local **AEC lux index and CCT** early enough to select the front LSC tree, preferably through an existing standard V4L2/libcamera request/metadata surface. Then perform one bounded producer→existing V4L2 IQ FIFO integration proof using the proven selection rule R5←G2 and R6←G3. Do not invent request IDs from source generation and do not add a private ioctl unless the standard surfaces are conclusively insufficient.

Reproduce with a readable copy of U's root-owned snapshots, for example:

`./prove-native-live-lsc-deadline.py --snapshot-dir /tmp/e003i-x-u`

The committed `RESULT.json` is the accepted run. No generated `.so` is committed; it is rebuilt from source for every proof.
