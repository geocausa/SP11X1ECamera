# Static proof

Pinned DLL SHA256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd9de785509c1fbebc975facc5286f12865cf675f1d`

## Table and fit

AQ mechanically closes `ApplyCoreTable@0x1803c35f8`, `UtilMakeTableExposureFit@0x1803c31f8`, the active T681 knee bytes and the positive normal-preview float32/truncation ordering. CH uses that exact arithmetic. The active preview limits are no longer inferred from a nearby qword: AQ's 2026-09-10 read-only controller recapture pins controller `+0x190` to the active T5 header and the same controller object to min gain 1.0, min time 37,516 ns, max gain 92.0, max time 66,666,664 ns, with policy `+0x1a0=0`. The recapture ZIP SHA-256 is `809e7d58ba5605cbd5f98bcc2e2b41c12843dcc79e91cf2fd86e43647a9e8c67`.

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

`verify-ch.py` compares native gain bits, time, correction bits, final retained qword and selected segment against the independent AQ replay plus the AX retained-product rule over 65,571 deterministic cases spanning every knee neighborhood and all three table segments.
