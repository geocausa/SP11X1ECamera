# Camera project chat handoff — 2026-09-13

## Purpose

Use this file to resume the SP11 Camera Stack project in a fresh ChatGPT chat without relying on prior chat context.

Work autonomously. Same-machine Windows is the behavioral authority. Do not ask routine approval questions. Preserve Golden and one-shot rollback discipline. Save/push meaningful checkpoints.

## Authorized systems

Camera work only:
- SP11 dual boot Windows/Linux
- SP7 Windows KDNET host
- PiMaster

Do not involve unrelated hosts/projects.

## Current durable Git state

Repository:
`/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera`

Branch:
`experiment/e004-front-ir-vd55g0`

Current pushed HEAD:
`4c0bd7839193d6e77152a18ee3e91818e4e402ea`
commit:
`4c0bd78 camera: reconstruct SecureISP trustlet ABI`

Important recent pushed checkpoints:

- `6c80b8a` — CSIPHY0 receiver programming proven 96/96 against same-machine Windows.
- `7bb4018` — normal Linux CSID runtime deliberately blocked pending Windows IR route authority.
- `0f79a1c` — same-machine Windows proved real IR frames bypass observable standard CAMSS CSID/VFE.
- `4c0bd78` — exact Windows SecureISP host/trustlet static ABI reconstructed.

## Current machine safety state

At handoff creation SP11 was recovered from a stale KD pause and verified back on Golden:

- kernel: `7.1.5-sp11-render-parity-v4+`
- BOOT_IMAGE: `/boot/sp11-7.1.5-audio-fullio-v19c/...`
- GRUB saved entry: `sp11-audio-fullio-v19c`
- `next_entry=` empty
- no camera/CAMSS modules
- no `/dev/media*`
- no `/dev/video*`

The stale KD process on SP7 was killed and the target was rebooted through KD. Windows BootNext had been one-shot and Golden returned normally.

## Golden / accepted RGB state

Protected Golden remains FullIO v19c, camera-free.

Accepted rear/front RGB unified parent remains the E003 IB DTB:
`experiments/E003-front-imx681-cphy/e003i-front-native-productionization/ib-unified-current-golden-rear-front-dtb/x1e80100-microsoft-denali-sp11-ib-unified-rear-front.dtb`

Do not change Golden as part of IR experiments.

## Front IR VD55G0 status

### Sensor / patch / Windows state

Same-machine exact package and Windows behavior are already reconstructed and proven.

Physical sensor:
- model: `0x3047`
- revision: `0x1111` CUT1
- I2C: 7-bit `0x60`
- D-PHY one lane
- 840 Mbps
- RAW10 VC0 CSI datatype `0x2b`
- Windows output: NV12 644x604 @ 60 fps

Surface-specific 552-byte patch SHA:
`5c07088c8871792e48a3d75d5b9af1cb3725739b8d6aaed229be6f7c0126b321`

Native Linux sensor state was proven exact:
- 552 patch writes
- 1 patch setup
- 1 boot
- 42 safe Windows final-config writes
- 596 sensor data writes total
- final SW_STBY
- sensor returns runtime-suspended
- no sensor stream / no illumination

The illumination-coupled sensor write `0x0468=0x02` remains isolated from Linux runtime authorization.

### Native bind / graph

Pushed `0907585` closed the native bind/graph/control gate:
- dynamic physical-device identity by OF compatible + address 0x60
- immutable sensor -> CSIPHY0 link
- Y10 644x604
- link frequency 420 MHz
- pixel rate 84 MHz
- HBLANK 556
- VBLANK 1351
- direct sensor `.s_stream(1)` deliberately returns `-EOPNOTSUPP`
- no capture / no illumination

### CSIPHY0 receiver

A real DT bug was found and fixed offline:
- old CSIPHY0 resource: `0x0ace4000 + 0x1000`
- exact X1E driver needs common block beginning at offset `0x1000`
- same-machine Windows aperture: `0x0ace4000..0x0ace5fff`
- corrected disposable resource: `0x0ace4000 + 0x2000`
- CSIPHY1 still begins at `0x0ace6000`
- correction changes one DTB byte only

