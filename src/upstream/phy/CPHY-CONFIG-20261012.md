# Internal C-PHY configuration preparation, 2026-10-12

Candidate17 adds an MMIO-free Qualcomm CSIPHY2.1.2 preparation helper to the
standalone PHY composite. It accepts an explicit sensor link frequency,
logical trios1..3 and an explicitly supplied settle counter. It bounds the
frequency before doubling it, rejects invalid/duplicate trios and nonzero
unused route entries, and publishes output only after all checks pass.

The supported nominal symbol-rate bins are extracted from the pinned GPL
Qualcomm2.1.2 table. Selection uses symbol-rate units directly, so the
2.4Gsymbol/s front link selects the2.5Gsymbol/s bin. It does not convert
through the downstream rounded2.28bits/symbol bandwidth thresholds, clamp
an above-maximum rate, estimate frequency from pixel-array rate, or supply
an implicit settle value.

Physical trio-enable bits are1,3,5. No dedicated D-PHY clock bit is included.
This checks route numbers and counter width only. Electrical routing,
wire permutations, receiver timing, clock-domain validity, power ownership
and a generic PHY C-PHY configure interface remain unqualified. The helper
has no runtime caller and contains no register, power or reset operations.
The standalone driver's C-PHY power-on path remains unsupported.

The input settle counter is explicitly hardware-specific. A nonzero16-bit
value is representable; that does not prove it is a valid MIPI settle time.
A future timing/provider implementation must derive and qualify it before
calling this helper or admitting hardware. No generic PHY ABI is changed here.

Apply after the candidate16 dependency checkpoint:

```sh
patch --batch --fuzz=0 -p1 -i /path/to/0001-qualcomm-csi2-prepare-cphy-config.patch
python3 -B tools/test-upstream-cphy-config.py \
  --candidate-source /path/to/candidate17-source \
  --public-header /path/to/cam_csiphy_2_1_2_hwreg.h
```

The three-file patch replays exactly. Nine modified/missing/symlink reference
controls reject. GCC and Clang ASAN/UBSAN each pass6,150 valid boundary/route/
counter combinations,150 atomic range rejections and21 other atomic errors.
Tests compile the unchanged actual helper/header; only Linux types and
BIT/ARRAY_SIZE/errno definitions are supplied for the hosted build.

Four AArch64 objects (CAMSS, generic ISP, PHY core and standalone PHY composite)
pass W=1/-Werror with zero warnings. A separate external composite link probe
uses the exact same five provider source files and candidate16's pinned
7.2.0 Module.symvers. Module/modpost linking also passes W=1/-Werror, with
matching AArch64 vermagic. This is module/source qualification; candidate17's
full Image has not been built or booted. Candidate16 remains the latest full
kernel link checkpoint.

Per-file checkpatch passes. Standard patch checkpatch has one
FILE_PATH_CHANGES advisory; the existing Qualcomm CSI2 MAINTAINERS wildcards
cover both new files. The advisory-reviewed check passes. The first patch
header/style attempt is retained. No project signoff, submission or review
claim is invented.

Evidence: `docs/UPSTREAM-CPHY-CONFIG-VALIDATION-20261012.json`.
Both private startup consumers/all14 upstream readiness blockers remain.
Golden, inactive daily services, original evidence and calibration are preserved.
Next: independently qualified receiver timing and register sequencing, typed
generic configure/consumer routing, the sensor/power graph, then guarded
hardware qualification. CDM physical retirement remains a separate requirement.
