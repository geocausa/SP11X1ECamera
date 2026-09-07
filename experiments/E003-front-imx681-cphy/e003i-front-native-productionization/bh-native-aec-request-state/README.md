# E003i BH — native AEC request state

Status: **PASS (static/offline + prior live replay)** — introduces a bounded, stateful offline request coordinator for the ordinary SP11 front AEC path without touching the live camera or sensor.

## History-layout correction

BH corrects one semantic label from AB while preserving AB's bit-exact arithmetic and live pairings.

`GetInternalFrameHistory()` returns the 432-byte saved payload at list-node `+0x10`. The payload begins with a 0x10-byte header; the seven saved exposure-lane blocks begin at payload `+0x10` and use stride `0x28`.

Algorithm001 computes `payload + 0x28*lane` and reads float `+0x20`. Therefore the actual read is **saved lane `+0x10`**, not saved lane `+0x20`. AB's old wording "history exposure record's dynamic Lux field at +0x20" is superseded by BH. The numeric value, F-3 selection, Algorithm001 formula, and all AB live/replay outputs remain unchanged.

The semantic producer of this float is intentionally left unnamed here. The state API calls it `history_reference` and requires it through an explicit commit seam rather than guessing.

## Steady-state Lux write closure

BG intentionally stopped short of claiming the ordinary steady-state writer. BH closes it mechanically inside `CAnalyzerAlgorithm001::RunAlgorithm`:

- constructs packed key `(type/bank=9, dataID=8)`;
- passes the computed Algorithm001 Lux float to generic setter `0x1803d6208`;
- the existing AB live capture breakpoint at the type-9 setter path observed the same dynamic values.

Thus the internal trigger recurrence is now explicit: FrameSA reads the Lux trigger present at request entry, then Algorithm001 writes the new `(9,8)` Lux value for subsequent request processing. AB's external publication remains a distinct **second-subsequent-publication** observation.

## Offline state model

`windows-aec-request-state.py` models the proven ordinary front boundaries:

1. request F enters with current `(9,8)` Lux trigger;
2. pinned BG FrameSA target curve is evaluated, including linear gap interpolation;
3. BD arithmetic produces the FrameSA Safe SI from current S1 source exposure and measured luma;
4. Algorithm001 reads explicitly committed F-3 `history_reference` and computes next Lux using the AB bit-exact formula (pinned alpha 0 on the captured front path);
5. internal Lux trigger updates after current target/SI evaluation;
6. the Algorithm001 result is queued as externally observable at F+2;
7. a separate seven-lane exposure-history seam exposes F-1 to downstream convergence without conflating it with the F-3 Algorithm001 history path.

This is deliberately not yet a complete autonomous AEC controller: the exact semantic producer of `history_reference` and the full AY/AZ/BA/BB convergence state are separate closure gates. Missing F-3 history fails closed.

No proprietary DLL, tuning blob, or live raw fixture is committed.

Reproduce:

```sh
./verify-bh.py | tee VERIFY-RESULT.txt
```
