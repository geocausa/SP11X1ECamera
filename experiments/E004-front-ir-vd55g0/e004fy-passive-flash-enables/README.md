# E004fy — single-use passive flash enable and trigger snapshot

Status: **PASS — SINGLE PASSIVE IDLE FLASH-STATE READ COMPLETED, E004fy CONSUMED (2026-09-19).** The prior E004fx and E004fy read identities must not be reused. This was a new six-register Golden idle observation, not a camera experiment or illumination request.

E004fw mapped Golden's disabled PM8550 flash-controller node to SPMI `0-01` at base `0xee00`. The exact isolated four-channel Linux driver specifies module enable bit 7 at `0xee46`, four channel strobe/trigger selectors at `0xee4a–0xee4d`, and channel-enable mask bits 0–3 at `0xee4e`. E004fx observed timer-byte `0x93` in all four channels **without measuring emitted light**. E004fy asks whether the current *idle controller configuration* has module/channels enabled or triggers set, not whether hardware will extinguish an LED safely.

`prepare.py` re-verifies the same Golden boot and clean synchronized repo, single disabled flash DT node and exact SPMI mapping, source hashes, all 65,536 lines of read-only regmap access metadata, readable/non-precious targeted addresses and registers-file read-only mode. It reads **no PMIC register values**. `read_once.py`, to be executed **only after this prepared stage is committed and pushed**, repeats those checks, fsyncs a new consumed marker, then issues six fixed-size `pread` requests (one nine-byte register record each) for only the named addresses. It records six idle register bytes and derived enable-mask fields, never an unrelated PMIC dump. It must not be retried even if the connection fails; instead inspect the consumed marker and result. No PMIC write, flash driver installation, camera stream or reboot is authorized.

## Observed result and Windows comparison

One fresh, committed E004fy identity read exactly six pre-authorized idle register bytes at SPMI `0-01` with no PMIC writes:

| Register | Golden idle byte | Source-backed interpretation |
|---|---|---|
| 0xee46 | 0x00 | Flash module-enable bit 7 **clear** |
| 0xee4a–0xee4d | 0x01 each | Four channel selectors have bit 2 clear (software trigger according to isolated Linux driver), bit 1 clear (level), bit 0 set (active-high polarity) |
| 0xee4e | 0x00 | Channel-enable bits 0–3 **all clear** |

E004fx had already observed timer bytes `0x93` on the same Golden boot. **A stored timer bit does not mean the flash path is on:** E004fy confirms the module and channel enable bits were clear in Golden idle. Separately, the *previous, consumed Windows E004fp 12-frame trace* observed read-modify-write transitions from 0x01 to 0x05 for the trigger selectors at 0xee4a and 0xee4d (paired logical LED1 sources 1 and 4). This is a **different Windows streaming session**, not an E004fy live Windows observation and not proof of LED current or physical emission.

Post-read verification confirmed the same protected Golden boot, flash DT disabled, unchanged EFI BootOrder/saved entry and camera idle. The original E004fy one-shot is marked **CONSUMED**; `verify_result.py` rechecks pinned evidence entirely offline, with no repeated hardware read. No camera, reboot, flash-module installation or illumination occurred.

Trigger selector values and module/channel configuration do **not** establish physical LED wiring, Windows capture-time timer state, safe exposure/current/irradiance, or independent shutoff on host crash/stuck-high GPIO. E004fs illumination remains **BLOCKED**. KDNET/SP7 can be used for a **separately prepared Windows-side evidence experiment** when comparison would resolve a distinct unknown; never rearm an already consumed Windows run.
