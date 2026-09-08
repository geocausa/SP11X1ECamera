# E003i BP — native AEC fixed normal-preview convergence profile

Status: **PASS (target-native/offline)** — the normal-preview convergence tuning/profile is now internal to the native boundary. BP removes BL's remaining caller-selectable tuning seam for the ordinary SP11 front IMX681 preview path. It does not alter any earlier checkpoint.

## Fixed Windows profile

BP injects the values mechanically closed by BM, BN and BO:

- PipelineDelay = `3`;
- FastConv baseSpeed = `0.8f` (`0x3f4ccccd`);
- baseCapping = `0.33f` (`0x3ea8f5c3`);
- drcSpeed = `0.15f` (`0x3e19999a`);
- cappingType = `2`;
- tolerance = `2`;
- minimumStep = `0.5f` (`0x3f000000`);
- ConvStretch = dataID 2 `DisableStretch`, leaf `(weight,factor,comp,tempWeight)=(1,1,1,1)`;
- DRC policy = `0`.

The DisableStretch leaf is preserved through the generic AZ filter rather than approximated: factor 1 materializes to offset 0 and tempWeight 1 makes `filtered=(1-1)*previousDelta + 1*0 = 0`, so Short/Safe/Long remain BasicSafe and predictive gain remains 1 for arbitrary retained delta.

## Public boundary after BP

`e003i_converge_front_preview()` accepts only:

- the seven current target-log lanes;
- F-1, F-2 and PipelineDelay-selected linear exposure history, including their runtime DRC gain / retained-delta state;
- the still-unresolved runtime BasicSafe gates (`intolerance_gate`, `small_delta_exemption`);
- the still-unresolved GetExposureInfo state words for Short and Long.

There is deliberately no public PipelineDelay, speed, capping, tolerance, stretch, minimum-step or DRC-policy input. Those are no longer choices at this boundary. Because DisableStretch fixes `StretchRatio=1`, BA policy-specific overlap branches (which require both stretch and DRC ratios greater than one) are also unreachable on this normal-preview path; BO policy 0 remains pinned but does not introduce a caller-visible branch choice here.

## Verification

`verify-bp.py` reruns BM/BN/BO, compiles both BL and BP warning-clean with `-fno-fast-math`, and differentially compares BP against BL configured with the exact fixed profile over a deterministic corpus spanning target/history motion, retained deltas, DRC gains and all combinations of the four unresolved runtime state controls. It also fails if the BP public header exposes any of the removed tuning knobs.

Safety: static/offline only. No camera stream, module load, sensor write, MMIO, reboot, Windows mount or Windows execution.

## Remaining seam

The next substantive upstream boundary is not tuning selection. It is generation of the seven current target-exposure lanes and closure of the four explicit runtime state/control fields. BK still owns temporal request/history recurrence; BP now owns a fixed-profile convergence tail once those request-local values exist.
