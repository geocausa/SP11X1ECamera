## Public split-PHY/platform source checkpoint, 2026-10-12

Candidate16 applies project CAMSS patches0001..0009, then12 selected public
PHY/API/platform patches. Two hunk contexts are separately rebased without
changing additions/deletions. Portable replay verifies16 changed and47 unchanged
CAMSS/ISP files;18 reference pin controls and nested-output/existing-path guards
pass. Four retained ARM64 objects pass W=1/-Werror with zero warnings. Targeted
binding examples and the disabled Denali OLED DTB pass scoped schema validation.
Full Image/modules link qualification is recorded in
docs/UPSTREAM-X1E-DEPENDENCIES-VALIDATION-20261012.json. See
../platform/X1E-DEPENDENCIES-20261012.md for reproducible ordering and limits.

The standalone PHY remains D-PHY-only. C-PHY rate audit and unchanged public
GPL reader tests are in ../phy/CPHY-RATE-AUDIT-20261012.md and
../phy/CPHY-PUBLIC-READER-20261012.md. Explicit link frequency, dynamic settle
timing and supported-rate rejection must precede the new C-PHY path. The CDM
backend remains dormant; physical retirement/provider integration are open.
No camera installation/runtime change; both private consumers/all14 gates remain.
Older checkpoints below are historical, not the current patch count.

## Latest reset checkpoint, 2026-10-12

A sixth patch now initializes CSID680 through a fresh single-command software
reset. Candidate08 builds CAMSS/generic ISP objects with zero warnings and
passes 102 hosted freshness cases plus26 actual public-reset comparisons per
compiler, five pin rejection cases and six-patch replay across ten files.
See CSID680-RESET-20261012.md. No camera/runtime consumer was changed; physical
streaming-stop and DMA retirement remain unqualified in this candidate.
The following completion and four-patch checkpoints remain reproducible history.

## Latest completion checkpoint, 2026-10-12

The original four source patches now have a fifth completion-routing patch.
Candidate06 builds the CAMSS/generic ISP objects with zero warnings and passes
2630 hosted cases per GCC/Clang, six source/patch rejection cases and five-patch
replay across ten files. It initializes CSID680 status and bounds completion
routing, including a single mapping snapshot in the unlocked composite scan.
See COMPLETION-ROUTING-20261012.md for reproduction and explicit limits.
The original candidate03 instructions below reproduce the historical four
patches. Candidate04/05 are preserved intermediate sources, superseded by06.
No pixel provider or physical stop/DMA/IRQ qualification is claimed; no runtime
consumer is removed by this fix.

# First CAMSS source series for SP11 upstream work

This four-patch series builds on the posted Oct5 2026 74-patch IFE RFC,
applied to its declared base `8d3ae59288f1e7d58d76558a6ee96d533bc5019f`.
It is a source/build candidate, with no installation or hardware qualification.
It uses public GPL kernel code and independently written changes. It does not
read private profiles or reproduce Windows tuning.

| Patch | Problem and resulting behavior |
| --- | --- |
| 0001 | Remove an unused format helper which breaks the strict warning build. |
| 0002 | Pair line/CSID completion-port reservation with port release. Give backends using `vfe_enable_v2` a paired `vfe_disable_v2`; retain write-master release for VFE17x and Gen1. |
| 0003 | Assign VFE680 RDI bus-client descriptors at subdevice initialization; use output start/update/stop callbacks. Preserve the existing ordered register writes. |
| 0004 | Update VFE17x's three obsolete output-array/write-master references after the RFC changes the common structure. |

VFE680 remains RDI-only. The existing software reset completion, halt stub,
IRQ behavior, address encoding and DMA ownership are not repaired by this
series. Clearing a software mapping is not proof that hardware stopped writing.
The series does not expose a PIX path, statistics provider or new userspace ABI.

## Evidence and limits

See `docs/UPSTREAM-CAMSS-DESCRIPTORS-VALIDATION-20261011.json`.

The full public source archive and all RFC patches were prepared in an isolated
stage. The original strict build failed on the unused helper; the first candidate
then exposed the VFE17x structure errors. Those failures persist. Candidate02
compiled but review found that its shared stop path mishandled VFE17x's allocator;
it is superseded and must not be used. Candidate03 fixes that pairing and passes
the strict ARM64 CAMSS composite and generic ISP helper object build.

