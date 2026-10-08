# Rear public V4L2 buffer integration

Rear23 proves two 4K native NV12 generations and clean output/ledger/owner/PM/
command release on physical SP11. The public video queue is not connected yet.

native-rear-video-dma.inc validates an ACTIVE VB2 buffer on the exact VFE1 PIX
endpoint and exact single-plane NV12 format. It walks every DMA-mapped SG entry,
uses mapped nents rather than orig_nents, rejects gaps/overlap/zero length/
32-bit overflow and checks the complete advertised plane fits. The output is
published only after all checks pass. It ignores cached buffer addr[0].
It neither maps CPU pixels nor writes MMIO, allocates, frees, completes a buffer
or grants hardware ownership.

The pure arithmetic and actual adapter pass GCC/Clang ASAN/UBSAN/Werror tests:
658 assertions, 155 negative cases and 64 valid mapped-segment partitions each.
The optional linear overlay compiles this adapter in a fresh source-only ARM64
build with three modules, W1/Werror, zero diagnostics. It installs no callback.
Evidence: docs/NATIVE-RGB-REAR-V4L2-DMA-ADMISSION-20261008.json.

Next connect an explicitly borrowed public FULL surface to the ten-WM ledger,
keeping auxiliary and command allocations independently owned. Retain the
actual VB2 mapping through hardware stop on every cancellation/close/failure
path; never pass borrowed output through dma_free_coherent. Then connect the
ordinary streaming worker/queue and rear-specific libcamera configuration and
typed semantic IQ. The one-use diagnostic and private compiled profile are
validation tools, not the production camera API. Continuous frames, metadata
pairing and matched-scene optical quality require physical application tests.

build-once.py creates a fresh external build path and never installs or boots.
Consumed/source build paths must not be overwritten; select a fresh suffix for
the next source revision. Run test-video-dma.py against that staged tree.
