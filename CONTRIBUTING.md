# Contributing

Contributions are welcome.  The repository is evidence-driven and is intended
to produce Linux camera support that can ultimately be reviewed upstream.

## Rights and provenance

Only contribute material you have the right to submit.  Preserve existing
copyright, attribution, and SPDX notices.  For adapted open-source material,
record the upstream project, exact revision, source path, and license.

Do not commit proprietary Windows/Qualcomm/vendor binaries, firmware, tuning
payloads, credentials, memory dumps, or other material whose redistribution
rights are unclear.  Document hashes, observations, and lawful reproduction
steps instead.

Read `LICENSING.md` before changing any license header.

## Developer Certificate of Origin

Kernel-bound changes must comply with the Linux Developer's Certificate of
Origin.  Sign commits you are entitled to certify with:

```bash
git commit -s
```

Never invent or copy another person's `Signed-off-by:`.  Use
`Co-developed-by:`, `Reviewed-by:`, `Tested-by:`, `Acked-by:` and related
kernel trailers only when the named contributor has actually provided or
clearly authorized them under kernel process rules.

Kernel submission guidance:
https://docs.kernel.org/process/submitting-patches.html

## Clean-room discipline

Windows and vendor components may be used as an evidence source for observable
hardware behavior, formats, timings, identities, and interfaces.  Linux code
submitted here should be independently written from that evidence and public
open-source documentation/source.  Do not paste decompiled or proprietary
vendor source into candidate Linux patches.

## Kernel-facing changes

For work intended for Linux upstream:

- rebase the accepted result onto an appropriate current upstream kernel tree;
- preserve target-file SPDX expressions;
- keep each patch focused on one logical change;
- use existing CAMSS/CCI/V4L2/media infrastructure where technically correct;
- put board-specific topology in the appropriate DT/binding layer rather than
  hard-coding it into generic drivers;
- update DT bindings/documentation when required;
- run relevant builds, schema checks, `scripts/checkpatch.pl`, and hardware
  tests before submission.

## Evidence

Tie hardware claims to reproducible evidence: device identities, logs, hashes,
resource packages, captures, register/state observations, or repeated tests.
Mark hypotheses as hypotheses and keep rejected experiments in the research
history rather than smuggling them into a final patch.
