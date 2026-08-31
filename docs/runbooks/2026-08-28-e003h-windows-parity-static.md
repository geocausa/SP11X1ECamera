# E003h Windows-parity transport static handoff — 2026-08-28

## Resume point

## E003h ACTIVE — 0052 clock-rate package installed/inspected unarmed — 2026-08-31

A distinct Golden-safe 0052 package is installed under `/boot/sp11-7.1.5-camera-e003h-csidclk-0052` with GRUB ID `sp11-camera-e003h-csidclk-0052-one-shot`. It binds static checkpoint `23ea4ce8b6ddc2bc76e15f2121087eeef34b8484` and CAMSS `42662121c848d863b06e3aba737e0f80a35fc047faf8cf5b0f47e2554ba3e92a`; helper, IMX681, front-only DTB, capsule, media setup and RT-CDM observer remain byte-identical to consumed 0051.

Package-only preflight and independent inspection are green. Golden kernel/initrd and saved default are exact, `next_entry` remains empty, camera modules are absent, DT is front-only with the accepted IOMMU set, no authorization exists, runtime preflight precedes module loading, one helper invocation is enforced, and a pre-existing RUN log refuses retry. The package inspection preserves the provenance distinction: Linux's old request is proven 300MHz, the bounded correction uses its existing link-derived 400MHz selection, HBI 400/300 correlation is proven, but a direct Windows 400MHz vote is not claimed.

Asset manifest `18d65aa6734ca1634a19607e1c377ac7b281bb26f1891bcf758e4594fea06974`; package inspector `03e1a86778462e1ed2fa58b31b32d1bb6ed7f2df78154fd0d132ffe35cd858c1`; inspection `b62e9ef8e9e1854bb4153872405b2761f04ec27a6ef93bc5eaee59e27005b1da`. **The candidate is installed but unarmed and runtime is not authorized.** Publish this package checkpoint before a fresh authorization review.


## E003h ACTIVE — first-Epoch boundary corrected; X1E CSID clock bug yields 0052 static PASS — 2026-08-31

0050/0051's earlier "by first Epoch" geometry wording compared unlike sampling points and is superseded. Windows `0x00600228` already contains CAMIF EOF while Linux `0x00600cc0` does not; both systems are width-only before EOF. The corrected divergence is the first completed frame/EOF measurement: Windows is 3840x2160, while Linux's first EOF completion is 3840x2640 with bit14 `ERROR_LINE_COUNT`. Fail-closed EOF oracle `db4476e159872f9005a127d84ea41032191402de2709a0835d2c2c5fbc9dffde` pins qccamisp read/clear semantics, both traces and the raw-Windows-log provenance warning.

That correction exposed a concrete Linux clock-selection defect. The proven front sensor reports fixed one-trio C-PHY `link_freq=1.2GHz`. Existing CAMSS math requires link/4 plus 5% margin = 315MHz, selecting 400MHz from X1E's 300/400/480 table. But `csid_set_clock_rates()` scales only legacy names `csi0..csi3`; X1E names the clocks `csid` and `csid_csiphy_rx`, so Linux falls through to `freq[0]` and requests 300MHz. X1E CAM_CC has distinct hardware 300/400/480MHz entries. Independent HBI telemetry matches the same 4/3 ratio: Windows 946/941 ticks versus Linux 709/704; scaling Linux 400/300 predicts 945.33/938.67. Direct Windows 400MHz clock-vote capture is not claimed.

0052 bounds the correction to X1E80100 CSID1 + CSIPHY2 + one-trio C-PHY. Only `csid` and `csid_csiphy_rx` enter the existing link-derived rate algorithm, yielding 400MHz for this mode. No tables/margins or camera register programming change. Patch `55c27634af4837e615145a7df9f4e92119b75c7a5b53957fa5864ddd16266788`; module `42662121c848d863b06e3aba737e0f80a35fc047faf8cf5b0f47e2554ba3e92a`; inspection `e20bf446fde42298988c586b941e4c96ec8017f8c67bc4a396b824f359f676ad`; checkpatch 0/0 and Golden vermagic exact. **No runtime is authorized.** Package and inspect unarmed before a separate one-shot authorization review.


## E003h ACTIVE — 0051 consumed; post-RUP +0x18 bug is real but non-causal — 2026-08-31

The single authorized 0051 differential executed exactly once and returned immediately to FullIO v19c Golden with no retry. RT-CDM reached FIFO sequence 17 without fault, no QC10C buffer was produced, and IMX681/CAMSS runtime PM returned to suspended. Golden identity, saved default, empty `next_entry`, and absent camera modules are verified.

0051 removed only the Windows-unmatched front-mode0 IPP post-RUP_DONE `REG_UPDATE_CMD +0x18` write while retaining Linux software bookkeeping and all RDI/non-front behavior. The result is byte-for-byte identical to 0050 at the critical CSID boundary: `00811dd0/00000f00 -> 00600cc0/00000f00 -> 00000cc0/00000f00 -> 00004ee8/0a500f00`. First-Epoch geometry does not improve, bit14 remains, VFE1 raw Epoch0 does not advance, and output remains absent.

Therefore the post-RUP zero write is a genuine Windows-parity defect but is not causal for the vertical-crop failure. The proven boundary remains after the matching first RUP_DONE IRQ and by the immediately following Epoch IRQ, where Windows is already 3840x2160 and Linux is still height-incomplete. The Windows first-Epoch status carries EOF-class side bits (`0x00600228`) while Linux carries SOL/EOL-class side bits (`0x00600cc0`), but that status-class difference must not be assumed causal until IRQ coalescing/clear timing and active-update semantics are closed statically.

Runtime extractor `3ac0fad9d4d34f54ebdd7cdc1d82d141b460df3bd63d71e1add6363108636e2f`; analysis `2e1fbd740073b98e9e86ef477f1986d9b7e94a26a5e486f4386197b8e331f9d1`. **No runtime is authorized.** Next gate: exact Windows/Qualcomm active-update and first-Epoch event semantics; no speculative crop-register write.


Branch: `experiment/e003-front-imx681-cphy`

Last pushed checkpoint entering E003h: `c60bad2` (`docs: align current state with E003g route oracle`).

Golden remains byte-exact FullIO v19c and is the saved default. E003h static CAMSS code remains undeployed. A same-machine Windows-only KD round trip has now resolved cross-driver lifecycle ordering; the machine returned to byte-exact Golden afterward. No Linux E003h module load, sensor transmission or frame attempt has occurred.

## Non-negotiable oracle rule

Same-machine Windows on this exact SP11 is the behavioral oracle. Qualcomm/upstream/external Linux source may provide register names, field layouts and implementation mechanisms only. A working Linux RDI stream is not parity if Windows uses IPP/VFE1 PIX/ISP.

## Windows path now established

Physical instances:

**IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1**

Sensor transport:

- 3840x2640 @ 30 fps;
- RAW10 / VC0;
- one-trio CSI-2 C-PHY;
- Windows stream-on = single `0x0100=0x01` write, zero delay;
- Windows stream-off = single `0x0100=0x00` write, zero delay;
- group hold `0x0104=1/0` is separate and must not be conflated with streaming.

CSID1 receiver:

- `RX_CFG0 +0x200 = 0x11300000`;
- `RX_CFG1 +0x204 = 0x00000001`;
- one active trio, CSIPHY2 selection, C-PHY type, Windows' stable bit-28 field, ECC correction only.

CSID1 IPP:

- `CFG0=0x802b2000` -> enabled VC0 / DT0x2b RAW10 / 10-bit decode;
- `CFG1=0x00007241`;
- crop 0..3839 x 0..2159;
- measured 3840x2160.

VFE1 bus clients:

- FULL Y 2560x1440;
- FULL C 2560x720;
- DS4 320x180;
- DS16 80x45;
- BE0/BHIST0/TINTLESS_BG/AWB_BG/RS statistics active;
- PIXEL_RAW and RDI0/1/2 are not the WinRT output.

## Exact Windows lifecycle evidence

Exact installed `qccamisp8380.sys` SHA-256:

`64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`

Static ARM64 disassembly of its DEVICE_START (`0x804`) path proves:

**IFE start -> initial IFE/CSID configuration packets -> CSID start**.

Static disassembly of DEVICE_STOP (`0x805`) proves:

**CSID stop -> IFE stop -> CDM/remaining core stop**.

The front sensor KMD powers/opens MIPI CSI before sensor init/config/crop and applies `SensorStreamOn` later through its async path. A two-pass same-machine Windows KD oracle now resolves the cross-driver boundary too. Both exact `Surface Camera Front` WinRT cycles mechanically produced:

**ISP_START_DONE -> SENSOR_STREAM_ON_APPLY -> ISP_STOP_DONE -> SENSOR_STREAM_OFF_APPLY**.

Combined with the static ISP-internal decode, Windows therefore uses:

**start: CDM -> IFE -> config packets -> CSID -> sensor `0x0100=1`**

**stop: CSID -> IFE -> CDM/remaining core -> sensor `0x0100=0`**.

Raw KD evidence: `experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-dynamic/E003H_LIFECYCLE_ABS_20260828.log`, 51,296 bytes, SHA-256 `2908392a619b14f229161dec616e43052103b53b161a3fc77edda56b782d1b36`. The parser and exact front-only holder are archived beside it.

A four-cycle MIPI follow-up closes CSIPHY placement. Raw evidence: `experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/windows-mipi-order/E003H_MIPI_ORDER_20260828.log`, 8,600 bytes, SHA-256 `09a9b0aa11c677563dee521b14157d76eaecebe9971491a8156b82020bbef224`. All starts are exactly **ISP done -> MIPI start enter -> MIPI start done -> sensor-on**. On stop, ISP teardown always completes first, but sensor-off is unordered relative to MIPI stop: Windows demonstrated sensor-off before MIPI entry, between entry/done, and after MIPI completion. The parser therefore validates a partial order rather than inventing a total order.

Detailed evidence: `experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/WINDOWS-ISP-LIFECYCLE.md`.

## Linux gaps discovered

1. X1E `camss-csid-680.c` parsed C-PHY metadata but failed to place PHY_TYPE_SEL into RX_CFG0; the prior E003d C-PHY bit fix affected only the Gen2 implementation.
2. Windows also leaves TPG_NUM_SEL=1 with TPG mux disabled. This is odd but stable in both same-machine live passes and must not be normalized away.
3. The static E003h RX patch now computes the exact Windows `0x11300000` for CSIPHY2 one-trio C-PHY and changes no D-PHY bits. CAMSS builds cleanly with Golden vermagic. It is not deployed.
4. Current CSID680 stream programming is RDI-only; Windows uses IPP.
5. Current VFE680 output is RDI-only. The generic PIX line mapping is explicitly invalid and would send line 3 through WM27/LTM_STATS. Do not enable PIX as-is.
6. Generic Linux stop traversal VFE -> CSID conflicts with Windows ISP-internal CSID -> IFE teardown. Static-only `0010-x1e-windows-stop-order.patch` changes X1E teardown to CSID -> VFE -> the existing remaining upstream tail. The current CSIPHY -> sensor tail is one Windows-observed valid serialization of the now-proven unordered sensor/MIPI stop tail; do not claim Windows requires that relative order. The patch applies reproducibly and is not deployed.

## Static artifact

- `experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/0009-x1e-csid680-cphy-rx-windows-parity.patch`
- `experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/0010-x1e-windows-stop-order.patch`

Build result:

