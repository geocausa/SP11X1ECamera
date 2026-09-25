# E005q — bounded Windows live OEM top-half + BF/WM16 correlation

Parent Git: `ba8d4281236b6499615870b41839b3bff4b9da0b` (E005p).

## Hypothesis

During one real Windows rear VideoRecord NV12 3840x2160 session, the exact OEM full-IFE top half will expose a reproducible raw interrupt tuple for BF-producing interrupts. The same session should also retain the already-proven live BF -> FIFO8 non-null -> matcher non-null path and permit a bounded read of WM16 CFG0/ADDR_STATUS0 from the same OEM VFE/BUS object.

The experiment is specifically looking for a same-session bridge between:

1. raw OEM TOP0/TOP1/BUS0/BUS1 before OEM writeback;
2. TOP1 bit7, which E005p source-locks as the BF event0x0F source;
3. BF FIFO group8 non-null and outstanding matcher non-null;
4. WM16 CFG0 and ADDR_STATUS0;
5. the live resource0x300D output-programming record, including the scalar fields around its resource entry.

This run does **not** predeclare which raw BUS bit is the completion witness. It must be observed and source-checked.

## Exact source-locked probe sites

Same-SP11 `qccamisp8380.sys` SHA-256:
`64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`.

All runtime addresses are rediscovered from the module base after this Windows boot; no historical absolute address is reused.

- OEM mode0 full-IFE top half RVA `0x1DC6C`: all four raw words have already been stored to the interrupt packet:
  - packet+0x04 = TOP0
  - packet+0x08 = TOP1
  - packet+0x0C = BUS0
  - packet+0x10 = BUS1
  At this site x19 is the device object; `[x19+0x150]` is BUS base = VFE+0xC00, therefore WM16 CFG0 is BUS+0x1200 and WM16 ADDR_STATUS0 is BUS+0x1270.
- BF event assignment RVA `0x1F190`.
- FIFO8 return materialization RVA `0x1FC98`.
- matcher return RVA `0x1FCE8`.
- resource0x300D write-master table match RVA `0x27FC8`; when the record matches, x10 identifies the live output record. Capture bounded scalar dwords only, no DMA payload.

## Runtime discipline

- SP7 is the external KD host. Never run local/on-target KD on SP11.
- True PTY/ConPTY KD only.
- Breakpoints are command breakpoints that print bounded scalar evidence and immediately `gc`.
- No data breakpoint, no register write, no MMIO write, no patching, no driver modification.
- Raw kernel pointers, DMA addresses, debugger log and optical data remain private on SP7/SP11 and are not committed.
- Use the existing direct EFI Windows one-shot helper. Persistent GRUB saved entry remains `sp11-audio-fullio-v19c`; BootOrder must not change.
- The Windows camera helper is single-use with an atomic consumed marker and is removed after the intended invocation.
- After capture: remove all breakpoints, close KD log, continue target, remove the one-shot task, normal reboot. The machine must return to Golden Linux and pass `tools/camera-overlap-guard.sh`.
- No E005n Linux observer load in this experiment.

## Success / interpretation

A useful PASS requires a successful rear4K session plus a source-coherent raw IRQ tuple for BF-producing activity, live FIFO8+matcher positives, and stable WM16 state from the same bounded session. Any proposed composite-group interpretation must be backed by an exact live scalar plus a source-defined field; a coincidental value 7 is not enough.

Even a positive run does **not** by itself authorize native rear ISP. Same-generation exact-buffer identity, DMA/IOMMU quiescence, safe reuse, and six-group retirement remain separate gates unless independently closed by the captured evidence.

## Rollback

The direct Windows EFI entry is BootNext-only. A normal reboot returns through GRUB to the persistent Golden Linux entry. SP7 remains available throughout any SP11 kernel pause.

## Runtime result — consumed / partial

The single E005q Windows attempt was consumed exactly once. Rear VideoRecord Start and Stop both succeeded, but the six debugger probes reduced delivery to 5 valid 4K handles in 8.402 s, below the predeclared >=10-frame acceptance threshold. The attempt therefore **does not receive a full capture PASS** and must never be replayed under the same identity.

The private SP7 KD log was reduced locally to safe scalars only: 35 BF events, 35/35 non-null FIFO8 entries, 35/35 non-null matcher returns, equal opaque FIFO/matcher keys for all 35 events, and 70 WM16 ADDR_STATUS0 samples spanning 10 distinct values. The two WM16 samples around each key were equal for 33/35 events and changed for 2/35, so this is live movement but **not** an exact per-buffer fence.

Resource 0x300D was observed in 37 write-master updates with source-proven W=25 and H=4. The 4 is height, not composite group. The 0x1DC20 snapshot probe emitted zero rows; E005r explains why this is not a hardware-negative result.

All breakpoints were removed, the private debugger log was closed, the triggerless scheduled task was unregistered, and a normal reboot returned SP11 to protected Golden Linux with the overlap guard PASS.

Native rear processed ISP remains **DENIED**. See E005r for the corrected type-1 CSID provenance and the exact OEM composite-group field.
