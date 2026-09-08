# E003i BN — Windows AEC default ConvBase controls

Status: **PASS (static/offline)** — identifies the normal SP11 front-preview ConvBase mode overlay and closes the two BasicSafe control words that BM deliberately left unresolved.

Pinned DeviceMFT and tuning hashes remain unchanged.

## Mode-tree identity

The third Parameter Bin section is a 18,700-byte tuning-mode index containing 935 fixed 20-byte records: 55 groups × 17 module slots. `aecxdbconvbase`'s symbol `c` field indexes slot 6 (AEC) in those groups.

The default ConvBase root `143` points to mode slot `6` and has no selector path. The other nine ConvBase roots form this mode tree:

```text
Sensor subMode 1
  Usecase 0 -> Feature1 4 / 5 / 6
  Usecase 1 -> Feature1 4 / 5 / 6
  Usecase 2 -> Feature1 4 / 5 / 6
```

`CapturePipe::FillTuningModeData` mechanically confirms the selector ABI: it stores mode type `Sensor=1`, stores the current sensor mode at the next word, then type `Usecase=2`, then `Feature1=3`. Its own verbose diagnostic reads that stored selector as `Sensor mode`.

The existing same-machine Windows KD checkpoint `0054` proves stock Windows Camera selects IMX681 firmware resolution/sensor mode index **2** (`3840x2160@30`). Therefore none of the nine overlays requiring Sensor subMode 1 can match normal front preview. Windows selects the unqualified/default ConvBase root `143`.

## Selected FastConv controls

Default root143's FastConv record is compactly:

```text
(dataID=1, description=FastConv,
 control=1, tolerance=2, cappingType=2,
 triggers=(9,3),(9,13),(9,6), count=5, triggerTree=2823)
```

The compact description `{length, descriptorRef}` expands into an aligned native pointer, shifting subsequent fields by four bytes. Runtime `ComputeBasicSafeConvergence` confirms the resulting layout by reading trigger descriptors at `+0x1c/+0x24/+0x2c`, **capping type at `+0x18`**, and **integer tolerance at `+0x14`**.

Thus normal Windows front preview uses:

```text
tolerance   = 2
cappingType = 2
baseSpeed   = 0.8f
baseCapping = 0.33f
drcSpeed    = 0.15f
```

The nine non-selected overlays instead carry tolerance 1 / cappingType 0.

## Correction to AY

AY's older raw-serialization observation read four bytes immediately after a three-float trigger leaf and tentatively treated them as capping type 0. That byte crosses the leaf boundary and is not the selected ConvBase control field. **BN supersedes that particular AY field interpretation.** AY's reconstructed BasicSafe branch semantics remain valid.

After BN, BL can fix the normal-preview BasicSafe controls to `tolerance=2`, `cappingType=2`, with BM's fixed `0.8/0.33/0.15` core and selector-independent DisableStretch no-op. Remaining convergence tuning/control work is primarily the global `aecxconvergence` DRC policy and any runtime control-state gates.

Safety: static/offline only; no camera stream, sensor write, module load, reboot, or Windows execution.
