# E003i-K — pure clean-room front LSC backend

This checkpoint removes the final DeviceMFT/Unicorn scaffolding from the validated front LSC producer. The production calculation is now entirely ordinary Linux/Python code:

`front tuning + golden + physical OTP + request ratio → clean geometry → clean Tintless → Q10/Titan680 LSC0/LSC1 → GIC alias`.

`generate-cleanroom-front-lsc-wire.py` uses a small sparse byte-addressable memory object only to preserve the already-proven Tintless state/ABI layout. It executes no ARM64 binary and loads no DeviceMFT image.

The sequential R4→R5→R6 proof remains strict. Before R5 and R6 it compares the clean wrapper/core carry against the Windows captures byte-for-byte (with only the synthetic core address normalized). Captured post-output is validation only. All prior hostile-state counterfactuals remain enforced:

- output initialized to zero;
- output initialized to `0xA5`;
- four planes initialized to float `1.0` with `0x5A` tail;
- request-4 core initialized to zero;
- request-4 core initialized to hostile `0xA5`.

Every case converges to the same exact R4/R5/R6 output and wire. Exact LSC0 identities remain:

- R4 `eb41b13a2049ecfe835266fefedd2d41c3e15564a8826ee06437f48a533234e5`
- R5 `1033e0732a1f2edf2263351be7ad213a98864ba0b9feb0a1d2eb27fbcf31953c`
- R6 `94dda0dd0c221da88a1087b13305c1cbe440cd314b3f0f6e324504494aab758e`

The pre-Tintless mesh is generated from tuning/golden/OTP and is not a capture input. Captured output-pre mesh and LSC staging are also not inputs. Windows request5/request6 wrapper/core captures are validators only.

The remaining LSC production boundary is now purely **live request-state acquisition**: replace the captured x1 Tintless config, x2 768-record Tintless statistics and x3/x4 descriptor metadata with state constructed from the Linux request pipeline. No Linux camera runtime, module load, STREAMON, sensor operation, or MMIO is performed here.
