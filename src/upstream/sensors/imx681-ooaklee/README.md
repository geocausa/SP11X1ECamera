# Reused ooaklee IMX681 sensor source — 2026-10-12

This is an isolated source candidate, not an installed driver or an upstream-ready
submission. It reuses the public standalone sensor from
[ooaklee/linux_ms_dev_kit-sp11](https://github.com/ooaklee/linux_ms_dev_kit-sp11)
at revision `2cbd1ec3e2da385e7bd91fd65c63ba5a8fb5b865`.
The examined camera files are byte-identical to the hardware-validated revision
`64999b9fc6e60ebccdc3755563cafcc63930cc90`.
Original SPDX declarations and provenance comments are retained.
`reference.json` pins the public originals by SHA-256, Git blob and immutable URL.

The source comments describe independently transcribed hardware observations,
not copied vendor source or extracted binary payloads. That declaration is
recorded as public-source provenance; our final attribution/provenance review
and contributor sign-offs remain required. No proprietary originals were read.

## Local adaptation

The accompanying patch changes only the control error paths:

- A negative runtime-PM result returns before I2C access or PM put.
- Group hold is released independently of the prior CCI error accumulator.
  The first error is preserved; a release failure is returned if no earlier
  failure occurred.

The init/mode table is unchanged. The table-free control changes do not establish
timing, electrical routing, regulator behavior, image quality or hardware recovery.

## Evidence and limits

The adapted driver builds and links as an AArch64 external module against the
candidate17 source/configuration and the pinned candidate16 symbol table.
`W=1 KCFLAGS=-Werror`: no compiler/modpost warnings. This is a source/link probe;
it was not loaded. GCC and Clang ASAN/UBSAN each pass 1,080 control fault cases,
after reproducing three counterexamples in the original function. Twelve
changed/missing/symlink pin cases reject before creating an output directory.

The original PHY admission functions also run unchanged in hosted tests.
Each compiler passes 36 profile, 66 submode and 3 D-PHY error/control cases.
Those tests prove that the public provider rejects our 2.400-Gsymbol/s profile;
its sole admitted profile is 2.406 Gsymbol/s, one physical trio zero.
Hosted context types and PM/CCI helpers are models, not live hardware.

Do not replace the current mode2 driver with this candidate. Differences include
3840x2640 versus 3840x2160; 1.203 GHz versus 1.200 GHz link frequency; and
CCI_REG16(0x0340) versus our qualified CCI_REG24(0x033d) frame-length write.
The public header explicitly distinguishes its 548571428-Hz bus pixel rate from
the VT timing clock. Its default frame-length metadata therefore still needs
review. Our measured 720-MHz timing checkpoint remains authoritative for our
qualified mode and must not be replaced by bus throughput.

Normal patch checkpatch reports only the deliberately absent Signed-off-by.
Local code review with `--no-signoff` is clean. This does not confer submission
readiness or add an author's certification.

See [comparison](../../../../docs/UPSTREAM-OOAKLEE-COMPARISON-20261012.md) and
[validation](../../../../docs/UPSTREAM-OOAKLEE-COMPARISON-20261012.json).
The working RAW/RDI receiver path is reusable groundwork. The target remains
native CAMSS hardware-ISP/NV12 and libcamera; software ISP is not substituted.

## Reproduction

On SP11, references are retained under
`/home/geoca/Documents/SP11-PROJECT/02-kernel/upstream-ooaklee-camera-20261012-01/current`.
From the repository root, choose fresh output paths:

```sh
python3 tools/test-upstream-ooaklee-imx681-controls.py \
  --reference-root /path/to/pinned/current \
  --output /path/to/fresh/control-gcc --compiler gcc
python3 tools/test-upstream-ooaklee-cphy-profile.py \
  --reference-root /path/to/pinned/current \
  --output /path/to/fresh/profile-clang --compiler clang
```

Repeat the hosted tests with the other compiler. Recreate the external module
probe with only `imx681.c`, unchanged `imx681-tables.h`, and a Makefile containing
`obj-m += imx681.o`; use the exact source/config/symbol hashes in the evidence.
