# E004dh checkpoint — exact SWABF/SWASF offline port

Status: **in progress, static contract substantially recovered; one bounded Windows oracle planned for final resolved tuning blobs.**

## Exact Windows transfer branch

For later requests (`request_id >= 10`), E004cf proved the trusted worker executes:

`SWABF(source -> scratch) -> SWASF(scratch -> destination) -> 0x80 tail`

E004dg intentionally returns `SP11_WORKER_ESWAB_PENDING` for this branch until the transform is reproduced without approximation.

## Static contract recovered in E004dh

### SecureISP KMD tuning ABI

The exact `qccamsecureisp8380.sys` dispatch sends:

- blob type `0x1c` / SWABF through trustlet opcode `9`, payload size `0x22`;
- blob type `0x1d` / SWASF through trustlet opcode `10`, payload size `0x804`.

The same dispatcher calls the exact task-send function already dynamically identified in E004AQ (`FUN_140004a90`). This gives a clean Windows oracle point: when `x0 == 9` or `x0 == 10`, `x2` is the final tuning payload and `x3` is the exact payload length.

### DeviceMFT output packing

`CamX::IFENode::UpdateSWABFData` packages:

- 16 signed 16-bit values;
- one final signed 16-bit value;
- total `0x22` bytes.

`CamX::IFENode::UpdateSWASFData` packages:

- first 256-entry 32-bit table (`0x400` bytes);
- second 256-entry 32-bit table (`0x400` bytes);
- one final 32-bit value;
- total `0x804` bytes.

### SWASF interpolation/scaling

`CamX::IQInterface::GetSWASF101Data` constructs the two 256-entry output tables from two 64-entry floating-point source curves, linearly interpolating four substeps between adjacent control points. The recovered exact constants are:

- first-table scale: `32.0f`;
- second-table inverted scale: `256.0`.

Each result is rounded by the Windows `+/- 0.5` rule and saturated to 8-bit (`0..255`) before being written as a 32-bit table element.

### Exact Surface tuning source exists locally

The shipped Surface auxiliary-camera Chromatix binaries contain both module identities:

- `mod_swabf10_trigger_data` / `swabf10_sw_v2`;
- `mod_swasf10_trigger_data` / `swasf10_sw_v2`.

Relevant exact VD55G0 files include:

- `com.surface.tuned.aux_vd55g0_MSHW0472.bin`;
- `com.surface.tuned.aux_vd55g0_MSHW0492.bin`.

So E004dh is not relying on generic Qualcomm tuning.

## Why use Windows once more

The binary Chromatix container is self-describing but the exact runtime interpolation point depends on the live request/tuning selectors. Rather than guess the selected region from file layout, the safest parity oracle is to capture the final `0x22` and `0x804` payloads at the already-proven KMD task-send boundary during one normal Windows FaceAuth IR stream.

The oracle is read-only. It does not patch the driver, trustlet, tuning or protected memory.

## Safety

Current Linux remains Golden FullIO v19c. No Linux SecureISP runtime, CPZ runtime, CB9 enable, protected ownership transition, camera runtime or firmware modification has occurred in E004dh.
