# Reuse the calibrated native front configuration

The working native driver, IPA, queue/retirement code and Claude-coauthored
calibration are the integration baseline. This package extracts a missing
standalone configuration fragment from that work; it does not rebuild those
subsystems or redo optical measurements. Source34/35 standard-path experiments
are retained separately and are not a reason to replace proven native code.

The own register file and the actual run93 configuration match exactly:
30 register-mask triples. A native override computes (old & AND) | OR.
Only AND & ~OR ==0 makes the resulting complete word independent of the old
private startup. Twenty-five triples meet that condition. The ABF enable at
0x4960 is deferred until owned DMI and complete setup exist, leaving24 words.

generate.py pins the existing measurement file and emits a fixed typed,
288-byte REG_CONT configuration fragment using the existing CDM encoder.
It accepts no profile bytes, raw register input, tables or new calibration.
There are no module-enable writes, DMI commands, MMIO, DMA ownership operations
or runtime callers. Only the original native3840x2160 ->2560x1440 calibration
domain is admitted;2640 and other geometry/tags fail. The parent must establish
the actual timing/precision/crop/colour domain: geometry/tag are not that proof.

The five partial writes remain unresolved:
- 0x3d60,0x4760,0x5460,0x5a60 disable one bit while preserving old word bits.
- 0x4b68 replaces measured high bits while preserving the old lower16 bits.
They are not emitted. Disabled modules and partial overrides do not remove the
private profile file or establish complete startup provenance. Other private
profile scalar/table inputs still require independent replacement.

test-native.py executes the actual pinned native_front_regmask_walk from the
native unified48 source on synthetic register-command capsules. The generated
fragment must match both startup occurrences for three distinct old-word seeds.
It proves the five deferred words still depend on old bits. No private profile,
calibration mesh or image data is read. GCC/Clang ASan/UBSan and five compiled
unsafe mutations exercise data/domain/activation/atomic-publication boundaries.

build-worker.py compiles a tiny standalone probe against the prepared7.1.5
native ABI with W=1/Werror. It rebuilds neither CAMSS nor the kernel, installs
nothing and loads nothing. Physical parity/complete startup are not claimed.
The original calibrated driver, tuning files, protected Golden and RAW33
artifacts remain intact.

Next use retained native functional RE and GPL field definitions to explain
the lower16 BLS bits and the four preserved module-control words. Complete
independent functional startup around existing own LSC/ABF/tone/CCM/AE/AWB,
preserving the calibrated native mode and pipeline. Reuse earlier evidence
before tracing or measuring again. Only then replace the private loader and
qualify the complete startup under a fresh guarded hardware identity.
Standard V4L2/ISP/libcamera adaptation follows the documented integration gaps;
the private startup file and full upstream/provenance/DCO/API review remain open.
