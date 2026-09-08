# E003i BS — native AEC three-target preview profile

Status: **PASS (native/offline)**.

BS narrows BR's ordinary front-preview request API from seven current target-log lanes to the only three that can affect the proven single-exposure convergence path:

- Short;
- Long;
- Safe.

Current target S1, S2, S3 and S4 are no longer public inputs. This is an API projection for the already-scoped normal-streaming, AEC-unlocked, temporary-metering-lock-inactive path; it is not a claim that Windows never constructs those four metering target values.

## Why the four current S targets are dead here

BR's convergence kernel consumes `target_log[Safe]` in BasicSafe. `GetExposureInfo` is then invoked only for Short and Long, so its target lookup can only select `target_log[Short]` or `target_log[Long]`.

BC independently proves the active Windows front path has `activeExposureCount == 1`. Immediately before PopulateOutput, that path forces final S1..S4 to the final Short value. BR implements the same step before linearization. Therefore changing only current target S1..S4 cannot change any field of the ordinary-preview convergence output.

BS keeps the internal seven-lane carrier unchanged and initializes hidden target lanes to zero; only the first three public target logs are copied into it. Full F-1, F-2 and PipelineDelay/F-3 history records remain public. History reduction is deliberately deferred to a separate checkpoint.

## Verification

`verify-bs.py` fresh-runs BR, compiles BR and BS with `-Wall -Wextra -Werror -fno-fast-math`, and tests two independent invariants over 2048 deterministic request states:

1. two BR requests with identical Short/Long/Safe targets but deliberately different S1..S4 targets produce byte-identical complete output structures;
2. BS's three-target request produces that same byte-identical output.

The verifier also retains the fail-closed null/missing-history behavior and checks the exact native consumption/overwrite anchors above.

No camera stream, module load, sensor write, MMIO, Windows boot, or reboot is used.
