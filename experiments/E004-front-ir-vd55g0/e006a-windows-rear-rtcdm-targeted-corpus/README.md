# E006a — targeted Windows rear RT-CDM command-corpus capture

Parent Git: `bd020723` (E005z result).

E005z proved that the rear path uses the same source-locked qccamisp selector-2 RT-CDM queue contract but a structurally different command corpus from front.

## Selected rear batches

The consumed E005z run established stable representatives:

- startup: batches 1, 2, 3, 4
- steady MAIN 0xAC8: batch 5
- steady MAIN 0xA98: batch 10
- steady MAIN 0x8F0: batch 16
- steady MAIN 0x658: batch 22

E006a captures exact command bytes only for those eight batches.

## Capture contract

At the selector-2 post-copy site RVA `0x287F0`:

- `w24` = record index within current batch
- stack `+0x20` = hardware BL IOVA
- stack `+0x28` = CPU alias of exact BL bytes
- stack `+0x30` = encoded byte length minus one
- stack `+0x50` = batch record count

One debugger-local batch counter increments when `w24 == 0`.

For selected batches only, the command breakpoint prints a bounded record marker and dumps exactly `w20 + 1` bytes from the CPU alias. Other batches auto-continue without output.

No raw pointer/IOVA value is intentionally printed in the marker. The debugger's memory-dump address remains private in the SP7 log and is stripped during local reduction.

## Runtime discipline

- SP7 external KD only.
- Direct Windows EFI BootNext only.
- One fresh single-use rear4K Windows camera trigger.
- Rear role: Surface Camera Rear Color / VideoRecord / NV12 3840x2160.
- >=10 valid handles plus clean Start/Stop required.
- No data breakpoint, no MMIO/register write, no driver mutation.
- Capture is read-only.
- Raw KD log and unnormalized command buffers remain private/local.
- After capture: remove breakpoint, close log, unregister one-shot task, resume target, normal reboot to Golden Linux, stop KD.
- Only after Linux returns: extract selected bytes privately, decode with the already-proven CDM parser, identify/normalize relocatable DMI/address fields, then commit normalized corpus facts/artifacts.

## Goal

Produce enough exact rear command material to build a separate rear capsule/materializer without cloning front command bytes by assumption.

Native rear Linux ISP remains DENIED.

## Offline reduction — structural PASS

The private E006a KD log was parsed locally on SP7 and reduced on protected Golden Linux. Debugger addresses and raw command bytes remain private and untracked.

The capture yielded 207 byte-complete selector-2 records across capture indices 0..34. Capture index 0 contains startup record indices 1..3 only; its 4-byte record0 was not observed and is deliberately not synthesized. All later batches contain complete 6-record vectors.

Rear startup MAIN lengths are confirmed as:

- batch1: 0xF1C (record0 missing from this capture; remaining 0x4/0x3C companions present)
- batch2: 0xEBC
- batch3: 0xA00
- batch4: 0x658

Rear steady state is a 6-BL shape:

0x4, MAIN, 0xC, 0x4, 0x10, 0x14

with the complete E006a census:

- MAIN 0xAC8: 17 samples
- MAIN 0xA98: 2 samples
- MAIN 0x8F0: 11 samples
- MAIN 0x658: 1 steady sample

The fixed wrappers are byte-stable across the bounded corpus except the GEN_IRQ userdata field, which equals the zero-based capture batch index. The 4-byte record0 is invariant across all 34 captured complete batches.

The front-proven CDM decoder closes the rear MAIN structures:

- 0xAC8: 72 commands, 530 ordinary register writes, 16 DMI commands
- 0xA98: 69 commands, 525 writes, 15 DMI commands
- 0x8F0: 50 commands, 459 writes, 13 DMI commands
- 0x658: 29 commands, 345 writes, 3 DMI commands

Repeated samples of 0xAC8/0xA98/0x8F0 normalize exactly after zeroing captured DMI address fields and observed varying register-value fields. No unexplained varying dword remains. The single steady 0x658 sample has the exact same CDM structure signature as startup batch4 0x658; their nine differing dwords consist only of three DMI-address fields plus six ordinary register-value fields, with no unclassified difference.

Rear DMI topology includes the front-known families plus a rear-visible 0xBC08 selector1/selector2 pair (300 and 128 bytes respectively). Dynamic register observations also include 0xBC58/0xBC5C and 0x49B8/0x49BC.

This closes command topology, but not payload ownership. Exact DMI payload bytes remain a separate gate. Native rear Linux ISP and RT-CDM submission remain DENIED.

### Next

Reuse the already-proven front Windows DMI source-slot/ring capture mechanism to capture only rear-referenced payload bytes, then hash/classify them and construct a normalized rear materializer. Do not freeze Windows ring geometry or source IOVAs.
