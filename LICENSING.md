# Licensing and provenance

Unless a file says otherwise, original material authored specifically for this
repository is licensed under the **BSD-2-Clause** license in `LICENSE`.

That means project-owned code, documentation, analysis, and tooling may be used,
modified, and redistributed, including commercially, provided the BSD
copyright/license notice is preserved.

## geoca contribution grant

To make future Linux upstreaming unambiguous: to the extent a contribution in
this repository is an original copyrightable contribution by **geoca**, it may
be reused, modified, redistributed, and submitted upstream under the license
expression that governs the destination kernel file.

For independently authored standalone project material that is not derived
from third-party code, BSD-2-Clause also applies unless a file-level notice
states otherwise.

This grant applies only to geoca's contributions and does not alter third-party
rights.

## Future Linux kernel files and patches

This repository currently contains research/tooling rather than a blanket
relicensed Linux source tree.  When kernel code is added:

- changes to an existing Linux file must preserve that file's existing
  `SPDX-License-Identifier` expression;
- a new, fully original kernel file should normally use
  `GPL-2.0 OR BSD-2-Clause` when the target subsystem accepts that expression
  and no incompatible source material was used;
- otherwise use the license expected by the target subsystem, commonly
  `GPL-2.0`;
- genuine UAPI headers must follow the kernel's UAPI licensing guidance,
  including `Linux-syscall-note` only where appropriate;
- place SPDX identifiers at the first possible line (second line for a script
  whose shebang must be first).

Linux kernel licensing rules:
https://docs.kernel.org/process/license-rules.html

## Reverse-engineering provenance

The project intentionally uses Windows on the same SP11 as a behavioral and
hardware oracle.  Evidence such as hardware IDs, observed sequences, timings,
register values, hashes, and independently derived descriptions may inform a
new Linux implementation.

Do not copy proprietary Microsoft, Qualcomm, camera-vendor, or other third-party
source code into this repository.  Do not commit proprietary drivers, firmware,
DLLs, SYS files, tuning binaries, dumps, or similar payloads merely because they
were used as local evidence.

Where public open-source material is used as a reference or adapted, preserve
its copyright/license notices and record the exact source/revision.

## Existing tooling references

`tools/aeob_decode.py` records that its format behavior was informed by the
MIT-licensed WOA-Project/AeoBUtils project and that this repository's Python
implementation was independently written.  Preserve that provenance note.  If
future work copies or adapts copyrightable code from that or another project,
carry the applicable upstream license notice with the copied/adapted material.

## Attribution

For BSD-2-Clause material, redistribution must retain the copyright notice,
license conditions, and disclaimer.  Existing third-party author notices must
also be preserved.

## DCO is separate

A repository license is not a Linux kernel `Signed-off-by:`.  Kernel-bound
patches must separately comply with the Developer's Certificate of Origin, and
each signer must provide their own sign-off.

See `CONTRIBUTING.md` and `UPSTREAMING.md`.
