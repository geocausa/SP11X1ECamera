# E003i BL — native AEC single-exposure convergence kernel

Status: **PASS (target-native offline)** — composes the already-proven AY/AZ/BB/BA/BC Windows convergence stages into one warning-clean ARM64 Linux C kernel. No live camera, sensor, module, MMIO, reboot, or Windows execution is involved.

## Closed native chain

The implementation accepts values after Windows' request-local tuning/trigger machinery has already resolved them and executes:

`AY BasicSafe -> AZ ConvStretch aggregation -> BB GetExposureInfo(0/1) -> BA DRC/stretch policy -> BC activeExposureCount==1 tail -> seven linear qwords`.

Inputs are explicit and bounded: seven current target-log lanes; F-1, F-2 and pipeline-delayed exposure history; the resolved ConvBase tuple and control words; already-materialized ConvStretch runtime records plus aggregation controls; two GetExposureInfo state words; and the DRC policy.

## Important coordinate-domain correction

BL keeps two previously easy-to-confuse log coordinates separate:

- **convergence history:** absolute `log_1.03(linear exposure)`;
- **Algorithm001/BJ history:** T681-relative `log_1.03(linear exposure / 37516)`.

BK/BI/BJ use the second form only for Algorithm001's F-3 S1 baseline. AY/BB convergence must use the first form. BL implements the absolute form with the exact shared Windows log10 scale recovered by BJ (`0x429bcc0c`) but without dividing by T681's base exposure.

## Differential verification

`verify-bl.py` freshly re-runs AY, AZ, BB, BA, BC and BJ, compiles `native-convergence.c` with `-Wall -Wextra -Werror -fno-fast-math`, and compares the composed native result against the five pre-existing clean-room Python stage models over 768 deterministic cases spanning:

- all three BasicSafe capping modes;
- all five ConvStretch aggregation modes;
- Short-history DRC-gain adjustment and Long history;
- state-word variations;
- all three valid DRC/stretch policies.

The older AY/AZ/BB/BA analytical models predate BJ's exact Qualcomm log10-helper closure and use mathematically equivalent natural-log scaling. BL intentionally uses the newer exact helper semantics. Results:

- maximum log-coordinate deviation from those older analytical models: `5.34057617e-05` step;
- 650/768 final seven-qword vectors exactly equal;
- every non-identical final qword differs by no more than one integer exposure quantum.

A fixed fully-composed case matches every important boundary exactly, including final `[18,19,20,18,18,18,18]`.

## Remaining seam

BL does **not** invent request-local tuning selection. The unresolved upstream seam is the request's actual ConvBase/ConvStretch/profile materialization and policy selection (plus the already-distinct metering/target-lane producer feeding `target_log[7]`). Once those values are supplied, the convergence-to-seven-linear-lanes tail itself is native and closed.

Reproduce:

```sh
./verify-bl.py | tee VERIFY-RESULT.txt
```