The full source archive is recorded by URL, size and SHA256. The 74 RFC patches
have 325 before/after Git blob checks and 37 final touched-file pins. This does not
claim independent verification of every untouched file against the Git root tree.

The host test extracts actual production C function bodies from hash-pinned
reference and candidate source. It compares 448 ordered fake-MMIO sequences,
checks 112 descriptor plane selections, 80 mapping releases and 48 successful/
failed stops across both allocator models. GCC and Clang run with ASAN/UBSAN.
The fake locks and stop callback cannot establish kernel concurrency, physical
DMA retirement or SP11 camera behavior. Five additional tests exercise rejection
of changed/missing/symlink public source and changed patches through the real tool.
Patch replay covers all eight modified files. Gen1's common release body remains
byte-identical; VFE17x retains its legacy allocation/release pairing.

`checkpatch.pl --no-tree --no-signoff` reports zero errors/warnings. That is a
style result only. These are plain reviewable diffs, without invented DCO
sign-offs. Upstream attribution, authenticated original mail, DCO, rebase and
maintainer review remain required. No mailing-list messages have been sent.

## Reproduce on SP11

From the project checkout, use the public reference stage and candidate03:

```sh
camss_stage=/home/geoca/Documents/SP11-PROJECT/02-kernel/upstream-ife-base-build-20261011-01
camss_reference="$camss_stage/linux-8d3ae59288f1e7d58d76558a6ee96d533bc5019f"
camss_source="$camss_stage/candidate-03/source"
python3 tools/test-upstream-camss-descriptors.py --reference "$camss_reference" --candidate "$camss_source" --cc gcc
python3 tools/test-upstream-camss-descriptors.py --reference "$camss_reference" --candidate "$camss_source" --cc clang
python3 tools/test-upstream-camss-pins.py --reference "$camss_reference" --candidate "$camss_source"
perl "$camss_source/scripts/checkpatch.pl" --no-tree --no-signoff src/upstream/camss/patches/*.patch
```

For a new build, preserve existing sources/results and choose a new output
directory. The successful recorded sequence is ARM64 defconfig; enable
MEDIA_SUPPORT, MEDIA_CAMERA_SUPPORT, V4L_PLATFORM_DRIVERS, VIDEO_DEV,
MEDIA_CONTROLLER, VIDEO_V4L2_SUBDEV_API and modular VIDEO_QCOM_CAMSS with
`scripts/config --file <output>/.config`; then olddefconfig, modules_prepare,
and the object targets below. CAMSS selects V4L2_ISP automatically.

```sh
make -C "$camss_source" O="$camss_output" ARCH=arm64 -j4 W=1 KCFLAGS=-Werror drivers/media/platform/qcom/camss/qcom-camss.o drivers/media/v4l2-core/v4l2-isp.o
```

Define `camss_output` as a fresh isolated output path before using this command.
The JSON evidence records the exact tested commands/config/object hashes. This
build does not run modpost, create a complete bootable kernel or load a module.
Do not install the resulting objects as camera hardware candidates.

To prepare another full RFC source, `tools/prepare-upstream-ife-source.py`
requires a new stage, the pinned public RFC archive and manifest, at least 5 GiB
free initially and a 2 GiB reserve. It retains failed attempts and rejects source
archives containing AGENTS.md until their instructions have been reviewed.
Copy source safely before applying this project's patches; never edit shared
hardlinks in place. The descriptor test independently replays all four patches
on temporary copies of the eight touched files.

## Next implementation

1. Establish the real VFE680/CSID IPP stop acknowledgment and IRQ/work draining
   required before image, statistics and CDM/DMI allocations can be released.
2. Add bounded output groups and correctly initialized completion status without
   enabling unimplemented parameter/statistics paths.
3. Build a complete minimal startup and DMI provider from owned math and public
   functional specifications, with both private consumers and fallbacks absent.
4. Integrate generic typed parameters/statistics and image/exposure provenance.
5. Compile/review, then qualify one fresh recorded hardware candidate with
   protected Golden rollback. OS suspend/hibernate tests remain prohibited.

Both private runtime profiles and all 14 upstream-readiness blockers remain.
