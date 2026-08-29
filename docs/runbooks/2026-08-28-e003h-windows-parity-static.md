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
