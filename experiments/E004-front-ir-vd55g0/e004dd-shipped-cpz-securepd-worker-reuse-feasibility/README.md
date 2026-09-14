# E004dd — shipped CPZ/SecurePD worker reuse feasibility

## Result

**PASS / route closed: the exact SP11 CDSP package contains several trusted modules with pieces of the required behavior, but no already-trusted, currently exposed entrypoint reproduces the Windows protected-frame transfer contract. The closest mmap+memcpy implementation is trapped behind an unexposed example runner function; the callable SecurePD and benchmark APIs perform Gaussian/benchmark work; sysmon's copy APIs export sysmon-owned data rather than copy arbitrary protected source to destination. A camera-parity worker therefore still requires a production-approved trusted worker image or equivalent admitted code path.**

This is static-only. No CPZ or camera runtime was activated.

## 1. Search scope

E004dd enumerated the exact qccdsp root static-hash policy names and compared them with every installed same-package Hexagon shared object. It then inspected all normal `*_skel_handle_invoke` / `*_skel_invoke` exports plus transfer-relevant internal symbols.

The trusted module set includes the SecurePD examples, benchmark, sysmon, CRM, stability, Q6 manager, and support libraries.

## 2. `example_image_runner.so`: right primitive, wrong reachable entry

This is the strongest code-reuse candidate.

Its `example_algo_run` operation 1 already performs essentially the desired low-level transfer shape:

`fd map -> cache invalidate -> second map -> memcpy -> cache clean -> release/unmap`.

However, the proven SecurePD dynamic loader resolves the fixed symbol `algo_main`, not arbitrary exported functions. Fresh decompilation of this module's `algo_main` shows it launches a thread named `sec_gaussian` and explicitly reports Gaussian processing.

`example_image_runner.so` exports no normal skel invoke handler, and no host-side `example_algo_run` caller/stub exists elsewhere in the captured SP11 driver store.

Therefore the trusted bytes contain a useful copy implementation, but the copy operation is not reachable through the established production invocation surfaces.

## 3. `libloadalgo_skel.so`: correct bridge, wrong algorithm

`libloadalgo_skel.so` is callable and is excellent authority for the FastRPC-to-SecurePD bridge. It passes mapped buffer physical identity to the protected worker through typed mailbox messages.

But its exposed algorithm is the SecurePD Gaussian example. It does not expose generic copy, 0x80 tail fill, SWABF, or SWASF.

So it can teach us how to deliver protected memory to a worker, but it cannot replace the worker logic.

## 4. `libbenchmark_skel.so`: broad processing surface, no generic transfer RPC

The trusted benchmark module exposes a large skel-dispatched image-processing API: dilation, integration, Gaussian, bilateral filtering, convolution, FFT, histogram, NCC, Sobel, and others.

The binary also contains internal utilities named `addTwoVectorsTogether` and `Vmemset`. Fresh decompilation of the complete `benchmark_skel_handle_invoke` dispatcher shows neither is a remotely selectable method. There is no generic source-to-destination copy or caller-selected fill RPC in the skel surface.

Using a different filter merely because it is trusted would not be Windows parity and would corrupt the frame semantics.

## 5. `libsysmon_skel.so`: apparent copy path is not arbitrary-buffer copy

This module initially looked promising because it remotely exposes:

- `sysmon_usermode_buffer_copy(output_buf, output_buf_size, size_copied)`;
- `sysmon_usermode_npu_buffer_copy(output_buf, output_buf_size, size_copied)`.

DWARF and Hexagon disassembly resolve the ambiguity. Both APIs have only one caller-provided buffer and forward it to internal QDI operations. They copy sysmon/NPU-owned data **out** to that buffer; the caller cannot supply an arbitrary protected source.

The module's `memtest_memcpy` and `memtest_memset` are also unsuitable. They allocate their own test buffers and benchmark memory operations rather than operating on the camera's two protected objects.

## 6. Remaining trusted modules

CRM, stability, Q6 manager, sysmon-query/domain/throttle, and version modules expose no relevant camera transfer surface.

A direct token scan across the trusted package finds no `SWABF`, `SWASF`, `ISPTRUSTLET`, or protected internal/external image-copy diagnostics. Those exact behaviors remain present in the Windows `QcISPTrustlet8380.dll` oracle.

This negative result is meaningful because it prevents us from forcing a superficially similar trusted module into the design and silently losing 1:1 parity.

## 7. Architecture after E004dd

The stack is now much less ambiguous:

- E004db: real protected dma-buf/FastRPC map and unmap lifetime is bounded;
- E004dc: real CPZ/SecurePD trusted-worker environment and protected-buffer ABI are bounded;
- E004dd: existing shipping callable modules do **not** provide the complete parity algorithm.

The remaining blocker is specifically **trusted admission of the parity worker implementation**. It is not a memory-provider problem and not a generic CPU-worker feasibility problem anymore.

## Safety boundary

SP11 stayed on Golden FullIO v19c with empty `next_entry`. No secure CB9 activation, FastRPC ioctl, ownership transition, CPZ migration, SecurePD worker launch, camera runtime, Windows boot, or Linux SecureISP runtime occurred.

## Next gate

**E004de — production CPZ/SecurePD worker trust-admission feasibility**, static first.

Determine whether the exact Qualcomm production policy exposes any source-controlled, legitimate path to admit a parity worker without weakening security:

1. identify where `/statichashes/*` policy data originates and how it is authenticated;
2. distinguish immutable/root-image trust data from externally supplied configuration;
3. inspect signed-module / TCG / certificate requirements for dynamic SecurePD ELFs;
4. determine whether the platform supports a development/manufacturer-authorized signing route available to this device;
5. if no authorized source-controlled admission path exists, close it explicitly rather than bypassing verification.

Do not patch verification, modify trusted firmware, launch CPZ, or execute an unsigned worker during this gate.