- PASS, no warnings/errors;
- RX-only 0009 module SHA-256 `900b016c6dca0f79a150eaf50bfe17e0c9cbfbb3cc5ab92596330c5698b4a7af`;
- RX + lifecycle 0010 module SHA-256 `b7c9ed932e2dccca4eaf73d085d2c5c8e6104d7cb807bafd00804051a9e82591`;
- CSID1 IPP 0011 patch SHA-256 `a002e6bbd0725bc46fbc911269c2ad6f946c2e19bff4b78d9de9b109ae9f1e9f`;
- CSID1 IPP 0011 module SHA-256 `ff02c59fa29001093cdeda8ace138cf6e5ef6e29fb27f86beb632237c4c0f90b`;
- Golden vermagic `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- no deployment.

`0011` makes X1E source pad 4 a dedicated IPP selection instead of RDI3/VC3, keeps the Windows front path on VC0, programs the stable CSID1 IPP mode-0 registers/crop/measure, and is fail-closed to the accepted CSID1/CSIPHY2/one-trio-C-PHY/SRGGB10 3840x2640 tuple. Rear RDI0/VC0 selection is unchanged. Full reproducibility details are in `CAMSS-IPP-BUILD.txt`.

## Windows initial IFE startup byte oracle

The same-machine Windows startup byte oracle is now closed at the four IFE `0x803` submissions inside DEVICE_START.

Main CDM evidence: `windows-ife-cdm/raw/E003H_IFE_CDM_INIT_EXACT_20260828.log`, 175,222 bytes, SHA-256 `a22f94b6a024226791c139336b17777f1359f1847146bafa6e092215e86e762a`. The deterministic decoder uses Qualcomm camera-driver commit `0f16924ff6a7f9bb56a7e958016da2ed8a174f2f` only for CDM encoding/names. All four streams decode exactly to their declared lengths with zero unknown opcodes: 278 CDM commands, 2,131 register writes and 46 DMI commands. Packet 3 independently matches the E003g Windows-live VFE1 values at `+0x24` and `+0x90`, mechanically pinning the CDM base to VFE1 `0x0ac71000`.

The main streams reach `VFE1+0xbe70`; 2,015 startup writes lie outside the current upstream X1E VFE `0x4000` aperture. The deterministic ownership classifier now proves the exact required span is `0xbe74`, page-rounded `0xc000`. The same-machine Denali VFE0->VFE1 bases are exactly `0xf000` apart and the historical Denali resource span is exactly `0xf000`, which covers the complete observed corpus. Static-only `0012-sp11-vfe-aperture-windows-parity.patch` therefore overrides only Denali VFE0/VFE1 sizes from `0x4000` to `0xf000`. The DT build passes, output size is unchanged, and a byte comparison shows exactly two changed bytes: one size byte for each VFE aperture. No common X1E resource is changed.

Final patch/DMI evidence: `windows-ife-cdm/raw/E003H_IFE_PATCH_DMI_EXACT_20260828.log`, 5,832,792 bytes, SHA-256 `719043805efd57d26483497c0c1964251e77461ccdb7213e5fdc1947defbffc7`. Exact ARM64 disassembly of installed `qccamisp8380.sys` proves the internal packet fields and 24-byte patch record mechanism. `extract_patch_dmi_oracle.py` mechanically proves:

- 46/46 patch records correspond one-for-one with 46/46 DMI commands;
- every patch destination is the exact DMI address word in the correct command-buffer slot;
- every patched IOVA is the captured source IOVA plus the patch source offset;
- DMI payload bytes are encoded length + 1, with all referenced bytes captured;
- maximum source end is exactly `+0x1bccc` inside the captured 0x20000 window;
- that 128 KiB source window is byte-identical across all four hits, SHA-256 `bbb9dc35ec2fccc68c81af7f2e13813c75d3c27d5b4450903f5004dc3cc69d9a`;
- 46 references form 21 exact `(DMI register, selector, bytes, SHA)` groups and 16 unique payload byte strings.

Supporting captures prove descriptor 1 is CSID1 IPP command data and reproduces the 3840x2160 crop; descriptor 2 is not the DMI source allocation. Full details and hashes are in `windows-ife-cdm/DMI-ORACLE.md` and `patch-dmi-summary.json`.

The pinned public VFE680 kernel header exposes top/bus layout but not the pixel-IQ DMI block map at the observed DMI register offsets. Do **not** guess semantic labels such as gamma/rolloff/GTM/LTM from payload size. Preserve exact register+selector+payload identity until an authoritative layout or exact Windows static proof supplies the names.

Ownership result: 695 unique startup offsets = 650 single-valued + 45 packet-phase-varying, with zero within-packet value changes. Five offsets independently proven live-volatile by the E003g two-pass oracle are classified `runtime_volatile_do_not_freeze`. The initial-CDM corpus contains zero writes in the public VFE680 BUS-client range, so Windows output-buffer programming is not mixed into the IQ startup replay.

The two-pass VFE1 BUS oracle independently closes the FULL surface: client 0 FULL_Y and client 1 FULL_C are stable writable configuration around a single contiguous 2560x1440 TP10-UBWC/QC10C surface. The kernel's existing QC10C tile geometry produces the same 3584-byte stride and exact camera core surface `0x76b000` with offsets `Y_META=0`, `Y_DATA=0x6000`, `C_META=0x4f2000`, `C_DATA=0x4f5000`. Dynamic Windows image/meta addresses and status readback are explicitly excluded from replay.

Windows IRQ behavior is cross-proven dynamically and statically: live `TOP_MASK0=0x0007f051`, `BUS_MASK0=0xd0000000`, and exact `qccamisp8380.sys` writes those literals in its VFE interrupt initializer. Its DPC maps TOP status1 bit0 to normalized event 3, logged as `IFE VIDEO buf done`. Rear X1E RDI completion remains CSID680 BUF_DONE-driven, while CSID1 IPP handles RUP only, so a front VFE VIDEO-done implementation can be isolated from the accepted rear path.

## Hardware CDM execution now resolved

The exact DMI selector/execution ambiguity is closed by two same-machine Windows follow-ups under `windows-ife-cdm/`.

First, `CDM-EXEC-ORACLE.md` records a bounded live diagnostic which rejects importing the older VFE17x direct LUT-dump sequence as VFE680 behavior. Second, `HW-CDM-ORACLE.md` records the decisive native path:

- acquire input `SW CDM = 0x00`;
- exact hardware-CDM branch hit; software-CDM branch did not hit;
- `RT_CDM_0` physical `0x0ac25000`;
- `RT_CDM_1` physical `0x0ac26000`;
- both `HW_VERSION=0x20010000`, matching public RT-CDM v2.1 layout;
- the front path is active on **RT_CDM_1 FIFO0**; RT_CDM0 BL state and RT_CDM1 FIFO1/2/3 base+length are zero;
- the archived POST sample, taken after normal StopAsync **and dispose/session teardown**, returns both RT-CDM windows to the `0x80000000` powered-off sentinel; it was not sampled exactly at DEVICE_STOP `0x805`.

Dynamic BL base/length values are command-buffer state and must never be hard-coded. The Linux parity target is now an equivalent fail-closed **RT_CDM1 hardware execution path**, not guessed direct VFE DMI MMIO.

### Dedicated RT-CDM interrupt closed

A controlled restart of only the same-machine Windows ISP device hit the exact `qccamisp8380.sys` interrupt-registration routine during WDF `PrepareHardware`. The focused raw oracle is `experiments/E003-front-imx681-cphy/e003h-windows-parity-transport-static/raw/E003H_RTCDM_IRQ_MAP_20260828.log`, 7,428 bytes, SHA-256 `0f4b30273ddd7af23bbad5158b2da57a320c143b43ce5119927bbfbcfa6cbf1b`.

Mechanical registration arguments prove RT_CDM0 = class 3 / instance 0 / raw firmware GSI 488 (`0x1e8`) and **RT_CDM1 = class 3 / instance 1 / raw firmware GSI 319 (`0x13f`)**. The Windows-translated vector is OS-local and is not a Linux DT value. The SP11's existing CAMSS DT provides a six-resource namespace cross-check: `GIC_SPI` cells 464..469 map exactly to Windows ISP GSIs 496..501. Therefore this platform uses `GSI/INTID = GIC_SPI cell + 32`, and RT_CDM1's Linux DT cell is exactly **`GIC_SPI 287` (`0x11f`)**. `windows-ife-cdm/extract_rtcdm_irq_oracle.py` is hash-pinned and fail-closed; see `RTCDM-IRQ-ORACLE.md`.

The controlled Windows ISP restart recovered `Started/OK`, and SP11 then returned to byte-exact Golden with all three canonical hashes unchanged and empty GRUB `next_entry`.

### Linux inert RT_CDM1 resource layer built

Static `0013-sp11-rtcdm1-inert-resource.patch` establishes only the resource contract. It appends Denali-only RT_CDM1 MMIO `0x0ac26000/0x1000` and `GIC_SPI 287 IRQ_TYPE_EDGE_RISING`, preserving all existing CAMSS resource positions. Generic Hamoa/other X1E boards are unchanged. The helper is optional, X1E-only and fail-closed on the exact physical base/span; it resolves the named IRQ and maps the aperture but deliberately performs no MMIO access, IRQ request, DMA allocation or command submission.

CAMSS build is clean with Golden vermagic; `qcom-camss.ko` SHA-256 is `7bdb7e43edda74c4f9b6fc0351fe46255e9696d4a7d008c3ab2817d83b8052ad`. The Denali DT grows 44 bytes (`215173 -> 215217`) and the decompiled structural diff changes exactly four CAMSS properties by appending `rt_cdm1`: `reg`, `reg-names`, `interrupts`, `interrupt-names`. Result DTB SHA-256 is `bbe48a77c5bc23f1c155ddc87b9a5b2ed56497656f06cab1a2db8e6346f0304b`. See `RTCDM1-STATIC-RESOURCE.md`. No runtime occurred.

### Linux disabled IRQ/DMA scaffold built

Static `0014-sp11-rtcdm1-disabled-irq-dma-scaffold.patch` adds the next layer without enabling the engine. The dedicated IRQ is requested using `IRQF_TRIGGER_RISING | IRQF_NO_AUTOEN`, matching CAMSS's existing disabled-at-probe CSID/CSIPHY pattern. No arm API exists and the source contains no assignment of `irq_armed=true`, so the ISR cannot touch MMIO in this layer. The compiled FIFO0 status model is pinned by `static_assert` to the Windows literal IRQ mask `0x00070007`; public v2.1 definitions are used only to identify reset-done, inline, BL-done, invalid-command, overflow and AHB-error bits plus status/clear offsets.

The same patch provides a caller-sized coherent DMA arena through the existing CAMSS 32-bit DMA domain, independently rejects DMA addresses above `0xffffffff`, allows one arena, and zeroes it both after allocation and before deterministic free. There is no FIFO0 base/length/store/config write, no IRQ-mask write, no reset/core/FE/core-enable write, and no submit API. Module build is clean with Golden vermagic, SHA-256 `0a3f1e64af5e69d428f08982aad1ad7dd39d32a5eb5baa11df6c4c78a9ce9a10`; the Denali DTB remains byte-identical to `0013` at SHA-256 `bbe48a77c5bc23f1c155ddc87b9a5b2ed56497656f06cab1a2db8e6346f0304b`. See `RTCDM1-IRQ-DMA-SCAFFOLD.md`. No runtime occurred.

### Windows RT-CDM1 init/start/commit/stop order pinned

`extract_rtcdm_init_order.py` is fail-closed to exact installed `qccamisp8380.sys` SHA-256 `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`. It mechanically pins open/init as `IRQ0_MASK=1 -> RST_CMD=9 -> reset wait <=500 ms -> DMB SY -> CORE_CFG=0x11f`; full DEVICE_START as **CDM -> IFE -> initial IFE/SFE/CSID packets -> CSID**; RT-CDM start as `IRQ0_MASK=0x00070007 -> DMB SY -> CORE_EN=1`; dynamic FIFO0 commit as `BASE -> encoded LEN/tag/arb -> STORE=1`; and DEVICE_STOP as **CSID -> IFE -> CDM**, with the direct CDM stop write limited to `IRQ0_MASK=0`.

The deterministic bounded mapped-base store sweep finds no direct software store to live `FE_CFG +0x20=0x07ff000f` or `FIFO0_CFG +0x5c=0x01000000`. This is intentionally classified as negative evidence only: it does not prove reset/default ownership. The conditional `CGC_CFG +0x14=7` path and final stop/power separation are closed by the subsequent exact-binary oracles; positive ownership/timing of the two live configuration values remains the RT-CDM initialization blocker. Extractor SHA-256 is `399a7a6ecd412d652fcce1bad469514c87a0e696ad7bf4e68a55c51f148e6629`; JSON SHA-256 is `489f47f45465603260a06f8aa2083cc417fff816478be9b6c8f68233bb0be927`. See `WINDOWS-RTCDM1-INIT-ORDER.md`. No Linux RT-CDM behavior was enabled.

### Windows RT-CDM1 configuration ownership narrowed

`extract_rtcdm_config_ownership.py` adds a second fail-closed exact-binary gate. The Windows CDM object is allocated as `0xa40` bytes and fully zeroed at RVA `0x1839c`; the RT-CDM mapping is acquired once in the CDM-object init and stored at object `+0x48`, while the later command parser uses the distinct target aperture field `+0x838`. Resource-getter call census, helper separation and mapped-base stores are pinned mechanically.

The optional `CGC_CFG +0x14=7` write is guarded by object byte `+0xa38`. That byte starts zero, has exactly one fixed-offset access in the executable (the guard read), has no overlapping direct store, and is not covered by subsequent object bulk-memory operations. Therefore the normal in-binary lifecycle leaves the branch **not taken**. Linux must not add the optional CGC write.

For live `FE_CFG +0x20=0x07ff000f` and `FIFO0_CFG +0x5c=0x01000000`, the stronger alias/resource/helper/parser census still finds no in-binary CPU write path. This is not promoted to a reset-default claim: positive hardware/reset origin timing remains unresolved. Extractor SHA-256 is `d25da738a827d81439d426b4de828300af0c6544d2e3d1d0dab78bb8a981b1e7`; JSON SHA-256 is `4c01a85709d9442953cfd5692219c04b57db5683312f788082e18b5aa6677b7c`. See `WINDOWS-RTCDM1-CONFIG-OWNERSHIP.md`.

### Windows RT-CDM1 stream stop versus power collapse separated

`extract_rtcdm_stop_power.py` is fail-closed to the exact installed `qccamisp8380.sys` and the exact prior HW-CDM live log. It proves that `DEVICE_STOP 0x805` is a stream-level stop: **CSID -> IFE -> CDM**, with the CDM command's direct mapped-MMIO write limited to `IRQ0_MASK +0x30 = 0`. There is no proven `CORE_EN=0` or reset write.

Later camera control `0x80e` dispatches manager/session delete. That path releases per-block CDM associations, closes the CDM software object, clears its manager slot, then explicitly powers off/closes CSID followed by IFE. The exact CDM close/cleanup range contains no access to the object's RT-CDM MMIO field `+0x48`, so it hides no shutdown register write. CSID and IFE `POWER_OFF` both converge on the same reference-counted platform helper, which invokes the platform callback only when the component use count reaches zero.

Accordingly the archived all-`0x80000000` POST state is scoped to **post StopAsync/dispose/session teardown**, not the exact `0x805` boundary. Linux must preserve stream stop and final runtime/power teardown as separate layers and must not invent a `CORE_EN=0`/reset sequence. Extractor SHA-256 is `3bf8189e2657fead2f7b1ee128e56f368d457e64618ebb1c732770c82d69f805`; JSON SHA-256 is `75711e2cf1bc1697db11e7415f23f71de1e12706d86d5fa55666bfd4ddfc39b8`. See `WINDOWS-RTCDM1-STOP-POWER.md`.

### Windows RT-CDM1 FE/FIFO positive origin timing closed

The two-cycle same-machine oracle in `raw/E003H_FEFIFO_ORIGIN_20260828.log` closes the remaining configuration-ownership timing question. Cycle 1 teardown leaves RT_CDM1 `+0x00..+0x7f` uniformly `0x80000000`. On cycle 2, at resource-map return RVA `0x1849c` and again at pre-first-MMIO RVA `0x187a0`, before the front CDM object's first write (`IRQ0_MASK=1` at RVA `0x187a8`), the mapped RT_CDM1 already contains `HW_VERSION=0x20010000`, `FE_CFG +0x20=0x07ff000f`, and `FIFO0_CFG +0x5c=0x01000000`. The FE/FIFO literals remain unchanged after reset wait and after `CORE_CFG=0x11f`; final teardown returns the sampled window to the sentinel.

This is positive same-machine timing evidence that FE/FIFO are restored by the pre-CDM-object platform/power-up/hardware layer. It deliberately does not distinguish firmware from hardware reset/default origin. Linux must **not write** these values: after equivalent power ownership is active and before the first RT-CDM write, it must read-only validate all three literals and fail closed on mismatch. Raw log is 18,444 bytes SHA-256 `4d54bca3a1c8d2c542b6b09361e9cdee50a4e85175cb0667f0b8dd10c92076bb`; extractor SHA-256 is `16f283a084152c8998f1b222dd681fdf7257998ce29c311af97e734d4e7b4243`; JSON SHA-256 is `7ab8eab8867393639d1a034d15bcd361e8773d64a5346a9de5f764f0a0a8ea3b`. See `WINDOWS-RTCDM1-FE-FIFO-ORIGIN.md`.

### Linux Windows-derived RT_CDM1 static recipe built but unreachable

`0015-sp11-rtcdm1-windows-static-recipe.patch` now compiles the Windows-proven RT_CDM1 mechanics without connecting them to runtime. The private preflight reads and requires `HW_VERSION=0x20010000`, `FE_CFG=0x07ff000f`, and `FIFO0_CFG=0x01000000`; it never writes FE/FIFO. Private helpers then encode open/init as `IRQ0_MASK=1 -> RST_CMD=9 -> reset-done wait <=500 ms -> DMB SY -> CORE_CFG=0x11f`, start as `IRQ0_MASK=0x00070007 -> DMB SY -> CORE_EN=1`, FIFO0 commit as dynamic `BASE -> observed encoded LEN -> STORE=1 -> BL-done wait`, and stream stop as `IRQ0_MASK=0` only. The optional CGC path is absent and no `CORE_EN=0` shutdown exists.

The helpers are retained only by a private `__used` ops table. Static binary inspection finds exactly five ABS64 relocations from that table to the five helpers and **no relocation/reference to the table itself**, so probe/media/stream/teardown cannot reach the write-capable code in this patch. Compiled ARM64 inspection confirms both required `dmb sy` barriers and the FIFO0 `+0x50 -> +0x54 -> +0x58` sequence with the observed `0x00100000` high field. Patch SHA-256 is `32661bf7e6eae864d857cd96bcfccdf01e820fbfbc3a2c2d9bf5cfa8f5ad9514`; `qcom-camss.ko` SHA-256 is `0c2f3df7423310c3384b02f6465b5ecb4b91ce73391b1f7fc10adca7157440d9`; inspector SHA-256 is `07338c3751c4d0cc53a6cb813b4f3fb43af9f9af26c27e9e0d65b8f31e3ad72a`; inspector JSON SHA-256 is `23f9f601f0e9b8880e447d17685585bbdc1e0058a8be60fcf330172e366aa346`. Denali DTB stays `bbe48a77c5bc23f1c155ddc87b9a5b2ed56497656f06cab1a2db8e6346f0304b`. See `RTCDM1-WINDOWS-STATIC-RECIPE.md`. No runtime occurred.

### VFE1 PIX/QC10C static contract built, stream still blocked

Exact `qccamisp8380.sys` disassembly now closes VIDEO completion ownership. Windows programs `TOP_MASK0=0x0007f051` and `BUS_MASK0=0xd0000000`; its DPC extracts TOP status1 bit0, converts it to event 3, and event 3 enters the exact `IFE VIDEO buf done` branch. FULL Y/C therefore completes as one VIDEO surface, not as two independent V4L2 frames. `extract_vfe1_video_completion.py` SHA-256 is `04d54dce4b103e6c8f50785d90db2fe6db71c70ffdc09b00efbc5c7bffd09409`; derived JSON SHA-256 is `c8436846bb73082de504da00d0760280b347cd5b8fbbc5e9702197ed0509573c`.

`extract_vfe1_pix_static_contract.py` combines that completion oracle with the already-pinned Windows BUS and FULL-layout oracles and closes the Linux-facing memory contract: exactly 2560x1440 `V4L2_PIX_FMT_QC10C`, 3584-byte stride, one V4L2 DMA plane, `sizeimage=0x76b000`, with internal offsets `0`, `0x6000`, `0x4f2000`, `0x4f5000`. FULL is WM0+WM1; DS4 WM2, DS16 WM3 and stats WM11/12/13/14/18 remain auxiliary Windows outputs. Contract extractor SHA-256 is `95efd94c70584a971dd79f074aed5cfb0a9904739bc530f0e6dffe3ac1dbd490`; JSON SHA-256 is `820c7971218e4b018994ed36e60ba5d04f8a75fec91fdca66fcf981d4a5fc3b5`.

Static `0016-x1e-vfe1-pix-qc10c-static-contract.patch` implements only that representation. Exactly one X1E PIX table changes: IFE1. IFE0 and both Lite entries remain unchanged. The VFE1 PIX sink/source uses `MEDIA_BUS_FMT_SRGGB10_1X10`, userspace memory is QC10C with one fixed discrete size, and the Windows FULL/aux/mask/event values are retained as read-only data with no runtime relocation. `vfe_enable_v2()` returns `-EOPNOTSUPP` for X1E VFE1 PIX before stream lock, IRQ enable, output allocation or WM programming. Existing VFE680 RDI WM start/update/stop functions are untouched. Build PASS: `qcom-camss.ko` SHA-256 `97fd2dd9a482c0ba8e6c0d3e5a7cf190612bdca4610a81c59a576bc5e4cf7834`; patch SHA-256 `4e0cbba5b169353a4f62cfdf1aacd93ac811ae3366f72658eeee7cefaca7ab03`; inspector SHA-256 `af5b43ac294f442260f132ca4e2731812cf5100186fc0cecc17a103a94936f51`; inspection JSON SHA-256 `cb2d5ae35b0879d2f716f1193aec54f921daddf4560e410f0cd0fed7d742fe10`. Denali DTB remains unchanged. No runtime occurred. See `VFE1-PIX-QC10C-STATIC.md`.

## Exact next task

1. Treat CSID1 IPP static representation as closed by `0011`; do not expand it beyond same-machine Windows-proven mode-0 state without new oracle evidence.
2. Treat the VFE1 FULL memory format as resolved: one contiguous 2560x1440 **TP10 UBWC / QC10C-family** surface with 3584-byte stride and `Y_META -> Y_TP10 -> C_META -> C_TP10` layout. Linear NV12 is not parity.
3. Treat the Windows IFE startup byte corpus as complete: four main CDM streams, 2,131 register writes and all 46 DMI payload references/bytes are captured. Further Windows byte capture is not the current blocker.
4. Treat register ownership and VFE aperture as closed by the deterministic classifier and `0012`: never replay the five live-volatile offsets or any Windows buffer/status address, and keep the `0xf000` override Denali-only.
5. Preserve the 21 exact DMI register/selector identities and 16 exact payloads. Native execution is RT_CDM1/FIFO0 and static Linux representation is now closed through unreachable `0015`: exact read-only preflight, reset/init/start/FIFO0/stop mechanics compile with no runtime caller, no FE/FIFO/CGC write, and no invented `CORE_EN=0`. Do not connect that recipe to runtime until the VFE1 PIX path is complete.
6. Treat VFE1 PIX format/surface/completion representation as closed through `0016`: IFE1-only RAW10 -> one 2560x1440 QC10C allocation, FULL WM0+WM1, exact four-region offsets, and one Windows VIDEO completion event. `0016` must remain stream-blocked.
7. Recover exact same-machine Windows BUS client configuration/address-update ordering and auxiliary DS/stats buffer ownership/lifetime relative to RT-CDM/IFE start and per-frame updates. Never freeze Windows IOVAs. Then build an unreachable BUS recipe before connecting any PIX runtime path.
8. Preserve the proven lifecycle: ISP -> MIPI -> sensor on start; ISP teardown first on stop, with no invented dependency between MIPI-stop and sensor-off. Keep `0010` static-only.
9. Build/static-test the complete parity candidate and prove rear D-PHY/RDI behavior is unchanged.
10. Only then define a bounded one-shot runtime gate with exact Golden rollback. No front parity frame is authorized before these conditions are met.

RDI remains available solely as an explicitly non-parity diagnostic if it becomes useful for fault isolation.


## 2026-08-29 — VFE1 BUS session order closed

A new same-machine KD capture (`raw/E003H_VFE1_BUS_ORDER_20260829.log`, SHA-256 `b6777baf442eab4cfea0985ad3a1274e80e3545505483935e506e2d9e086dd41`) was parsed by `extract_vfe1_bus_order.py` (SHA-256 `c7edb8f1b17f83b91ee5f8c08a72b872c904a3a3f50eac1952bb1e5d2018013b`). The resulting `vfe1-bus-order-oracle.json` is byte-reproducible and proves three complete Windows sessions with identical ordering:

`BUS static config -> BUS enable -> ISP_START_DONE -> BUS disable`

The exact resource sequence is `FULL[0], FULL[1], DS4, DS16, AEC_BE, RS, BHIST, AWB_BG, TL_BG`; enable and disable both use `FULL, DS4, DS16, AEC_BE, RS, BHIST, AWB_BG, TL_BG`. This aligns mechanically with the earlier two-pass VFE1 live oracle: the active write clients and all writable non-address configuration remain stable between starts, while image/meta IOVAs change and therefore remain per-buffer state.

The capture also corrects the next breakpoint target. `qccamisp8380+0x1e928` did not fire; the active path repeatedly enters `qccamisp8380+0x27920`, whose `x1` argument is a command-buffer descriptor containing a 64-bit request buffer reference followed by offset/length fields. Pre-start descriptors advance through `0x9000`-sized regions, and later request processing continues through the same builder. The exact buffer contents/address patch order and lifetime are not yet captured, so Linux PIX/RT-CDM execution remains blocked.

Next: dump and decode the `0x27920` request-buffer contents on same-machine Windows, correlate their dynamic address patches with FULL Y/C, DS4/DS16 and statistics clients, then build an **unreachable** BUS recipe. Do not freeze Windows IOVAs and do not arm Linux streaming yet.

## 2026-08-29 — dynamic VFE1 address writer closed; Linux BUS recipe remains unreachable

The prior instruction to chase `qccamisp8380+0x27920` as the dynamic address writer is superseded. A focused same-machine Windows KD pass identifies the real VFE1 address writer as RVA `0x1dd20`. Its image write site at `0x1dea4` writes client `IMAGE_ADDR +0x04`; when FULL metadata exists, RVA `0x1dee8` writes `META_ADDR +0x40`. The exact address sequence is `FULL_Y, FULL_C, DS4, DS16, AEC_BE, RS, BHIST, AWB_BG, TL_BG`. FULL enable/disable uses WM0 then WM1.

The lifecycle capture is exact: **static BUS config -> BUS enable -> first complete nine-client dynamic address set -> ISP_START_DONE -> repeated per-frame address sets -> BUS disable**. The first and subsequent sets use different IOVAs. Observed slot strides are evidence about Windows allocation/ring behavior only and are not Linux constants. Raw initial-order log SHA-256 is `3a2dd357e994f8f5d52668f7c914ad27a2dda6fdee8804e55daa3fcde1c5bed6`; deterministic extractor SHA-256 is `e8d9e278de52f1e1d363c60621a2cc789dc33f149cb53d222bab0b0092419211`; derived oracle SHA-256 is `925028750e8be60c65a69f24349bb540b0ba0776726f40d59273b0be7f464282`. The supporting address-writer/live-correlation captures are archived under `windows-vfe1-dynamic-address/`.

Static `0017-x1e-vfe1-pix-bus-unreachable-recipe.patch` encodes only the mechanically proven BUS semantics. It accepts caller-supplied Linux DMA IOVAs, derives the exact QC10C internal Y/C metadata/data offsets, programs static client state in the Windows resource order, enables WM0 then WM1 plus auxiliaries, writes the initial IOVAs, and provides a separate update helper for subsequent buffers. Captured Windows IOVAs and Windows ring strides are absent. The helpers are retained only by a private `__used` recipe table and have no runtime caller or VFE ops reference; X1E VFE1 PIX still returns `-EOPNOTSUPP` before stream lock/IRQ/output programming.

Build/static proof: patch SHA-256 `55e88685bf71fff5ba74ceb53972b28f71c6c9120659cd756847d8308a7b2d5e`; inspector SHA-256 `db54f0feec5948c68cf6450a1d424f1c447fcf8444c203671cf295aabefbd09d`; inspection JSON SHA-256 `92715605c99523366dd619331c6abe9bb09c7e6476bf8921ccb5b18cbaae262e`; module SHA-256 `44b9233d668cad0eb8da3c7805845d006ee3bd000ef17a5e2173fac9846783ef`. Forward/reverse patch reconstruction passes, compiler diagnostics are empty, Golden vermagic matches, and no module was loaded.

**Next:** keep all runtime blocked. Define and statically prove PIX buffer/completion ownership: one userspace QC10C VIDEO surface for FULL WM0/WM1, with DS4/DS16 and five statistics outputs backed by separate internal Linux allocations and lifetimes. Combine that model only with the unreachable `0017` BUS recipe and unreachable `0015` RT-CDM/IQ recipe. No RT-CDM submission, VFE1 PIX enable, sensor transmission or frame is authorized.
## 2026-08-29 — VFE1 completion ownership closed; independent group FIFOs

A bounded five-cycle same-machine completion capture observed `VIDEO(0x03) -> AEC_BE_BHIST(0x0d) -> TINTLESS_BG(0x0e) -> AWB_BG(0x10) -> RS(0x12)` on every cycle. Raw log SHA-256 is `1e3e810ae170dabb003491b6b8522c3b77dbd5964a14445ce7bbd3636e5b77ec`.

Do **not** turn that observed order into a protocol dependency. Exact installed `qccamisp8380.sys` disassembly pins helper RVA `0x26460`: the event branch passes one group index in `w1`; the helper selects `object + (0x66b + group_index) * 8`, pops one record, decrements that queue's count, advances its own ring read index and wraps by that queue's capacity. Active group indices are `0,5,6,7,9`. Windows therefore owns five independent completion FIFOs. Extractor SHA-256 is `461899f4b32e0208466db17ac23b366987caeb9d59210faba65023ce265c8162`; oracle SHA-256 is `696f476a18bbfe4d6a30e06198c744d6495048b85399d22ff1bfe6c6176763f9`.

Static `0018-x1e-vfe1-pix-buffer-ownership-unreachable.patch` models two frame slots. Each slot has one caller/vb2-owned QC10C surface plus seven separate coherent Linux auxiliary allocations (DS4, DS16, AEC_BE, BHIST, TL_BG, AWB_BG, RS). Begin enqueues the slot into all five independent group FIFOs and returns an IOVA bundle for the still-unreachable `0017` BUS recipe. Completion pops only the FIFO selected by the event. VIDEO may return the userspace buffer, while the slot is reusable only after all five groups retire in any cross-group order.

`0018` does not call BUS helpers, modify ISR/`vfe_buf_done`, touch VFE ops or weaken the PIX `-EOPNOTSUPP` gate. Patch SHA-256 `fb1d0acece63c9acde2f48bb51d1bac19fcdc17d3c7f1fd46de6f2bf0adc924f`; inspector `1f91e87fce072a37d7c870b65fd186f3e56d18c271ec6149e465bbf668c27d2e`; inspection JSON `bc8bf64152882e8c312e0e1379b544e2ae733dc75b4e571784fac3b88b4b7dcf`; module `7d88c0d6c69d3690c4e83437b41e8afb05560d1390d0d819e8b8374db71e5010`. Build and forward/reverse reconstruction pass with exact Golden vermagic and no compiler diagnostics. No runtime occurred.

Next: build an **unreachable RT-CDM command-corpus materializer** from the already-captured four IFE main-CDM streams and 46 DMI commands/16 unique payloads. Preserve exact bytes and patch only mechanically classified dynamic fields. Do not submit FIFO0 or connect VFE1 PIX runtime yet.

## 2026-08-29 — RT-CDM command/data materializer closed; dynamic startup fields exposed

A cross-capture normalizer now compares the original four main-CDM captures with the independent final patch/DMI capture. After removing the 46 DMI IOVA words, the only additional byte-level difference is VFE680 `period_cfg +0x8c`. Together with the five offsets already proven live-volatile by E003g (`+0x3b70`, `+0x3d78`, `+0x3d7c`, `+0x3d80`, `+0x3d84`), the four templates have exactly 20 dynamic register-value fields. Zeroing those 20 values plus all 46 DMI addresses makes both Windows captures byte-identical. Extractor SHA-256 is `3f02b5860996c95a323f3e1fce49c927674511e231a0466536f146b83c572faf`; oracle SHA-256 is `1d1b753eeaf25bcdfd1105154138bb9123d40330f070b1b8fd0eb6ab69f38cdc`.

`materialize_rtcdm_corpus.py` packs the 16 unique payloads into a deterministic Linux `0x3a00` DMI arena and the four commands into independent 4 KiB Linux slots. It reconstructs both independent Windows variants at synthetic Linux DMA bases and both decode to exactly 278 commands, 2,131 ordinary register writes and 46 DMI commands. Static proof SHA-256 is `7e3577fba84d50e02fb43d0c47ac2b440e9714575acb93ae0db64a5fc2c9938b`.

Static `0019-x1e-rtcdm-corpus-materializer-unreachable.patch` mirrors only those mechanics. It embeds no captured command/payload arrays, rejects any non-zero normalized hole, requires all 20 dynamic values plus a complete valid mask, allocates 32-bit coherent Linux command/DMI arenas, and patches only Linux DMI addresses plus caller values. Windows `0xa000` command spacing and DMI source offsets are not frozen. The helper pair is retained only by a private `__used` table: exactly two ABS64 relocations target `materialize/release`, while the table itself has no runtime relocation/reference. There is no MMIO, IRQ arm, FIFO0 commit, VFE op or stream connection. Patch SHA-256 `5e6f557ef692b32ada97a98daa9188db979c70ba46b9c8dd21b6f8a93ced25a2`; inspector `1264822dd10f71a3eb90acf2d903f51464f0241082198eec381dbc08527f2ea2`; inspection JSON `f0a4fc0fcc83306db0fec7c1345240bc91eb1b267636af35a86203d38ee0b62e`; module `f783550d532c20066a4b378d6ba0a86c9242d567b036603fd8623681e3e3ae66`. Build, forward/reverse reconstruction and all deterministic reproductions pass with Golden vermagic. No runtime occurred.

**Next:** recover same-machine Windows producer semantics for `period_cfg +0x8c` and `+0x3b70/+0x3d78/+0x3d7c/+0x3d80/+0x3d84`. Do not use captured values as Linux defaults. Only after their exact source/update rules close may the private `0011/0015/0017/0018/0019` pieces be combined into an unreachable start orchestrator.

## 2026-08-29 — startup dynamic ownership correction (`0020`)

The conservative `0019` 20-dynamic-word boundary is superseded by a tighter same-machine Windows oracle. `E003H_VFE1_DYNFIELD_KMD_PASS_20260829.log` proves `qccamisp8380+0x26838` leaves the tracked fields unchanged for packets 0..3. The cadence capture then shows `period_cfg +0x8c` reading zero after startup, `+0x3b70` stable in the bounded samples, and `+0x3d78..+0x3d84` changing while streaming.

The startup command corpora tell a different and crucial story: the 16 non-period words are identical across independent captures and fresh KMD entry. After normalizing 46 DMI addresses plus only four period words, both startup corpora are byte-identical. Therefore the 16 words remain exact startup-template data and only the four period fields remain caller-dynamic. This distinction prevents live-mutating register state from being mistakenly replayed as a caller-generated startup patch. Ownership oracle SHA-256 `402510679bae860f801166bd7ff36834ca8284650aa29d64f1c08d7c6afda856`.

Static `0020` changes the private materializer to four dynamic entries and `GENMASK(3,0)`. It embeds no captured values, introduces no runtime call path, and keeps VFE1 PIX fail-closed. Refined static materialization remains 278 commands / 2,131 ordinary writes / 46 DMI. Patch SHA-256 `147b89961803f3812c10dfd6f89cc00a4273d077514fc39756e5eb78f2d2d86e`; inspection JSON `a589a5546342bb9ad127bc6b5b880071cb1be35bdc8327524b7e521eb48f4add`; Golden-vermagic module `ccafdf9e94ec6e5e1609bb5e36ec8c1f6bb97055d8e6a4ce80a09c3cecd73d2f`. Forward/reverse reconstruction and build pass; no module was loaded.

**Next:** resolve the upstream `period_cfg +0x8c` value/production rule and the later live-update semantics needed by an unreachable orchestrator. Keep FIFO0, VFE1 PIX and IMX681 transmission blocked.

## 2026-08-29 — period_cfg transport narrowed to two opaque upstream values (`0021`)

The four packet-local `period_cfg +0x8c` holes retained by `0020` are not four independent inputs. Four accepted same-machine Windows starts/captures all satisfy the same relation: packet 0 carries one start-dependent value, while packets 1/2/3 carry one identical shared value. The absolute values vary between starts. The earlier KMD pass-through proof also establishes that these words arrive already populated and are not changed by the captured downstream IFE handler. The kernel transport layer must therefore accept **two opaque upstream inputs** and must not invent a formula or freeze any observed Windows value. Contract oracle SHA-256 `0e6128140b6126845ca2656977f7cc137b1a32e6063b51497d3e808db29fed0d`.

Static `0021-x1e-rtcdm-period-cfg-two-value-contract-unreachable.patch` implements only that relation: two caller values, four patch sites, mapping `0 -> value0` and `1/2/3 -> value1`, with a two-bit valid mask. The deterministic materializer reproduces both independent Windows startup variants with exactly 278 commands, 2,131 ordinary writes and 46 DMI commands. Patch SHA-256 `2f30286f01e6214c6af4fdf1e8908837ae3db39cb4a68075584fc2732b689636`; inspection JSON `169cf024d87e2f9a4ec620fb15be657767d8e01dd87da0b47ebe9c11375e37c3`; built module `6f29ccec021c0f2a6662bf9f7b27ec799d842ce14e1e235be3794e050dc6b921`. Build, strict source inspection and forward/reverse reconstruction pass with Golden vermagic. No module was loaded.

**Next:** build a private **unreachable** front-start orchestrator that composes the already-proven route, RT-CDM, BUS, PIX ownership and command-corpus layers while leaving the two period values explicit inputs. It must remain disconnected from probe/VFE/media runtime and must not submit FIFO0, enable VFE1 PIX, transmit IMX681 or attempt a frame.

## 2026-08-29 — front-start cross-order and unreachable orchestration contract (`0022`)

The missing cross-layer ordering between the four initial IFE `0x803` packets and VFE1 BUS setup is now closed. In the bounded same-machine Windows capture, the exact prefix through the first `ISP_START_DONE` is: packet0, packet1, nine BUS static configurations, eight BUS resource enables, one complete nine-client initial address set, packet2, packet3, then `ISP_START_DONE`. Raw log `E003H_VFE1_BUS_CDM_CROSSORDER_20260829.log` is 47,032 bytes, SHA-256 `c32acebd61e0b2364450035c2b9e383a86e0ad355387760c149fb0e113342963`; extractor SHA-256 `e0cd5d690b60b8a9a18dc7a413a4bf0956b44ce25dc6d8e176218e80939913ad`; oracle SHA-256 `b495cc833c45e97b1467749bf094bb3035c5e6070bd0ea13d26a99ceec6acce6`.

Combined with the accepted Windows manager order, the host lifecycle is `RT-CDM start -> IFE resource start -> packet0 -> packet1 -> VFE1 BUS prepare -> packet2 -> packet3 -> CSID1 IPP start -> ISP_START_DONE`. MIPI/CSIPHY start and IMX681 stream-on remain after `ISP_START_DONE` and outside this host contract.

Static `0022-x1e-front-start-orchestrator-unreachable.patch` does **not** execute that lifecycle. It retains a target-exact contract plus a validator: X1E80100 / CSIPHY2 one-trio C-PHY / CSID1 IPP RAW10 3840x2640 / IFE1, period map `{0,1,1,1}`, Linux-only preparation markers, exact host stage order, `hardware_execution_authorized=false`, and `mipi_sensor_start_included=false`. The validator calls only the existing corpus-input validator. No RT-CDM write/FIFO helper, VFE1 BUS helper, CSID start helper, VFE stream path, IRQ arm or MMIO write is added.

Static proof: patch SHA-256 `1bf7d406e50bb3b57884d6f3a043d6c728327a8d8162f6ed9a678d2b8317e190`; module SHA-256 `d845b027f2c0ae70c47deb24d6cf08cf597cb02a1c4545b2a97a66508a8ac8c8`; inspector SHA-256 `aa4348699216c7bdbb623a552f6e1b235249d115868a3f26f1874fd49358ba47`; inspection JSON SHA-256 `dc4a86ae51cfc608074194d89874268d03cd52569591694b4e32c71dd3ec700a`. Build and forward/reverse reconstruction pass with Golden vermagic. Checkpatch has zero code/style checks; only mail-patch metadata is absent. No module was loaded.

**Next:** superseded by the post-start ownership closure below. Keep all runtime blocked.

## 2026-08-29 — post-start VFE1 ownership and scheduling contract (`0023`)

The remaining post-`ISP_START_DONE` ownership ambiguity is now closed. Accepted same-machine Windows evidence `E003H_VFE1_POSTSTART_OWNERSHIP_VALID_20260829.log` is 8,616 bytes, SHA-256 `81aa7b23e2434dd89ddea21868917e23a2ce3abc1220a19b53805324c37825b5`. The fail-closed extractor SHA-256 is `54bf175c539255fde78c9483cdd7511394cd4593845e5c43e932ff0ff5730f30`; derived oracle SHA-256 is `d426c7cf4525f36c80623cab628061005c880abd5df02d17d8a76683fea4e66e`.

Two local Windows windows independently show the same sequence. Session 1 has a complete nine-client address bundle at seq `0..8`, `ISP_START_DONE=9`, another complete bundle at `10..18`, the first observed VIDEO/AEC-BHIST/Tintless/AWB/RS completion cycle at `19..23`, then a refill bundle at `24..32`. Session 2 repeats the same relationship at `42..50`, `51`, `52..60`, `61..65`, and `66..74`. Windows therefore visibly primes two complete address bundles before the first completion. This is an observed startup prime depth, not an allocator-ring constant. The five completion groups remain independent FIFOs; their observed cross-group order is not a Linux dependency.

Exact `qccamisp8380.sys` ARM64 disassembly closes the software scheduler behind that timeline. IFE ISR call site `0x1f410` invokes Epoch0 handler RVA `0x25268` before completion dispatch begins at `0x1f438`. Epoch0 calls the resource/BUS-update wrapper at `0x25a38`, which reaches the existing X1E BUS address-writer callback RVA `0x1dd20`; it then calls RT-CDM dispatcher RVA `0x28480` with selector `2` at `0x25ec8`. That selector dequeues/programs the queued BL batch and reaches RT-CDM FIFO0 base/length/store writes at relative `+0x50/+0x54/+0x58`. The same dispatcher uses selector `1` to accumulate BL descriptors and selector `0` to queue the accumulated batch. Steady-state Windows software ownership is therefore **IFE Epoch0 -> complete VFE1 BUS IOVA update -> queued RT-CDM BL consume/program -> completion dispatch/retirement**.

This does not turn live VFE state into Linux writes. `period_cfg +0x008c`, `+0x3b70`, and `+0x3d78/+0x3d7c/+0x3d80/+0x3d84` remain the startup-template identities established by `0020/0021`; the latter four mutate while Windows streams and are hardware-live observation only. No periodic post-start software rewrite of those six identities is proven.

Static `0023-x1e-front-post-start-ownership-unreachable.patch` records only this ownership/scheduling contract as read-only data in `camss.c`: four stage identities, nine clients per bundle, two observed initially primed bundles, five completion groups, independent cross-group completion, all-groups slot retirement, software-owned BUS/RT-CDM/completion actions, and explicit `hardware_execution_authorized=false`. It adds no function, ops table, MMIO/IRQ/DMA primitive or hardware-helper call. Object/module inspection retains only one read-only `camss_x1e_front_post_start_contract` symbol and no relocation references it.

Static proof: patch SHA-256 `962c8f6792b1ceb1649d6928df325ee1ed884f292342b0633b98c826a52cd7be`; module SHA-256 `15754a8529b12b65cc37adfd9135e10de4b30418613204488c7722c37c1e2b6d`; inspector SHA-256 `e6c19ce210caf4e65b2fb18dcbf5230c9ef42846063644f6228f8a2d7b4ce1ca`; inspection JSON SHA-256 `e7251c0bd0f047473891c7b4011ed760e1821bebf8b7fea2e2602a29b9875625`. Build and forward/reverse reconstruction pass with exact Golden vermagic. Strict checkpatch has zero code/style checks; only mail-patch metadata is absent. CAMSS was not loaded and no Linux camera runtime occurred.

**Next:** keep runtime blocked. The remaining steady-state parity blocker is the exact **post-start RT-CDM BL batch content** queued before and consumed at Epoch0; the current command corpus covers the four startup IFE `0x803` lists only. Capture several same-machine Windows queue/consume batches, preserve their descriptors and command bytes, and classify invariant versus per-frame/request-dependent content. Do not create a caller for `0022/0023`, arm RT-CDM IRQ/FIFO0, start CSID1 IPP/VFE1 PIX/MIPI, transmit IMX681 or attempt a frame.

## 2026-08-29 — steady-state Epoch0 CDM batches closed; 0024 remains unreachable

A clean same-machine Windows selector-2 capture now preserves exact steady-state RT-CDM command bytes. `E003H_VFE1_EPOCH0_CDM_BATCHES_CLEAN_20260829.log` is 3,994,804 bytes SHA-256 `1e8dc9671296e35a0704315588669fc8ed97612fd4b72c1d71b11bb7244d9a7f`. Exact driver anchors prove the 0x28-byte queue record carries BL IOVA, CPU alias and encoded length; the encoded length is **byte_count - 1**. The deterministic extractor SHA-256 is `d02f7faaeb034e0d7b0931f6c1490a37211784cf535599b29544baf8f3fc329a`; oracle SHA-256 `3bcf4efe34c891dcc6bc78c3cefc94d916ffd71e27dab81e75493f9ed320dce4`.

The capture has 179 batches / 894 records: four startup batches then 175 steady Epoch0 batches. Every steady batch is `{4-byte CHANGE_BASE 0xf000, main IFE BL, 4-byte CHANGE_BASE 0x57000, fixed 0x10 BL, fixed 0x14 register+GEN_IRQ BL}`. The main BL has five real structural variants: `0x958` (8 samples, 56 commands/472 writes/14 DMI), `0x868` (42, 45/436/12), `0x83c` (46, 43/429/12), `0x6b8` (24, 35/352/8), `0x5a4` (55, 22/315/2). Within each variant, zeroing all DMI IOVA words plus only observed varying register values yields one byte-identical normalized template.

This corrects one 0023 inference: Windows does carry `period_cfg +0x008c` and `+0x3b70/+0x3d78/+0x3d7c/+0x3d80/+0x3d84` in queued per-frame RT-CDM command lists. Do not convert that into a CPU/direct-MMIO periodic rewrite; the writes belong to the CDM program. Static `0024-x1e-epoch0-cdm-batch-contract-unreachable.patch` records that correction plus the five batch shapes as retained data only. Patch SHA-256 `4b234a789b25bb1f37d703d2cbfdf8824c0443466523b3d4484e06457689f095`; module `1f88683b72263db8a425d2ef54627c5e9ce7db7e4c6f66e71463fa01c9fdd9ad`; inspector `193eddc9a3dc4fb95dcdc02119d641724f0721450935b8d8093c9da319538afb`; inspection JSON `2f7bab800b36d9fc1529b4f08552b069c0d8bd6163025306d553ba62c0a8f90a`. Forward/reverse reconstruction passes, Golden vermagic matches and CAMSS remained unloaded.

**Next:** do not repeat batch capture. Recover the real steady-state DMI payload source CPU aliases/bytes for all five variants, the upstream variant-selection rule and GEN_IRQ batch-tag producer. Only then build an unreachable steady-state materializer. No RT-CDM FIFO0 submit, VFE1 PIX/CSID1/MIPI enable, IMX681 transmission or Linux front frame is authorized.

## 2026-08-29 — steady-state DMI payload topology hash-closed; upstream IQ ownership remains

Representative DMI payload bytes are now captured locally for all five `0024` main-BL variants without placing proprietary payload bytes in Git. Accepted live mapping log `E003H_VFE1_DMI_VARIANT_RING_20260829.log` is 8,868 bytes, SHA-256 `f44d09f8669576fe868a51d2b410c443dd863c8d00b7ab53ad1375b3b4acf3b0`. The local source-ring/slot `.bin` files are intentionally untracked.

The fail-closed hash extractor `extract_vfe1_epoch0_dmi_payload_variants.py` (SHA-256 `b802a9005581b636405cc4f43f6dd024b8691b5271ee5bf5fd6262c79b715e05`) validates the exact driver, `0024` topology, live packet/variant mapping and local evidence hashes, then emits only payload identity/length/SHA-256 sets. Derived oracle SHA-256 is `90155ed2f0dce9eefc2f3c1c32fb2c60eec58ed0f8ebf0a0e74622bc686357e7`. Samples cover `0x958=2`, `0x868=10`, `0x83c=2`, `0x6b8=4`, `0x5a4=2`. `4308/1` and `4308/2` vary in every multi-sample variant carrying them; `0x958` additionally varies `4708/1` and `5a08/1`. The second `0x83c` sample confirms only `4308/1` and `4308/2` vary; its other ten carried DMI identities are invariant across both.

Static qccamisp disassembly changes the ownership model: `DAL_ife_process_iq_packet` (`0x26838`) consumes an upstream IQ packet and derives changed resource-group masks before processing only those groups. The five observed command-list sizes are therefore not selected by a hidden KMD five-way state machine. They are shapes of upstream-supplied IQ content. Windows source-ring geometry (`0x8000` slots, 15 observed slots) remains allocator evidence only.

**Next:** keep runtime blocked. Close the upstream producer/value rule for frame-varying IQ payloads and the exact GEN_IRQ request/tag source; obtain another dedicated `0x83c` payload sample if needed for within-variant stability. Do not build a reachable materializer or submit RT-CDM FIFO0 yet.

## 2026-08-29 — GEN_IRQ tag source and second 0x83c payload sample closed

A focused same-machine correlation captures 246 BL4 `GEN_IRQ` tags `1..0xf6` and 245 selector-2 Epoch0 request identities `2..0xf6`. The first two tags are the already-proven primed batches; thereafter every tag `N` immediately precedes selector-2 `requestId=N`, with `subRequest=0` throughout this stream. Raw log SHA-256 `7a182c14f2f797fef4143177e2c9e17dae885766a6c2a4781564a3f5250a974c`; extractor SHA-256 `157d566b0690ec7e9df8e87749cd5082760ae8c5b3bf0851ced444dc7a744f9e`; oracle SHA-256 `ddbc97e3213287a7d02f879bd8b9ee81e5b2d3a1d7338a2d6d9b002067535ab6`. Linux steady BL4 userdata is therefore request-derived (`low32(requestId)`), not an independent CDM counter.

A second dedicated `0x83c` DMI slot (local/untracked raw SHA-256 `3ff9097d63db3386670287519c2e95133fe6cbaa145fcc668626825346d62659`) confirms the same payload rule seen in the other multi-sample variants: only `4308/1` and `4308/2` vary; the other ten carried DMI identities are invariant across the two samples. The updated hash-only DMI extractor/oracle remain raw-byte-free.

**Next:** move above qccamisp KMD and identify the producer/value contract for the frame-varying IQ register and DMI values supplied in each incoming IQ packet. Runtime remains blocked.


## 2026-08-29 — registered CamX DeviceMFT owns steady-state IQ values

The remaining upstream ownership ambiguity is closed from the exact Surface camera package. `surfacecamavs8380.inf` (16,736 bytes, SHA-256 `4db3acab414e344dc460478b54d964c9c7b5d3d648ee0c19db13523431262fcb`) registers CLSID `{4C2331F0-66BE-4177-9841-2FCBA8CCF5CA}` to `QcDeviceMFT8380.dll`. The exact DeviceMFT is 23,998,368 bytes SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`; it contains Qualcomm CamX IFE node, IQ-module and Titan680 hardware-setting paths. `surfacecamavs8380.sys` (547,192 bytes SHA-256 `b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed`) explicitly receives UMD CSL command descriptors/address patches and queues/sends packets.

