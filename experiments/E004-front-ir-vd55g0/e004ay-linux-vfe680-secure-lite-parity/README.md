# E004ay — Linux VFE680 vs SecureISP IFE-Lite bus parity

## Result

**PASS: the SecureISP trustlet's IFE-Lite bus-writer sub-block matches the register geometry already implemented by Linux `camss-vfe-680`.**

This is a static parity result only. No protected Linux camera resource was accessed.

## X1E Linux resource model

Linux 7.1.5 has native `qcom,x1e80100-camss` resources containing:

- IFE0 and IFE1 using `vfe_ops_680`;
- IFE_LITE_0 and IFE_LITE_1, marked `is_lite = true`, also using `vfe_ops_680`.

The X1E table therefore already models the same full/full/lite/lite family split recovered independently from the SecureISP trustlet in E004aw/E004ax.

## Bus sub-block translation

The trustlet stores an IFE-Lite **bus-writer sub-block pointer** rather than the IFE top-base pointer used by Linux.

Accounting for the bus sub-block's +0x200 position in Linux's top-relative map produces exact register matches:

| Trustlet bus-relative | Linux lite top-relative | Linux vfe-680 meaning |
| --- | --- | --- |
| +0x18 | 0x218 | bus IRQ mask 0 |
| +0x28 | 0x228 | bus IRQ status 0 |
| +0x30 | 0x230 | bus global IRQ clear |
| +0x64 | 0x264 | write violation status |
| +0x68 | 0x268 | write overflow status |
| +0x70 | 0x270 | image-size violation status |
| +0x200 + n*0x100 | 0x400 + n*0x100 | write-client CFG |
| +0x204 + n*0x100 | 0x404 + n*0x100 | image address |
| +0x208 + n*0x100 | 0x408 + n*0x100 | frame increment |

The trustlet's client-enable routine uses bus-relative client windows at +0x200, +0x300, +0x400, +0x500 and later windows with the same 0x100 stride. Linux describes IFE-Lite write clients from top-relative 0x400 with the same 0x100 stride.

## Semantic match

The register-position match is supported by behavior, not offsets alone:

- the trustlet reads the bus IRQ status at bus +0x28;
- clears via bus +0x30;
- reports bus violation and image-size violation from +0x64 and +0x70;
- enables/disables individual IFE-Lite bus clients through the client CFG window;
- configures frame address/size/drop/stride state through per-client windows.

Linux `camss-vfe-680` implements the same classes of operations for its lite VFE path.

## What this means for Linux parity

The ordinary Linux X1E camera driver already contains a substantial reusable description of the **IFE-Lite DMA/bus register semantics**.

The missing protected-camera work is therefore not "invent an IFE-Lite bus driver from scratch." The unresolved pieces are instead:

1. protected ownership / trusted-execution transport;
2. the secure CSID side;
3. lifecycle coordination so Linux never directly touches resources while the secure world owns them.

E004ay does **not** say the non-secure Linux VFE registers may be used as a substitute for the protected aperture.

## Evidence

- `evidence/TRUSTLET-IFE-LITE-BUS.txt`
- `evidence/LINUX-VFE680-LITE.txt`
- `evidence/LINUX-X1E-IFE-RESOURCES.txt`
- `evidence/PARITY-MAP.txt`

## Safety boundary

No QCOMTEE module was loaded. No secure memory was mapped or reassigned. No secure CSI service call or SecureISP task was issued. SP11 remains on protected Golden Linux.

## Next static gate

Perform the same comparison for the secure CSID function table against Linux's X1E `csid-680`/lite resources, and separate exact register parity from secure-only wrapper behavior.
