# IMX681 endpoint and clock admission — 2026-10-13

This table-free patch adds explicit admission for the independently observed
standalone sensor profile. It rejects missing/wrong bus type, anything except
one zero-based C-PHY trio, unsupported clock/polarity/wire options, an ambiguous
or nonmatching link-frequency list, and an input clock other than 19.2 MHz.
The clock is rechecked before each runtime power-on; reset GPIO is required.

Admission precedes reset acquisition, rail/clock enable and sensor register
access. Raw endpoint properties are checked before the common parser can
silently default or truncate them. Mode/init transactions and the control ABI
are unchanged. The qualified local 2.400-Gsymbol/s mode remains separate from
this 2.406-Gsymbol/s / 1.203-GHz-link profile.

The parent is the attributed GPL sensor in ../imx681-ooaklee, with its existing
two control-error fixes. The unchanged observed mode table has SHA-256
fad73d655d9afb511d537690ec32e4c14426e4f2be615c2db5b7f4a002468710.
The patch introduces no extracted vendor calibration, tuning or firmware.
See the prior source provenance and reuse review; public licensing alone
does not establish derivation or upstream acceptance.

## Qualification

Candidate23 on SP11: GCC and Clang each pass 106 ASAN/UBSAN cases using the
actual sensor function bodies, constants and supply declarations. Parser,
clock, regulator and GPIO helpers are modeled; this is not hardware evidence.
Six changed/missing/symlink/occupied-output/fixture/optimized-Python controls
reject without creating a new output or clobbering the retained sentinel.

The actual AArch64 sensor module compiles and passes modpost/link with W=1 and
KCFLAGS=-Werror, zero warnings/errors, against the retained compatible 7.2.0
configuration and pinned candidate16 symbols. Exact patch replay and checkpatch
with --no-signoff pass. The latter does not supply DCO or maintainer review.

Evidence: ../../../../docs/UPSTREAM-IMX681-HWCFG-VALIDATION-20261013.json.
Failed preparation, fixture, syntax and packaging attempts remain on SP11 and
are excluded from the final pass. The first body-only fixture missed a stray
generator '+' at the clock definition; full module compilation caught it.
The corrected harness imports actual constants/supply declarations.

## Reproduction

From a normal checkout, choose fresh output paths outside the repository:

~~~sh
python3 src/upstream/sensors/imx681-hwcfg-20261013/prepare.py --parent-source /path/to/qualified/candidate17/source --output /path/to/fresh/source
python3 src/upstream/sensors/imx681-hwcfg-20261013/test-hwcfg.py --source /path/to/fresh/source/drivers/media/i2c/imx681.c --manifest src/upstream/sensors/imx681-hwcfg-20261013/manifest.json --output /path/to/fresh/gcc --compiler gcc
python3 src/upstream/sensors/imx681-hwcfg-20261013/test-hwcfg.py --source /path/to/fresh/source/drivers/media/i2c/imx681.c --manifest src/upstream/sensors/imx681-hwcfg-20261013/manifest.json --output /path/to/fresh/clang --compiler clang
~~~

The preparer verifies the pinned receiver preparation tool/manifest, reproduces
that series, detaches the changed sensor before patching a hardlink clone, and
rechecks all retained receiver/CAMSS files. For the external-module probe, use
only the new imx681.c, unchanged imx681-tables.h and obj-m += imx681.o; use the
exact compatible config/symbol checkpoint recorded in the evidence.

Nothing is installed or loaded. Candidate16 remains the latest full Image.
Next qualify VT/frame-length semantics, endpoint/power graph and the recorded
standard-regulator boot failure, then a compatible full candidate and guarded
fresh open RAW stop/reopen. Hardware ISP/NV12 and Windows parity remain targets.
Reuse existing measured/generated calibration; all14 readiness gates remain.