Exact ARM64 command-builder anchors map every `0024` changing register and DMI identity to CamX: DemuxBLS141 (`0x3b70/74`), PDPC311 (`0x3d58/5c`, `0x3d78..84`, DMI `0x3d08`), LSC411 (`0x4358/5c`, DMI `0x4308`), WB201 (`0x456c/70`), GIC311 (`0x4758/5c`, DMI `0x4708`), BPCABF411 (`0x4958/5c`, DMI `0x4908`), GTM131 (`0x5a58/5c`, DMI `0x5a08`), Gamma151 (`0x5f58/5c`, DMI `0x5f08`) and DSX101 (`0xa058/5c`, `0xa258/5c`, DMI `0xa008/0xa208`). The five steady BL shapes are thus incoming CamX IQ-module/dirty-group subsets, not a hidden KMD mode selector.

Dependency strings pin the semantic boundary without reverse-engineering proprietary algorithms: LSC uses AEC/AWB/calibration/tintless state; Gamma consumes AEC/AWB; GTM uses TMC/AEC/DRC tone-mapping state; DSX is crop/MNDS/DS4 geometry driven; PDPC uses sensor/PDAF state; WB uses application/AWB gains; DemuxBLS uses format/gain/BLS state. Extractor SHA-256 `85f8b405b3e10b195f972f732df658daec66be45f03cce76883fbe4bf129ba18`; derived oracle `cbd8908d967f4831e67f8eb3c36ae9799c4bcb42e1923f0ee34c2152841c03ef`.

