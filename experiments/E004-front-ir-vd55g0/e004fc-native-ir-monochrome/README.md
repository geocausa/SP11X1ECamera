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

## Monochrome processing implemented and tested

`0002-softisp-monochrome-raw10.patch` adds true R10_CSI2P processing to the CPU
software ISP, preserving all ten bits through black-level/gamma adjustment and
producing neutral RGB/BGR output (24/32-bit). No Bayer impersonation or colour
interpolation is used. Full-array 644x604 output is allowed, including borders.
Monochrome sensors select the CPU backend automatically unless the caller
explicitly requests another mode. The generic uncalibrated monochrome fallback
runs BlackLevel, Adjust and Agc; no AWB or CCM. This is not sensor calibration.

The statistics histogram is computed from full samples; equal channel sums use
the existing IPA eight-bit domain. Short planes, short payloads and error frames
produce invalid statistics and return both buffers with an output error. Output
padding is cleared. The standalone statistics path rejects incomplete buffers.

Four focused normal tests pass, including the new mono-processing test, and the
monochrome test also passes with address/undefined-behaviour sanitizers. Fixtures
cover all 1024 values, all histogram bins, low-bit sensitivity, six output formats,
minimum/odd-height sizes, distinct cropped borders, padding, error buffer return,
metadata and a full-size x+66 ramp with three black-level settings. The full-frame
fixture is synthetic, based on E004ev geometry; it is not a new hardware capture.
Test memory is memfd-backed, so expected DMA_BUF_IOCTL_SYNC ENOTTY messages do not
validate DMA cache coherency. Real DMA buffers still need a hardware gate.

`MONO-MANIFEST.json` records exact source/patch hashes. Both patches reapply to
the recorded pristine upstream commit and match all 14 source files byte-for-byte.
The earlier helper manifest remains historical; this manifest supersedes its
unimplemented-monochrome status. Neither modified library nor tuning is installed.

To reproduce, apply patches 0001 then 0002 to the recorded upstream base, configure
using HELPER-MANIFEST.json options and run `ninja -C BUILD -j4`, then
`meson test -C BUILD --no-rebuild --print-errorlogs mono-processing vd55g0-helper bayer-format pixel-format`.
For the bounds gate, configure another build with `-Db_sanitize=address,undefined`,
build `test/mono-processing`, then run that test through Meson.

## Next hardware gate

E004fd will test 16 processed RGB888 frames from the already-proven sensor pattern.
The kernel now reports the generic vd55g0 model using the standard V4L2 naming
helper, allowing the generic gain helper to bind without a board alias. All
sensor register/power/control code is unchanged. The fresh candidate and isolated
libcamera build will be hashed before installation; Golden remains permanent.
No claim of hardware-processed output, useful optical signal, endurance or
Windows Hello parity follows from these offline tests.
