# Static proof

Pinned DLL SHA256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd9de785509c1fbebc975facc5286f12865cf675f1d`

## Table and fit

AQ mechanically closes `ApplyCoreTable@0x1803c35f8`, `UtilMakeTableExposureFit@0x1803c31f8`, the active T681 knee bytes and the positive normal-preview float32/truncation ordering. CH uses that exact arithmetic and the pinned preview limits.

## Final retained qword

AX proves the post-convergence selected compact exposure is consumed through the type-5 T681 path. In the final `ApplyCoreTable` tail `0x1803c3bd0..0x1803c4210`:

- the fitted gain is stored at table result `+0x00`;
- exposure time is stored at `+0x08`;
- correction is loaded and multiplied with the fitted gain/time product;
- `0x1803c41e4` invokes the `FRINTA` helper;
- the converted qword is stored at result `+0x18`.

The helper at `0x1800014b0` is exactly `frinta d0,d0`. For this positive finite scope CH implements that as nearest integer with halfway cases away from zero.

AX further proves result `+0x18` becomes rich arbitration record `+0x20` and is copied by `runEndOfFrame` into the next history record. Therefore `retained_exposure` is the correct feedback quantity, not AQ's intermediate `desired` field.

## Differential verification

`verify-ch.py` compares native gain bits, time, correction bits, final retained qword and selected segment against the independent AQ replay plus the AX retained-product rule over 65,569 deterministic cases spanning every knee neighborhood and all three table segments.
