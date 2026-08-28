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

**start: IFE -> config packets -> CSID -> sensor `0x0100=1`**

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

The main streams reach `VFE1+0xbe70`; 2,015 startup writes lie outside the current upstream X1E VFE `0x4000` aperture. That proves 0x4000 is insufficient for the Windows PIX/ISP path. The old Denali `0xf000` aperture remains a hypothesis, not an automatic Linux change.

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

## Exact next task

1. Treat CSID1 IPP static representation as closed by `0011`; do not expand it beyond same-machine Windows-proven mode-0 state without new oracle evidence.
2. Treat the VFE1 FULL memory format as resolved: one contiguous 2560x1440 **TP10 UBWC / QC10C-family** surface with 3584-byte stride and `Y_META -> Y_TP10 -> C_META -> C_TP10` layout. Linear NV12 is not parity.
3. Treat the Windows IFE startup byte corpus as complete: four main CDM streams, 2,131 register writes and all 46 DMI payload references/bytes are captured. Further Windows byte capture is not the current blocker.
4. Classify the register corpus into writable static/config state, runtime output-address state, counters/status/debug state and command/update triggers. Never blindly replay live Windows addresses or status.
5. Preserve the 21 exact DMI register/selector identities and 16 exact payloads; resolve semantic IQ-block names only from authoritative layout or exact Windows binary evidence.
6. Mechanically determine the VFE1 MMIO resource size required by the observed access set. Current 0x4000 is proven insufficient; do not select 0xf000 merely because historical Denali used it.
7. Derive a fail-closed VFE680 PIX/ISP implementation for the Windows 3840x2160 input -> 2560x1440 TP10 UBWC FULL path, including only DS/statistics state that Windows startup actually requires.
8. Preserve the proven lifecycle: ISP -> MIPI -> sensor on start; ISP teardown first on stop, with no invented dependency between MIPI-stop and sensor-off. Keep `0010` static-only.
9. Build/static-test the complete parity candidate and prove rear D-PHY/RDI behavior is unchanged.
10. Only then define a bounded one-shot runtime gate with exact Golden rollback. No front parity frame is authorized before these conditions are met.

RDI remains available solely as an explicitly non-parity diagnostic if it becomes useful for fault isolation.
