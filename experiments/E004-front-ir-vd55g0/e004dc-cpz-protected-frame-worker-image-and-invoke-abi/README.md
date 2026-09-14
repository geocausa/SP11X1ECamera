# E004dc — CPZ protected-frame worker image and invoke ABI

## Result

**PASS: the exact SP11 CDSP stack contains a real Qualcomm SecurePD/CPZ worker architecture with a concrete protected-buffer mailbox ABI, trusted physical-buffer verification/mapping, static and dynamic worker launch modes, and a shipped mmap+memcpy worker primitive. However, the camera-parity worker itself is not yet admitted: production CPZ migration is disabled in the unsigned shell, dynamic SecurePD modules are signature/static-hash gated, and no shipped module has yet been proven to implement or expose the Windows SWABF/SWASF protected-frame algorithm.**

This gate is static and layout-compile-only. Nothing was loaded or executed on CDSP.

## 1. CPZ is a production/signed-shell capability

The exact SP11 package ships both `fastrpc_shell_3` and `fastrpc_shell_unsigned_3`.

In the production shell:

`fastrpc_migrate_cpz -> fastrpc_uprocess_migrate_cpz`

is a real migration path. The migration routine reaches CPZ physical-map handling and protected-process setup.

In the unsigned shell, the identically named `fastrpc_migrate_cpz` entry simply returns error `0x80000414`.

So an ordinary unsigned FastRPC process cannot be treated as a CPZ process merely because the host selects a different context bank.

## 2. SecurePD dynamically loaded code is trusted code

The exact Golden qccdsp image contains a full secure dynamic-loader verification surface, including signature verification and static-hash policy.

It also contains named static-hash policy entries for the shipped example stack:

- `/statichashes/example_image.so`
- `/statichashes/example_image_runner.so`
- `/statichashes/libloadalgo_skel.so`
- `/statichashes/libbenchmark_skel.so`
- `/statichashes/fastrpc_shell_3`
- `/statichashes/fastrpc_shell_unsigned_3`

Fresh Ghidra recovery shows the loader tracks signed, signature-valid, and static-hash-found state. Its parser has a reachable explicit rejection path for an unsigned dynamic module.

This closes an important ambiguity from E004db: **a source-built camera worker cannot simply be copied to CDSP and launched inside CPZ.** It needs an accepted trust path.

The static-hash node names are security-policy evidence; E004dc does not claim their stored values equal ordinary whole-file SHA-256 digests.

## 3. Qualcomm ships the SecurePD reference architecture on this machine

The Windows CDSP package includes unusually useful, debug-bearing Qualcomm SecurePD example modules:

- `libloadalgo_skel.so` — proxy/control side;
- `example_image.so` — protected worker side;
- `example_image_runner.so` — example runner including fd mapping/copy tests.

Their embedded source paths identify the implementation as Qualcomm's `cdsp_proc/platform/securepd/example/...` code, not an unrelated third-party library.

The root qccdsp image independently embeds the corresponding SecurePD loader support.

## 4. Exact protected-buffer type ABI

DWARF recovers `buffer_type_ext` exactly:

| Value | Meaning |
|---:|---|
| 4 | ALGO |
| 5 | HEAP |
| 6 | POOL |
| 7 | DATA |
| 8 | STATIC_EXEC |

The proxy's generic protected-buffer message is `loadalgo_packet_t`, exactly 12 bytes:

- `+0x00` — 32-bit DSP physical address;
- `+0x04` — length;
- `+0x08` — buffer type.

The recovered structures are encoded in `scaffold/sp11-securepd-worker-abi.h`; all recovered sizes/offsets pass compile-time assertions.

## 5. The proxy passes FastRPC buffer identity into SecurePD

`libloadalgo_skel.so::loadalgo_physbuffer` proves the handoff shape:

1. resolve the FastRPC fd-backed mapping with `HAP_mmap_get`;
2. obtain the corresponding DSP-side physical-buffer identity;
3. form `{paddr, len, type}`;
4. send it over `proxy_to_secure_mb`;
5. wait on `secure_to_proxy_mb`;
6. receive success/failure from the protected worker side.

That is the missing bridge between E004db's host `MEM_MAP` result and a protected worker protocol: Qualcomm's own same-machine SecurePD design converts a mapped FastRPC buffer into a typed physical-buffer mailbox transaction.

## 6. SecurePD verifies before trusted CPU mapping

`example_image.so` is a real protected worker image. It imports:

- `get_secure_channel_handle`;
- `dsc_verify_buffer`;
- `secure_pd_mapping_create_64` / `secure_pd_mapping_delete_64`;
- secure mailbox and thread APIs.

