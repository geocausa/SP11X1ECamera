# E007w — rear VFE680 PERIOD_CFG semantic provider

Parent Git: `14d64501` (E007v DSX101 clean provider PASS).

Status: **STAGED / COMPILE-ONLY**.

## Goal

Close the final first-native-rear-frame blocker: derive VFE680 register `0x008C` from its actual CAMIF subsample semantics instead of preserving opaque Windows command-buffer words.

## Surface Titan680 source lock

Pinned `QcDeviceMFT8380.dll` resolves the write to:

`CamX::IFEPipelineTitan680::UpdateSubsampleConfig` at `0x1808a2d30`.

The relevant ARM64 sequence is source-defined as:

- load the batch-count field;
- compute `numBatchedFrames - 1`;
- choose zero for zero/one-frame cases;
- replace **only bits [4:0]**;
- write the resulting word to register `0x008C`;
- write pattern `1` to `0x0090`.

The function logs the field as **Subsample Period Cfg** and explicitly masks it with `0x1f`.

The matching CamX reference implementation names the semantic input `pipelineIFEData.numBatchedFrames` and documents it as “Number of Frames in the batch mode, otherwise it is 1.” Its CAMIF path sets `IRQ_SUBSAMPLE_PERIOD = numBatchedFrames - 1` only when the count is greater than one.

## Why the old Windows words varied

E003h conservatively classified the full 32-bit Windows words as two opaque values because packet 0 differed from packets 1/2/3 and the raw words varied between starts.

The Surface machine code now explains that variation. The low five semantic bits are merged into an existing local stack word. In the compiled function the slot supplying the upper bits has **no write after the final stack-frame allocation before its load**. Those upper 27 bits therefore do not come from the subsample-period producer.

Across **28 accepted Windows startup/replay samples**, every real `0x008C` value has:

`value & 0x1f == 0`.

The raw high bits vary, but the active field does not.

Linux therefore canonicalizes the undefined/non-semantic upper bits to zero instead of reproducing stack residue.

## Rear first-frame semantics

The accepted rear oracle is ordinary:

`Surface Camera Rear Color / VideoRecord / NV12 3840x2160@30`.

It is not an HFR/batched capture mode. The equivalent CamX pipeline state is:

`numBatchedFrames = 1`.

Therefore:

`PERIOD_CFG = 0`.

## Compatibility with E007c

E007c remains the packet-aware startup API because the rest of the materializer already consumes it. E007w initializes both E007c logical slots from the same canonical semantic value.

The former packet0-versus-packets123 distinction is retained only as an ABI shape; it no longer represents two semantic period values.

## Consequence

After E007w, there are **no remaining first-frame register, DMI-payload, or transport-state blockers**. The next gate is complete non-submitting rear startup-request assembly and structural comparison before any native rear runtime attempt.

## Safety

Compile-only. No module load, camera access, MMIO, DMI submission or RT-CDM submission.
