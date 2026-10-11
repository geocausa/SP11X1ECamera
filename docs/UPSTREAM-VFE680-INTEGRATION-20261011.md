# VFE680 integration against the pinned IFE reference

The complete October 5 posted 74-patch RFC has been recovered and replayed
against its declared base, `8d3ae59288f1e7d58d76558a6ee96d533bc5019f`.
All 325 before/after Git blob checks match the hashes in the patches. This is
source identity and application proof. The reference was not compiled, loaded
or tested on SP11, and it is not a merged or accepted interface.

The archive is pinned by `UPSTREAM-IFE-RFC-REFERENCE-20261011.json`: 369
files, covering the public HTML/mail bodies, original and normalized patches,
32 required base files and 37 resulting files. It is a touched-file source
snapshot, not a full kernel tree. Generic ISP helper dependencies carried in
patches 3..10 are included; the separate X1E PHY/DTSI series still needs its
own comparison. The original raw-mbox failures and partial archives remain.

One mail-mirror redaction changes an unchanged MODULE_AUTHOR context line in
patch 8. The original patch and failed unmodified application are retained.
The normalized copy restores that one line from the pinned base. Its pre/post
Git blob checks match. No executable code or tuning was substituted. Mail
headers/signoffs remain obfuscated: this does not authenticate author mail,
recover complete submission metadata or provide permission to sign for others.

Primary posted cover: https://lkml.iu.edu/2610.0/09021.html
Direction discussed by authors: https://lkml.iu.edu/2610.0/12136.html
No maintainer was contacted. Later revisions must be checked before submission.

## A separate author branch

The public author branch `arm64-laptops-v7.2-rc1-camss-v6-ife-bringup` is
pinned at `8fba120842097db3284f4b1c7fa7351b6cbe3f93` in
`UPSTREAM-VFE680-BRANCH-REFERENCE-20261011.json`. Comparing it to the posted
base gives a diverged history (105 ahead, 21145 behind); it is not a checkout
of the posted RFC. Eleven selected public source files are archived separately.
An initial guessed UAPI filename returned 404; the actual include path was
then retrieved, with a separate receipt. No missing-source success was claimed.

This branch enables X1E IPP declarations and supplies GPL-tagged VFE680
register headers. Its actual VFE680 operations still use the RDI write-master
mapping, an interrupt stub, no pixel line preparation, no output-group backend
and no generic parameter/statistics callbacks. It is useful source material,
not a complete SP11 ISP implementation. The generated register-header origin
requires provenance review before incorporating it in our curated submission.

All 130 addresses owned by our typed fragments have named definitions in that
public VFE680 header. `UPSTREAM-VFE680-ADDRESS-COMPARISON-20261011.json`
records every match. This confirms public address/name correspondence only;
it does not establish bit fields, channel order, ISP domain, safe defaults,
licensing clearance, frame timing or hardware behavior. Coverage remains
130 fields / 270 historical scalar occurrences, not 130 new replacements.

## Concrete backend work

| Area | Reference behavior | SP11 work before qualification |
|---|---|---|
| Lines and outputs | RFC uses output arrays, explicit write masters/planes and completion groups; PIX identity uses is_pix. | Add VFE680 image and statistics descriptors to these structures. Keep RDI support. Do not identify front/rear by requested format. |
| NV12 DMA | VFE780 programs each plane's bus client from the queued buffer; addresses use its generation's encoding. | Use actual mapped NV12 allocation, checked Y/C extents and VFE680-specific address/stride/packer rules. Never transplant VFE780 bus encodings or observed DMA addresses. |
| Processing startup | VFE780 prepares its VFE880 helper outside output_lock, before output enable/reg update. | Build an independent VFE680 module graph, black/WB/demosaic/CCM/CST/scaler/crop policy and own DMI tables. Supply actual DMA allocations/bank ownership. No private profile/schema-value fallback. |
| Parameters | Generic extensible buffers are copied/validated at prepare. Startup drains queued updates; image completion applies one update under output_lock and returns a predicted first-effect sequence. | Extend typed block validation for VFE680. Compile/allocate outside IRQ locks; commit only nonblocking prepared updates. Keep CDM/DMI objects alive through hardware acknowledgement, independently of the userspace metadata buffer. |
| Statistics | A separate group fills a managed coherent histogram buffer, then CPU copies it into generic metadata. Each output increments its own sequence when a queued buffer completes. | Add our required Bayer/row-sum/focus layouts and sizes only when documented. Establish hardware frame identity and image/statistics join under starvation/restart; equal software sequence numbers are insufficient. Audit single-buffer reuse timing. |
| Stop/error | Group stop clears WM enable; generic disable calls reset, then returns buffers. VFE680 reset/halt hooks in the references provide software completion/no extra hardware halt. | Retain/prove VFE680 physical DMA and IRQ quiescence before returning/freeing allocations or switching sensor owner. Audit all metadata/image stop orders, late completion, allocation/start failure, unbind and restart. A register write or software completion is not retirement proof. |
| libcamera | Generic metadata transport provides a framework, not sensor exposure timing or SP11 IPA integration. | Replace local QCIP/private transport with reviewed blocks; preserve asynchronous IPA behavior and relate actual sensor controls, image identity and statistics. Avoid inventing another submission ABI. |

The DMA stop, statistics timing and sequence observations above are source
review findings/integration requirements, not reproduced runtime faults in the
RFC. Our older SP11 lifecycle proofs do not automatically transfer to this tree.

## Next source changes and gates

1. Prepare a buildable isolated candidate on the pinned kernel base with the
   generic ISP helpers and existing CAMSS framework. Record full-tree and
   configuration identity; budget disk before a full source/build copy.
2. Add the smallest VFE680 output/backend changes with explicit plane/client
   descriptors, frame routing, completion status and reviewed stop ownership.
   Keep every private startup consumer disabled in the new provider path.
3. Complete source-owned minimal processing and DMI tables; extend typed
   blocks through the generic interface. The existing 656-byte fragments
   remain field tests and are not a complete hardware submission protocol.
4. Compile and review locking/error/DMA lifetime. Only then create a fresh
   single-use hardware candidate, with Golden rollback and no private fallback.
5. Qualify front first, then the distinct rear startup. Curate sensors, focus,
   regulator/DT and PHY series separately; integrate libcamera and open tuning.

Neither private runtime profile has been removed. All 14 readiness components
remain blocked. Running cameras, Golden, module trees and boot configuration
are unchanged. No capture, reboot or system suspend was performed.

## Reproduce source verification

```sh
python3 tools/verify-upstream-ife-reference.py \
  --archive /home/geoca/Documents/SP11-PROJECT/02-kernel/upstream-public-ife-20261011-05 \
  --manifest docs/UPSTREAM-IFE-RFC-REFERENCE-20261011.json --replay
python3 tools/test-upstream-ife-reference.py \
  --archive /home/geoca/Documents/SP11-PROJECT/02-kernel/upstream-public-ife-20261011-05 \
  --manifest docs/UPSTREAM-IFE-RFC-REFERENCE-20261011.json
```

The verifier checks pinned bytes before replaying patches in a temporary tree.
It does not fetch private data, run archived build scripts or change the source
archive. Nine tests cover real replay and rejection of modified/missing files,
symlinks, path escape, duplicate/incomplete pins, wrong identity and blob mismatch.