**Next:** build an unreachable **consumer-side** steady-state materializer. It may accept an observed normalized template shape and module-level values/payloads and repatch Linux-owned DMI DMA plus request-derived GEN_IRQ. It must not embed Windows values, reproduce Windows allocator geometry, invent CamX algorithms, or submit RT-CDM hardware.

## 2026-08-29 — Linux steady-state module-input materializer closed (`0025`)

Static `0025-x1e-epoch0-module-input-materializer-unreachable.patch` represents the already-proven steady Windows consumer boundary without embedding or recreating CamX algorithms. The caller must provide exactly one normalized `0024` main-BL shape (`0x958/0x868/0x83c/0x6b8/0x5a4`) plus the exact module-level register-value and DMI-payload valid masks implied by that shape. Every proven dynamic/DMI field in the template must be zero. `request_id` must be nonzero, `subrequest` must be zero, and BL4 `GEN_IRQ` userdata is generated as `low32(request_id)`.

The helper allocates a Linux-owned 4 KiB command arena and compact 12 KiB DMI arena. Fourteen named payload slots cover PDPC311, LSC411, GIC311, BPCABF411, GTM131, Gamma151 and DSX101; every DMI address is rewritten to Linux DMA. The four tiny companion BLs are synthesized from public CDM encodings and independently reproduce the accepted `0024` hashes. No captured main template, payload bytes, Windows IOVA or Windows ring geometry is present in kernel source.

Independent userspace proof `materialize_vfe1_epoch0_module_inputs.py` (SHA-256 `9da0f3772102f4576181d36ee476bc6ce2deaec01ed70a8086999f249d1a6009`) takes real normalized Windows samples for all five shapes and injects synthetic module values/payload bytes at synthetic Linux DMA addresses. The resulting main lists still decode exactly to `56/472/14`, `45/436/12`, `43/429/12`, `35/352/8`, and `22/315/2` commands/register-writes/DMI respectively. Proof JSON SHA-256 is `7c4b37c2579bd1bf4eae8e1756a7557cad9505929bbc21a986855209af94b4bc`.

The final patch is SHA-256 `75b882588d2945721ccd000b76fee79266bc88c6b69aeddbddf506cd7982ae68`; candidate `camss.c` `378bd309fdd6246f7ce2742891a0a9cfa3ec6df4a1cd830d8c5e902d7fdaed85`; Golden-vermagic module `09abae83c74330806359af7b095c988abd2680af765ea148ee48c996252b6c35`. Inspector SHA-256 `46d3601e3ba1e8f2478156947d5f64abfa218821782cc791f2bb7cba4e903c10`; inspection JSON `ae60274a57a0b95d1a56f074daa90f98f9c672ef60a6f4af5028fef0ca041b46`. Forward/reverse reconstruction is byte-exact; the retained recipe has exactly two ABS64 relocations to materialize/release and no reference to the recipe itself. Strict checkpatch has zero code/style findings; only raw-mail metadata is absent. CAMSS was not loaded.

**Next:** keep runtime blocked. Close the named IQ-module **input-provider/priming boundary**: determine which outputs are deterministic from sensor mode, geometry and tuning versus which require live statistics/AEC/AWB/TMC/tintless feedback, and establish what Windows primes before the first steady Epoch0 update. Do not freeze captured Windows IQ values, create a caller for `0025`, submit FIFO0, enable VFE1 PIX/CSID1/MIPI, transmit IMX681 or attempt a Linux front frame.

## 2026-08-29 — selector-2 priming replay closed; bounded runtime authorized

The four selector-2 batches bracketing `ISP_START_DONE` are not duplicate host-start submissions. Deterministic replay comparison proves each is the corresponding startup main stream with exactly one changed command dword: `period_cfg +0x8c`. Mapping remains packet0=value0 and packets1/2/3=value1. Observed order is `replay0 -> replay1 -> ISP_START_DONE -> replay2 -> replay3 -> first steady 0x958`. LCAC111 `0x5408` selectors 1/2 and BHistStats16 `0xb208` selectors 1/2 occur only in startup/priming, not steady Epoch0. Extractor SHA-256 `28e305f28db1e7ffa9687306a89fe9033f8eb5ab51677018e90d7248f6718f08`; oracle SHA-256 `4d49864c26d0bf311b92f65d7020a7942421b9a216fc6068bae45bf47c8c1ef2`.

Runtime camera/image testing is authorized from this checkpoint. Use a disposable candidate boot with Golden still saved/default; stage RT-CDM/VFE1 BUS/CSID1/CSIPHY2/IMX681 activation with bounded timeout and mandatory teardown before any wider integration.

## 2026-08-29 — first native front RDI frame proven; PIX parity remains next

A disposable front-only candidate now closes the basic Linux physical-transport gate without confusing it with the Windows production path. The boot uses the normal Golden initrd plus `modprobe.blacklist=qcom_camss,imx681,ov13858`, then manually loads generic media dependencies followed by candidate qcom-camss SHA-256 `09abae83...b6c35` and candidate IMX681 SHA-256 `389c4a8c...7388`. The media graph binds IMX681 immutably to CSIPHY2 and enables only `CSIPHY2 -> CSID1 RDI0 -> VFE1 RDI0 -> /dev/video4`.

The chain negotiates `3840x2640 SRGGB10` and `/dev/video4` as packed `pRAA` RAW10, 4800-byte stride / 12,672,000-byte sizeimage. One bounded STREAMON dequeues sequence 0 at exactly 12,672,000 bytes; raw SHA-256 is `8e892cfeb8f9aea6c9454dbc1fe22b0c26a11e4a108e551a2995069d76e000ac`. Unpacking yields no zero pixels, 295 distinct 10-bit values, and a percentile-mapped preview visibly resolves the room/window scene. The raw/unpacked/preview scene files remain local and untracked.

STREAMOFF immediately logs IMX681 `MODE_SELECT=0` and runtime power-off. Sensor and CAMSS both return `suspended`; mutable media links are disabled; `cam_cc_mclk4`, CSIPHY2, CSID and IFE1 clock enable/prepare counts return zero; camera regulator use counts return zero; no kernel BUG/Oops/panic/SError is present. Filtered evidence is in `e003h-bounded-front-first-frame-runtime/RDI-V3-FIRST-FRAME-PASS.md`, `RDI-V3-V4L2.log`, `RDI-V3-FIRST-FRAME-stats.json`, and `RDI-V3-CAMERA-DMESG.txt`.

**Consequence:** native front C-PHY sensor/receiver/CSID/VFE RDI transport works. This is **not** Windows parity: RT-CDM FIFO0 and VFE1 PIX/QC10C were not used. Do not repeat the RDI proof. The next runtime candidate must compose the closed RT-CDM start/priming, BUS, CSID1 IPP, completion and 0025 module-input contracts with Linux-owned DMA and explicit live-IQ provider inputs, with the same bounded teardown/Golden rollback discipline.