Pushed `6c80b8a` proves:
- E004k receiver programming executes
- 96/96 modeled CSIPHY0 registers match same-machine Windows
- 420 MHz link
- timer 266666667
- lane mask `0x81`
- settle `0x10`
- receiver cleanly powers off
- sensor stays suspended before/after
- no warnings/Oops
- no sensor/CSID/VFE stream
- no capture/illumination

## Critical Windows IR route discovery

Pushed `0f79a1c` / E004y is the key architectural result.

Windows was run with exact `Surface IR Camera Front`:
- SourceKind Infrared
- VideoPreview
- NV12 644x604 @ 60fps
- StartAsync Success
- active holder called `TryAcquireLatestFrame()`
- 12 real frames acquired
- StopAsync Success

While those real frames were being delivered:

Standard observable CAMSS:
- CSID wrapper: no OUTPUT_IFE_EN
- CSID0 = exact known Windows inactive/default 8 KiB image
- CSID1 = exact known Windows inactive/default 8 KiB image
- CSID2 = exact known Windows inactive/default 8 KiB image
- VFE0 = all zero
- VFE1 = all zero

Therefore:
**Windows IR does not use the normal observable CAMSS CSID/VFE route.**

A Linux normal-CAMSS IR route may be useful diagnostically, but must never be called 1:1 Windows parity.

Windows instead has:
- `CameraSecureISP`
- exact driver `qccamsecureisp8380.sys`
- ACPI `QCOM0CCC\19`
- Qualcomm Spectra 395 SecureISP
- started
- MMIO aperture `0x0acca000..0x0accdfff`
- IRQ 392,391
- aperture rejects both normal KD physical reads and explicit uncached `[uc]` reads during real IR streaming

E004y raw KD log is committed and mechanically verified.

## E004z SecureISP static ABI authority — current main checkpoint

Directory:
`experiments/E004-front-ir-vd55g0/e004z-secureisp-static-authority/`

Verifier:
`verify_e004z.py`

Result status:
`PASS_SECUREISP_HOST_TRUSTLET_ABI_STATIC_RECONSTRUCTED`

Exact same-machine package files:

`qccamsecureisp8380.sys`
SHA:
`47c944fa497477751073ec79a27a589a55e884178c1859d6f27388ec7af2ad53`

`QcISPTrustlet8380.dll`
SHA:
`55ebf254447b9ff8c0a5b20ae81e84f04355f84ce6fa6a09f6205562a5b0b606`

SecureISP INF:
`22bffc4795803de62825ee8eab6bd13cdd2d18e505a39b410eecad52b092e05f`

QcTrEE.sys:
`9cd8252c1b501c1d58e4c49d020d526a5b9bc41a3f5de2ec08e866c3a26c16a2`

QcTrEE INF:
`9e6d38df0b0ff8f766a4b67084f1d55e3bf44ddac766c5466b179e99adda8d6b`

### Secure Companion proof

The exact SecureISP INF explicitly installs:
- `QcISPTrustlet8380.dll`
- `ServiceType = SecureCompanion`
- `TrustletIdentity = 4096`
- `libbitml_nsp_v2_skel.so`
- `bm3a68v08s11n52.bin`

The KMD calls:
`WdfCompanionTargetSendTaskSynchronously`

The trustlet imports secure/isolation APIs including:
- CreateSecureSection
- OpenSecureSection
- AssignMemoryToSocDomain
- MapSecureIo
- MapViewOfFile
- UnmapViewOfFile
- FlushSecureSectionBuffers

The trustlet contains:
- `DAL_csid_process_iq_packet`
- `DAL_secure_ife_process_iq_packet`

This is consistent with E004y: secure CSID/IFE processing exists while ordinary CSID/VFE MMIO remains inactive.

### Class-1 SecureISP task map

Interpret task IDs with their Companion task class.

For class 1 (normal camera-control path):

- task 0 = INIT
- task 1 = DEINIT
- task 2 = START
- task 3 = STOP
- task 4 = PROCESS_DMFT_SURFACE (0x60-byte input)
- task 5 = PROCESS_CMD_BUFFER
- task 6 = PROCESS_DMI_BUFFER
- task 7 = PROCESS_CSL_PACKET (8-byte output)
- task 8 = diagnostic-buffer retrieval (1000-byte output; descriptive name only)
- task 9 = GET_SWABF_DATA (0x22 bytes)
- task 10 = GET_SWASF_DATA (0x804 bytes)
- task 11/12 = unimplemented/default
- task 13 = NOTIFY_EVENT (8 bytes)

