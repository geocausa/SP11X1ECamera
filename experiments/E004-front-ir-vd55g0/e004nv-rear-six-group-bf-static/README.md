# E004nv — six-group source-only rear candidate, BF CSID bit7 now observed live but no WM16 DMA fence

**2026-09-24 E004ph/E004pi UPDATE:** E004ph resolves original type1 BF input to **CSID0/CSID1 BUF_DONE STATUS+0x8C bit7** (separate from IFE snapshot queue), and E004pi physically observed CSID1 BUF_DONE STATUS `0x000002F1` with bit7 unmasked in BOTH original Windows rear4K LIVE physical register snapshots. This **does not** independently prove original software BF event0x0F/group8 FIFO8 same-frame delivery or VFE1 WM16 BUS/IRQ/DMA/IOMMU safe completion/owner handoff. The E004nv candidate stays compiled but unwired and **runtime DENIED**. Accepted Linux CSID ISR already ACKs BUF_DONE; do not relabel bit7 as VFE WM16 IRQ. [E004pi read-only live evidence](../e004pi-original-live-rear-csid-bf-bit7-wm16-fence-offline/README.md).

# Historical E004nv original static BF event/GROUP8 and source-only kernel candidate

Parent E004nu commit `f06338233da184dde44e3bdb898ad10a37514ef0`. The existing front-camera E003h reverse engineering established five independent OEM Windows completion groups. E004nq then proved an additional active VFE1 WM16 **BAF autofocus statistics** write master in **both** Windows rear 3840×2160 live recording passes. E004nu compiled a separate ten-client rear VFE1 static BUS contract, keeping all ten WM buffers conservatively in flight, but deliberately did **not** assign an unknown completion interrupt to WM16.

**E004nv now independently recovers the omitted BF event branch from the original, exact same-SP11 OEM Windows camera driver** and compiles a rear-specific *six-group candidate*. Neither the original Windows driver nor any camera pixels/DMA addresses are exported, and the candidate has no runtime caller.

## Additional static BF caller / WM16 register chain

[STATIC-BF-CALLCHAIN.md](STATIC-BF-CALLCHAIN.md) and
`verify_static_bf_callchain.py` trace 47 exact ARM64 instruction
anchors in the same private OEM driver. The real indirect caller at
RVA0x239A0 invokes a **mode-dependent** interrupt handler registered
at RVA0x1A100; the event0x0F dispatcher at RVA0x1EF90 is chosen only
in **mode 0**, while mode 1 selects a distinct handler. In mode 0,
incoming status **word2 bit7** generates event0x0F, dequeues FIFO8,
then its per-event callback reads the actual **WM16 CFG0
(VFE+0x1E00) and WM16 ADDR_STATUS0 (VFE+0x1E70)**. CFG0 bit0 is
copied to the precise scratch byte that gates the extended BF
completion record, outstanding-item match, port0x300D tagging and
software notification. This directly links the BF branch to WM16
registers in OEM code; the active Windows rear dispatch mode and any
live BF event/physical buffer retirement are still unproven.
No proprietary Windows binary, private KD log or optical data exported.

## Same-SP11 OEM Windows driver branch: BF event 0x0F, FIFO index 8

The already archived same-SP11 OEM `qccamisp8380.sys` is 376,560 bytes and has SHA256 `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`. The file stays **private on the SAME SP11** at `/home/geoca/Documents/SP11-PROJECT/00-RE-archive/sp11-driverdump/qccamisp8380.inf_arm64_068a5d125dcec104/qccamisp8380.sys`. The new `extract-bf-driver-static.py` validates its entire SHA, PE section addressing and **exact ARM64 instruction anchors** using `llvm-objdump` before exporting ONLY derived event/group/resource scalar evidence to `BF-RESULT.json`.

The following are *literal, independently inspected ARM64 driver instructions*, not interpretations of the front camera's event order:

| OEM driver RVA | Static instruction / property |
|---|---|
| `0x1FC60` | `cmp w8, #0xF`: branch for event **0x0F** |
| `0x1FC6C–0x1FC78` | Loads diagnostic text at RVA `0x37B88`: **“IFE%d IFE BF stats buf done Irq occured.”** |
| `0x1FC8C` | `mov w1, #8`: BF queue group index **8** |
| `0x1FC94` | Calls independent FIFO dequeue helper RVA `0x26460`, the SAME helper used by the previously proven front groups |
| `0x1FCE8` | Records BF resource port **`0x300D`** |
| `0x2650C / 0x26514` | Helper indexes `object + (0x66B + group_index) * 8` and loads the corresponding group-specific queue |

The prior E003h front driver observations captured these five groups: VIDEO event `0x03` index0 (FULL Y/C + DS4/DS16), AEC_BE_BHIST `0x0D` index5 (WM11/12), TINTLESS_BG `0x0E` index6 (WM13), AWB_BG `0x10` index7 (WM14), RS `0x12` index9 (WM18). E004nv adds the statically decoded **BF event `0x0F` index8**, associated by OEM BF diagnostic/port with the rear-only physical **WM16 BAF** output. The original E004nq Windows rear LIVE1 and LIVE2 physically show WM16 enabled; the front static BUS contract omits it.