## 2026-08-29 — bounded front RDI transport frame and Golden rollback verified

A disposable front-only candidate captured one 3840x2640 packed RAW10 frame through `IMX681 -> CSIPHY2 -> CSID1 RDI0 -> VFE1 RDI0`. The frame SHA-256 is `8e892cfeb8f9aea6c9454dbc1fe22b0c26a11e4a108e551a2995069d76e000ac`; scene bytes remain local/untracked. STREAMOFF restored `MODE_SELECT=0`; sensor/CAMSS runtime PM suspended, camera clock counts and regulator use counts returned to zero, and no kernel fault was observed. A normal reboot then returned to Golden FullIO v19c with unchanged Golden hashes and no candidate camera module loaded. This is transport proof only, not VFE1 PIX/QC10C parity.

## 2026-08-29 — raw VFE1 Epoch0/VIDEO IRQ mapping closed

Exact KMD IRQ-reader RVA `0x1dc20` reads TOP status0/1 from `+0x44/+0x48` and BUS status0/1 from BUS `+0x28/+0x2c`, preserving them in the DPC message before clear. DPC decoding proves `VIDEO = TOP status1 bit0` and `Epoch0 = BUS status1 bit21`. A focused same-machine IFE1 hit records `TOP0=0x00002010`, `TOP1=0x00000271`, `BUS0=0x00000017`, `BUS1=0x00611ff8`; mask registers are `TOP_MASK0=0x0007f051`, `TOP_MASK1=0`, `BUS_MASK0=0xd0000000`, `BUS_MASK1=0`. The Windows clear sequence is TOP/BUS status0 -> `+0x3c`, status1 -> `+0x40`, then global clear `+0x30=1`. This closes a bounded polling implementation for the disposable PIX candidate without enabling a guessed Linux VFE IRQ mask.

## 2026-08-29 — disposable PIX oracle capsule reproducible

The first Windows-matched PIX runtime input package is now deterministic without committing proprietary payload bytes. `build-pix-oracle-capsule.py` emits a 41,088-byte local `E3HPIX01` capsule with 36 64-byte-aligned sections: four normalized startup mains, sixteen startup DMI payloads, one normalized steady `0x958` main, nine named-module value/mask records, and fourteen steady DMI payloads. Header metadata carries the two startup and two priming `period_cfg` values plus steady requestId/subrequest. A/B builds are byte-identical at SHA-256 `6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20`.

The capsule binary remains `.gitignore`d and local. Git stores only schema, deterministic builder, hash-only manifest and fail-closed validator. The validator enforces magic/version/length, the exact 36-section type census, descriptor/hash identity, non-overlap, zero padding/header reserve and named-module masks. This closes the input-container boundary only; it does not submit RT-CDM or enable VFE1 PIX.

**Next:** implement and inspect an unreachable bounded PIX runner consuming the local capsule into Linux-owned DMA. Compose only the already-proven RT-CDM start/priming, VFE1 BUS, CSID1 IPP and raw Epoch0/VIDEO polling/clear contracts. Do not arm the disposable PIX run until the runner has no unproven MMIO/FIFO/teardown behavior.

## 2026-08-29 — PIX capsule parser/materialization and raw polling compiled unreachable (`0026`–`0028`)

`0026-x1e-vfe1-raw-irq-poll-unreachable.patch` compiles only the two same-machine raw event identities required by the bounded PIX experiment: Epoch0 = BUS status1 bit21 and VIDEO = TOP status1 bit0. The helper snapshots TOP/BUS status0/1 and applies the exact Windows clear registers/global-clear order. Timeout is caller-owned; no IRQ mask or additional event bit is inferred. The private recipe has exactly two retention relocations and no runtime reference.

`0027-x1e-pix-capsule-parser-unreachable.patch` maps the versioned `E3HPIX01` local capsule to two `camss_rtcdm1_corpus_input` objects (startup/priming) and one `camss_x1e_epoch0_input`. It validates section census/bounds/non-overlap, u64 requestId/u32 subrequest, module masks/payload lengths and then calls the already-existing startup and steady fail-closed validators. The parser contains no MMIO, DMA allocation, firmware loader, IRQ or FIFO operation and has no runtime caller.

`0028-x1e-pix-capsule-materialize-unreachable.patch` composes the existing 0019/0021 and 0025 materializers into three Linux-owned DMA products: startup corpus, priming corpus, and first steady Epoch0 command/DMI set. It introduces no hardware access and remains unreferenced. Final module SHA-256 is `522033b849552e4a62d572a09fdbec8b1ad4ece55538d676370f32dece8976f1` with Golden `7.1.5-sp11-render-parity-v4+` vermagic.

**Next:** compile the actual bounded hardware-order runner, still unreachable: RT-CDM preflight/open/start, exact startup/priming FIFO ordering, VFE1 BUS prepare/update, CSID1 IPP placement, raw Epoch0/VIDEO bounded waits, and exact stop/clear sequence. Do not arm it until binary/source inspection proves every MMIO/FIFO callsite is already oracle-backed.

## 2026-08-29 — PIX RT-CDM submit primitives compiled unreachable (`0029`)

`0029-x1e-pix-rtcdm-submit-primitives-unreachable.patch` composes no new RT-CDM register semantics. `open_start` delegates the existing same-machine Windows `open_init` and `start` helpers; startup/priming packet submission delegates FIFO0 commit with `packet_len - 1`; the steady path submits all five materialized BLs with `bl_len - 1`. Stop delegates the Windows DEVICE_STOP action (IRQ0 mask to zero) and then performs Linux software-only IRQ ownership close (`disable_irq` + `irq_armed=false`) with no RT-CDM MMIO, matching the separately proven later session-delete boundary.

The private recipe has exactly four ABS64 retention relocations and no runtime reference. Build is warning-free with Golden vermagic; patch SHA-256 `3ffd45d64e1f25fd8f81f67b22fca930c516eaf22146d6a1548650783f107182`, candidate module SHA-256 `64ab3390f7dd19b72f819acce16cb9de46d499a5be0e98ebd5552fb94bc4c3e2`.

**Next:** close a static cross-file hardware-order/rollback contract around existing VFE1 resource power, VFE1 BUS, CSID1 IPP and CSIPHY2 operations before creating any callable PIX runner.

## 2026-08-29 — PIX cross-file hardware-order/rollback contract compiled unreachable (`0030`)

`0030-x1e-pix-hardware-order-contract-unreachable.patch` records only orchestration ownership and ordering data; it calls no hardware helper. The future PIX callback is required to reuse the normal V4L2 `prepare_streaming`/`unprepare_streaming` power boundary (`v4l2_pipeline_pm_get/put`) rather than duplicate VFE/CSID/CSIPHY power references. VFE1 resource power remains the existing `vfe_get/put` path; CSID1 reuses existing subdev power and the X1E CSID680 IPP `configure_stream` path; CSIPHY2 reuses existing subdev power plus lane stream enable/disable. The generic VFE1 PIX `s_stream` path stays fail-closed because it would still select the invalid RDI-style WM27 mapping.

The retained host prefix remains RT-CDM open/start -> IFE1 resource held -> startup packet0 -> packet1 -> VFE1 BUS prepare -> packet2 -> packet3 -> CSID1 IPP start -> ISP_START_DONE. Steady ownership remains raw Epoch0 poll -> complete BUS IOVA update -> five-BL RT-CDM submit -> raw VIDEO poll/retirement. Stop is CSID1 IPP stop -> VFE1 BUS stop -> RT-CDM mask/close, followed by one already-observed-valid CSIPHY2/sensor serialization; Windows does not require an order between those final two. Rollback is explicit reverse ownership: sensor -> CSIPHY2 -> CSID1 -> BUS -> RT-CDM -> capsule DMA -> pipeline PM.

The contract intentionally does **not** invent the two remaining cross-orders: selector-2 replay0/1 are known only to be before `ISP_START_DONE`, not yet placed exactly versus CSID1 start; replay2/3 are known only to be after `ISP_START_DONE`, not yet placed exactly versus CSIPHY2/sensor start. `callable_runner_authorized=false` until those are mechanically closed. Patch SHA-256 `494256d23ec7cfa4dee4076e4aeffffa765168d6f9dc5e649d2242a27e0cc894`; source `79f488a794036c8d4e706d47334d6dcf0b991e4280cc78314501e848ac661ca8`; object `0ec5f0501cc31662d461b4f28c45784742633546c337110198052d0effd45cca`; module `235b334f1245f0395a6c3ada3a8c6cd152c4e26d8bf7b30870e9a75b1029f16a`; inspector `6ae629cb76a440221bd99db930a317ec53c104f2690272d48f78f8048f44909b`; inspection JSON `e1237d8c470f3d3ab3ecc025230edfa83fdd1cd8343d0ebcb991ac43acfa36db`; build-log SHA-256 `9f038e815505e840c436c71b6fe784dc67713d9abc147b6f04c05b1c0a388539`. Golden vermagic matches and CAMSS remained unloaded.

**Next:** use a focused same-machine Windows cross-order oracle to place replay0/1 against CSID1 start and replay2/3 against MIPI/CSIPHY and sensor-on. Do not arm Linux PIX while either relation is unknown.

## 2026-08-29 — priming/CSID/MIPI cross-order closes both `0030` placement booleans

A focused KD oracle reuses only already SHA-pinned event sites and the selector-2 main-length identities. Raw log `E003H_PRIMING_MIPI_CROSSORDER_20260829.log` is 7,420 bytes SHA-256 `06127e46dca5759cfded698b1a1a8dc0dcd40dd04ca271d515a54fbed42987ee`; extractor SHA-256 `ff4397b20f1019f52f7ff6d716236e055441d8b60bd2ee191151f196289b140b`; derived oracle SHA-256 `849687aaa5206c25484b9a6e015aba320d7d01610d5292a33df54605f20ae599`. Two independent WinRT starts reproduce exactly: `replay0(0xe94) -> replay1(0xe34) -> CSID1 start -> ISP_START_DONE -> MIPI start enter -> MIPI start done -> sensor stream-on apply -> replay2(0x904) -> replay3(0x4e8) -> first steady 0x958`.

Therefore `0030`'s `replay01_vs_csid_start_closed` and `replay23_vs_mipi_sensor_start_closed` unknowns are now mechanically closed. Linux still must not invent the remaining pre-CSID interleave: existing `0022` separately proves `packet0 -> packet1 -> BUS prepare -> packet2 -> packet3 -> CSID1 start`, while this oracle proves `replay0 -> replay1 -> CSID1 start`; their mutual order before CSID1 has not yet been captured.

## 2026-08-29 — startup/priming/BUS interleave closed; `0031` refines PIX order

A narrow same-machine Windows boot-start capture combines IFE packet processing, selector-2 replay consumption, VFE1 BUS static/enable/address events and CSID1 start. The canonical first window in `E003H_STARTUP_PRIMING_INTERLEAVE_20260829.log` is 9,624 bytes SHA-256 `cae67c10421246f86a469d95c73cdfa3684c1004827847fe922ab59c2d9273ed`. Its exact order is `startup0 -> replay0 -> startup1 -> BUS static config -> BUS enable -> initial nine-client addresses -> replay1 -> startup2 -> startup3 -> CSID1 start -> ISP_START_DONE`. The later `CYCLE2_ARMED` continuation is intentionally ignored by the fail-closed parser because it is not a clean first-start window.

The deterministic extractor SHA-256 is `d75dd99d654036708d47d662c257374e686a718e57a2d0e097a9d8f97dac654b`; derived oracle SHA-256 `849b6cc2d9e49c3cf912e1b1c6041b68cc1a76c8ba05496e278dc763f1a24032`. Combined with the independently repeated priming/MIPI oracle, the complete start placement is now: `startup0 -> priming0 -> startup1 -> BUS -> priming1 -> startup2 -> startup3 -> CSID1 -> ISP_START_DONE -> CSIPHY2/MIPI -> sensor-on -> priming2 -> priming3 -> first steady 0x958`.

Static `0031-x1e-pix-startup-priming-interleave-unreachable.patch` updates only the retained `0030` order contract. Host stage count is now 16 with all four priming replay markers explicitly placed. `replay01_vs_csid_start_closed`, `replay23_vs_mipi_sensor_start_closed` and `startup_priming_interleave_closed` are true, while `callable_runner_authorized` remains false. Forward/reverse reconstruction passes, Golden vermagic matches, and no runtime relocation references the retained contract. Patch SHA-256 `e19cdd47ce6d0fd307d8c022b65ce80fe31bfe83b7907b6a43b1a4ca1bf8066d`; source `1902c56b0258c789c17260163ad0e46d9cf52df7cdbdbfbd677e53a8cafb5e68`; object `809593d8aa1a8ff13527c72c056649b86fdf052d35fc71a09a9ad5a6a95c4f0d`; module `cb6f4de7398743dfaac076c8bbdd25a42d5571e7b3f4940e24cbe96bb1881225`; inspector `fc3c83e0a0abf8ecc7f11f668d6bc227fb726a7eff1690221968cc4e5e48434a`; inspection JSON `ed6cc17f5ba69397e1cb2ba45a4ab0a05f610414622916276798c2f726d81b5f`.

**Next:** build and inspect a callable-but-unarmed PIX runner that consumes the already parsed/materialized capsule and composes only the now-closed 16-stage start order, bounded Epoch0/VIDEO waits, stop prefix and rollback. Do not connect that runner to V4L2/probe/stream paths or arm hardware yet.

**Next:** one narrow Windows start capture combining only packet0..3, BUS-prepare boundary, replay0/1 and CSID1 start. Once that relation is closed, refine the retained hardware-order contract and inspect a callable-but-unarmed runner before any Linux PIX activation.

## 2026-08-29 — replay/Epoch0 pacing closes bounded first-PIX frame prefix

A focused same-machine Windows trace fixes the pacing that a first callable-runner draft had guessed incorrectly. After IMX681 stream-on, the **first Epoch0** executes a complete nine-client BUS-address update, then selector-2 consumes replay2 (`0x904` bytes, requestId 2, subRequest 0); the first VIDEO completion follows. The **next Epoch0** executes the next complete nine-client BUS-address update before replay3 (`0x4e8`, requestId 3). Raw log `E003H_REPLAY_EPOCH0_PACING_20260829.log` is 2,008 bytes, SHA-256 `db0d038625843d77428633fcd229a0818a8dc9aafa0af06bc63c06cc6b949b35`; extractor SHA-256 `b65103e41e944f7777ed8160d11af1e2c2d693dc17cf10171c61c21b8f0be29a`; oracle SHA-256 `73899c498339c10c3d919fa563c76e3d30dc9917dd09b0e179fdbb380303c0c8`.

**Consequence:** do not submit replay2/replay3 back-to-back after sensor-on. A deliberately bounded first-QC10C proof can stop after `Epoch0 #0 -> BUS retarget slot1 -> replay2/request2 -> VIDEO(slot0)` and then execute the already-closed stop/rollback path. Replay3 belongs to the next Epoch0 and is not required before returning the first VIDEO buffer. Later Epoch0 hits in this intrusive debugger window are not interpreted for steady-state cadence.

## 2026-08-29 — complete priming batches and first-frame runner compiled unreachable (`0032`/`0033`)

`0032` corrects the selector-2 transport representation before any runtime runner is allowed. Windows replay0..3 are complete RT-CDM batches with `4/5/5/5` BLs. Linux synthesizes the small companion BLs byte-identically in a Linux coherent arena and reuses the already-materialized Linux-patched main BL as BL1. Every BL uses the already-proven `byte_count - 1` FIFO length rule. Companion verification is exact against the canonical selector-2 capture; no Windows IOVA/ring geometry is imported.

`0033` then compiles a single-frame runner behind an unreferenced retained recipe. Its accepted first-frame prefix is exactly `startup0 -> prime0 -> startup1 -> BUS(slot0) -> prime1 -> startup2 -> startup3 -> CSID1 -> CSIPHY2 -> sensor-on -> Epoch0#0 -> BUS(slot1) -> prime2/request2 -> VIDEO(slot0) -> stop`. It explicitly contains no prime3 submission and no steady five-BL submission before first VIDEO. The generic VFE1 PIX `s_stream` gate remains untouched and is never called.

The VFE680 bridge stays internal to `qcom-camss`: two caller QC10C surfaces acquire private aux ownership, BUS preparation starts from slot0, raw Epoch0/VIDEO polling reuses `0026`, and VIDEO retirement returns only the caller slot0 surface. Normal stop is `CSID1 -> BUS -> RT-CDM -> CSIPHY2 -> sensor`; failure rollback is the proven reverse ownership. Any stop failure pins DMA/pipeline power until reboot. Patch SHA-256 `431cd2b5f8736dac25abf4f2a9f675002406874968a879cf7d2c7193342883c4`; inspector `dbd70a81f1057f5992e3b9afecbb930ce29e1f5e603c27915b31b6eab2449983`; inspection JSON `86aa949f8dd41fc9a55e16a34a72ffbb00f75cc2eae10d4b65c2ee5f385df2d3`; source `camss.c` `2a94daa17493af214335e541853ff733251410f0b0d6fe3e8ba9ab6aed90a237` / VFE680 `96781d29a02e0a153be8d4e5500bf69b5fafa5b6abd435c9f3b52f72c2b8c435` / header `3b65be0e3527bc3e8baaacc8cdb977f6bccb86d31390fb874cd48e2e0de8fcd6`; object `bd696a7657bee48a12cec7489d77e6b6fdfffe86c633fae5bd53cc19102daf16` / VFE object `1358d2a157c98007986856890f2239a38adb533c27ba5c7fde49a27fdf3f8dc7`; linked object `06896ad2a4b54d2af757638ae84c60c24ab1c96039a02e81be95b9fdba32c9d7`; module `4f57a18339b7c11c423df767fa70c65a71a8ec84b6fa545a85097c40de9d8e59`; build log `1bc1fbb5e8a3feb94b69b00dab3cf4c755074a458e9cd478ca4cd6752ba2ea52`. Golden vermagic matches, zero compiler diagnostics, and strict checkpatch has zero code/style findings. The runner recipe has one retention relocation and zero runtime references.

