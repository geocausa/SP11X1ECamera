# AY static proof anchors

Pinned function: `CAECXConvergence::ComputeBasicSafeConvergence` at VA `0x1803ce400` in the pinned DeviceMFT.

## Request-local tuning and histories

- `0x1803ce43c`: load request-local ConvBase pointer from convergence `+0x2f0`.
- `0x1803ce460`: load camera/context pipeline selector byte `+0x8ec`.
- `0x1803ce468`: `GetInternalFrameHistory(selector)`.
- `0x1803ce550..55c`: explicit history selector `1`.
- `0x1803ce6bc..6c8`: explicit history selector `2`.
- selected safe history exposure is `history +0x78` and is converted through the common reciprocal-log(1.03f) scale.

## Interpolated ConvBase core

- `0x1803ce810..820`: three trigger values feed the ConvBase interpolator.
- returned core pointer is saved at convergence `+0x308`.
- `0x1803ce8c8`: core `+0x08` (`drcSpeed`).
- `0x1803ce8d0`: core `+0x00/+0x04` (`baseSpeed/baseCapping`).
- `0x1803ce8d4`: request-local capping type `ConvBase +0x18`.
- Windows diagnostic at `0x1813becd0`: `Core data: baseSpeed:%f baseCapping:%f cappingType:%d drcSpeed:%f`.

## Deltas and direction

- `d14 = targetSafeLog - history1SafeLog` (`0x1803ce5f4..5f8`).
- `d15 = history1SafeLog` (`0x1803ce680..6a8`).
- temporal motion `d8 = history1SafeLog - history2SafeLog` (`0x1803ce6d8..708`).
- `0x1803ce70c..720`: save whether `temporalMotion * targetDelta >= 0`.
- delayed delta `d13 = targetSafeLog - delayedHistorySafeLog` is formed earlier from selector `+0x8ec`.

## Capping law

- candidate: `0x1803ce9f0`, `baseSpeed * targetDelta`.
- type 0: `0x1803cea4c`, `baseCapping * delayedDelta`.
- type 1: `0x1803cea30..44`, signed `baseCapping` using target-delta sign.
- fallback: `0x1803cea20..28`, delayed delta divided by camera/context `+0x8ec` pipeline delay.
- `0x1803cea50..6c`: `fabs` both candidate/cap and select the lower-magnitude signed operand.

## Guards

- intolerance log string: `CID:[%d] Skip safe convergence. willBeIntolerance:%d, prevDelta:%f, tol:%d.`
- request-local integer tolerance: ConvBase `+0x14`.
- runtime intolerance gate: convergence `+0x2b4 == 1`.
- history(1) previous delta: float at `+0x17c`.
- inline float guard `0x33d6bf95 ~= 1e-7` at `0x1803cecc0`.
- inline float guard `0x3f800001` at `0x1803cecc4`.
- residual snap to exact target: `0x1803cea9c..ac0`.
- runtime minimum-step threshold: config pointer `convergence+0x138`, float `+0x2c` (`0x1803ceac4..ad8`).
- direction-reversal suppression: `0x1803ceb44..b60`.

## Seven-lane BasicSafe output

`0x1803cebfc..0x1803cec0c` broadcasts the same resulting double to:

`+0xa0,+0xa8,+0xb0,+0xb8,+0xc0,+0xc8,+0xd0`.

This is BasicSafe output only. `ComputeTargetStretchOutput`, DRC aggregation and final sensor-exposure conversion run later.