Its `algo_main` launches the `sec_gaussian` worker. The worker receives a 96-byte image packet, verifies source and destination physical ranges against the DSC secure channel, creates mappings only after verification, performs CPU image work, removes mappings, and replies through the mailbox.

This is the strongest same-machine proof yet that the CPZ/SecurePD habitat can satisfy the E004cf requirement: trusted CPU code can simultaneously operate on protected source/destination memory without making those mappings ordinary HLOS pointers.

## 7. The image-processing message shape is already suitable

Qualcomm's recovered `gaussian7x7_packet_t` is 96 bytes and contains:

- source protected-memory handle;
- width;
- height;
- source stride;
- destination protected-memory handle;
- destination stride;
- heap/scratch protected-memory handle.

Each `mem_handle` contains fd, size, 64-bit mapped address and ION/fd state.

This is not the Windows camera ABI, but it proves that geometry plus multiple protected memory objects is a normal SecurePD message shape. A parity worker does not need a fundamentally new communication mechanism.

## 8. SecurePD exposes static and dynamic worker admission modes

The qccdsp root loader's `process_msg` state machine distinguishes at least two worker-execution routes.

**STATIC_EXEC (8)** starts a built-in worker thread. The exact root image contains the static Gaussian `algo_main`/`sec_gaussian` implementation used by this path.

**ALGO (4)** accepts a protected algorithm image only after its buffer is registered with the secure channel and the channel has reached the expected data-loaded state. It maps the ALGO backing, treats it as `sec_algo.elf`, resolves symbol `algo_main`, and launches it in a new thread. The secure dynamic loader's signature/static-hash policy applies to that image.

So source-controlled worker logic is mechanically plausible, but worker **admission** is the blocker: an arbitrary unsigned ELF is not accepted by the production route.

## 9. A shipped mmap+memcpy worker primitive already exists

`example_image_runner.so::example_algo_run` has an especially relevant operation-1 path:

`HAP_mmap_get`
→ cache invalidate
→ `HAP_mmap2`
→ `memcpy`
→ cache clean
→ `HAP_mmap_put`
→ `HAP_munmap2`

The module's own diagnostics explicitly describe retrieving one buffer from an fd, mapping a second, copying between their VAs, then releasing/unmapping them.

That is extremely close to the Windows early-copy branch at the execution level.

But there is an important boundary: a complete driver-store search found the `example_algo_run`/`example_algo_open` symbols only inside `example_image_runner.so` itself, and the module does not expose a normal `*_skel_handle_invoke` entry. E004dc therefore does **not** claim the camera can invoke this operation today.

## 10. It is not the Windows camera worker

The Windows `QcISPTrustlet8380.dll` still contains the actual parity behavior:

- `ImageProcessingModule_SWABF`;
- `ImageProcessingModule_SWASF`;
- direct protected internal/external buffer copies;
- the synthetic/copy transfer modes already extracted in E004cf.

That trustlet has no static references to FastRPC, CDSP, `libloadalgo_skel.so`, `example_image.so`, or `example_image_runner.so`.

The Qualcomm SecurePD examples are therefore **architecture and reusable-code candidates**, not evidence that Windows itself uses CDSP for its current protected camera transfer.

## 11. What is now proven

E004dc closes the worker-habitat ABI question at the mechanical level:

- CPZ has a real production migration path;
- unsigned FastRPC shell cannot enter it;
- SecurePD has typed protected-memory mailbox messages;
- protected physical ranges are DSC-verified before worker mapping;
- multiple protected buffers + geometry are supported;
- ordinary CPU work occurs inside the protected worker;
- a shipped trusted module even contains an fd-map + memcpy primitive;
- dynamic custom worker images are trust/signature/static-hash gated.

The remaining question is no longer “can CDSP/CPZ host a protected CPU worker?” The answer is yes. The question is **whether an already trusted/shipped entrypoint can be reused to implement exact camera transfer semantics without requiring a new signed worker image.**

## Safety boundary

SP11 remained on Golden FullIO v19c with empty `next_entry`. No secure CB9 was enabled, no FastRPC ioctl was issued, no ownership transition occurred, no CPZ migration or SecurePD worker launch was attempted, and no Linux camera/SecureISP runtime ran.

## Next gate

**E004dd — shipped CPZ/SecurePD worker reuse feasibility**, static first.

Search only already trusted same-machine modules/entrypoints for a mechanically reachable route that can reproduce the Windows transfer contract:

- direct byte copy;
- UV/tail fill where required;
- SWABF/SWASF-equivalent pixel transformation or a sufficient generic processing primitive;
- source/destination protected mapping;
- completion before E004db MEM_UNMAP;
- no HLOS CPU-visible fallback.

If no such shipping entrypoint is reachable, close that route explicitly and leave the remaining blocker as worker signing/trust admission rather than weakening the protection model.
