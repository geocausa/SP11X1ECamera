# E004fc: native libcamera monochrome integration (offline)

The maintained kernel route has proven stock libcamera raw capture through E004fb.
This experiment is offline source/build work on Golden. No camera candidate is
installed or armed and no modified libcamera is installed system-wide.

## Completed

Built unmodified upstream libcamera v0.7.0 at
`b7854fd07d42168f099b5ce30d1702e0e0875bf5` (360 Ninja steps), then added a generic
VD55G0 gain helper using the documented 32/(32-code) conversion. The helper uses
the established libipa model rather than a custom gain implementation. Tests
verify independent gain operating points, fractional requests and registration;
the existing Bayer-format and pixel-format tests also pass.

The helper deliberately leaves black level unspecified. Near-black frame means
alone are not a complete fixed-pedestal/calibration policy. It registers the
generic sensor model `vd55g0`; the current board candidate still identifies as
`sp11-vd55g0-native`. Future integration must reconcile that model identity.
No board-name alias was added to the reusable helper. The 8x conversion test is
an offline encoding check, not a new kernel gain range or hardware validation;
the current native driver's advertised maximum remains code 24 (4x).

Patch: `src/front-ir-vd55g0/libcamera/0001-vd55g0-gain-helper.patch`.
Exact base, file/patch hashes, build options and dependencies are in evidence.
The source checkout is at
`/home/geoca/Documents/SP11-PROJECT/06-camera/reference/libcamera-v0.7.0-native-ir`
on branch `sp11/native-ir-helper`; its intended three-file delta is staged and
preserved as the committed camera-repository patch. The incremental build tree
is `build/libcamera-baseline`; BASELINE-BUILD.json describes its initial unmodified
build, while HELPER-MANIFEST.json describes the current patched state.

## Remaining

Stock 0.7.0 rejects mono R10_CSI2P in both CPU/EGL conversion and the statistics
path. Proper monochrome conversion and exposure statistics need implementation;
do not disguise monochrome samples as a Bayer pattern. Add offline fixtures for
all RAW10 low bits, padded rows, odd/minimum geometry as supported by the API,
buffer bounds, brightness transforms and metadata/lifecycle. Preserve existing
Bayer behavior. Hardware remains a fresh, separately gated experiment afterward.

No claim of processed camera output, auto-exposure, useful optical scene signal,
endurance or Windows Hello parity follows from this helper-only checkpoint.
