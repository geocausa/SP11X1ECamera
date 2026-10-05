# Linux camera upstreaming workflow

The research tree is optimized for hardware discovery and reproducibility.  A
Linux upstream submission should be a much smaller, reviewable result derived
from that evidence.

## 1. Re-check current upstream

Before preparing patches, verify the current state of X1E80100 CAMSS, CCI,
CSI-PHY, V4L2/media drivers, sensor drivers, and DT bindings.  Do not assume a
research snapshot from an earlier experiment is still current.

## 2. Separate generic and board-specific work

Prefer existing generic Qualcomm/media infrastructure.  If a generic driver
really needs a change, make that change independently reviewable.  Keep Surface
Pro 11 board topology, GPIO/regulator/clock/lane data, graph endpoints, and
other board-specific facts in the appropriate DT/binding layer.

Do not copy values from another laptop simply because it is also X1E80100.
Each Denali value should have a defensible provenance.

## 3. Reduce experiments to a minimal patch series

Do not submit Windows-oracle logs, extraction tooling, rejected experiments, or
large source snapshots as kernel patches.  Convert the accepted result into the
smallest upstream delta that reproduces the hardware behavior.

A typical series may separate:

1. binding/schema additions or updates;
2. generic CAMSS/CCI/CSI/sensor support, if actually required;
3. Surface Pro 11 device-tree/topology support;
4. narrowly related documentation.

## 4. Licensing and provenance

Preserve the existing SPDX expression of every modified kernel file.  For new,
fully original files, follow `LICENSING.md` and target-subsystem convention.
Preserve authorship and third-party notices.

Never manufacture another contributor's `Signed-off-by:` or
`Co-developed-by:` trailer.

## 5. Validation

Before submission, run the checks relevant to the patch set, including as
applicable:

```bash
./scripts/checkpatch.pl --strict <patches>
./scripts/get_maintainer.pl <patches>
make dt_binding_check
make dtbs_check
```

Build the affected architecture/configuration and media subsystem, then test on
the actual SP11.  Record front/rear sensor enumeration, media graph, stream
format, resolution, frame rate, power-cycle behavior, suspend/resume when in
scope, and failure/recovery behavior relevant to the change.

## 6. DCO and submission

Create commits with your own DCO sign-off (`git commit -s`), generate patches
with `git format-patch`, and use the current `scripts/get_maintainer.pl` output
to address maintainers/lists.  Follow the Linux submission guide:

https://docs.kernel.org/process/submitting-patches.html

## 7. Preserve research provenance outside the patch

The `experiments/`, `oracle/`, `docs/`, and durable state files remain useful
for proving why a patch is correct.  Link to concise public evidence when it
helps review, but keep the submitted kernel patch itself independent of
proprietary artifacts and local-only data.