**Important evidence boundary:** this proves the OEM driver HAS a BF event branch and its independent group index; **it does NOT prove that event 0x0F actually occurred in either OEM Windows rear capture**, that WM16's DMA completed, or that the driver's BF callback was connected to the active rear sensor's live request. A targeted, private **live Windows rear BF-completion trace** is still required before treating the group association as a proven operational Linux ISR mapping. The six-group model is an explicitly labelled static candidate, not a native rear 4K optical frame.

## New separate rear-only compiled kernel candidate

`camss-vfe-e004nv-rear-six-group.inc` retains E004nu's ten-WM register contract and source-pinned private 4K buffer and adds a group descriptor table:

| Event | Group index | Candidate WM ownership |
|---|---:|---|
| `0x03` VIDEO | 0 | 0, 1, 2, 3 |
| `0x0D` AEC_BE_BHIST | 5 | 11, 12 |
| `0x0E` TINTLESS_BG | 6 | 13 |
| `0x10` AWB_BG | 7 | 14 |
| `0x0F` BF (rear candidate) | 8 | **16** |
| `0x12` RS | 9 | 18 |

The 10-bit full ownership mask is `0x03FF`; the six group masks are disjoint and cover it completely. `vfe680_e004nv_rear_frame_ack_group()` accepts only one source-matched group event at a time, rejects unknown or duplicate IDs, and clears the **group's entire ownership mask at once**, unlike incorrectly inventing per-WM hardware events. No cross-group arrival order is imposed; independent per-group FIFO order must still be preserved by the **future** active ring owner. `vfe680_e004nv_rear_frame_retire()` still requires complete ownership AND a separately verified BUS-stopped condition before returning the surface. A real IRQ handler, front/rear core switch and hardware-stop provenance are not implemented or authorized.

`vfe680_e004nv_rear_runtime_authorization()` **always returns `-EOPNOTSUPP`**. No caller to either event or retirement function exists in the new kernel's probe/V4L2/stream/ISR/sysfs paths. The accepted front nine-WM path and existing Linux rear RAW/software4K fallbacks remain untouched.

## Actual ARM64 compiled module, offline tests and Golden integrity

`stage-build.sh` checks protected Golden and exact HEAD `f063382`; source-pins the original accepted integrated `camss.c`, `camss-csid-680.c`, `camss-vfe-680.c` and E004nr/E004ns/E004nt/E004nu/E004nv source hashes. It builds a **fresh isolated CAMSS copy**, with only the five rear header includes added at established source-local boundaries. Removing those includes yields byte-identical original front/rear RAW source; the integrated kernel's pre-existing modified Denali DTS is untouched.

SP11 compiled real ARM64 `qcom-camss.ko`, `W=1 -j4`, with **zero compiler warnings/errors**. The private binary is **not installed, loaded or committed**; it remains on SP11 at `/home/geoca/Documents/SP11-PROJECT/02-kernel/e004nv-rear-six-group-bf-build/camss/qcom-camss.ko`. Its size is 13,694,760 bytes, SHA256 `e7981c01e51ae4246f060b416ac6c11eb01546e2b182bce445478e36f490b80b`, and its vermagic matches protected Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`. `aarch64-linux-gnu-nm -a` confirms all five new rear six-group symbols alongside the compiled E004nr/E004ns/E004nt/E004nu components.

`verify.py` verifies the exact driver/original-source and module SHA, direct static BF event branch and FIFO anchors, prior front event mappings, BOTH Windows rear WM16-live static contracts, actual six-group C table, disabled runtime, compiled ARM64 retained symbols and immutable front source. It runs **720 offline cross-group arrival-order simulations** (not live hardware) and **20 fail-closed negative mutation cases** rejecting missing/wrong BF event, wrong FIFO index/resource/WM bit, front-only five-group substitution, falsely claimed live BF proof and inconsistent second Windows capture. The source-only verifier never loads a module, allocates DMA, touches live camera MMIO or retrieves image data. Run:

```bash
cd /home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera
PYTHONDONTWRITEBYTECODE=1 python3 experiments/E004-front-ir-vd55g0/e004nv-rear-six-group-bf-static/verify.py
./tools/camera-overlap-guard.sh --require-clean-tracked --require-golden --require-no-camera-process
```

**Next hardware dependency:** independently verify BF event 0x0F/group8 during an actual Windows rear VideoRecord 4K session and its relationship to WM16 resource port0x300D; then implement/source-check per-group rear stats DMA/ring ownership, rear OV13858-specific IQ/3A/RT-CDM packet lifecycle and exclusive CSID1/VFE1 front/rear switching with bounded hardware stop and rollback. Do not arm native Linux rear 4K or mark it optically proven merely because source-compiled six-group mappings now exist.