**Next:** do not arm `0033` yet. Build and inspect a one-shot disposable caller/preflight that supplies the local capsule and exactly two validated QC10C buffers, confirms the front-only candidate/links and Golden rollback state, and exposes no repeated/probe/vb2 auto-start path. Runtime authorization belongs to a later checkpoint.

## 2026-08-29 — one-shot PIX caller/preflight gate compiled unarmed (`0034`)

`0034-x1e-pix-one-shot-runtime-gate-unarmed.patch` wraps the retained `0033` runner in a second retained-only gate. The gate consumes an irreversible atomic one-shot latch **before validation**, so a failed attempt cannot be retried without module reload/reboot. It requires the exact 41,088-byte local oracle capsule digest `6aed028d1caaf0366b004038aee3e954ca95a95c117e2619555bdd9605746a20`, VFE1 resource `0x0ac71000/0xf000`, RT-CDM1 `0x0ac26000/0x1000`, a front-only graph with no CSIPHY1 rear-sensor link, and the exact front route already revalidated by `0033`.

The caller must supply two distinct VFE1 PIX vb2 buffers that are still `DEQUEUED`; the queue must not be streaming or driver-owned. Active format is required to be exactly QC10C `2560x1440`, stride 3584, one plane, `sizeimage=0x76b000`. Each DMA base must be nonzero, page-aligned, wholly below 4 GiB and non-overlapping. `0034` neither allocates nor queues those buffers and contains no normal vb2 STREAMON path. The pinned digest is compared against a caller-reported digest; the kernel does not hash the capsule itself, so actual file/module/DT hashing remains a mandatory host-side preflight responsibility.

Patch SHA-256 `6c015395dbb199d94bdd23e01d0a9266f8e71b377c4b5943d36675ae77119b14`; inspector `fd5c5c283bfa9e3bf34ff7995755a6ce7fa1af790373471f07c581e8adfcee38`; inspection JSON `50ed709b0963dab0d1aa6c81414e7bda689ff6598c38a0bf017030800ffe2076`; `camss.c` `df79291cde9784233204970155dcf3d30c1e5ef46d90b175e8bbf50afe0d4536`; object `b26b2a245b0e941c137ec6b029e9ee9e48819d12775c58b29f39084a4309b8c4`; linked object `b3f3e8bba4452d86d9b128e7372b4f12ef5aacf3a9c4c8acf214ecd420435e5d`; module `d3d636c8b587ddfc3891150824acbad8b0f310b1c0edfde709b9e62d94c8ea4b`; build log `b60f8dccadc64ca83283b878633d1d88eb1f2c95956691b750bc214f335c2565`. Forward/reverse reconstruction returns exact `0033`; one gate-recipe ABS64 retention relocation exists and the recipe has zero runtime references. Compiler diagnostics are zero, Golden vermagic matches, and strict checkpatch reports zero code/style findings.

**Next:** prepare but do not arm the disposable trigger/package that verifies capsule/module/DT hashes and Golden rollback externally, then supplies two preallocated QC10C buffers to `0034` without invoking normal vb2 STREAMON. Inspect that trigger before any hardware authorization.

## 2026-08-29 — disposable one-shot PIX trigger/package complete, not armed (`0035`)

`0035` adds the only prospective external entry point, still disabled by default. `e003h_pix_runtime_arm` is a load-time read-only bool whose zero-initialized default creates no trigger. When explicitly set to 1 on X1E80100, probe creates owner-write-only `e003h_pix_run_once`; the only accepted payload is `RUN`. The handler loads fixed firmware `sp11/e003h/E003H_PIX_ORACLE_CAPSULE.bin`, locks the PIX video/vb2 queue, requires exactly two allocated buffers 0/1, validates their mapped SG ranges are contiguous, moves cache ownership to the DMA device, calls `0034`, then returns cache ownership to CPU only after safe teardown. It never QBUFs and never enters normal vb2 STREAMON.

The userspace helper source SHA-256 is `98c97a468e3ab120b99e329f88e6b55dd8742a8f063e0f43c99c4d8600cff140` and compiled local binary `d13ab2d324516c28507ee41aa468b2b98bdfc5402a93c00cc3cea2172036ac09`. It sets exact QC10C 2560x1440/3584/0x76b000, REQBUFS exactly two MMAP buffers, QUERYBUF+mmap only, writes `RUN`, then saves the first 0x76b000 bytes. Source contains no VIDIOC_QBUF or VIDIOC_STREAMON call. The front-only DT builder is `e071b29e50dc1641ef9aa793f00d39abf59e2700c0991a7d67c44c383febdecc` and yields DTB `083fd7d3a207cb329938c561aee84c8642cb02e52034b753b36aaff599a381ed` from the already-proven RDI front-only DT; only VFE spans are widened to 0xf000 and RT-CDM1/GIC_SPI287 is appended. Graph validation has no graph warning.

The installed `sp11-camera-e003h-pix-one-shot` entry reuses Golden kernel `bca0a336c15d2995c61b8df9d449afb9df5fc8776a3da1ad034616f917bb428a` and initrd `ac3ba64bd1c6bd6b8c0dc01b9836fb7466128fcc687903673b6fd598ebefb66d`, blacklists camera modules for manual loading and points firmware_class.path at the local experiment tree. It does not call grub-reboot. Package inspection `7f08beebd6df54bd22bc6a1afacc8abea19c02fea309fbc606d52e6e7c181033` confirms the boot entry is installed but not armed, Golden is saved/default, next_entry empty, camera modules unloaded, DT front-only, and every capsule/module/DT/helper hash exact. `0035` patch SHA-256 `7c7f33340fcd698e422729ee6cb4ad5c7611b97cc4227a6d69e40d199dd2ca38`, module `5a09b33c73feb7060c9e0f504cf893fc2e120f6225c4f8b222765c57fc135c79`, trigger inspector `c4339c9f7f766425c2978c24162b98eae13b1b2fa466c9b6bc2e92e03575b353` / JSON `a18a8f48c98871cd99b91e16e1d1c014dfc7a5abe475e79b2b56f3b6d85d5b7d`. Strict checkpatch has zero code/style findings.

**Next:** a separate explicit runtime-arm checkpoint may schedule exactly one candidate boot/one `RUN`. Abort on any package, media-link, buffer or rollback mismatch; after RUN or any failure, reboot to Golden before further work.

## 2026-08-29 — one first-PIX attempt explicitly authorized

The post-checkpoint arm review reran both package inspection and host preflight with the final `0035` module and installed boot artifacts. All pinned hashes match; candidate camera modules are unloaded; Golden remains saved/default with empty `next_entry`; and the write-only PIX trigger is absent on Golden. Authorization is therefore limited to **one** `sp11-camera-e003h-pix-one-shot` boot and **one** `RUN`. The irreversible latch prohibits same-boot retry. Any mismatch before `RUN` aborts, while any result after `RUN` is archived and followed immediately by reboot to Golden.


## 2026-08-29 — complete selector-2 priming BL batches compiled retained-only (`0032`)

The rejected first runner draft exposed another implementation error: selector-2 priming replays are **whole RT-CDM BL batches**, not one replayed main BL. The canonical selector-2 capture has packet BL counts `4,5,5,5`. Packet0 is `{CHANGE_BASE 0xf000, main 0xe94, CHANGE_BASE 0x57000, 0x3c companion}`. Packets1..3 use the same two CHANGE_BASE BLs, their main `0xe34/0x904/0x4e8`, the common 0x10 companion and a 0x14 register+GEN_IRQ BL with userdata `1/2/3`.

`0032-x1e-pix-priming-full-batch-unreachable.patch` adds a Linux-owned 4 KiB companion arena. BL1 points at the existing priming corpus materialization, preserving Linux-repatched DMI IOVAs; the small companion lists are synthesized locally. `verify-pix-priming-full-batch.py` parses the clean Windows capture and proves every generated companion byte string exact for all four packets, while each main hash matches the accepted priming replay oracle. Submission iterates the per-packet 4/5 BL count and passes `len - 1` to the existing Windows FIFO0 primitive for every BL.

Patch SHA-256 `fc8752b0b0f8e681340d0577dea23d029cee550c73f13204e660e07a4d694b35`; verifier `064f63f974c4b5834f6f95a55b3371253fef0236400dbd503e6ca1468667e477`; proof JSON `fde1a5891b3d5aed069d5676bf19e09af0dcf0a9bf953223083d694c94440b41`; inspector `4245eea85666cb1c6742ab660d78f85a61b8e342cf41253aede70a9d483f36d4`; inspection JSON `8d154bce52dbc065e9ba16b01f2816744302dc72842d4b3cd27541d8f43f472b`. Candidate source `1111d3e88b88729a8851a60f31ef1bbc877dc127ccb9d4cb998311f5ba7834f5`; object `10ffb2f154459f2cb4d1c35bdbaf80e5ea32e563ed68b693e45bb908fd33caaa`; module `a5572a5211807ba5338af27e4a558d5f194021f710930fa9a2c040bf5457522d` with Golden vermagic. Reverse/forward reconstruction is exact; strict checkpatch has zero code/style checks, only raw-patch metadata warnings. The retained RT-CDM recipe has five ABS64 function relocations and no runtime reference; no callable runner symbol exists.

**Next:** rebuild the first-frame callable-but-unarmed runner using the corrected complete priming batches and the pacing prefix `sensor-on -> Epoch0 #0 -> BUS slot1 -> replay2/request2 -> VIDEO slot0 -> stop`. Do not pre-submit replay3 and do not connect the runner to a runtime path yet.

## 2026-08-29 — first VFE1 PIX one-shot reached hardware but timed out before sensor-on

The sole authorized `0035` runtime attempt passed package/media preflight and invoked `RUN` exactly once. The write returned `ETIMEDOUT` after approximately 0.76 s; no QC10C file was created. The candidate kernel log has no IMX681 `MODE_SELECT=1`/transmission-start message, so execution failed before sensor transmission. The existing trigger does not expose the internal RT-CDM stage at timeout, therefore this evidence cannot distinguish reset-done from first FIFO0 BL-done and no stronger claim is accepted.

The one-shot latch was respected and no same-boot retry occurred. IMX681 and CAMSS were runtime-suspended after failure, no kernel fault/panic was observed, and the machine immediately returned to byte-exact FullIO v19c Golden with saved/default Golden and empty `next_entry`. Runtime summary SHA-256 `ea63866026effce95e56779a4321df64b8e1d45384bf6ff74ecb64af481614cf`.

**Next:** keep PIX runtime blocked. Add static stage telemetry around RT-CDM preflight/open-reset, core start and each FIFO0 commit/wait so a separately authorized future diagnostic can identify the exact timeout boundary without repeating the full experiment blindly.

## 2026-08-29 — RT-CDM stage telemetry compiled after first PIX timeout (`0036`)

`0036-x1e-rtcdm-stage-diagnostics.patch` is diagnostic-only. It does not add a new trigger and adds no RT-CDM MMIO write. The existing open/reset, core-start and FIFO0 paths now record a stage code; FIFO commits carry a monotonically increasing sequence plus DMA base/length. On an error only, Linux performs read-only snapshots of RT-CDM IRQ context, IRQ0 status and userdata and logs them together with the last ISR context/status/userdata. Higher-level submission wrappers identify startup packet index, priming packet+BL index, or steady BL index. This is sufficient to distinguish the previous ambiguous reset-done versus FIFO BL-done timeout in a future separately authorized diagnostic.

Patch SHA-256 `c7bf338b99c75bcd0589c14f15deabd23b161ce760b28b9f88fca02151d15a5d`; inspector `9afd596a079f5713d07db70431249e20ece5ff0a1742bccc9029310a589acff3` / JSON `590e50fc74ed94f3f45c2f0d9813bc4593f23dc58835773b287b44d9589b2750`; build log `b60f8dccadc64ca83283b878633d1d88eb1f2c95956691b750bc214f335c2565`; checkpatch `00fb143e51c15a224439325fb1e768d91536fc876fba41763d65f2794b3f4f01`; source `792ffcd7eee4779342ecaa7490c4d718fd8cd50b810b3065abba8145b96b5c56`; header `3c0380205253e10d07c087e55dd3745ebc1961ca447f6c6ebb3b6adad4dbcde2`; object `d694e93ffc57ba744cb47e65f9ff4e2efc1fff37e0dde7878e86a24415f7cf0e`; Golden-vermagic module `49f9a374f7282d40b7552f61c7a3b4d8d87b9aa3ec31d3a3d3958c6e2b2795f9`. Forward/reverse reconstruction passes, compiler diagnostics are zero, patch inspection proves zero newly added `writel`, and CAMSS remained unloaded.

**Next:** runtime stays blocked. First re-audit the RT-CDM interrupt trigger/context/reset assumptions from the already captured Windows oracle and Linux resource setup; only then decide whether a new one-shot diagnostic is justified.

## 2026-08-30 — exact Windows RT-CDM IRQ handler closes Linux context-gate mismatch (`0037`)

Static disassembly of the exact installed KMD now closes the interrupt-consumption ambiguity. Fail-closed extractor `5a258eaf97a768262ea6a843948e48d707ade70eb5dca69fe95e20cdf3f8b43b` pins `qccamisp8380.sys` RVA `0x29120..0x2930c`: the handler reads FIFO0..3 status at `+0x44/+0x144/+0x244/+0x344`, masks every value by `0x00070007`, and has no `IRQ_CONTEXT_STATUS +0x2c` read. It writes the masked values to the corresponding CLEAR registers and then `1` to each CLEAR_CMD. Oracle SHA-256 `99ffd25d52f154915d6462c7b6d9fa35f86cf75026855d5afce983f77d41cf05`; narrative `e87e48d7b47a775a40170229911e276afe2e0b96af94cab9eddeb92fc66baf55`.

The first Linux PIX runtime had two mismatches in this exact path: an invented `IRQ_CONTEXT_STATUS bit0` prerequisite before FIFO0 status, and raw-status CLEAR. `0037-x1e-rtcdm-irq-handler-windows-parity.patch` removes the context prerequisite and writes only `status & CAMSS_RTCDM_IRQ_KNOWN` to CLEAR. Unknown or known-error raw bits continue to fault/disable the Linux IRQ after recognized status acknowledgement. The correction changes no start/stop/FIFO submission sequencing and adds no new runtime entry point.

Patch `5406e8d7683ba1b9d27ff0fc70e65ff7ca7c7c024c2930d17de2494fb9adf021`; inspector `cb3fd45b095426fc1a3cde67569dd9bb69680e7de2b6b2ca0116deb92e7638b2` / JSON `c37fb0a4bd7403f1d4e48ddb1e153627009248fc91c5def6ede9614f2ee8e835`; source `ed7d5887a9bfe41d7b677005884493e3e2fb7b1493ba96b9ff43f3f7ac9119d5`; object `3f1b4bd39e718423f4ad72828776c781301b4d054d1261ad0155dce8cec79474`; module `96e48ff176a048c391841d2c56bafdce76cfbe8a78b7310173caf175af49c9e9`; build log `b60f8dccadc64ca83283b878633d1d88eb1f2c95956691b750bc214f335c2565`; checkpatch `72af08b64e3dfb97cd72531499a0f417037e48ae61554326e56e62faaaef4d97`. Golden vermagic matches, compiler diagnostics are zero, strict checkpatch has zero code/style findings beyond raw mail metadata, and forward/reverse reconstruction passes. The removed context gate is a plausible explanation for the prior reset/BL wait timeout but causality remains unproven until a newly authorized instrumented diagnostic.

**Next:** package `0036+0037` into the existing front-only one-shot environment and inspect it while unarmed.

## 2026-08-30 — disposable PIX diagnostic package refreshed with `0036+0037`, unarmed

The existing front-only one-shot package was repinned to CAMSS module `96e48ff176a048c391841d2c56bafdce76cfbe8a78b7310173caf175af49c9e9`. No DT, sensor, capsule or helper behavior changed. Package inspection v2 SHA-256 `991534b4dd4db9bf7201864f54f07cf8d4faabe24582f8b5d5a4ce3b361a5eb8` proves stage telemetry is present, the IRQ context gate is absent, the boot entry remains installed but unarmed, and normal QBUF/STREAMON remain unused. Golden-host preflight `1a0b26722dc74118a2d68b0fad69a0401105a6ab17194d730738be367af2c74c` passes with saved/default Golden and empty `next_entry`. Runtime remains unauthorized pending a fresh one-shot authorization checkpoint.

## 2026-08-30 — one instrumented second PIX diagnostic authorized

Fresh package/Golden review passed after the exact Windows IRQ correction: candidate CAMSS `96e48ff176a048c391841d2c56bafdce76cfbe8a78b7310173caf175af49c9e9`, front-only DT/capsule/helper hashes exact, branch/origin synchronized, saved/default Golden with empty `next_entry`, candidate camera modules unloaded and trigger absent. Review JSON SHA-256 `991534b4dd4db9bf7201864f54f07cf8d4faabe24582f8b5d5a4ce3b361a5eb8`.

Exactly one candidate boot and one `RUN` are authorized. The diagnostic must not retry in the same boot. `0036` stage telemetry must be archived whether the run fails or succeeds, and the machine must immediately return to Golden afterwards.

## 2026-08-30 — second PIX diagnostic ended in unclean reset; Golden recovered

The non-root helper probe could not open the root-write-only trigger and never issued `RUN`. The subsequent root invocation is treated as the one authorized trigger and was not repeated. The candidate reset before any result or `0036` error line became persistent. The prior boot has no systemd shutdown/reboot sequence; the next Golden boot reports EXT4 orphan cleanup, proving an unclean reset. No QC10C output exists, `RUNTIME-PIX-DIAG2-RUN.txt` is zero bytes, and `/sys/fs/pstore` contains no crash record.

Golden return is verified with `saved_entry=sp11-audio-fullio-v19c`, empty `next_entry`, byte-exact protected kernel/initrd and no candidate camera modules. The run does not prove whether reset/open, core-start or a FIFO submission was the last stage. No third PIX attempt is authorized. Persistent evidence hashes: previous-boot `01578d825d07401fc4c879608028a2b6d2c2215124b24c0d65b93c76da4aed3c`; Golden-return `06d033c19dfe1e1482e0f8388eef5d8d51ff91346a1f60b9a13d88fc16f9312b`; result record `fdc2c2166dc9dcf7497864cce034e74fc6fd121d40041b1be2aaf376fd56fbe9`.