Important:
the helper also supports task classes 2 and 3. Class 3 is a separate debug/image retrieval namespace and reuses numeric task IDs. Do not treat the task number alone as globally unique.

### Outer SecureISP KMD operation map

- `0x801` GetInitParams
- `0x802` DeviceConfig; worker setup/power + class1 task0 INIT
- `0x803` SendCSLPacket
- `0x804` DeviceStart
- `0x805` DeviceStop
- `0x806..0x80b` unsupported/default
- `0x80c` GetDeviceInfo
- `0x80d` Init
- `0x80e` DeInit / PowerOff
- `0x80f` SupplementalDeviceConfig; captures CSIPHY/lane parameters
- `0x810` NotifyEvent

### Secure CSI-lane protection

START ordering:
1. exported SecureISP function-table command `0x2e` = protect computed CSI lane mask
2. class1 task 2 START

STOP ordering:
1. class1 task 3 STOP
2. exported command `0x2f` = unprotect same lane mask

The protection helper calls `ConfigSecureCamera()`.

That opens QcTrEE device interface GUID:
`{AE865C08-4A07-404D-BE51-D9A0465E23E5}`

Exact QcTrEE INF identifies it as:
`PassThroughService`

SecureISP sends synchronous IOCTL:
`0x00568004`

Request begins:
`0x02001807`
then protect boolean + computed lane bitmask.

Do not invent a semantic name for `0x02001807`; exact secure-world meaning remains unresolved.

## Dynamic trace that was being prepared when chat became unreliable

Experiment directory:
`experiments/E004-front-ir-vd55g0/e004aa-windows-secureisp-task-runtime/`

Only these preparation files existed:
- `PREBOOT-LINUX.txt`
- `ARMED-WINDOWS.txt`

The intended dynamic test was:
- one Windows one-shot
- KD breakpoint/log at KMD Secure Companion send helper
- log outer operation, Companion class, task ID, lengths, and secure-lane mask
- start exact IR holder
- acquire real frames
- clean stop
- return Golden

**This trace did NOT complete and must not be treated as evidence.**
No accepted E004aa task trace/result exists.

During chat/tool instability, a stale KD process left Windows paused. For this handoff it was recovered:
- stale SP7 KD process killed
- KD reattached on port 50005/key 1.2.3.4
- target broken deliberately
- `.reboot` issued
- SP11 returned to clean Golden

Start E004aa again from scratch if still desired.

## Important untracked directories discovered at handoff

These currently exist untracked:
- `e004ab-windows-secureisp-cold-task-runtime/`
- `e004ac-windows-secureisp-first-use-runtime/`
- `e004af-windows-secureisp-cold-task-trace/`
- `e004ag-windows-secureisp-reload-trace/`

They were not reviewed or modified during handoff creation.

**Before inventing new experiment names or continuing E004aa, inspect these directories carefully.** They may be partial work from another prior/parallel context. Do not assume they are valid, and do not delete them.

## Immediate next steps for the new chat

1. Verify:
   - SP11 Golden
   - branch/head/upstream
   - `python3 experiments/E004-front-ir-vd55g0/e004z-secureisp-static-authority/verify_e004z.py`
2. Inspect the untracked E004ab/ac/af/ag directories and determine whether any contains valid newer task-trace work.
3. If none supersede E004aa, prepare a **fresh** one-shot Windows SecureISP dynamic task trace.
4. Dynamic trace should capture:
   - outer KMD operation code at dispatcher
   - Companion task class
   - task ID
   - input/output lengths
   - secure-lane 0x2e / 0x2f protection calls and computed mask
   - exact order around INIT/START/frame-processing/STOP/DEINIT
5. Use the exact `Surface IR Camera Front` active-frame holder requiring real `TryAcquireLatestFrame()` frames.
6. Return immediately to Golden after trace.
7. Decode and checkpoint/push before considering any Linux SecureISP runtime.
8. Linux SecureISP runtime remains **NOT AUTHORIZED** by E004z.

## User preference / working style

User is a coding novice and wants concise noob-friendly progress summaries, but expects autonomous technical judgment. Save/push meaningful checkpoints so chat-context loss does not strand the project. Do not repeatedly ask for routine confirmations.

