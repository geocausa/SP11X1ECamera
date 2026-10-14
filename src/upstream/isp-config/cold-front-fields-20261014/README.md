# Independent cold front fields around the calibrated native baseline

Reuse the working unified48/libcamera21/run93/v15 stack and its own calibration.
This package fills a narrow configuration gap; it replaces no proven driver,
queue, allocator, IPA, matrix, shading mesh or noise algorithm.

The earlier E006t exact Titan680 source audit already derives a cold disabled
LCAC image. Earlier front E003h work pins the native PDPC/GIC/GTM packers.
We reuse those anchors and the public VFE680 register names. The new work
examines only their disabled subcommands and the separate BLS121 packer.

## Derived fields and independently selected policy

| Register | Retained/native field fact | Candidate complete word |
| --- | --- | --- |
| 0x3d60 PDPC | CreateSubCmdList updates bit0; native range starts0x3d58,count3 | zero cold image |
| 0x4760 GIC | CreateSubCmdList updates bit0; native range starts0x4758,count3 | zero cold image |
| 0x5460 LCAC | CreateSubCmdList updates bit0; E006t cold-zero proof reused | zero cold image |
| 0x5a60 GTM | CreateSubCmdList updates bit0; native range starts0x5a60,count1 | zero cold image |
| 0x4b68 BLS_CFG_0 | BLS121 selector13 packs18-bit offset at bit14 | own measured integer1649 shifted16; fraction2=0 |

The old BLS mask preserves low16. Under the selector13 layout, that includes
the low2 offset bits and fourteen additional bits. These are inherited state,
not newly measured configuration. The independent candidate selects fraction0
and zero for the other bits. The fourteen bits are not claimed to have been
individually named or proven reserved.

The native packer also supports selector199, with a12-bit offset at bit20.
It is explicitly rejected by the candidate. The exact BLS121 packer branch was
executed on synthetic objects; the live front object's selector was not observed.
The register mapping uses the retained public BLS_CFG_0 address and existing
own override. Establishing the actual front selector/precision remains a gate.

Cold zero is an explicit Linux-owned policy. The four native subcommands preserve
the other31 bits on an existing image. Running them on zero images proves this
candidate's disabled words; it does not prove those words equal every prior
private-dependent image or establish a physical cold reset. The complete
original constructors were not executed by the acceptance verifier.

## Implementation and validation

sp11-front-cold-fields.h emits five count1 REG_CONT commands,60bytes, using the
existing bounded encoder and native calibration-domain type. No enable writes,
DMI, private reader, MMIO, DMA allocation, installation or runtime caller exists.
The original2160->1440 geometry/tag and selector13/fraction0 are the only
admitted policy. Geometry/tag is not proof of timing/precision/colour context.
Late-invalid policy, short capacity and aliasing reject before publication.

test-native.py runs the exact SHA-pinned Surface DeviceMFT locally on SP11 with
synthetic objects only. Four actual CreateSubCmdList routines are observed at
their CDM-builder boundary. The BLS121 actual function returns without shims.
No packing/calculation/branch shim is used. CDM-builder interception observes
arguments and stops before hardware. Original code, profiles, tuning, tables,
disassembly and pixels remain private; only derived field facts/counts are saved.

Acceptance covers560 actual module cases,1668 actual BLS vectors over both
layouts/three prior-word seeds, and four old-mask fractional counterexamples.
The independently written C helper tests all262144 legal offsets per GCC/Clang
under ASan/UBSan, policy rejection and atomic publication. Four compiled unsafe
mutations are rejected. A tiny7.1.5 ARM64 probe compiles W1/Werror; no CAMSS or
kernel rebuild is performed.

Run on SP11, with unique unused output directories:
- python3 test-native.py <unique-output-directory>
- python3 build-worker.py <unused-two-digit-tag>
- python3 qualify.py

Evidence is docs/COLD-FRONT-FIELDS-20261014.json. The existing24-word measured
fragment remains unchanged. Together there are29 configuration candidates,
without the withheld ABF activation; concatenation/ordering/runtime integration
is not implemented or qualified by this package.

## Remaining work

Reuse retained front source/trace metadata to bind the BLS121 selector and
processing precision. Qualify the chosen fraction and cold-state policy in the
original calibrated mode. Complete the surrounding functional startup and bind
existing own LSC/ABF/tone/CCM/AE/AWB through the proven native pipeline before
replacing the private loader. Remaining copied scalar/table regions are not
closed by these five words. Preserve calibration; no new optical measurement
was performed or required merely to extract these definitions.

Both installed private startup consumers remain. Complete startup, physical
parity, upstream API integration and whole-series provenance/license/DCO review
remain open. Upstream readiness is false.
