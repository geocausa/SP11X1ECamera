# E003i-F — native IQ proof backends

This checkpoint moves one layer upstream from the template-free capsule composer. It provides executable offline backends for every request-generated IQ class already isolated by E003i-E.

## Scalar and bank backend

`generate-steady-scalar-state.py` computes the 16 deterministic ping-pong bank fields from request parity and computes all eight true scalar fields from explicit AWB/predictive-gain/dGain/Demux-BLS inputs. The accepted matched request6 fixture reproduces all 8/8 scalar registers exactly.

## Front LSC backend

`generate-native-front-lsc-wire.py` executes the exact Surface Tintless callback sequentially for request4 → request5 → request6. It starts from request4 pre-state, carries its own generated wrapper/core state, and consumes config/stats/descriptors/pre-Tintless input mesh as request inputs. Captured post output is only a validator.

The generated four-channel mesh is converted directly to Titan680 LSC0/LSC1, with LSC2 zero and GIC0 derived from the proven LSC wire alias. **Captured 0x18a0 LSC staging is no longer an input.** Both zero and hostile `0xA5` fresh-core fills produce the same exact results.

`prove-native-lsc-0076-composition.py` feeds these generated LSC wires into the unchanged E003i-E composer and reproduces the accepted 0076 R4/R5/R6 capsule SHA256 values exactly.

The 44-file raw front atomic fixture remains outside Git under `.local-oracles` and is SHA-verified against the tracked manifest before use.

## GTM backend

`generate-native-gtm-wire.py` reproduces the independent 0073 adaptive-live request4/5/6 GTM payloads from TMC state using the exact Surface helpers plus the closed Titan680 setting loop. Captured `GTM_OUT` bytes are validation only. This fixture is intentionally a **different producer session** from the 0076 compatibility GTM state, so its hashes are not substituted into the 0076 regression.

## Production boundary

These are proof backends, not the final Linux runtime implementation. DeviceMFT execution under Unicorn remains an oracle mechanism. The next layer must acquire live Linux request state and replace proprietary native replay with clean-room runtime calculations while preserving the already-stable output contract:

`live state → {16 banks, 8 scalars, LSC, GTM} → template-free capsule → V4L2 IQ control → normal VB2 STREAMON`.

No Linux camera runtime is performed or authorized here.
