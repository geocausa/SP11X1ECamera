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

## Exact next task

1. Treat CSID1 IPP static representation as closed by `0011`; do not expand it beyond same-machine Windows-proven mode-0 state without new oracle evidence.
2. Derive a valid VFE680 **PIX/ISP** architecture for the Windows path; do not reuse the current RDI-only WM mapping as a shortcut.
3. Map the minimum FULL Y/C path first, then determine which DS/statistics blocks are required for Windows-equivalent startup rather than copying every live counter/status/address field.
4. Preserve the proven lifecycle: ISP -> MIPI -> sensor on start; ISP teardown first on stop, with no invented dependency between MIPI-stop and sensor-off. Keep `0010` static-only.
5. Build/static-test the complete parity candidate and prove rear D-PHY/RDI behavior is unchanged.
6. Only then define a bounded one-shot runtime gate with exact Golden rollback. No front parity frame is authorized before these conditions are met.

RDI remains available solely as an explicitly non-parity diagnostic if it becomes useful for fault isolation.
