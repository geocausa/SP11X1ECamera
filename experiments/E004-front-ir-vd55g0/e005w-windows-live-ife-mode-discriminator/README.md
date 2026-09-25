# E005w — minimal live IFE interrupt-mode discriminator

Parent Git `b9c698b5db7440d4ab3790f46ab0146fda49f70e` (E005v).

## Purpose

The exact OEM qccamisp driver has two interrupt schemas selected per IFE instance at runtime. Static source proves the selector is derived from IFE core id versus a runtime hardware threshold, and the same choice selects BUS aperture `+0xC00` versus `+0x1200`. Existing rear-4K evidence proves the physical route uses VFE1/IFE1, but the runtime threshold is not a fixed PE constant.

This one-shot Windows run identifies the actually selected rear-4K schema directly before more completion-path work.

## Probes

Same-SP11 qccamisp8380.sys SHA-256:
`64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`.

All absolute addresses are recomputed from the current module base after this boot.

Only three command breakpoints are permitted, all auto-continue:

- mode0 top-half BUS0 snapshot at RVA `0x1DC5C`: marker + IFE id + raw BUS0 scalar;
- mode1 top-half BUS0 snapshot at RVA `0x1C2EC`: marker + IFE id + raw BUS0 scalar;
- BF event assignment at RVA `0x1F190`: marker only.

No data breakpoint, register/MMIO write, patch, driver mutation or local SP11 debugger is permitted.

## Runtime discipline

- SP7 is the only kernel debugger host.
- Start SP7 KD before arming Windows BootNext.
- Direct Windows EFI BootNext only; persistent BootOrder and Golden GRUB saved entry stay unchanged.
- Use a fresh single-use Windows camera trigger with an atomic consumed marker at script entry.
- Run rear Surface Camera Color / VideoRecord / NV12 3840x2160 for a bounded interval.
- Full camera acceptance requires clean Start/Stop and >=10 valid frame handles.
- Raw debugger logs and any addresses/pointers remain private on SP7/SP11; commit only reduced scalars.
- After capture: clear all breakpoints, close private log, unregister trigger, continue target, normal reboot.
- Verify return to Golden Linux with `tools/camera-overlap-guard.sh`.
- E005n remains unloaded.

## Interpretation

Exactly one of the two top-half schemas should dominate for the rear-4K IFE instance. The active mode plus IFE id and BUS0 behavior chooses the correct proprietary completion path for the next source/dynamic correlation.

This experiment does not itself authorize native rear ISP or claim DMA/IOMMU-safe retirement.

## Runtime result — consumed / accepted camera run, mode discriminator negative

The single E005w Windows attempt was consumed exactly once.

The bounded rear Surface Camera Color / VideoRecord / NV12 3840x2160 capture completed successfully:

- StartAsync: Success
- elapsed: 8,091 ms
- valid 3840x2160 frame handles: 50
- StopAsync: Success
- predeclared acceptance threshold: >=10 frames — PASS

The SP7 external-KD private log was reduced to safe marker counts only:

- BF event marker: 86
- mode0 top-half BUS0 probe at RVA 0x1DC5C: 0 runtime hits
- mode1 top-half BUS0 probe at RVA 0x1C2EC: 0 runtime hits

Because the BF marker fired repeatedly from the same module while both proposed top-half probe sites remained silent, this run does **not** identify mode0 or mode1. It instead rejects the assumption that either of those two selected probe sites can be used as the live rear4K mode discriminator without a deeper source trace. The zero counts must not be promoted into a claim that IFE interrupts or WM16 completion were absent.

Cleanup completed: all KD breakpoints were removed, the private KD log was closed, the one-shot Windows task was unregistered, the target was resumed, SP11 was rebooted normally, and protected Golden Linux returned with overlap guard PASS. E005n remains unloaded.

Native rear processed ISP remains **DENIED**.

### Next smallest step

Stay static. Trace backward from the proven BF/type-1 path and its actual registered interrupt/preparer callbacks to the precise runtime mode selector/IFE instance dispatch. Source-lock the real physical WM16 completion predicate/ACK path before another Windows run. Do not repeat E005w under the same identity.
