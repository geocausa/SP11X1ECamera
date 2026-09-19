# E004fx — single-use, four-register passive Golden PMIC timer snapshot

Status: **PREPARED / NOT YET CONSUMED.** Do not run read_once.py before this exact prepared experiment is committed and pushed, Golden is reverified, and the fixed SPMI target remains unchanged. All previous E004ft/E004fu camera experiments remain consumed; E004fx opens no camera, does not reboot or install a kernel module, and never enables the IR emitter.

## Why the target is specific

E004fw verified on this Golden boot that the single disabled flash-controller DT node is at PM8550 SPMI bus 0, SID 1, base `0xee00` (Linux regmap `0-01`). The isolated Linux 4-channel flash register table places the four per-channel timer bytes at `0xee3e..0xee41`. Other PMCs (SIDs 3–6) are *not* that Linux flash-node parent. Neither the address arithmetic nor an idle register read proves physical Surface IR LED wiring or a hardware-safe optical cutoff.

Golden's PMIC regmap advertises 16-bit addresses, 8-bit values and a 0xffff range. This SP11 kernel's inspected regmap debugfs read interface supports positioned, bounded reads; its read-only access metadata shows all addresses before/through 0xee41 are printable, non-precious, and read-permitted. The exact debugfs byte offset corresponding to 0xee3e is 548910, with **four 9-byte text records / 36 requested bytes**. The offline preparation checks the full access metadata (no PMIC value reads), exact file layout and source hashes. It rejects sparse, reordered, unreadable or precious targets.

## One-use observation protocol

After offline preparation and GitHub checkpoint, `python3 read_once.py` repeats Golden, camera-idle, same-boot, repository, SPMI mapping and access checks. It writes and fsyncs evidence/CONSUMED.json **before** one privileged, read-only `os.pread` of exactly 36 bytes at offset 548910 from the specific debugfs register view. It verifies that the returned labels are exactly ee3e, ee3f, ee40, ee41 and records only their four idle configuration bytes. A read error or unexpected response is **inconclusive and still consumes E004fx**: do not repeat during the same boot or reuse this identity. No whole-regmap dump, PMIC register write, LED driver, camera activation or reboot is permitted.

An actual four-byte observation would constrain **idle state only**. It cannot prove Windows streaming-time timer state, physical timer duration, safe radiant power/current or independent extinguishing of a stuck-high trigger or host failure. E004fs remains BLOCKED regardless of numeric output. After the one-shot attempt, check Golden boot, camera-idle guard and register state evidence; retain only a concise result, no unrelated PMIC dump. Fresh hardware experiment and independent electrical/optical evidence would still be required before illuminated capture.
