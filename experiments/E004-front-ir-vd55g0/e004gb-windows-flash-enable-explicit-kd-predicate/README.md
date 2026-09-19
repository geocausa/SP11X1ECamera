# E004gb — Windows KDNET flash module/channel observation (COMPLETED)

**2026-09-19 result: PASS, ONE-SHOT CONSUMED, SP11 RETURNED TO PROTECTED GOLDEN.** This experiment was executed exactly once. Do **not** rerun `generate-kd.ps1`, the KD scripts, the OEM `capture.ps1`, or a Windows BootNext using E004gb's identity. E004ga, its aborted predecessor, is also consumed.

The original SP7 KD dry and observer logs, the original Windows capture log, and original run/consumption metadata are preserved *byte for byte* in `evidence/ORIGINAL-WINDOWS-LOGS.zip` (SHA-256 `330afa1f20fc2714d8e8a172c6d754dbb4d32e5dc1a41e174825bb2c0eb0bfbf`). The separately retained original SP7 KD trace is SHA-256 `cf889c909142b786a8778fe7528b7b315af64eb3742c71fd61addf29286997ae` (6,211 bytes); the original Windows OEM capture log is SHA-256 `12675cc0bac2b70775215c3b6234d79c527965825de9a842739d63df725c07fc` (2,135 bytes). `evidence/RESULT.json` and `verify_result.py` summarize and check these unchanged originals; `test_verify_result.py` rejects six tampered in-memory variants. No image files were saved.

## Verified observations

SP7's *live* WinDbg/MASM preflight accepted all eleven target addresses, including the previously omitted module/channel registers `ee46`/`ee4e`, rejected eight negative addresses and validated post-register extraction. Exactly two read-only KD observer hooks were armed on the fresh installed `qcpmic8380.sys` module at base `fffff802a5e40000`. Windows' normal OEM Surface IR Front preview delivered **12 frames** (NV12 644×604, nominal 60 fps) and stopped normally. The KD trace contains eleven ordered, paired helper read and write calls with return code 0:

| Windows helper register | Observed *software* read → requested merged byte | Mask |
|---|---|---|
| Four trigger selectors `ee4a..ee4d` | all initially `01`; high-bitfield setup requests (resulting post buffers remain `01`) | `70` |
| Paired trigger selectors `ee4a` and `ee4d` | `01 → 05` | `07` |
| Common trigger `ee67` | `01 → 00` | `01` |
| Flash module enable `ee46` | `00 → 80`, then `80 → 00` | `80` |
| Four-channel enable mask `ee4e` | `00 → 09`, then `09 → 00` | `0f` |

Windows requested module enable **before** channel enable, and module disable **before** channel disable, during this particular capture session. The selected helper recorded **zero accesses to timer registers `ee3e..ee41`**. This is only absence at the selected hooks over one bounded preview; Windows may use other helpers or existing timer configuration. Successful helper status and post-write *memory buffer* are **not** proof of a physical PMIC readback, electrical LED state, absolute light pulse duration, or autonomous hardware cutoff.

On completion, SP7 cleared all debugger breakpoints and closed/hashed the logs; Windows was resumed and rebooted. SP11 returned to Golden boot `6ca88e8c-525b-4944-bffa-037a4337a01d` with protected kernel `7.1.5-sp11-render-parity-v4+`, saved FullIO v19c entry, empty GRUB next_entry, preserved EFI BootOrder, disabled Linux flash DT node, and no camera nodes/modules/processes. See `evidence/POSTBOOT.txt` and `evidence/CONSUMED.json`.

**Safety gate remains BLOCKED:** Windows' driver-requested `00→80→00` and `00→09→00` transitions do not demonstrate physically measured optical current, irradiance, pulse width or reliable independent shutdown on a stuck-high strobe or host/SPMI failure. The previously built Linux timer/rollback flash patches remain **uninstalled**; no native Linux IR illumination or working face unlock is authorized. The next engineer should use this new evidence to refine the safe, independently bounded illumination path and can separately develop the offline HLOS face-processing path, without repeating consumed camera experiments.
