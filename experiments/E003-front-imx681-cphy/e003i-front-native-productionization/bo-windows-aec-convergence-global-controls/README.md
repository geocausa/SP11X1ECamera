# E003i BO — Windows AEC global convergence controls

Status: **PASS (static/offline)** — closes the remaining sensor-wide `aecxconvergence` controls consumed by the normal BL convergence tail.

Pinned DeviceMFT SHA-256: `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.
Pinned IMX681 tuning SHA-256: `2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d`.

## Global lookup

Unlike ConvBase, the pinned IMX681 tuning contains exactly one `aecxconvergence` module. `CAECXContextManager` looks up literal `aecxconvergence`, takes `lookupResult + 0x120`, and caches that expanded payload. It is therefore sensor-wide rather than a request-local mode bank.

## Generated deserializer mapping

The compact root (entry 131) begins:

```text
word0..7 = 10, 0, 0, 2, revisionRef(2426), 3, 0x3f000000, 0
```

The vendor-generated module deserializer mechanically consumes those words in order. With runtime payload base at object `+0x120`:

```text
compact words 0..2 -> runtime +0x08/+0x0c/+0x10
compact words 3..4 -> revision child at runtime +0x20
compact word 5     -> runtime +0x28 = 3
compact word 6     -> runtime +0x2c = 0x3f000000 = 0.5f
compact word 7     -> runtime +0x30 = 0
```

This directly resolves a prior ambiguity: compact value `3` is **not** the DRC policy; it becomes runtime `+0x28`.

## Runtime semantics

Independent AEC consumers establish:

- runtime config `+0x2c` is the convergence **minimum step**, used by BasicSafe, ConvStretch quantization and GetExposureInfo;
- runtime config `+0x30` is the `DRCStretchAggregator` **policy**.

Therefore the pinned SP11 IMX681 configuration is:

```text
minimumStep = 0.5f
DRC policy  = 0
```

BA already proves policy 0: DRC-versus-stretch overlap arbitration, including predictive-gain consumption when DRC lies below stretch and full-DRC selection when DRC dominates.

## Normal-preview convergence constants after BM/BN/BO

The previously explicit BL tuning inputs can now be fixed for normal Windows front preview:

```text
baseSpeed       0.8f
baseCapping     0.33f
drcSpeed        0.15f
cappingType     2
tolerance       2
minimumStep     0.5f
ConvStretch     DisableStretch / identity
DRC policy      0
pipelineDelay   3
```

The remaining native-controller work is no longer tuning selection; it is state/control integration and joining BL's generated seven exposure lanes into the retained arbitration/sensor path.

Safety: static/offline only; no camera stream, sensor write, module load, reboot or Windows execution.
