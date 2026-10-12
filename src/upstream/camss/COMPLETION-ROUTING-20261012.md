# Completion routing before the independent VFE680 pixel provider

Patch 0005 follows the original four CAMSS source patches. It fixes a recorded
source issue in the pinned IFE reference: CSID680 fills a completion record's
hardware and port IDs but leaves its status field unset. That field now selects
completion groups in the generic receiver. Zero initialization preserves this
RDI backend's single-output behavior until a real processed completion backend
exists. No group status, IRQ encoding or pixel provider is invented here.

The dispatcher rejects absent records and invalid hardware IDs before indexing.
The generic VFE receiver rejects invalid ports, mapped lines and output counts;
active groups must fit the 32-bit completion status before any shift. Its map and
output validation runs under the existing output lock. The older composite scan
uses one READ_ONCE mapping snapshot for both bounds and index; it does not reread
an independently changing mapping between the checks and lookup. The eventual
callback still owns its normal locking/ownership validation. This snapshot is
not a claim that late events belong to the current sensor or allocation epoch.

Valid RDI/TFE fallback, independently completed image/statistics groups and one
parameters update per completed image are retained. The actual four production
function bodies are compiled in a hosted harness; buffers, MMIO, locks and
READ_ONCE are explicit test adapters. Tests cover mixed RDI/RUP/reset events,
full/lite devices, absent records, bounded routes, output state, all legal status
bits, invalid groups and a mapping changed after the snapshot. Hosted results
cannot establish kernel concurrency or physical DMA retirement.

## Qualification

Final source candidate06 builds ARM64 CAMSS and the generic ISP helper objects
with W=1 and KCFLAGS=-Werror, zero warnings. GCC and Clang each pass 2630 hosted
cases under address/undefined sanitizers. Six real tool-input rejection cases
pass. All five patches replay onto the pinned RFC source, matching ten actual
candidate files. Patch0005 checkpatch --no-tree --no-signoff: zero errors/warnings.
No DCO/authorship or maintainer acceptance is claimed.

Candidate04 and candidate05 source/build/patches remain preserved. Candidate04
was followed by an explicit dispatch cast for hosted signedness checks;
candidate05 was followed by the reviewed single mapping snapshot. Initial
hosted adapter errors are recorded, not counted as successful runs.

The final tree is
/home/geoca/Documents/SP11-PROJECT/02-kernel/upstream-ife-base-build-20261011-01/candidate-06/source.
Exact commands, hashes and limits are in
../../../docs/UPSTREAM-CAMSS-COMPLETION-VALIDATION-20261012.json.

```sh
camss_stage=/home/geoca/Documents/SP11-PROJECT/02-kernel/upstream-ife-base-build-20261011-01
python3 tools/test-upstream-camss-completion.py --parent "$camss_stage/candidate-03/source" --candidate "$camss_stage/candidate-06/source" --cc gcc
python3 tools/test-upstream-camss-completion.py --parent "$camss_stage/candidate-03/source" --candidate "$camss_stage/candidate-06/source" --cc clang
python3 tools/test-upstream-camss-completion-pins.py --parent "$camss_stage/candidate-03/source" --candidate "$camss_stage/candidate-06/source"
```

No module was linked/loaded, no hardware experiment was started, and the daily
stack and Golden are unchanged. Neither private startup dependency is removed.
VFE680 remains RDI-only in this source candidate. Still required: exact core and
Bayer/precision setup; owned CSID/VFE/CDM/image resources; real completion/stop
acknowledgement and synchronized IRQ/work retirement; then fresh hardware
qualification with private loaders and retained carrier fallback absent.
