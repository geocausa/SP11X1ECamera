# Independent disabled CSID680 RAW10 input plan

sp11-csid680-ipp.h derives the processed-image input route from bounded virtual
channel, DT slot and ten-bit sensor input. It produces seven internal,
host-endian register writes with an explicit CSID680 target. It does not produce
a VFE CDM stream, read a firmware/carrier/schema, allocate memory, perform MMIO
or enable a path. It has no caller in the installed driver.

The public references are six GPL-labelled files from Qualcomm's camera-driver,
revision 3f5ef25e12b501a518d2d4f4a870288e9bb127a0, tree
27e77a604ec38e82dcc0cd30d7685679b0f91ebb. Exact URL, size, Git blob and SHA-256
pins are in csid680-ipp-reference-20261012.json. The new implementation is
independently written, GPL-2.0-only. Reference identity does not waive wider
project provenance, copyright attribution or upstream review requirements.

## Definitions and supported policy

| Part | Basis |
|---|---|
| Input decode | The unchanged public cam_ife_csid_get_format_ipp_ppp() maps RAW10 to decoder 2 and plain-format metadata 1. The CSI-2 RAW10 packet datatype is 0x2b. Unsupported sensor depths fail closed in our supported subset. |
| Route fields | Exact cam_ife_csid680.h common descriptor: VC shift 22, DT shift 16, DT-slot shift 27, decode shift 12, path enable at bit 31. The plan bounds VC to its five-bit field and DT slot to two bits; enable stays clear. The provider must reserve the actual routing resource. |
| Processed-path CFG1 | Pixel store and timestamp enable/strobe come from the exact IPP descriptor and unchanged public processed-path initialization. No crop/drop, binning, HDR, frame-ID packet decode, VFR or second VC/DT is enabled. The RDI plain-format/packing interpretation must not be applied to this register. |
| Timing policy | Frame-drop and IRQ-subsample pattern 1 with period 0 request every frame. The exact IPP addresses are taken from the public descriptor. Actual frame cadence and timestamp semantics are hardware qualification gates. |
| Register target | CSID680 is separate from VFE. Its offsets must be applied only to the mapped CSID register window. CTRL, reset, IRQ masks and register-update/apply are absent from this plan. |

The plan passes the full sensor frame through CSID. Sensor mode and VFE scaler
geometry remain separate inputs; it does not crop or reinterpret Bayer order.
RAW10 decoding does not establish VFE internal precision, channel order or
DEMUX/CHANNEL_GAIN bypass. Those remain explicit unresolved integration gates.

Writing a disabled CFG0 is configuration, not a physical-halt proof. Before
applying this plan the provider must own an already stopped CSID/IPP and the
reserved CID route. It must also prove CSID/VFE linking, PHY/reset ownership,
IRQ synchronization, CDM/DMA lifetime and rollback. This helper provides none of
those capabilities, and a target tag alone does not prove a live mapping.

## Validation and reproduction

```sh
python3 src/upstream/isp-config/test_csid680_ipp.py --reference-dir "$SP11_CSID_PUBLIC_SOURCE"
```

The public reference is required; all six files must match size, SHA-256 and
Git blob. Missing, modified and symlink inputs are rejected by the actual
verifier. Both GCC and Clang with ASan/UBSan check 128 VC/slot combinations and
31 atomic rejection cases, including unsupported depths and aliased inputs.
Invalid inputs leave the destination unchanged.

The tests extract and compile four unchanged GPL functions: format selection,
SOF-retiming policy, processed CFG1 preparation and processed-path initialization.
They preserve the source license/copyright header. Test-only resource structures,
IDs and fake MMIO adapt the context; no real hardware is accessed. The reference
initialization enables its fake path, while our output is compared to its first
CFG0 write before enable and its CFG1. No activation write is emitted by our plan.
The unused soc_private assignment in the unchanged public code has a narrow,
reference-only diagnostic suppression; production code remains strict.

The owned helper also compiles as an ARM64 kernel object with W=1 and
KCFLAGS=-Werror. The final object has no firmware/MMIO dependency; only stack
protection is undefined. The production header passes checkpatch. Initial
attempt01 compiled but had one comment-alignment style warning; it is retained.
Attempt02 pins the final source and passes all checks. No module was linked or
loaded. Source/commands/results are recorded in
docs/UPSTREAM-CSID680-IPP-VALIDATION-20261012.json. The object-only probe is in
csid680-ipp-compile-probe and must never be loaded.

## Remaining work

Combine this input preparation, the independent front processing sequence and
disabled FULL NV12 bus setup only after the exact VFE core/Bayer/precision and
resource-lifetime requirements are resolved. Keep Claude's existing measured
calibration packages and fit generators, documented in
docs/UPSTREAM-EXISTING-CALIBRATION-AUDIT-20261012.json; revalidate their domains
on the new processing path instead of restarting all calibration.

The installed front and rear consumers still require their private startup
files. This source-only plan does not remove those runtime dependencies or
establish complete startup, optical parity or upstream readiness.
