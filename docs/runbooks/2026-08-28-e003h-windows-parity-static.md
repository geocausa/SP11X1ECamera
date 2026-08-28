# E003h Windows-parity transport static handoff — 2026-08-28

## Resume point

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
- normal StopAsync returns both sampled RT-CDM windows to the `0x80000000` powered-off sentinel.

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

The deterministic bounded mapped-base store sweep finds no direct software store to live `FE_CFG +0x20=0x07ff000f` or `FIFO0_CFG +0x5c=0x01000000`. This is intentionally classified as negative evidence only: it does not prove reset/default ownership. Final CDM teardown after mask-zero, applicability of conditional `CGC_CFG +0x14=7`, and ownership/timing of those two live configuration values remain blockers. Extractor SHA-256 is `399a7a6ecd412d652fcce1bad469514c87a0e696ad7bf4e68a55c51f148e6629`; JSON SHA-256 is `489f47f45465603260a06f8aa2083cc417fff816478be9b6c8f68233bb0be927`. See `WINDOWS-RTCDM1-INIT-ORDER.md`. No Linux RT-CDM behavior was enabled.

## Exact next task

1. Treat CSID1 IPP static representation as closed by `0011`; do not expand it beyond same-machine Windows-proven mode-0 state without new oracle evidence.
2. Treat the VFE1 FULL memory format as resolved: one contiguous 2560x1440 **TP10 UBWC / QC10C-family** surface with 3584-byte stride and `Y_META -> Y_TP10 -> C_META -> C_TP10` layout. Linear NV12 is not parity.
3. Treat the Windows IFE startup byte corpus as complete: four main CDM streams, 2,131 register writes and all 46 DMI payload references/bytes are captured. Further Windows byte capture is not the current blocker.
4. Treat register ownership and VFE aperture as closed by the deterministic classifier and `0012`: never replay the five live-volatile offsets or any Windows buffer/status address, and keep the `0xf000` override Denali-only.
5. Preserve the 21 exact DMI register/selector identities and 16 exact payloads. Execution is proven to use native hardware **RT_CDM_1 v2.1 at `0x0ac26000`** with `SW CDM=0`, and its dedicated interrupt is firmware GSI 319 -> Linux **`GIC_SPI 287`**. Resource representation is closed by `0013`, disabled IRQ/DMA scaffolding by `0014`, and init/start/commit/stop ordering by the new static oracle. Before any Linux MMIO initialization, close same-machine ownership/timing for `FE_CFG +0x20`, `FIFO0_CFG +0x5c`, conditional `CGC_CFG +0x14=7`, and final CDM stop/power semantics.
6. Treat the FULL BUS topology as closed: WM0+WM1, one QC10C/TP10-UBWC surface, exact 3584-byte stride/`0x76b000` core layout, VIDEO completion from VFE rather than CSID IPP. Dynamic addresses remain per-buffer.
7. Derive a fail-closed VFE680 PIX/ISP implementation for the Windows 3840x2160 input -> 2560x1440 TP10 UBWC FULL path, including only DS/statistics/IQ state Windows proves necessary.
8. Preserve the proven lifecycle: ISP -> MIPI -> sensor on start; ISP teardown first on stop, with no invented dependency between MIPI-stop and sensor-off. Keep `0010` static-only.
9. Build/static-test the complete parity candidate and prove rear D-PHY/RDI behavior is unchanged.
10. Only then define a bounded one-shot runtime gate with exact Golden rollback. No front parity frame is authorized before these conditions are met.

RDI remains available solely as an explicitly non-parity diagnostic if it becomes useful for fault isolation.
