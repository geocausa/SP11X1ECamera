# IMX681 frame-length source correction — 2026-10-13

The imported mode initializes frame length 3554 at byte addresses
0x033d..0x033f. Its control and startup paths previously wrote a 16-bit
value at 0x0340 and advertised default 2708. This patch changes only the
frame-length register definition to CCI_REG24(0x033d) and default to 3554.
The 65535 maximum, exposure margin, other defaults, control/start bodies
and independently observed initialization/mode transactions remain unchanged.
The narrower maximum is retained conservatively; no wider hardware range is claimed.

Parent: the source-qualified endpoint/clock candidate23, sensor SHA
285ce0d786e09e59536232d706a6e0ebfe62904fdce35f87db1f48456828e2fd.
The imported source attribution and transaction provenance remain in
../imx681-ooaklee/reference.json and the unchanged table header.

## Reproduction

First reproduce the prior full receiver tree and sensor admission patch using
../imx681-hwcfg-20261013/prepare.py and its documented parent. This helper then
creates a **sensor-only source package**, not a complete kernel checkout:

```sh
python3 prepare.py --parent-source /path/to/hwcfg-source --output /path/to/fresh-sensor-package
python3 test-fll.py --source /path/to/fresh-sensor-package/drivers/media/i2c/imx681.c \
  --parent-source /path/to/hwcfg-source/drivers/media/i2c/imx681.c \
  --kernel-source /path/to/compatible-kernel --output /path/to/fresh-host-output --compiler gcc
```

Repeat with clang and a fresh output. The pinned CCI inputs come from the
retained compatible7.2.0 kernel. Test output is rejected if occupied, symlinked
or nested in an input. Inputs/fixtures are checked before output creation;
Python -O is refused. Apply the patch to a fresh full candidate23-equivalent
tree and verify manifest hashes before any later full kernel build.

## Qualification

Candidate24 final-qual01 passes exact patch replay, real AArch64 external
module compile/modpost/link with W=1 KCFLAGS=-Werror, zero warnings/errors,
and checkpatch --no-signoff with zero errors/warnings. GCC and Clang each pass
63430 ASAN/UBSAN cases, including an old-code register counterexample, every
2688..65535 frame-length encoding, PM/range/CCI failures and each of446 startup
write failures. The test imports actual sensor constants/control/start bodies,
mode tables, CCI macros and CCI write/multi-write bodies. Regmap, PM, control
setup, bitfield and unaligned primitives are models. Eleven input/output/fixture
rejections preserve retained data and reject before new output creation.

The initial aggregate stopped on missing patch-message separator formatting;
the compiler and sanitizer results passed. That failed record is retained.
The final qualification changes patch packaging only, replays the exact same
source and verifies the retained module. No build result was overwritten.
Local fixture development had a naming collision and unavailable LSAN in the
container; only the later SP11 GCC/Clang runs count toward qualification.

Evidence: ../../../../docs/UPSTREAM-IMX681-FLL-VALIDATION-20261013.json.
Retained run: /home/geoca/Documents/SP11-PROJECT/02-kernel/upstream-ife-base-build-20261011-01/candidate-24/final-qual01/result.json.

## Hardware limits

No installation, module load, capture, boot graph change or full candidate24
Image. Candidate23 remains the latest full source tree, candidate16 the latest
full Image. The exact2.406-Gsymbol/s sensor/receiver profile stays separate from
the qualified local2.400 profile and its3840x2160/720-MHz measurements.

This patch resolves a source table/control inconsistency. It does not measure
the imported3840x2640 mode's VT clock, physical frame-length response, supported
fastest cadence or exposure latency. The existing548571428 PIXEL_RATE value is
transport-derived; it is not qualified as the array timing clock. It must not
be treated as measured timing. Normal regulator/provider boot failure, reset/
privacy polarity, sensor/power graph, compatible full build and fresh guarded
RAW stop/reopen remain required before runtime qualification. Both private
startup consumers and all14 end-to-end readiness categories remain open.
No DCO, upstream submission, maintainer acceptance or hardware proof is claimed.
