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
