# E003h CSID1 prepare → RUP/AUP → enable 0043 runtime result — 2026-08-30

The separately authorized 0043 one-shot was consumed exactly once. The helper completed all 13 pre-CSID RT-CDM FIFO0 submissions without fault, IMX681 entered `MODE_SELECT=1`, and the bounded runner timed out waiting for VFE1 raw Epoch0. No QC10C output was produced and there was no same-boot retry. Evidence was archived before immediate reboot; FullIO v19c Golden is restored with empty `next_entry` and no candidate camera modules loaded.

The decisive result is that 0043 reproduces the 0042 CSID boundary exactly despite the corrected Windows-observed host ordering. At timeout CSID1 again reports 37,016 packets, zero ECC/CRC errors, `RX_IRQ_STATUS=0x17`, `IPP_IRQ_STATUS=0x00011e00`, `IPP_CTRL=1`, `CFG0=0x802b2000`, `CFG1=0x7241`, epoch config `0x00130013`, and observation `+0x340=0x48000a08`. Therefore the explicit `prepare -> existing RT-CDM RUP/AUP 0x01f501f5 -> enable` split did not move the hardware failure boundary. The simple “RUP was issued before shadow configuration existed” hypothesis is closed.

The RT-CDM command target is also not an obvious address-map error: X1E CAMSS DT maps VFE0 at `0x0ac62000`, so Windows `CHANGE_BASE 0x0f000` resolves to VFE1 `0x0ac71000` and `CHANGE_BASE 0x57000` resolves to CSID1 `0x0acb9000` exactly. Windows and Linux both use BL-done waits for this RT-CDM commit path, so a superficial host-side wait/queue timing mismatch is not accepted as the next cause.

A teardown-only V4L2 `call_s_stream()` warning is present after the Epoch0 timeout. Sensor and CAMSS nevertheless suspend cleanly. The warning is not accepted as the cause of the missing Epoch0, but prepared-state rollback bookkeeping must be corrected before any future runtime candidate.

No further Linux runtime is authorized. The next static gate is to enumerate every exact same-machine Windows CSID1 common/path MMIO write and lifecycle prerequisite surrounding configuration/RUP acceptance and mechanically compare that complete set against Linux. Only a proven native delta may reopen runtime authorization.
