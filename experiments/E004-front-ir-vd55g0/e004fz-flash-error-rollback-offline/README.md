# E004fz — software-error rollback for an **uninstalled** flash driver

Status: **OFFLINE SOURCE/CODE TEST PASS; NO INSTALL, NO EMITTER ACTIVATION (2026-09-19).** This is a fresh code-only experiment. E004fx/E004fy passive register snapshots and all earlier camera/Windows boots remain consumed.

## Specific defect and bounded code correction

After E004fv's uninstalled Linux/Windows timer-encoding parity patch, the isolated Linux `qcom_flash_strobe()` callback had six early-error return paths. In particular, it could enable the flash module and then fail while arming the final trigger without explicitly attempting to disable the module; an error at the initial disarm could also return without another shutdown attempt.

The reproducible `generate_patch.py` applies the SHA-pinned E004fv patch `0003` to the SHA-pinned isolated E004fk source, then produces `src/front-ir-vd55g0/illumination/0004-qcom-flash-best-effort-error-disarm.patch`. The new code routes all six failing stages through a common **best-effort** sequence: request channel disarm, then request removal of that LED's module-enable ownership, log any failed rollback requests, and return the **original error**. The ordinary successful enable/disarm sequence is unchanged. The existing nonzero, representable timeout guard from patch `0003` remains in force.

## Explicit limit: software fallback is NOT a physical safety cutoff

This patch does **not** prove that the PMIC executed either shutdown request. If the SPMI bus is unresponsive, a channel remains selected, hardware returned an error after enabling, or another flash LED keeps the shared module active, an emitter may remain on after the callback returns. A host crash, hung sensor trigger or CPU failure may prevent the callback from running at all. A watchdog, error log, retry or Golden reboot does not constitute an independently validated LED-off mechanism. The live physical current, pulse width and optical irradiance have not been measured, and the Linux flash driver's original 1000 mA default is **not approved** as a safe optical current. Native IR illumination remains prohibited by E004fs.

## Reproduction

`python3 generate_patch.py` deterministically regenerates patch `0004`. `python3 test_rollback.py` applies it to a temporary source copy, extracts and compiles the **actual modified C dispatcher**, and runs ASan/UBSan fault injection through all six forward stages. It verifies the preserved original error, attempted channel-then-module rollback, rejection of an enabled request with a zero timeout, normal disarm, and explicit errors when initial/final disarm plus module rollback fail. Those latter cases are deliberately modeled as **hardware potentially still ON**, never as safe. `python3 test_kernel_build.py` compiles the full source after patches `0003`+`0004` against prepared Golden kernel headers with `W=1` in a disposable directory. `python3 verify_result.py` pins the source and patch hashes, reruns both tests and writes the concise `evidence/RESULT.json` with emitter authorization set to false.

Neither the kernel/module nor camera DT, firmware, PAM, device login, Windows boot or PMIC register state is modified. KDNET via SP7 is available for a **separately staged, bounded Windows driver shutdown-path question** if it helps establish what Windows requests, but debugger activity and software return values alone cannot validate independent optical eye safety. Next: establish an electrically independent limit and measured safe emitter pulse/current/irradiance before any Linux illuminated capture.
