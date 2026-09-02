# Camera project continuation handoff

Use this file when resuming E003h in a fresh ChatGPT conversation.

## Goal

The project goal is the **entire Surface Pro 11 camera stack with Windows behavior/parity as close to 1:1 as practical**, not merely making the front camera show an image. Preserve rear OV13858 behavior while completing front IMX681, ISP/IQ, request generation, userspace integration, switching, suspend/resume and reliability.

## Current branch / safe machine state

- repo: `/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`
- branch: `experiment/e003-front-imx681-cphy`
- persistent Golden kernel: `7.1.5-sp11-render-parity-v4+`
- persistent Golden GRUB: `sp11-audio-fullio-v19c`
- SP11 Linux/Windows can be rebooted and instrumented as needed.
- Use the normal **GRUB one-shot Windows entry**; do not repeat the temporary offline BCD experiments from 2026-09-02.
- SP7 has a faulty cooling fan. Use it only as a lightweight/passive KDNET host when needed; do not give it heavy compute jobs.
- Same-machine Windows/QcDeviceMFT is the authoritative oracle.

## Safety gate

**Do not run Linux request6 yet.** The gate remains fail-closed until the remaining runtime LSC interpolation representation is reproduced byte-for-byte and the full atomic Windows producer/output capsule matches offline.

## Latest accepted closures

- GTM/TMC exact replay: closed, 256/256 qwords.
- Windows GIC wire anomaly/alias: closed.
- LSC calibration application: bounded/closed.
- LSC geometry/resampling: closed.
- LSC post-calculation `0x18a0` staging -> Titan680 LSC0/LSC1/LSC2: closed.
- sequential embedded Tintless request5 -> request6 at DeviceMFT RVA `0xc95fd0`: byte-exact, including persistent state; see `LSC-TINTLESS-SEQUENTIAL-REPLAY.md`.
- latest runtime interpolation/trigger boundary: see `LSC-RUNTIME-INTERPOLATION-BOUNDARY.md` and its oracle/proof.

## Latest live oracle

Raw/untracked Windows capture directory:

`C:\Users\Geoca\Documents\SP11CameraOracle\E003H_20260902_LSCTRIGSRC`

On Linux after mounting the Windows volume read-only:

`/mnt/windows/Users/Geoca/Documents/SP11CameraOracle/E003H_20260902_LSCTRIGSRC`

At LSC411Interpolation post RVA `0x93c8e8`:

- `x22` = generic pre-calibration LSC41 interpolation result.
- `x23` = calibrated destination.
- request5 x22 SHA `e35ad052a2d219bcded1283c72922fd0c5722431ad511c496ab1ab4ec03dc9de`
- request6 x22 SHA `3acd68d81103656463b65b448f3a6106c907a48f1f08acb4c3132d30c1b28ca8`
- request5 x23 SHA `94cbaac591fabf97ebff4a005b02fbcfa7a2bfff5783134794e1c52f0bcead71`
- request6 x23 SHA `62b39d4ee8f66dc4931c0a99bf4c51cc7069ea4829f78df6c80dbfa82b48ad15`

Exact 42-float trigger vector is captured for both requests. LSC control vector `[8,2,5,100,0,6]` consumes indices `[8,2,5,19,20,21,0,6]`. Request5 mapped values are `[370,1,1,1,0,0,400.9328003,4999]`; request6 differs only in index0=`400.2722778`.

## Current open problem / immediate action

The Windows-installed tuning blob is byte-identical to the archived blob. The entire container has 25 serialized `0xdf0` LSC regions but only five unique payloads—the known effective front `sid41` leaves. Live `x22` is not an exact direct, two-leaf, or affine combination of those five under the current raw serialization interpretation. Channel permutations and simple gain-domain transforms were ruled out.

Therefore the next task is **not more trigger fitting**. Trace how the runtime Chromatix object materializes/represents LSC41 leaves before Qualcomm generic interpolation. Focus on runtime leaf pointer/data construction. If static tracing cannot close it, do one narrow Windows capture of the actual runtime leaf pointer(s)/`0xdf0` leaf data handed to the interpolation engine at request5/6 and compare directly with the serialized regions and `x22`.

Then chain the resolved interpolation through already-closed calibration -> geometry -> exact sequential Tintless -> staging -> Titan680/GIC and demand byte parity. Only afterward reconsider Linux request6.
