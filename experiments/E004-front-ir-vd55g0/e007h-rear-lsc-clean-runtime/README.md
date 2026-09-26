# E007h — rear OV13858 clean LSC/Tintless userspace runtime

Parent Git: `ad6c9e40` (E007g fresh rear Windows oracle + 15/15 clean replay PASS).

Status: **USERSPACE PRODUCER PASS — 15/15 BYTE-EXACT / NO LINUX CAMERA RUNTIME**.

## Goal

Turn E007g's clean rear LSC/Tintless proof into a reusable production-shaped userspace producer, following the same architectural split already accepted for the front camera:

- adaptive IQ math/state in userspace;
- fixed clean authority rather than proprietary tuning bytes at runtime;
- kernel/materializer consumes already-produced wire payloads;
- live stats/3A scheduling remains a separate ownership boundary.

## Clean authority

`authority.json` is a 35,072-byte derived authority file. It contains only:

- selected rear lower-AEC LSC41 leaves `0x29c/0x29e/0x2a0`;
- decoded golden calibration values;
- decoded OV13858 calibration-slot channels;
- preserved rear Tintless x1 configuration;
- source-derived rear geometry/domain metadata and provenance hashes.

It does **not** embed the proprietary rear tuning blob, raw Windows captures, or raw request DMI payloads.

`derive-authority.py` deterministically regenerates the authority from the pinned reverse-engineering evidence. Current SHA-256:

`30f7b36402e8f55c8824d7d97ef560409e15f9f2495a62db56befca2f49c0965`.

## Runtime

`rear-lsc-runtime.py` exposes `RearDynamicLsc`.

Inputs per request:

- parsed Tintless stats object;
- lux;
- CCT.

Outputs:

- selector-1 LSC payload (884 bytes);
- selector-2 LSC payload (884 bytes);
- selector-3 LSC payload (884 bytes);
- derived GIC alias (512 bytes).

The implementation reuses the already-accepted clean interpolation/calibration helpers, generic source-derived geometry resampler, native mode-2 Tintless C core, wrapper temporal carry, Q10 conversion and Titan680 wire packer.

The runtime has no path to the rear proprietary tuning blob and no path to the E007g Windows capture.

## Validated domain

The fresh E007g sequence proves the **rear lower-AEC branch** only. E007h therefore fails closed outside the source-locked range rather than extrapolating:

- lux: 1..340 inclusive;
- CCT: 1..10000 inclusive;
- lower-AEC CCT topology: `0x29c -> 0x29e -> 0x2a0` with exact source gaps.

Upper-AEC rear LSC topology remains a separate future closure item.

## Differential proof

`prove-runtime.py` was run against the private E007g R4..R18 oracle from the Windows volume mounted read-only, then the volume was immediately unmounted.

Result: **15/15 requests exact** for LSC0, LSC1, LSC2 and GIC.

No raw Windows payload is committed.

## What remains

This closes the reusable rear LSC/Tintless **userspace producer** for the validated lower-AEC domain.

Still open:

- live rear Titan680 TLBG -> parsed Tintless-stats ingress;
- rear live lux/CCT/3A reconstruction and request-generation correlation;
- kernel/capsule scheduling and 884-byte selector handoff;
- upper-AEC rear LSC authority;
- GTM/TMC and other remaining DMI/live-state families.

No Linux camera stream, module load, DMI submission or RT-CDM submission occurred.
