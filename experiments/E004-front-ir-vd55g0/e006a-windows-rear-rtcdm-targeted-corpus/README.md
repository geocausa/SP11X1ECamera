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
