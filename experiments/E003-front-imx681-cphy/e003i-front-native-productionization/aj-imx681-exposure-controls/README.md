# E003i-AJ — IMX681 exposure / gain control parity

Status: **PASS (static/offline); live one-shot validation is the next gate.**

AJ starts from the exact mode2 IMX681 source/module lineage used by the proven E003i-AI six-frame runtime. It does not alter the AI LSC/IQ producer or its accepted R5/R6 path. The purpose of AJ is narrower: expose request-local sensor timing/gain controls using the active same-machine Windows IMX681 custom sensorlib contract.

## Windows oracle carried into Linux

The Windows cleanroom artifacts were copied from the Windows partition read-only and SHA-verified before the volume was unmounted again:

- `windows-oracle/oracle.py`: SHA256 `2dffc0370dbc19345bbfc09d80bd7ea6919259a371fc7f35e6b4cf65fe5fad9f`
- `windows-oracle/results.txt`: SHA256 `86b063443cdc30b1ebc585b15d3abb7ae30dabb4b95be50cb256482a480d7f19`

The active Windows wrapper points to custom IMX681 callbacks at stable MFT RVAs `0x870ee0` (CalculateExposure), `0x871000` (FillExposureSettings) and `0x8712f0` (GetSensorModeIndex). The active single-exposure callback emits one 10-byte dynamic transaction:

1. FLL at `0x033d..0x033f` (24-bit, MSB first)
2. even long coarse integration at `0x0229..0x022b` (bit 0 cleared)
3. analogue gain at `0x0204..0x0205`
4. one **global** digital gain at `0x020e..0x020f`

`0x0210..0x0215` are not dynamic per-colour gains on this active path. They remain at their static mode-table values.

The separately decoded Windows lifecycle proves group hold `0x0104=1` / `0x0104=0`; AJ wraps the four multi-byte CCI writes in that hold pair and unconditionally attempts hold release on error.

## Linux V4L2 ABI

AJ deliberately does **not** preserve the older PR164 combined-gain guess. The newer RFC lineage already treats analogue gain as a raw sensor code, and the live Windows custom callback now proves the actual mapping. The kernel ABI therefore exposes raw hardware quantities:

- `V4L2_CID_VBLANK` -> FLL = mode height + vblank, 24-bit
- `V4L2_CID_EXPOSURE` -> coarse integration lines, even step, written to `0x0229`
- `V4L2_CID_ANALOGUE_GAIN` -> raw `0x0204` code, `0..0x3c0`
- `V4L2_CID_DIGITAL_GAIN` -> raw global Q8.8 code at `0x020e`, `0x0100..0x0f00`

All four controls are one V4L2 cluster with vblank as master, so a control update republishes a coherent FLL/exposure/analogue/global-digital transaction under group hold.

The exact Windows real-gain-to-register conversion remains in `windows-oracle/oracle.py`: analogue target clamp `[1,16]`, scale 1024 with FCVTZU semantics, actual analogue recomputation, then single-precision digital residual with scale 256 and real-digital cap 15. Keeping this outside the kernel avoids turning a userspace AE policy into an opaque V4L2 raw-code ABI.

The `IMX681_EXPOSURE_MARGIN=4` range guard is a Linux V4L2 safety policy inherited from the public IMX681 RFC lineage; it is **not** claimed as a newly decoded Windows callback rule. The Windows rule directly proven here is the even-line mask.

## Identity-preserving startup

Mode2 already initializes:

- FLL `3554` (`0x000de2`)
- exposure `3546` (`0x000dda`)
- analogue code `0`
- global digital code `0x0100` (1.0x)

AJ uses those same values as control defaults. After runtime resume, the driver restores the Windows mode2 table, then reapplies the cached V4L2 control cluster, and only then writes `MODE_SELECT=1`. Merely enabling AJ therefore does not alter the established first-frame register state.

## Static proof

`prove-aj.py` SHA-checks the transferred Windows oracle, verifies source register identities and write ordering, verifies the four-control cluster and stream-on restore ordering, reconstructs the mode2 default bytes, and compares the Linux CCI transaction model with the Windows `FillExposureSettings` replay.

Results:

- Windows oracle self-test: PASS
- AJ source transaction structure: PASS
- mode2 default identity: PASS
- randomized Windows/Linux dynamic-byte comparison: **20,000 / 20,000**
- kernel build with `W=1`: PASS, no compiler warnings
- module vermagic: `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`
- AJ module SHA256: `15855b65512a15e66a732b1bf023fa8935a86b937426e2f590e161d25944bd54`

Kernel checkpatch on the AJ delta reports only the expected missing commit-description / Signed-off-by diagnostics from a synthetic raw diff; no source-style defect is reported.

## Boundary / next gate

AJ has not yet executed a camera stream. Static/offline proof does not itself prove the new controls enumerate correctly on the live subdevice or that a non-default request survives the real I2C path. The next gate is a fresh isolated one-shot runtime derived from the already proven AI transport assets, substituting only the AJ IMX681 module. It must enumerate the four controls, exercise at least one non-default clustered request, preserve frame capture/kernel health, and return to Golden Linux with no same-boot retry.
