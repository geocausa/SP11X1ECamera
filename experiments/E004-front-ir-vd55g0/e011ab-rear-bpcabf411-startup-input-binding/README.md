# E011AB — rear BPCABF411 startup input binding

Status: LIVE SELECTED COMMON ARITHMETIC AND THREE STARTUP SEVEN-WORD PACKET BRIDGES CLOSED. RUNTIME TUNING SELECTION AND FULL FOUR-PACKET COMPOSITION OPEN.

Parent: 1a0470aa3a47cc153857f2007dd8eb082f85eead (E011AA clean producer). Prepared/observer-correction checkpoints: 551e9368 and 64502232.

## Proven result

Fresh E011AB-20260929-2100B on the original SP11 Windows stack completed rear Color / VideoRecord / NV12 3840x2160 Start/Stop with 712 valid 4K handles. Eight common-input captures were paired with eight live common outputs at the Titan680 packer boundary. The independent E011AA producer reproduced all 30 selected output scalars in each sample: 240 exact scalar matches. Its seven packed words also matched the original retained startup packets for phases 0, 1 and 2: 21 exact register matches. Private packet bytes were comparison targets only.

The actual schedule corrects the initial hypothesis:

| boundary | producer sample | selected semantic state |
| --- | ---: | --- |
| before first atomic request | 1 | cold state |
| request 1 | 2 | populated state |
| request 2 | 3 | recalculation; same selected terms as sample 2 |
| request 3 | no common or packer call | hold |
| requests 4 through 8 | 4 through 8 | normal updates |

There are three startup producer invocations and two distinct states for the selected E011AA terms. A trace request tag 0 means before the first request hook; it is not an actual camera request ID. Different module families have different schedules: do not copy LSC/GTM's request-2 hold onto BPC/ABF.

## Source and observation boundaries

Installed DeviceMFT SHA-256: c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35.

Atomic request / BPCABF common / Titan680 packer RVAs: 0x746F18 / 0x9C16B0 / 0xB41090. Common entry captures the 107-float region, six-word runtime reserve, and 0x160-byte dependence. Packer input x1+0x10 points to the completed 0x90-byte common output. Selected levels, preserve curves, byte curves and runtime anchors are passed into the independent producer, without register captures as producer inputs.

The observer attaches before PREINIT, stops at actual QcDeviceMFT DLL load, then binds resolved module-relative bp addresses. All three concrete addresses were checked before initialization resumed and before START.GO. holder.ps1 atomically consumes its identity before camera enumeration, uses manual-only sign-in task execution, and automatically stops acquisition after 30 seconds. The task was removed after completion; no same-boot camera retry occurred.

Run B observed eight common and eight packer hits plus 22 request hooks. Intended request bound 16 was interpreted as hexadecimal by WinDbg MASM, making the actual finite bound 22. The committed generator now explicitly uses 0n16. The verifier accepts --request-limit 22 to validate the actual historical run; it does not relabel it as 16. Original per-run scripts remain private and unchanged.

Run A, E011AB-20260929-2045A, delivered 711 valid 4K handles but its deferred bare-module-offset breakpoints did not bind: zero captures and no semantic proof. Its task was removed and SP11 returned to Golden before the fresh Run B. See RUN-A-SAFE.json.

## Reproduce the private verification on SP11

Run verify-private.py against the private E011AB Run B directory with --request-limit 22 and --startup-corpus pointing to the private E006A-PRIVATE-RECORDS-v2.json. It checks request coverage/order, common/packer sample pairing and file sizes, independently calculates all selected scalars, and compares the three startup seven-word records by phase. LIVE-VALIDATION-SAFE.json contains only aggregate/derived results.

## Remaining work

Live selected inputs, arithmetic, and the three startup seven-word bridges are proven. Installed tuning-root/leaf selection, interpolation trigger provenance, and the serialized tuning-reserve-to-runtime structural mapping remain open. Runtime snapshots must not become Linux policy. Bind source-generated tuning semantics and the remaining non-adaptive E008o base objects into the complete four-packet composer; preserve the module-specific producer/hold schedule.

The separate VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement and safe-stop gate also remains open. Native rear Linux hardware ISP runtime remains denied. No Linux module build/load, camera/MMIO/DMI/RT-CDM access occurred.

SP11 returned to protected FullIO v19c Golden Linux, boot e8987a75-f514-42b8-81cc-5fe15d206817. Linux-first EFI BootOrder and saved Golden GRUB entry were preserved. Raw captures, process addresses, source tuning and transcripts remain private on SP11.
