# libcamera integration patches

`0001-vd55g0-gain-helper.patch` targets upstream v0.7.0, commit
`b7854fd07d42168f099b5ce30d1702e0e0875bf5`. Apply with `git apply --check`
then `git apply` in a clean checkout. E004fc records a complete baseline build,
patched build and passing helper/format tests on SP11 ARM64.

The patch adds the generic VD55G0 analogue-gain mapping only. It neither adds
monochrome processing nor installs a board-specific alias or guessed black level.
Current SP11 model naming must be aligned before runtime use. These changes have
not been submitted upstream or deployed to the system library.
