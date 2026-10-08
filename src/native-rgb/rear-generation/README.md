## 2026-10-08 rear generation04 sensor start; generation05 transport fix ready

Generation04 accepted packet0/1 and started OV13858, then first Epoch0 timed out.
No completed stream; Golden1986da69-9b65-4018-ab78-9856c44882b7 returned automatically.
No observed kernel hazard/watchdog. Identity04 retired, services disabled.
Old fault dma_pin flag was incomplete telemetry: exposed DMA/PM/owner remained
held through reboot. Stop helpers were attempted; their physical success is unproven.
Main rear path lacked receiver lane/decode/drop/EPOCH initialization after reset.
New source helper derives exact Linux route/format and writes15 transport fields
before packet0, excluding packet-owned crop/format/subsample/RUP/IRQ ACKs.
GCC+Clang ASAN/UBSAN86 assertions/20 negatives verify scope. Sourcebuild07
W1/Werror all3 modules zero diagnostics; pinning2452 assertions/52 steps/51 failures
per compiler. Complete-success stop helpers called once; all DMA retained until reboot.
Candidate-only read-only CSI/IPP snapshots will establish physical transport state.
Root/actual119-edge graph preflight and12 negatives PASS. No rear NV12/quality proof.
Evidence docs/NATIVE-RGB-REAR-GENERATION-04-20261008.json and
docs/NATIVE-RGB-REAR-GENERATION-05-PREP-20261008.json.
Native44 completed streams/37 IDs/74 boots; failed started captures6.
Windows2/2/4; combined39 IDs/78 boots. Generation05 not installed/armed yet.
NEXT install, verify and boot fresh05 autonomously, inspect transport and frame events.
Rear FIRST; front calibration deferred; same-SP11 optical/tuning privacy unchanged.
Earlier status entries below are historical.

## 2026-10-08 generation03 reached kernel trigger; exact video link fixed

Generation03 made one kernel trigger. Hook rejected ENOLINK before composition,
command DMA/owner acquisition or sensor start: legacy required-PIX-video check
used first enabled remote pad, but immutable stats precedes immutable video.
Current main-path integration now locates exact required enabled IMMUTABLE
video link, with source/sink direction and identity checks. Metadata fan-out
allowed without relying on list order. Pinned52 historical parents unchanged;
new helper and consumer derivative separately pinned. GCC+Clang ASAN/UBSAN19
helper assertions each include both orders and missing/disabled/wrong edges.
Fresh generation04 sourcebuild06 W1/Werror zero diagnostics; pinning2278/52
failures per compiler and root/real-graph12 negatives PASS.
Golden c3c024ab-ae34-4ebf-9441-724ae01af5ab returned automatically unchanged,
no hazard/watchdog; consumed03 retired/services disabled, zero new streams.
Evidence docs/NATIVE-RGB-REAR-GENERATION-03-20261008.json and
docs/NATIVE-RGB-REAR-GENERATION-04-PREP-20261008.json.
Native44streams/36IDs/72boots;Windows2/2/4;combined76boots/38IDs.
NEXT install/verify/boot fresh04 autonomously, retain all exposed DMA through reboot.
Rear FIRST; front calibration deferred; same-SP11 optical/tuning privacy unchanged.
Earlier status entries below are historical.

## 2026-10-08 generation02 route configured; source-width preflight corrected

Generation02 loaded all3 sensors bound/idle and exact rear PIX-only119-edge
graph, then stopped before trigger/sensor start. Generic VFE PIX source crops
4076 input width to16-aligned4064; worker incorrectly expected4076 everywhere.
Actual boot graph now validates in source regression. VFE graph source4064x2806
is diagnostic negotiation, NOT pixel output; native profile ISP crop4064x2286
and full output3840x2160 remain independent. No optical quality/NV12 claim.
Golden5e09eb64-8675-4128-9533-6befb088f52c returned automatically unchanged,
no hazard/watchdog. Generation02 consumed/retired and services disabled.
Fresh generation03 sourcebuild05 W1/Werror zero diagnostics, GCC+Clang2278
assertions/52 failures, actual rear graph+root service environment and12 negatives PASS.
Evidence docs/NATIVE-RGB-REAR-GENERATION-02-20261008.json and
docs/NATIVE-RGB-REAR-GENERATION-03-PREP-20261008.json.
Native44streams/35IDs/70boots;Windows2/2/4;combined74boots/37IDs.
NEXT install/verify/boot fresh generation03 autonomously; retain DMA until reboot.
Rear FIRST; front calibration deferred; same-SP11 privacy unchanged.
Earlier status entries below are historical.

