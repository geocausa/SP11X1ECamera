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