**Next:** add only a non-MMIO persistent observer for the existing `0036` diagnostic state so an abrupt reset cannot erase the last stage. Do not alter RT-CDM programming or authorize another runtime in that checkpoint.

## 2026-08-30 — persistent RT-CDM stage observer compiled static (`0039`)

`0039-x1e-rtcdm-persistent-stage-observer-static.patch` adds no MMIO write and does not change the one-shot `RUN` path. Under the same false-by-default runtime-arm parameter, it creates read-only sysfs `e003h_pix_rtcdm_diag`. The existing diagnostic state gains a published transition generation and sysfs notification. New stage names `reset-command` and `core-starting` are set before those hardware-write sequences; `fifo-wait` was already set before FIFO BASE/LEN/STORE. The sysfs reader uses only `READ_ONCE`/acquire state and performs no MMIO.

`watch-rtcdm-stage.py` (`8698afdc615ee1d544d0068441241625487cc8459ca97a758b62d3b863743d84`) records the initial state, waits on POLLPRI with a 1 ms fallback poll, and `fdatasync()`s every changed snapshot. It contains no trigger, ioctl or `/dev/mem` operation. Forward/reverse reconstruction passes for both `camss.c` and `camss.h`; strict checkpatch has zero code/style checks beyond raw patch metadata. Patch `b4349284fabdba7be35a0973894e51e1d872ae8838724f9f68fc863df32aef8a`; source `7ccbd4008e44af0dd35d5443c4aa43e12b43b96b62d3ea6c469bd4ccd943063c`; header `062125bad5d1fe16429563996f5728abc14873d6a4c58389dca932b26d1836cc`; object `19b013c2042bc3d7a409468199e2590197af164a8430dd354c9e6b543a2efc73`; module `cabc1851006f86e83f4086226342c11702aed6b8734d2f5144e9f51fb8042ed3`; inspector `06e5f423ab40f90c54f10c4531ab19277dbede63a2b0666256cacf1377ba3432`; inspection JSON `2deb71213db9f07d4a5b875a4cfb99a40dda44db7cff8ed4ac2966925a77a48b`. Golden remains active with empty `next_entry` and no candidate camera module loaded.

**Next:** runtime remains blocked. Audit exact Windows handling of FIFO1/2/3 status during RT-CDM interrupts and prove the Linux coherent command-buffer mapping covers the RT-CDM1 SMMU requester before any third one-shot authorization.

## 2026-08-30 — exact four-FIFO RT-CDM interrupt acknowledgement closed (`0040`)

A new fail-closed extractor against the exact `qccamisp8380.sys` proves the handler at RVA `0x29120..0x2930c` reads FIFO0/1/2/3 status from `+0x44/+0x144/+0x244/+0x344`, masks every bank by `0x00070007`, and gates the clear/callback block on **masked FIFO0 status** (`w21`, `CBNZ` at `0x29208`). It then writes masked status0..3 to `+0x34/+0x134/+0x234/+0x334` and writes `1` to all four CLEAR_CMD registers `+0x38/+0x138/+0x238/+0x338`. The asynchronous callback payload is constructed from masked FIFO0 status plus the CDM context. There remains no `IRQ_CONTEXT_STATUS` read. Extractor SHA-256 `99c9a0f1451daf9753b39a5b255e9ac274a21b3ec55ac9c0a17b6ecfcc0b59f7`; oracle `4664eb9ea3f5552303351d7d49d4148218ba431fb7c42f48b6e98af226ba6b40`.

`0040-x1e-rtcdm-multififo-irq-windows-parity.patch` updates the Linux ISR to the same four-bank status/ack shape. FIFO0 remains the only dispatch/completion source; FIFO1–3 are recorded and acknowledged but no front-path semantics are invented for them. The observer now includes all four last-status values. Patch `a3a728b67523dfa39cb99f313ed97c715ba272202ba74f1836b0ccde6e6d3aed`; source `fbdb8786067a4e6df78893974e8dd17f8bd043c7bae8391cfb3fa1ff1fd71384`; header `4e69f21ea8a04022722912f24133edcd38cad3348ff06bf4b07ac19a422c1176`; object `4c082b79f9964e5157f8fd5393442bde4bc056a4f153ba7884cfe1774c020eae`; module `7d8c8953f8c14e34d36e3d2352b3ea2581d66a5af777f061f6cd0951fcee1680`; inspector `8e59097540ba81c97be2b4b5f8ba63b5e909d517bcc095f2e7c057461dee0d76`; inspection JSON `937f842fd02e86a4189afe9696aa5bb3eae17abbd1402ca05d9c24fb97236fbd`. Golden vermagic and zero compiler diagnostics; forward/reverse reconstruction passes and strict checkpatch has zero code/style findings beyond raw mail metadata. CAMSS remained unloaded.

**Next:** do not run PIX. Prove the RT-CDM1 command-fetch requester/SMMU stream identity and whether the CAMSS device DMA domain maps Linux coherent command buffers for that requester.

## 2026-08-30 — X1E CAMSS five-entry IOMMU Linux implementation built static (`0041`)

The provenance audit found the integrated `hamoa.dtsi` still used an obsolete eight-entry CAMSS IOMMU list that omitted `0x18a0`. Static `0041-x1e-camss-iommu-five-entry-linux-implementation.patch` replaces only that list with `0x800/0x60`, `0x820/0x60`, `0x840/0x60`, `0x860/0x60`, `0x18a0/0`. This is a Linux implementation decision, not a Windows literal: `parity_claim=false`. Same-machine Windows qcsmmu independently proves `0x18a0/0` belongs to VFE client CB16 `S1_IFE_HLOS`; the public X1E CAMSS v13 binding independently labels it `CDM IFE`.

The Denali DTB rebuild is reproducible. Old DTB SHA-256 `bbe48a77c5bc23f1c155ddc87b9a5b2ed56497656f06cab1a2db8e6346f0304b` (215,217 bytes) becomes `333e3c81c8a490f1b8b444e9a8d8005539799c438f2d03ebc6acfc366074b14e` (215,181 bytes). Decompiled structural diff SHA-256 `8f6f893b30e94f44e146440f496b40e37f0e14893120d81cad24daa8abe17f06` contains exactly one removed/added property: the CAMSS `iommus` list. Patch SHA-256 `41b7187b9b2cf35f471ba2627f689e80ff35e9019c84865d792dfa9dbad9bef0`; build log `cec90f34a16586be016f0ecf015d5c71613348d1af9c58e4a5002f761f895024`.

`inspect-camss-iommu-five-entry.py` proves the Linux DMA semantics separately: `dma_alloc_coherent -> dma_alloc_attrs`, `use_dma_iommu(dev) -> iommu_dma_alloc`, each DT SID/mask enters the CAMSS device `iommu_fwspec`, and arm-smmu installs every fwspec entry as `S2CR_TYPE_TRANS` to the same `smmu_domain->cfg.cbndx`. Inspector SHA-256 `671cdcee8cbe7e21ec9923c4c555f50f139b6d7b32abd5f24e489b71d0a61827`; JSON `bbff1a0b2d2127c1fc389db257c57a75ac39320135f42024a77e6bd44e2dc935`. This proves the corrected Linux CAMSS device domain will map coherent allocations for its five declared streams. It does **not** prove which stream RT-CDM1 itself emits.

**Next:** keep PIX runtime blocked. Close the exact same-machine RT-CDM1 command-fetch requester → SID relation. Only after that fact is Windows-established may the provenance gate reconsider bounded PIX runtime.

## 2026-08-30 — RT-CDM1 requester SID closed; bounded provenance blocker removed

A fail-closed same-machine extractor combines four independent Windows facts rather than relying on public X1E naming: installed `qciommuext8380.inf` (SHA-256 `18e06ef557a9b0ef7d22fa3c8f97909699e915946aeec0a758f3e32cb9676a6c`) defines VFE HLOS aggregate `0x01030000` with count 5 as `S1_IFE_HLOS — Camera CDM IFE, IFE/SFE RD/WR non-protected stream`; live IORT (`c561d68b2c3e731c927481ca37bc97302a2f3dcd24747ebf530b8be19795445b`) maps its five IDs to `0x18a0, 0x800, 0x860, 0x840, 0x820`; installed qcsmmu independently groups the four 0x800-family IDs with mask 0x60 and leaves 0x18a0 singleton in CB16; and the accepted qccamisp hardware-CDM oracle proves front IFE commands execute on RT-CDM1. Thus **RT-CDM1 IFE command fetch -> SID 0x18a0 -> CB16/S1_IFE_HLOS**.

Static Linux `0041` remains an independent `LINUX_IMPLEMENTATION`: it includes `0x18a0` in the CAMSS fwspec and the Linux DMA/SMMU implementation inspection proves coherent CAMSS allocations use the same device translation domain. This closes `rtcdm.command_dma_domain_visibility` for the bounded provenance target without calling a public Linux label Windows evidence. Runtime remains unauthorized pending a separate reviewed one-shot checkpoint.


## 2026-08-30 — post-provenance one-shot package refreshed, unarmed

The disposable package is repinned after requester-SID closure and Linux `0041`. Candidate CAMSS is `7d8c8953f8c14e34d36e3d2352b3ea2581d66a5af777f061f6cd0951fcee1680`, containing persistent stage observation and exact four-FIFO Windows acknowledgement. The rebuilt front-only DTB is `019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f` and contains exactly the five-entry CAMSS IOMMU set `0x800/0x60,0x820/0x60,0x840/0x60,0x860/0x60,0x18a0/0`, VFE spans `0xf000`, RT-CDM1 `0x0ac26000/0x1000`, and only front port@2.

`preflight-pix-one-shot.sh` now requires a green bounded provenance gate and validates the exact IOMMU set. Package inspection v3 `d28f04d96f0e405fbf8710f3e0e0a872c845b781af05b60a6ed98ecc10c5cce4` passes with Golden saved/default, empty `next_entry`, candidate modules unloaded and the candidate boot installed but unarmed. No runtime authorization follows from this refresh.


## 2026-08-30 — one post-provenance third PIX diagnostic authorized

Fresh Golden/package review passes with bounded provenance green, CAMSS `7d8c8953f8c14e34d36e3d2352b3ea2581d66a5af777f061f6cd0951fcee1680`, front-only corrected-IOMMU DT `019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f`, persistent stage observer required and candidate boot installed but unarmed. The two earlier failure modes now have concrete mitigations: exact Windows IRQ acknowledgement replaces the first context-gate mismatch, and the stale Linux CAMSS IOMMU list is corrected with the same-machine requester SID 0x18a0 now proven. Review JSON SHA-256 `73cec6f240c8c20f54eca1dfa141dc8330564e763fd6d9fc2cb43709a723d6d6`.

Authorization is exactly one candidate boot and one **root** `RUN`. There is no non-root pre-trigger probe and no same-boot retry. The persistent RT-CDM watcher must be active and fsyncing before RUN. Any result is archived and followed by immediate Golden reboot.
## 2026-08-30 — post-provenance candidate boot aborted before hardware RUN

The authorized candidate boot passed corrected-IOMMU/front-PIX preflight and started the persistent RT-CDM observer at idle. No hardware `RUN` occurred: a shell redirection to a root-owned evidence file failed with `Permission denied` before the sole privileged helper executable was entered. The persisted observer remained `seq=0 stage=idle`, `irq_armed=0`; sensor transmission never began; no QC10C output exists; CAMSS/sensor stayed suspended; Golden return is clean. The candidate boot is considered consumed but this is not a failed PIX attempt and no same-boot retry occurred.

A corrected wrapper now creates its evidence log before the privileged helper invocation and fails closed on any existing actual-run log. A replacement candidate boot/root `RUN` requires a new explicit authorization checkpoint.
## 2026-08-30 — replacement post-provenance one-shot authorized after pre-exec abort

Fresh bounded provenance, package, branch-sync, Golden boot-state and corrected-wrapper review all pass. The previous candidate boot did not enter the helper/sysfs trigger and does not count as a PIX hardware run, but its boot authorization is consumed. Corrected wrapper SHA-256 `7724dabef6fe147809919d0349d1adfe1a4b1c2418ede82c7235e0d79e1d396d` prevents the root-owned-redirection failure and refuses reuse of an actual-run evidence path.

Exactly one replacement candidate boot and one root helper invocation are authorized. Persistent RT-CDM watcher must be ready/fsyncing before the helper. No non-root pre-trigger and no same-boot retry. Any helper result is archived and followed immediately by Golden reboot. Review JSON SHA-256 `555d2cbb35cbffa8da1183201efab1d17a92e904fa035460bc98bd7029ab1ec7`.
## 2026-08-30 — replacement post-provenance run reaches sensor-on, times out at VFE1 Epoch0

The single authorized replacement helper invocation returned `ETIMEDOUT` after approximately 0.80 s and produced no QC10C file, but it materially advances the hardware boundary. The persistent observer records 13 successful FIFO0 BL-done completions with no RT-CDM fault. These are exactly the pre-CSID command prefix: startup0, all four prime0 BLs, startup1, all five prime1 BLs, startup2 and startup3. IMX681 then logs `MODE_SELECT=1 front transmission started`.

The first-frame runner next waits for raw VFE1 Epoch0 before BUS retarget to slot1 and prime2/request2. No Epoch0 arrived within the bounded wait, so prime2 was never submitted. Teardown wrote `MODE_SELECT=0`, stopped/masked RT-CDM, returned CAMSS/sensor PM to suspended and rebooted to Golden; no same-boot retry occurred.

The runtime therefore proves Linux CAMSS coherent command IOVAs are visible to RT-CDM1 through the corrected requester/SMMU domain. The next static discrepancy is the retained `0022` host stage `IFE resource start`: Windows places it between RT-CDM start and startup packet0, but the callable runner currently only acquires pipeline/VFE power and has no distinct IFE resource-start operation. No further runtime is authorized until the exact same-machine Windows IFE `0x804` start semantics are recovered, represented and inspected.


## 2026-08-30 — CSID1 common lifecycle closed and Linux 0044 built static

The consumed 0043 run proved the earlier `configure -> RUP/AUP -> enable` correction was insufficient, so the next boundary was recovered from exact same-machine `qccamisp8380.sys`. The accepted common-reset oracle SHA-256 `43a265f0cd63fa9e01406e8b5ff0b62c756dc2bc2f8c3a24df74a4f832b76996` proves normal front DEVICE_CONFIG performs `wrapper 0x101 -> TOP mask 1 -> RESET_CFG 0x11 -> software-only RESET_CMD 2 -> reset completion -> full Gen2 builder`. The reset callback has no pre-reset IRQ_CMD write; `IRQ_CMD=1` belongs to ISR acknowledgement. Windows stop invokes the same reset callback with argument 1, i.e. hardware-only reset.

Full-builder ownership is also separated from the later initial packets. The full Gen2 builder runs immediately after DEVICE_CONFIG reset. Each DEVICE_START IFE `0x803` packet is then followed by its exact CSID companion; packet0 owns `+0x330`, IRQ subsample, crop and format-measure writes, packets1..3 repeat crop, and later `0x804` IPP enable remains `CTRL=1 -> 0x3cbc601c -> TOP=1`. Live-final `+0x328/+0x32c=0xffff0000` are not written by either proven software owner, so Linux no longer replays them.

Static `0044-x1e-csid1-common-lifecycle-windows-parity.patch` SHA-256 `a96339ab84094cfa0d103d73e6c04294dce5f211738fcbbe2bd370b9c5bb3340` implements only the fail-closed X1E front-mode0 delta. qcom-camss SHA-256 is `98b3252e9d1e8c46e81ea48fe0a6b4b0ecea77e1206915b4b1378040dc473cbc` with exact Golden vermagic. Strict checkpatch is `0 errors, 0 warnings, 0 checks`; fail-closed inspection JSON SHA-256 `4d1dfc9d264e3b19d6e7e688b9c0d56f7db40a6f238b50856c26072fc9447ac7` proves reset/builder/companion/enable/stop ordering, patch byte-roundtrip, retained ISR ack and removal of the teardown-only public CSID `s_stream(false)` rollback.

Bounded provenance remains green after explicitly adding the new Windows and Linux implementation facts. **No runtime is authorized.** Next build and inspect a distinct one-shot 0044 package while Golden remains the saved/default recovery entry and the package remains unarmed.

## 2026-08-30 — 0044 common-lifecycle package installed and inspected unarmed

The static 0044 base is published at `b0f4cded52b242ceeb8743bc51db19819b500237`. A fresh package under `e003h-csid1-common-lifecycle-0044-candidate` is pinned to CAMSS `98b3252e9d1e8c46e81ea48fe0a6b4b0ecea77e1206915b4b1378040dc473cbc`, front-only DTB `019c062a718e58d0e303afbb7d454ed6674cf39a287ed453fb2cd4dd0dfdf77f`, sensor `389c4a8c...7388`, capsule `6aed028d...a20`, helper `d13ab2d...c38c`, the 0044 Linux inspection, both CSID Windows oracles and stable bounded provenance `5b016ae79b599a4675f7c5fde31619d53ef2c9c6143791f683504513058e78b1`.

Golden preflight passes, the new GRUB ID `sp11-camera-e003h-csid1-0044-one-shot` is installed at `/boot/sp11-7.1.5-camera-e003h-csid1-0044`, and package inspection passes with JSON SHA-256 `be15d0f6558efbe7c00b3257ceed60cb7af9e4895a2957368a55ba159e649128`. Golden remains the saved default, `next_entry` is empty, no camera modules are loaded and `AUTHORIZATION.json` is absent. The provenance IQ production blocker now cites only its dedicated immutable IQ producer oracle rather than mutable `state/project.yaml`, removing the previous hash cycle without changing blocker semantics.

**Package installation is not runtime authorization.** A later hardware diagnostic requires a separately committed authorization checkpoint for exactly one candidate boot/root helper invocation, persistent observer, no same-boot retry and immediate Golden return.

## 2026-08-30 — one 0044 common-lifecycle diagnostic authorized, unarmed

