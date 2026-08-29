# Windows VFE1 upstream IQ producer oracle

Date: 2026-08-29

Same-machine Windows remains the behavioral oracle. This pass closes **ownership and module semantics** for the steady-state IFE IQ values; it does not reproduce Qualcomm's proprietary image-quality algorithms.

## Registered producer

The exact Surface camera package `surfacecamavs8380.inf` is UTF-16LE, 16,736 bytes, SHA-256 `4db3acab414e344dc460478b54d964c9c7b5d3d648ee0c19db13523431262fcb`. It copies and registers `QcDeviceMFT8380.dll` as the DeviceMFT under CLSID `{4C2331F0-66BE-4177-9841-2FCBA8CCF5CA}`. The exact DLL is 23,998,368 bytes, SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`.

The DLL contains the Qualcomm CamX tree and the exact IFE node paths (`CreateCmdBuffers`, `FetchCmdBuffers`, `CreateIFEIQModules`, `ProgramIQConfig`, `CommitPacket`, `SubmitPacket`). The paired AVStream miniport `surfacecamavs8380.sys` is 547,192 bytes, SHA-256 `b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed`; its strings explicitly expose UMD CSL address patches, command-memory descriptors, packet enqueue and packet send. The already-pinned `qccamisp8380` `DAL_ife_process_iq_packet` path is therefore the downstream KMD consumer of IQ packet content, not the producer of the values.

## Exact Titan680 ownership

`extract_vfe1_upstream_iq_producer.py` verifies the PE identity and exact ARM64 command-builder anchors. The 24 changing steady-state register identities and all eight DMI register identities from the clean `0024` oracle are fully named:

| CamX module | Changing VFE1 registers | DMI programming |
| --- | --- | --- |
| IFEDemuxBLS141 | `0x3b70`, `0x3b74` | none |
| IFEPDPC311 | `0x3d58`, `0x3d5c`, `0x3d78..0x3d84` | `0x3d08`, sel1, `0x200` bytes |
| IFELSC411 | `0x4358`, `0x435c` | `0x4308`, sel1/2/3, `0x374` bytes each |
| IFEWB201 | `0x456c`, `0x4570` | none |
| IFEGIC311 | `0x4758`, `0x475c` | `0x4708`, sel1, `0x200` bytes |
| IFEBPCABF411 | `0x4958`, `0x495c` | `0x4908`, sel1, `0x100` bytes |
| IFEGTM131 | `0x5a58`, `0x5a5c` | `0x5a08`, sel1, `0x800` bytes |
| IFEGamma151 | `0x5f58`, `0x5f5c` | `0x5f08`, sel1/2/3, `0x400` bytes each |
| IFEDSX101 | `0xa058`, `0xa05c`, `0xa258`, `0xa25c` | `0xa008` sel1/2 `0x300`; `0xa208` sel1/2 `0x180` |

The five `0x958/0x868/0x83c/0x6b8/0x5a4` main-BL shapes are therefore **incoming CamX IQ-module/dirty-group subsets**. No hidden five-way selector exists in the qccamisp KMD path.

## Dependency boundary

The exact DeviceMFT also retains the higher-level CamX dependency/calculation paths:

- `IFELSC411`: AEC update, AWB update, sensor calibration, geometry and tintless/ALSC state; this matches the observed per-frame changes in LSC `0x4308` tables 1/2.
- `IFEGamma151`: requires AEC and AWB updates plus gamma tuning state.
- `IFEGTM131`: uses TMC/tone-mapping state, AEC gain, DRC gain and GTM/LTM percentages; this matches observed `0x5a08` variation.
- `IFEDSX101`: crop/MNDS/DS4 geometry driven; its captured payloads are stable in the accepted run.
- `IFEPDPC311`: sensor mode/format, PDAF configuration and PDPC tuning/mapping state.
- `IFEWB201`: application/AWB white-balance gains and WB tuning.
- `IFEDemuxBLS141`: pixel format, ISP/channel gain and BLS/tuning state.
- `IFEGIC311` and `IFEBPCABF411`: their exact CamX IQ calculation/interpolation paths are identified; the present oracle does not invent undocumented formulas.

Observed stability is not promoted to a universal invariant. The payload-hash oracle remains the evidence for what changed in the accepted run.

## Linux consequence

The next Linux layer may be a **consumer-side, unreachable steady-state materializer**. It may accept a caller-provided observed shape/template plus module-level register values and DMI payload bytes, rewrite DMI words to Linux-owned DMA, and derive BL4 userdata from `requestId`. It must not embed captured Windows values, reproduce Windows ring geometry, invent a KMD five-way selector, or claim to implement CamX AEC/AWB/TMC/tintless algorithms.

No RT-CDM IRQ/FIFO0 submission, CSID1/VFE1 PIX/MIPI enable, IMX681 transmission or Linux frame is authorized by this oracle.