## 2026-10-08 generation01 retired before modules; fresh generation02 prepared

Generation01 returned automatically to Golden602875be-51f9-4a06-9e6e-4c676548f9da.
Worker consumed identity but Git rejected root-service repo ownership before
camera module load. Zero sensor starts/streams; no kernel hazard or watchdog.
Reproduced in clean HOME=/root environment. Fix trusts only this exact repo in
each subprocess environment; no global Git exception. Clean root runner/guard
preflight now PASS. Fresh sourcebuild04/generation02 W1/Werror zero diagnostics,
GCC+Clang2278 orchestration assertions/52 injected failures and12 graph negatives PASS.
All exposed DMA/PM/owner remain pinned until mandatory Golden reboot.
Evidence docs/NATIVE-RGB-REAR-GENERATION-01-20261008.json and
docs/NATIVE-RGB-REAR-GENERATION-02-PREP-20261008.json.
Native44streams/34IDs/68boots;Windows2/2/4;combined72boots/36IDs.
NEXT install/verify/boot fresh generation02 autonomously. Never retry01.
Rear FIRST; front calibration deferred; same-SP11 optical/tuning privacy unchanged.
Earlier preparation/status entries below are historical.

# Rear generation and stop diagnostic

This isolated build connects the current typed rear startup composer to the
single-use E008N wrapper and actual E008K hardware runner. It requests two rear
generations with all ten output/statistics write masters. It does not request
userspace pixel buffers or claim NV12 or optical quality.

The one-use V4L2 boolean control exists only with the diagnostic module parameter.
It provides no configuration, commands or DMA addresses. The kernel reads a
fixed, size-checked and SHA-pinned private data-only input prepared from the
actual built libipa and validated clean source algorithms. The compiler-bound
native structure is a diagnostic transport, not a release firmware format or UAPI.
Private tuning, input bytes and their digest stay on this SP11.

Every exposed return holds output/command DMA, PM and ownership until reboot.
Even complete generations and successful stops return EINPROGRESS with no DMA
reclaim. A one-shot service and independent 90-second watchdog return to unchanged
Golden; consumed identities are never retried. Default production authorization
remains denied outside the isolated diagnostic.

Source build01 failed a READ_ONCE on a vb2 bitfield. Build02 compiled but review
found the shared PIX format table still admitted front RGGB only. Build03 retains
that default and adds rear GRBG in the isolated table. It passed W1/Werror for all
three modules with zero diagnostics. Source attempts were never installed/armed.
The runner now accepts media-ctl's stream-zero format spelling and rejects other
streams, wrong Bayer order/geometry and incomplete/fan-out routes.

GCC and Clang ASAN/UBSAN each passed 2278 orchestration assertions and 52 injected
failures. Lifecycle/IRQ helpers and DMA allocations are host models. The retained
actual 119-edge/45-node media graph passed neutral/rear PIX admission and 12
negative cases; probe compiled with Werror. These are preflight checks, not
physical completion or image-quality evidence.

Build, private input generation and installation are separate scripts. Installation
requires a clean checkpoint and idle Golden, verifies source/module/Golden assets,
creates a fresh identity, and leaves it unarmed. Hardware identity
E-NATIVE-REAR-GENERATION-01 is consumed only by its boot worker.

The product path remains native Linux sensors/Qualcomm ISP plus standard libcamera
pipeline/IPA. This diagnostic one-shot is engineering tooling, not a product daemon.