Separate authorization review SHA-256 `b733c2576378268804e98d25fd9431002187357e61dbaced53d4152956034e44` passes against package commit `8f5b405cc89de074c84e2318c33be90c9875bfc8`: branch/origin equal, Golden current boot, package inspection exact, bounded provenance green, no prior 0044 run evidence, no candidate modules loaded and empty `next_entry`. Authorization SHA-256 `94d4c1b8eb34e42990ed02ea5c228d37a2521cc44417bba64c97cc70ae9d6162` permits exactly one candidate boot and one root helper invocation. Persistent observer is mandatory, no same-boot retry is allowed, and any helper result must be archived then followed by immediate Golden reboot. Production parity remains unauthorized. The authorization checkpoint itself leaves the candidate unarmed.

## 2026-08-30 — 0044 boot-1 pre-exec abort; runtime harness v2 corrected

The first authorized 0044 boot reached the correct candidate but no camera code ran. Package-only `preflight.sh` was mistakenly reused after authorization and correctly rejected the active authorization. Evidence proves helper invocations `0`, camera modules loaded `false`, no RUN log/sysfs trigger, no same-boot retry and clean Golden return. Preflight/abort/hash evidence SHA-256 values are `32a67cc7...277b`, `1935368a...6aa` and `a4f2b0fd...a76e`; boot-1 consumption record is `b462e768...07f9`. The original authorization bytes are retained as `AUTHORIZATION-BOOT1-CONSUMED.json` (`94d4c1b8...6162`).

Package v2 adds authorization-aware `runtime-preflight.sh` (`6f778ebc...e9b4`) and makes corrected `load-candidate.sh` (`1f7be8b1...072e`) call it before any module load. The runtime gate checks candidate identity, HEAD/origin sync, authorization contract, exact package/provenance/candidate hashes, one-shot GRUB state, clean module/run/watcher state and exact front-only DT/IOMMU geometry; it contains no module load or trigger write. Package-only preflight remains authorization-free by design.

Package inspector v2 (`e015b70e...e887`) proves that ordering plus the no-hardware boot-1 record and regenerates package inspection v2 `99396b73...2429`. Golden package-only preflight v2 and package inspection both pass with no active authorization. **Runtime is blocked pending a fresh replacement authorization review.**

## 2026-08-30 — replacement 0044 diagnostic authorized after v2 harness correction

Fresh replacement review `0bed79f1a6fd4a8edbfcfc906206f902c6740be81712623341c1b52b6e78f2ac` passes against corrected harness commit `2e87aa9`: boot-1 hardware execution false/helper count zero, package-v2 inspection exact, authorization-aware runtime preflight/load hashes exact, Golden current boot, HEAD/origin equal, bounded provenance green, empty `next_entry`, no active authorization at review time and no actual 0044 RUN log. Replacement authorization `6fc9802e64d1ba16b5b30c961e1a0ceceb9e270131d8cb28b609e53e962f4f53` permits exactly one candidate boot and one root helper, with runtime preflight before module load, persistent observer READY/idle, no same-boot retry and immediate Golden return after any helper result. Production parity is not authorized. This checkpoint remains unarmed until pushed.

## 2026-08-30 — 0044 boot-2 pre-exec abort; cwd-independent package v3

The replacement candidate boot reached the new runtime preflight but failed before module load because its embedded `git merge-base` lacked a repository cwd. Candidate identity/auth were correct; qcom_camss/IMX681 were never loaded, helper/RUN count was zero, no same-boot retry occurred, and Golden return is clean. The consumed authorization is preserved. Package v3 fixes both `runtime-preflight.sh` and `run-once.sh` to use explicit `git -C <repo> merge-base --is-ancestor`, tests the operation from `/tmp`, and pins both zero-hardware consumed boot records in the inspector. Runtime is blocked pending a fresh authorization checkpoint.

## 2026-08-30 — 0044 boot-3 hardware result: same Epoch0 boundary; BUF_DONE drift exposed

The package-v3 boot-3 diagnostic executed exactly one root helper and returned `ETIMEDOUT` at VFE1 Epoch0. RT-CDM completed 13 pre-CSID BLs without fault; IMX681 streamed; CSID1 received exactly 37,016 packets with zero ECC/CRC and IPP status `0x00011e00`; no QC10C output. Golden return is clean and there was no retry. Runtime analysis `1f826e629328c182d3c1d8571a480f89100737c697dc44c4d5e3364b5804e746` proves the stable 0042/0043/0044 boundary is identical and 0044 removes the prior teardown warning. The next static discrepancy is `BUF_DONE_IRQ_MASK`: Windows/0042 `0x1ffff`, 0043/0044 `0x1`. Do not patch it blindly; trace its post-builder owner/transition first.

## 2026-08-30 — Windows RT-CDM BL boundary ambiguity closed dynamically

Fresh same-SP11 Windows KD logging at qccamisp commit RVA `0x28884` records every RT-CDM BL descriptor and live arena neighbors. Static decompile of `FUN_140028480` independently proves `+0x50=BL base`, `+0x54=(length-1)|0x00100000`, `+0x58=trigger`; consequently `0x00100003`, `0x0010000f`, and `0x00100013` are exact 4-, 16-, and 20-byte BLs. The first-start queue submits `0x0800f000` as one 4-byte BL and `0x08057000` later as a distinct 4-byte BL. The intervening arena word `0x0803c000` is skipped and is not a hardware command.

The same trace shows all submitted CSID common RUP/AUP blocks use `+0x18=0x01f501f5` for replay1, replay2, replay3 and steady state; adjacent `0x000001f5` / `0x01f50000` words are not submitted. CSID1 path enable occurs exactly once with selector `5` (IPP), with no hidden RDI/PPP start. Physical base arithmetic remains `0x0ac62000+0xf000=0x0ac71000` VFE1 and `+0x57000=0x0acb9000` CSID1.

Raw logs are frozen under `windows-rtcdm-bl-boundaries/`. Fail-closed extractor SHA-256 `e823b0048ebe786d9e9320dd17e8c20e1459edd71c7784c97df2d6d91b845e6d` reproduces oracle SHA-256 `6741c46589c6bc976ad87a0aad566088e831c452e41961df309bda40f62dc45f` and output SHA-256 `6e192974185085eff4839b135168254e7655c63a05f28dff75a10764e135e19b`. No Linux delta follows from this closure. Continue with the already-selected Windows first-start lifecycle after VFE BUS start and before sensor-on.

## 2026-08-30 — Linux IRQ observer audit and 0048 read-only CSID history

The 0047 timeout interpretation was audited against the exact Linux IRQ handlers. VFE680's ISR does not read or clear any VFE status, so the private VFE1 BUS-status1 Epoch0 poll is observer-safe. CSID680's ISR does read IPP `+0xac` and clears the complete non-zero value at `+0xb4`, so a later timeout snapshot cannot establish historical absence of CAMIF/RUP/Epoch events. Treat all earlier `IPP=0x00011e00 therefore no CAMIF/RUP/Epoch ever occurred` language as superseded; retain the raw final status and all other measured facts.

0048 is deliberately diagnostic-only. It latches OR/last/count from the IPP value the ISR already read, before the existing clear, with a software epoch reset after front software reset and before startup/RUP. It adds zero MMIO accesses and leaves all hardware behavior unchanged. Patch `91d292888e563c2d4e0ffc65664cfa4b0a3225cb1f56af9053652998ff0be1d7`; module `94cc14d9702492bffa2b4e72989db45356cf59ffcce7f4c382be13e7130030b7`; checkpatch 0/0; exact Golden vermagic; static inspector PASS. Package and authorize separately before any camera activation.

## 2026-08-30 — 0048 in-ISR history moves boundary past CSID CAMIF/RUP/Epoch

The single authorized 0048 observer-only diagnostic executed one helper invocation, timed out waiting for VFE1 raw BUS Epoch0, archived its evidence, and immediately returned to FullIO v19c Golden. There was no same-boot retry and no QC10C output. RT-CDM reached 17 FIFO BL completions without fault; IMX681 started/stopped cleanly; CSID1 received 37,016 packets with zero ECC/CRC.

The new software-only CSID ISR history is decisive: OR=`0x00e15ff8`, last=`0x00004ee8`, count=`4`. The OR includes CAMIF EOF/SOF, CAMIF Epoch0/1, and RUP_DONE. Thus the old 0042–0047 inference from final `IPP_IRQ_STATUS=0x00011e00` is superseded: those events did occur and were cleared by the normal CSID ISR before the timeout dump. VFE1's no-Epoch0 observation remains observer-safe because its normal ISR does not read/clear VFE status.

The accepted same-machine Windows live IPP status is `0x00e11ff8`; Linux's accumulated history differs by exactly `0x00004000`, bit14 `ERROR_LINE_COUNT` in the pinned CSID680 layout. This transient mismatch was also hidden by the final snapshot. VFE1 remains `TOP_STATUS1=0x00030003`, `BUS_STATUS1=0`, with exact Windows masks/FULL state and no raw BUS Epoch0 bit21. The current boundary is therefore after CSID1 CAMIF/RUP/Epoch progression and before VFE1 raw BUS Epoch0. Runtime is blocked; statically close bit14 line-count provenance/Windows handling and the CSID1-to-VFE1 handoff before another hardware run.

Fail-closed extractor SHA-256 `54026e02919b9fb7ab8bd4455fca2f1e1b0660952baafd6114abd4d3b029c58e`; analysis SHA-256 `70d0dad027d266026bde7b2c81cc8d9e4d73a477f12fcb3e831f9d10a9a98866`.

## 2026-08-30 — CSID1 bit14 line-count error classification closed

Exact qccamisp reader/handler linkage proves CSID1 IPP `+0xac` is stored at IRQ payload `+0x10`, reloaded as the IPP field, and tested against Windows error mask `0x3c1c6004`; bit14 is included. Same-machine Windows live IPP `0x00e11ff8` lacks bit14. Windows expected/actual format-measure registers `+0x388/+0x38c` are both stable `0x08700f00` (2160×3840). Exact Qualcomm CSID680 commit `0f16924f...` identifies bit14 as fatal `ERROR_LINE_COUNT` / `CAM_ISP_HW_ERROR_CSID_FRAME_SIZE` and reads actual/expected frame-size plus HBI/VBI on the error path.

Oracle `2081159e5a28a02fa79a933c83fe0838a6efe778f1ccdd85a804c6f3d8ec9b3e` is fail-closed. The bit14 mismatch is real, but causality for missing VFE1 Epoch0 is not yet proven. A read-only 0049 capture of `+0x38c/+0x390/+0x394` at the instant bit14 is observed is justified; no hardware programming delta is authorized.

## 2026-08-30 — 0049 read-only line-error frame telemetry static PASS

0049 adds only three conditional MMIO reads to the existing CSID ISR error path: `+0x38c/+0x390/+0x394`, retained in software when IPP bit14 is seen before the normal clear. Zero writes and no transport programming change. Patch `58f9080b7ae1e9addbfb035930374d073a1694c0a666132dcd1604e13b14f4e3`; module `610c0def762e6449c342452ffc436b195cd1330a41055076d25cca95f077a1f5`; inspection `e5d53e72e90406023616c2658f413ca80d6c49e9ff1f4622929012299eb17afe`; checkpatch 0/0. Package and authorize separately.
## 2026-08-31 — 0050 ordered first-IPP geometry telemetry static PASS

Windows first-IRQ work narrowed the next Linux question to ordering rather than another programming guess: determine whether Linux sees RUP_DONE while measured IPP geometry is still 3840x2640, and whether its first Epoch-bearing IRQ is already wrong. 0050 therefore adds an eight-entry software-only sequence retaining the already-read IPP IRQ status plus one `FORMAT_MEASURE0 +0x38c` read per retained IRQ before the existing clear. It adds no MMIO writes and changes no masks, crop/RUP-AUP programming, VFE, RT-CDM, CSIPHY, sensor or DT behavior.

Patch `61440f2452badd0d01f312af4ef4e08505c2263a3557af1693f1a5e04db7020b`; qcom-camss `b69a20b517953a96cf5ff806a26c78e52ce5e177ef8dcdf69afa0dd561e8439b`; inspector `097a1f617c6130cae086b36c1fa34897226a69d6ffd16cb90419d1f40a72e4fc`; inspection JSON `6ccfd7e88586721dbc1b4050e041e8b128a8409d8ee2f1dd40fd0030f70a047d`. Reverse/forward patch round-trip proves exact 0049/0050 source boundaries; Golden vermagic matches and compiler/checkpatch diagnostics are zero. **No runtime is authorized by this checkpoint.** Package and inspect a distinct unarmed 0050 candidate before any separate authorization review.
## 2026-08-31 — 0050 candidate installed and inspected unarmed

A distinct Golden-safe 0050 package is installed under `/boot/sp11-7.1.5-camera-e003h-csidseq-0050` with GRUB ID `sp11-camera-e003h-csidseq-0050-one-shot`. The package pins static commit `5613ea361e3361200921ccb063d2b0d8bfcda71f` and CAMSS `b69a20b517953a96cf5ff806a26c78e52ce5e177ef8dcdf69afa0dd561e8439b`; all non-CAMSS runtime assets are byte-identical to consumed 0049.

Package inspector `a2e816a588652e5f5e79be990e0f8ffec29d8cc83db564258e50a2481b5242af` emits inspection `e28726d1c7c89d7fdb4681519752c6e2540a505155a21624b41038c02d673b49`: Golden saved default retained, `next_entry` empty, no camera modules, no authorization, front-only DT/IOMMU exact, runtime preflight before module load, single helper invocation and no same-boot retry. **The candidate remains unarmed and runtime is not authorized.**
## 2026-08-31 — one 0050 ordered-geometry diagnostic authorized, unarmed

Fresh review `f4b643320e444dc34a6db5ea5793f35a109eb6b7768d526c4ba3b8e682ea08c8` passes against package commit `e8ae5eba3f91d8b0bb681fb4258c37ce82ad325d`: package/provenance hashes exact, no prior 0050 RUN, Golden current, no camera modules, and empty `next_entry`. Authorization `016ede970efbc7653ab390fbdc5bc72d503cc2dc5068059dd2c5ca72968039ac` permits one candidate boot and one root helper only, requires the persistent RT-CDM observer, forbids same-boot retry and mandates immediate Golden return after any helper result. Production parity and any new hardware-programming delta remain unauthorized. The checkpoint remains unarmed until pushed.

## 2026-08-31 — 0050 runtime moves crop failure to RUP_DONE -> first Epoch; Windows IRQ ownership closes post-RUP +0x18

0050 executed one authorized helper and returned cleanly to Golden. Ordered Linux IPP status/actual pairs are `00811dd0/00000f00`, `00600cc0/00000f00`, `00000cc0/00000f00`, `00004ee8/0a500f00`. The first pair matches Windows phase/status: RUP_DONE with width initialized and height incomplete. At the next Epoch-bearing IRQ Windows is already `00600228/08700f00` = 3840x2160, while Linux is `00600cc0/00000f00`; Linux later measures 3840x2640 and bit14. Extractor `7c736bfb37d95ea252cbcc9734321e37df396c6915423c2aea3374d22f70917c`; analysis `bc8c2fd7033121592e540e3eedde134e56cab6d2525526f7771a74ec7b424459`.

Exact qccamisp IRQ disassembly is now fail-closed: reader direct MMIO writes are only `+0x84,+0xa4,+0x94,+0xb4,+0xd4,+0x14`; handler has no direct MMIO writes and no IPP bit23/RUP_DONE conditional path. Extractor `a11a4fc1ba6ed00fa69065cfae09918cace87f0e07a1bf4deb68d9fa2310806c`; oracle `4ec65044495ea7040b8fa350bee67b83c563eae824ba6e171e7e7b8e8e9b8eb8`. Thus Linux generic RUP_DONE bookkeeping must not emit the current second `+0x18` write on the fail-closed X1E front IPP path. The next static delta may clear only the software shadow and omit that MMIO write, preserving all RDI/non-front behavior.

## 2026-08-31 — 0051 front RUP_DONE ownership correction static PASS

0051 removes no register globally and adds no hardware access. In the exact X1E80100 front-mode0 IPP RUP_DONE ISR branch it clears only Linux software `reg_update_ipp()` bookkeeping and skips generic `csid_reg_update_clear()`, preventing the Windows-unmatched post-RUP write to CSID `+0x18`. All fallback/non-front/RDI behavior remains byte-for-byte through the existing helper; IPP IRQ clear and global IRQ clear are retained. Patch `7d658f5a0c57aa5749aaa76078cce0fb05b35918ec62430786b4d9bd20c7952d`; module `6b7287e6eb96c44060d58691333b82f4e4103df929f98ad39ec50347b379f020`; inspector `b2c72a59fcf6c926a91bff4e9337ed0c92129af73aebc4d4b5b1078220ea0c01`; inspection `a0595d75392871542812ec185e632af37e8da889d6758e61cea794f25517d132`. Runtime remains blocked pending a distinct unarmed package and separate authorization.

## 2026-08-31 — 0051 candidate installed and inspected unarmed

A distinct 0051 package is installed under `/boot/sp11-7.1.5-camera-e003h-rupclear-0051`, boot ID `sp11-camera-e003h-rupclear-0051-one-shot`. It pins static commit `01d17d96a1882e6d3462c1b9e2caa261f8750821` and CAMSS `6b7287e6eb96c44060d58691333b82f4e4103df929f98ad39ec50347b379f020`; all non-CAMSS runtime assets are byte-identical to 0050. Package inspector `ed534bfd75486fbd9e41999f8ecb46392fd4664c57081622b96292245357a5ab` emits `be455f237db0864af6a667c36968ae1055add607716c1eec9368c2a831786009`. Golden is saved/default, `next_entry` is empty, authorization is absent and no camera module is loaded. Runtime remains blocked pending a separate authorization review.

## 2026-08-31 — one 0051 RUP_DONE ownership diagnostic authorized, unarmed

Fresh review `f364d91485f5103cbfea28e74f7554523fee177eb76c7377d41c65acdaf5ee47` passes against package commit `42824cb69eb15a9124fb80d042c0c8f90d5197d0`. Authorization `0f4837282f952a38b53d1ec99dd940594b52203cc0e830f48ca0e98058e847b5` permits one candidate boot and one helper only, requires the persistent observer, forbids same-boot retry and mandates immediate Golden return after any helper result. The sole differential is suppression of the Windows-unmatched post-RUP front IPP `+0x18` command; no new register write/value is authorized.
