# E003i BM — Windows AEC convergence tuning selection

Status: **PASS (static/offline)** — closes the request-local tuning-selection pieces that are selector-independent in the pinned SP11 IMX681 tuning, without overclaiming the remaining convergence control words.

Pinned inputs:

- `QcDeviceMFT8380.dll` SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`
- `com.surface.tuned.ffc_imx681.bin` SHA-256 `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`

## Request-local bank mechanics

`CAECXConvergence::RunConvProcesss` queries the controller rings at `+0xdef0` (`aecxdbconvbase`) and `+0xdf50` (`aecxdbconvstretch`) with dataID 0, then retains the selected records at convergence `+0x2f0/+0x2f8`.

The Windows priority evaluator at `0x1803d4438` constructs a context bitmask. A rule containing only context 0 is the unconditional fallback; other rules match only when all required context bits are active. Strictly higher signed priority wins and selects that rule's dataID. `GetData@0x1803d4968` with query 0 returns the cached automatic selection.

## ConvStretch is selector-independent

The pinned tuning contains exactly one `aecxdbconvstretch` module. Its five priority records are:

```text
contexts {0}  priority 0 -> dataID 2
contexts {2}  priority 1 -> dataID 2
contexts {10} priority 2 -> dataID 2
contexts {23} priority 2 -> dataID 2
contexts {11} priority 2 -> dataID 2
```

Thus every reachable context combination selects **dataID 2 = `DisableStretch`**. `DarkBrightStretch` exists as dataID 1 but no automatic priority record selects it.

`DisableStretch` has `stretchType=0` and a single nested leaf with `(weight, factor, comp, tempWeight)=(1,1,1,1)`. Under the already-proven AZ semantics, factor 1 becomes `log_1.03(1)=0`; `tempWeight=1` makes the history filter select that zero directly. Therefore the selected ConvStretch stage is an identity transform for arbitrary BasicSafe output and previous retained delta: Short/Safe/Long remain BasicSafe and predictive gain stays 1.

## FastConv core is invariant, control header is not

The tuning contains ten `aecxdbconvbase` mode variants. Every variant's context-0 automatic fallback selects **dataID 1 = `FastConv`**, and every terminal FastConv leaf contains the identical three-float core:

```text
baseSpeed   = 0.8f  (0x3f4ccccd)
baseCapping = 0.33f (0x3ea8f5c3)
drcSpeed    = 0.15f (0x3e19999a)
```

However, the surrounding FastConv data-record control header is **not** invariant: the first mode variant differs from the other nine. BM intentionally does not label those differing words as capping type/tolerance. That semantic mapping belongs to the next checkpoint and prevents the older adjacent-byte assumption from leaking into the native controller.

## Scope after BM

BL no longer needs dynamic ConvStretch materialization for the pinned front tuning, and its three FastConv speed inputs can be fixed for the ordinary context-0 path. Remaining convergence-control seams are the exact runtime **capping type, tolerance/control words, DRC policy and special-context activation**.

Safety: static/offline only. No camera stream, module load, sensor control, MMIO, reboot, or Windows execution.
