# DL — exact failure and omitted cap stage

## Consumed runtime

DB attempt4 used base commit `8bc6598` and the DK helper. Its three successful control sets were {FLL3562, EXP3554, AG851, DG256}, {FLL3562, EXP3554, AG960, DG556}, and {FLL7116, EXP7108, AG960, DG1111}. The fourth AEC generation returned -142 before a fourth write. The failed pair is preserved, with matching generation/source/slot headers. The persistent helper deliberately remained pinned; it was not killed or retried. Golden return passed and the disposable boot bundle was archived outside /boot.

The unchanged source replay reproduces every first-three control field and the G4 error. CU returns -132; CV adds -10. At G4, delayed S1 is request4's retained exposure 197,553,039. Current metering produces Short 32,233,622,719 and Safe 45,127,069,396. Native convergence produces Short 24,819,566,146, above T681's serialized maximum 6,133,333,272. Error handling preserves both caller recurrence and caller control output.

## Missing Windows stage — primary next boundary

Pinned DeviceMFT SHA256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

Windows RunConvProcesss calls PopulateOutput at RVA 0x3b63f0. PopulateOutput converts seven log exposures to integer qwords, then **unconditionally calls CapExposure at 0x3ce03c -> 0x3d33e0**, before publishing PredGain at 0x3ce040..044.

The native DJ loop sends CG convergence output directly to CH arbitration. There is no corresponding cap stage. `verify-cap-stage.py` checks this omission and the exact Windows instruction anchors.

Bounds are request-local data, not safely inferred from the four serialized T681 knees:

- runConvergence saves the pre-convergence arbitration bridge return at controller+0x14ca8 (convergence input+8).
- RunConvProcesss copies input+8 to convergence+0x98 at 0x3b44d0..4d8.
- The bridge returns child+0x688, holding seven 0x50-byte min/max records.
- Internal CapExposure reads lower/upper qwords at +0x18/+0x40, then stride 0x50 for all seven lanes.
- Its unconditional tail clamps each lane, imposes cross-lane order, sets S1 to Short, orders S2..S4, and limits PredGain using float32 Safe/Short.
- Its earlier conditional path can proportionally rescale Short and S1..S4 when Safe exceeds its maximum, with a history-based snap. A simple universal clamp would omit that behavior.
- RunConvProcesss also consumes the common bound field +0x230 before PopulateOutput; its ordinary meaning remains to be recovered.

**DC and DG do not close this stage.** DC observed a separate controller-level cap loop at 0x3754d8 with flag0/no hits. That does not disable the internal PopulateOutput cap. DG injected an over-range compact Short at 0x3723d0, after convergence and its internal cap had already run; Windows' later table rejection remains valid but says nothing about the input/output law of the omitted cap.

This establishes a concrete native parity gap. It does not yet establish the exact normal-preview min/max values or prove that this is the only remaining cause of DB's failure. No cap math or delay was patched speculatively.

## Secondary timing observation

Measured FrameSA luma is 0.898956835, 0.886852384, 0.886802614, 0.883978605 for G1..G4. BHist mean G4/G1 is 0.9826156057. Thus no brightness increase is visible by G4 in this capture.

DB's first full-tuple ioctl lasts 20.605353 ms, compared with 1.802121 ms for CY's single exposure step (11.43x). DB's DQBUF counter gate passes, but it does not timestamp sensor group-hold release or prove the exact optical latch frame. G5/G6 raw pairs were not preserved by the old failure collector. These facts justify a later association/timing audit; they do not establish a new delay constant.

## Validation and scope

Run `python3 verify-dl.py` and `python3 verify-cap-stage.py` in this directory. They perform offline work only. Tests pin capture hashes and source baseline, verify paired identities, compile with warnings as errors, compare replay against actual live tuples, reproduce the failure, verify atomic error handling, and check Windows cap-stage anchors.

No production source, exposure table policy, boot payload, or control schedule is changed by DL. No new hardware experiment was started.
