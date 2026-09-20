# E004hu — original current-version Surface UEFI PMIC/SPMI boot-stage timer-literal audit

**OFFLINE PASS (2026-09-20). A new pre-Windows software source is now in scope; the original `0x93` first writer remains UNKNOWN.** This stage follows the CONSUMED E004ht original early Windows common-SPMI-controller debugger run (natural original controller READ control, NO matching timer WRITE in that bounded observer window). It does NOT repeat the Windows no-hit watch, issue a SPMI request, reboot the machine, change ESP/UEFI, run an emitter or prove a PMIC reset value.

## Direct provenance to the SP11's reported firmware version

Protected Golden's **read-only** `/sys/class/dmi/id/bios_version` returned **`175.222.235`** during this stage. The original pre-existing SP11 local archive contains `Surface_UEFI_175.222.235.bin` copied from a Windows OEM update package, 13,608,082 bytes, SHA256 **`2908e3152b5d3c6141c34114bfee39a15f5e94f20acfe1c49be6a5084ec8cb47`**. Its already-existing firmware-volume parser report lists two original **DXE drivers** inside that package: **`PmicDxe`** FFS GUID `C44697D5-B4AA-4030-9749-29860844183D`, and **`SPMI`** FFS GUID `2A7B4BEF-80CD-49E1-B473-374BA4D673FC`. These are *firmware* components, distinct from original Windows `qcpmic8380.sys` and `qcspmi8380.sys` that were previously traced. The firmware **version match is not a byte-for-byte dump of the active flash firmware and does not by itself prove which DXE routines actually ran on this boot**.

The two corresponding already-extracted original ARM64 UEFI PE32 section images are independently hash pinned and read **only from the existing archive** (never copied into Git):

| Original firmware DXE image | Original PE-section bytes | Original SHA256 | ARM64 entry RVA |
| --- | ---: | --- | --- |
| `PmicDxe` | 253,952 | `402315711a6761441234eac8c0cd3c0ad23cb4fdb7d0a9de3dd94c3ffac38dff` | `0x1000` |
| `SPMI` | 49,152 | `62b53f5daaf46e016962895ff19f26b7449b4566c9859ad3140e2748f87f3ef0` | `0x1000` |

The original `PmicDxe` PE **contains** source/diagnostic strings `pm_pmicdxe_init`, `pm_comm_spmi_lite.c`, `SPMI_WR` and `SPMI_RD`; thus a pre-Windows firmware component with generic PMIC/SPMI read/write functionality is present in the version-matched package. This establishes a **specific additional candidate boot stage** worth analyzing. It does **not** prove this DXE component programmed flash timer `ee3e..ee41`, supplied `0x93`, or drove the Surface IR LED.

## Exactly what the literal search does and does not establish

All **255** already-extracted `PE32 image section/body.bin` firmware executables were inspected, including the two original UEFI PMIC/SPMI modules. **None** contained an explicit little-endian 32-bit word `0x0000ee3e`, an adjacent four-register table expressed as four 32-bit or four 16-bit little-endian addresses `ee3e..ee41`, or four adjacent literal `0x93` bytes. The exact entire original 13,608,082-byte *capsule* likewise contained zero instances of those sequences. Both dedicated UEFI `PmicDxe` and `SPMI` original PE bytes also contained **zero standalone little-endian 16-bit `ee3e`**. Two completely different extracted keyboard DXE images contained the **low-byte-only** sequence `3e 3f 40 41`, which has no demonstrated relationship to PMIC timers.

The capsule **does** contain 95 occurrences of the bare two-byte little-endian `3e ee`. In arbitrary ARM64 opcode bytes, compressed firmware payloads, unrelated metadata and numerical tables, a two-byte match or nearby `0x93` byte is *not* evidence of a SPMI register operation. Absence of an explicit literal also **cannot exclude** ARM64 immediates constructed through multiple instructions, peripheral base + computed offset, other address encodings, generated register tables, compressed/unextracted boot stages, secure firmware, boot-loader initialization, reset defaults or a prior power-retention state. No firmware writer or software initialization callsite is identified by E004hu; neither a negative firmware attribution nor a silicon reset-value assertion is justified.

## Verification, safe state and next discriminating lead

Run from the protected Golden repo: `python3 experiments/E004-front-ir-vd55g0/e004hu-installed-version-uefi-pmic-spmi-timer-literal-audit/verify_firmware.py` and `python3 experiments/E004-front-ir-vd55g0/e004hu-installed-version-uefi-pmic-spmi-timer-literal-audit/test_firmware.py`. They pin the original capsule, both extracted PE image hashes/architecture and FFS names, all 255 extracted PE paths, exact bounded literal counts and prior E004ht evidence scope. The **four in-memory malformed-archive/inventory tests** fail closed without altering a file or opening a camera or PMIC interface. The results store only hashes, module identifiers, names and counts, never the original firmware binary, a KDNET key or user camera data. The full original extracted UEFI directory remains untouched in the archive.

**Next distinct lead:** inspect original `PmicDxe` **computed-address writes and its early initialization/configuration data**, and any earlier Qualcomm XBL/PBS initialization package, rather than repeating identical post-boot SPMI timer no-hit breakpoints. Obtaining a genuine pre-OS timer-address/value trace or a PMIC silicon reset specification remains essential to attribute the *first* `0x93` writer. Independently qualified actual emitter drive current, irradiance, bounded optical pulse and autonomous host-crash/stuck-trigger OFF under E004fs/E004ge are still BLOCKED; native Linux flash/emitter and PAM/login stay OFF/UNINSTALLED.
