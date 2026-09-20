# E004hv — a computed-address, indirect firmware PMIC write routine that a literal scan misses

**OFFLINE ORIGINAL UEFI ARM64 PASS, 2026-09-20.** This is a distinct positive *static software-path* finding following E004hu's bounded literal scan of the version-matched Surface UEFI image. No firmware, PMIC, SPMI, camera or IR device was accessed and no BIOS/ESP content was modified. The first writer of idle timer byte `0x93` remains **UNKNOWN**.

## Original binary and reachable-function-pointer evidence

The original archived `Surface_UEFI_175.222.235.bin` is version-matched to SP11's current DMI BIOS version `175.222.235` as observed at E004hu, but active firmware byte parity or runtime function execution is **not** established by that version match. In the already-extracted exact ARM64 `PmicDxe` PE section (original SHA256 `402315711a6761441234eac8c0cd3c0ad23cb4fdb7d0a9de3dd94c3ffac38dff`) an original **64-bit data pointer at RVA `0x38d98` contains RVA `0x222f8`**. The same original PE has **zero direct ARM64 `bl` calls** to `+0x222f8` in its extracted executable sections. Its location among neighboring firmware function pointers makes it an *indirectly published service candidate*, **not proof that any caller actually invoked it during SP11 startup**.

The `PmicDxe+0x222f8` routine prepares **two original generic PMIC write-helper calls**:

| Original code | Source of requested bytes | Original PMIC input index | Peripheral index | Register offset within computed base | Byte count |
| --- | --- | ---: | ---: | ---: | ---: |
| `+0x22320 → +0x12154` | caller's low 32 bits of `w0` | 0 | `0x0e` | `0x26` | 4 |
| `+0x2233c → +0x12154` | caller's low 16 bits of `w1` | 0 | `0x0e` | `0x3e` | 2 |

At `+0x22304` the first input is stored to a stack-local four-byte field; at `+0x2230c` the **second, caller-supplied input value is stored as a halfword**. The two different buffer addresses are passed to the same original helper `+0x12154`, with byte counts 4 and 2 respectively, while the result codes are combined. **Neither requested byte value, the effective register address, nor a live invocation is present in this experiment.** A `0x3e` *relative offset* is not automatically absolute SPMI address `0xee3e`.

## Why the literal check could not exclude this function

The original generic helper `+0x12154` validates its argument dimensions and obtains original per-device runtime metadata. Its main request block `+0x12228..+0x12244` reads a device-specific address offset and **peripheral stride** from the runtime metadata. Its original ARM64 arithmetic combines those values with the original caller's peripheral index and low-byte register offset:

```text
computed_address = runtime_additional_offset
                 + runtime_device_base
                 + (peripheral_index × runtime_peripheral_stride)
                 + original_relative_register_offset
```

The original instructions at `+0x12228/+0x1222c/+0x12230/+0x12234/+0x1223c/+0x12240` establish this formula, then call a separate original firmware SPMI software-write wrapper at **`PmicDxe+0x8cd0`**. The wrapper's original `+0x8ce0` clears its operation argument and `+0x8d34` dispatches the request through a lower original firmware routine. **The runtime base, stride, per-device index table, actual controller completion and physical silicon effects were not observed here.** No literal `0x0000ee3e` is required in the executable for a dynamically computed address to equal that value; conversely, a relative `0x3e` alone **does not** demonstrate that this routine targets timer registers.

A complete static ARM64 direct-call scan in the original firmware PE found **47** direct calls to the generic write helper `+0x12154`, including the two calls in this indirect routine. It found no direct call to the indirect routine itself, although one concrete original function-pointer-table entry refers to it. This difference is why an analysis restricted to direct callsites or literal address tables cannot exclude an indirect firmware initialization writer.

## Evidence limits and next discriminating work

`verify_indirect.py` SHA-pins the original firmware image and E004hu's archive provenance, verifies the exact original ARM64 provider, data-pointer, two payload fields, generic address-composition instructions and software write dispatch. `test_indirect.py` rejects **33 in-memory mutations** of the exact original pointer, input/offset/size instructions, runtime address composition and dispatch. The source file and small derived result contain NO copied proprietary firmware PE bytes, no raw personal/camera/face content and no KDNET secret.

**Next distinct lead:** identify the firmware protocol containing pointer table `PmicDxe+0x38d98`, whether its service is actually invoked in the boot chain, and—only with reliable original descriptor/provenance—resolve the runtime address base and stride. If a credible candidate ultimately reaches `ee3e..ee41`, the original *caller-supplied input value* and actual execution order/physical register completion must still be established before attributing idle `0x93`. Separately investigate independent PMIC silicon reset documentation or earlier XBL/PBS initialization; do not infer firmware causation from previously consumed Windows SPMI no-hit observers.

**Safety remains unchanged:** E004fs/E004ge actual optical power/current, emitted pulse, stuck trigger and autonomous host-failure OFF are BLOCKED. Native Linux flash/IR emitter and PAM/login remain OFF and uninstalled, protected Golden kernel/DT/boot defaults unmodified.
