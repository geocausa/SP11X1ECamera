# E003i BR — native AEC unlocked-preview convergence profile

Status: **PASS (native/offline)**.

BR projects BP onto the exact ordinary front-camera scope closed by BQ:

- normal streaming (`AECAlgoOperationModeStreaming`, enum 1);
- AEC unlocked;
- temporary metering-lock context inactive;
- single-exposure normal preview.

The public convergence input now contains only request data:

- seven target log-exposure lanes;
- F-1 history snapshot;
- F-2 history snapshot;
- PipelineDelay/F-3 delayed history snapshot.

There are **no public tuning inputs and no public scalar runtime-mode controls**.

Internally BR retains BP's proven Windows profile:

- PipelineDelay 3;
- FastConv `(0.8f, 0.33f, 0.15f)`;
- capping type 2;
- tolerance 2;
- minimum step 0.5f;
- DisableStretch identity;
- DRC policy 0.

BQ then fixes the four residual BP controls to zero for this exact wrapper:

- old `intolerance_gate` / convergence `+0x2b4` word = 0;
- `small_delta_exemption` / context bit 3 = 0;
- Short metering-lock status word = 0;
- Long/lock-marker low word = 0.

This is deliberately not an API for AEC-lock, snapshot, preflash, FastAEC, or other temporary contexts. Those remain outside BR rather than being silently forced into normal-preview behavior.

## Verification

`verify-br.py` fresh-runs BQ and BP, builds both BP and BR with the native Linux compiler under `-Wall -Wextra -Werror -fno-fast-math`, and compares BR against BP with all four BP runtime controls set to BQ's zero projection.

The deterministic corpus covers 1536 request states with varied target lanes, F-1/F-2/F-3 histories, DRC gains, and retained convergence deltas. Every complete output structure matches byte-for-byte.

Fail-closed behavior is retained: null input returns `-1`, and missing/zero exposure histories return `-2`.

No camera stream, module load, sensor write, MMIO, Windows boot, or reboot was used.
