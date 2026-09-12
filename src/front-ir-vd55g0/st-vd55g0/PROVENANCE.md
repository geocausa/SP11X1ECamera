# ST VD55G0 upstream provenance

This directory is an exact source snapshot from the public STMicroelectronics `vd55g0-linux-driver` repository.

**Authority role: REFERENCE ONLY.** Same-machine Surface Pro 11 Windows evidence is the behavioral/parity oracle. Nothing in this directory may be used by itself to prove SP11 lane wiring, timing, patch policy, power sequencing, or other Windows-parity behavior.

- upstream repository: https://github.com/STMicroelectronics/vd55g0-linux-driver.git
- upstream commit: a05627b0f6d8775aa54b6fa306e91f425f2cbf9e
- upstream commit time observed: 2026-07-28T09:43:27+02:00
- upstream commit subject: ci: Run package job on docker image too
- license: GPL-2.0 driver source; repository LICENSE copied unchanged

Pinned source SHA256:

- `vd55g0.c`: `7d268c6204f1d85fe6047af5204693a428dc396667ee68ec12785462540cff03`
- `vd55g0_patches.h`: `abfdee386588e72f237aa4975efdce68cc2bea9f23b03694a0f8371a2bfc402b`

The snapshot is intentionally unmodified in E004a. SP11-specific implementation changes must be carried as explicit later deltas. When an upstream default differs from same-machine Windows, Windows wins for the parity target.
