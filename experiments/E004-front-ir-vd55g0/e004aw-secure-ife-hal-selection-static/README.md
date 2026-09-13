# E004aw — secure IFE HAL selection static map

## Result

**PASS: the trustlet selects full IFE versus IFE-Lite from the logical IFE core index before it samples the hardware-version register.**

No Linux SecureISP runtime occurred.

## HAL-family selection

The secure IFE open path receives a logical core ID in the range 0..3 and derives the secure sub-block layout from that ID.

For logical cores **0 and 1**:

- the trustlet marks the context as non-lite;
- CSID is derived from secure base + `0x4000`;
- bus-writer is derived from secure base + `0x0c00`;
- the HAL callback table uses the full-IFE implementation;
- the hardware-version callback is `HAL_ife_get_hw_version`.

For logical cores **2 and 3**:

- the trustlet marks the context as lite;
- CSID is derived from secure base + `0x0000`;
- bus-writer is derived from secure base + `0x1200`;
- the HAL callback table uses the IFE-Lite implementation;
- the hardware-version callback is `HAL_ife_lite_get_hw_version`.

This selection is made while opening the logical IFE device. It is therefore earlier than and independent of the subsequent hardware-version read.

## Hardware-version lifecycle

Both full and lite version callbacks perform the same essential operation: read the first 32-bit dword through the selected IFE base pointer and return it.

The IFE command dispatcher samples that callback during its POWER_ON command and stores the returned dword in the IFE context.

This refines E004av: `IFE_HW_VERSION` is real hardware state returned to the host and retained by the worker, but it is **not the discriminator that selects full IFE versus IFE-Lite**.

E004aw does not make a global claim that no later code can ever consult the stored version. It only proves that HAL-family selection precedes the version sample and is controlled by core index in the recovered open path.

## CSID HAL selection is separate

The secure CSID path has a second two-way HAL selection. DeviceConfig copies one input bit into an internal manager field; CSID initialization later chooses one of two CSID function tables from that field.

That selector is separate from the IFE hardware-version callback and separate from the IFE full/lite core-index decision.

The semantic name of that DeviceConfig input bit is not claimed yet.

## Architectural consequence

There are now three independent pieces that must not be conflated:

1. **logical IFE core ID** -> full IFE vs IFE-Lite HAL family and secure-base topology;
2. **DeviceConfig selector bit** -> CSID HAL variant;
3. **IFE hardware-version dword** -> sampled after power-on and retained/reported.

The remaining Surface-specific question is therefore not "what HW-version value chooses the HAL?" but **which logical IFE core ID(s) the Surface IR DeviceConfig requests**.

## Evidence

- `evidence/IFE-HAL-SELECTION.txt`
- `evidence/HW-VERSION-LIFECYCLE.txt`
- `evidence/CSID-HAL-SELECTION.txt`
- `ghidra/IFE-DISPATCH-DECOMP.txt`
- `ghidra/TRUSTLET-HAL-SELECTION.txt`
- Ghidra extraction scripts in `ghidra/`

## Safety boundary

No qcomtee module was loaded. No secure aperture was mapped from Linux. No CP_CAMERA memory reassignment was performed. No secure CSI SIP call or SecureISP task was sent.

SP11 remains on protected Golden Linux.

## Next static gate

Trace how the SecureISP DeviceConfig input populates the logical IFE core list used by the trustlet, then determine whether the Surface AUX/IR configuration selects a full IFE core or an IFE-Lite core. Do this statically before considering another runtime experiment.
