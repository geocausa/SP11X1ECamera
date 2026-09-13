# E004bz — SHM-bridge ACL capability versus protected-camera requirements

## Result

**PASS: the Qualcomm SHM-bridge ABI can encode an explicit VMID/permission sharing set and Windows MemShare does not require HLOS VMID 3 to be present in that set. However SHM-bridge creation is not a memory-ownership revocation mechanism: Windows MemShare allocations remain host-virtual-addressable, Linux TZMEM deliberately keeps HLOS RW, and ownership transfer remains a separate SCM MP ASSIGN operation. Therefore SHM bridge alone cannot implement the E004bw protected external sample.**

This is static-only. No bridge was created, no SCM assignment occurred, QCOMTEE remained disabled, and no camera runtime was activated.

## 1. Exact Windows MemShare create request

`MemShareServiceSHMBridgeCreateSyscall` accepts a 0x30-byte input and a 0x10-byte output.

The input fields consumed by `SendShmBridgeCreateReqToTZ` are mechanically:

| Offset | Static meaning |
|---|---|
| `+0x00` | primary 4 KiB-aligned physical address |
| `+0x08` | optional alternate/internal 4 KiB-aligned physical address; zero falls back to primary |
| `+0x10` low u32 | 4 KiB-aligned size / base for `size_and_flags` |
| `+0x14` | VMID/permission pair count, accepted range 1..4 |
| `+0x18` | pointer to repeated `{ u32 vmid, u32 perm }` pairs |
| `+0x20` low u32 | secure-side permission bits combined with the alternate/internal PFN |
| `+0x24..+0x2f` | not consumed by this helper path in the recovered implementation |

The output contains status plus the opaque 64-bit SHM-bridge handle returned by secure world.

## 2. Windows VMID/permission packing

For every `{vmid, perm}` entry Windows builds the four raw SCM arguments.

### VMID 3 / HLOS

If `vmid == 3`, the function:

- marks that HLOS was present;
- places HLOS permission bits into `size_and_flags` as `(perm << 2) | 2`;
- removes HLOS from the count of separately packed non-HLOS VMIDs.

### Other VMIDs

For non-HLOS VMIDs:

- VMIDs are packed 16 bits at a time into the fourth SCM argument;
- their permission values are packed three bits at a time into low bits of the primary-PFN argument.

Finally Windows constructs the four arguments and calls SMC `0x02000c1e`.

The important structural result is that **VMID 3 is optional**. There is no check requiring the VMID list to contain HLOS; only the overall list count must be 1..4.

This proves that the raw firmware ABI can describe bridge configurations other than the current Linux convenience wrapper's fixed HLOS sharing pattern.

It does not prove those configurations are authorized for camera buffers.

## 3. Omitting HLOS from the bridge request does not revoke HLOS access

This distinction is decisive.

QcTrEE's `MemShareServiceAllocSyscall` allocates from the Windows TrEE host memory arena through `AllocMemFromTreeSMB`.

That allocator returns both:

- a normal host virtual address;
- a physical address obtained from that virtual address with `MmGetPhysicalAddress()`.

The virtual address remains part of the allocation record until `FreeMemFromTreeSMB` releases the allocation.

The SHM-bridge create routine receives those physical addresses but does not unmap or invalidate the host virtual address, and it does not invoke the MP memory-assignment command.

Therefore a bridge ACL describes secure-world/non-secure sharing access. It is **not** evidence that the original Windows host mapping has been revoked merely because VMID 3 was omitted from a requested bridge list.

In security terms:

`not listed in bridge sharing set != ownership revoked`

## 4. Linux TZMEM wrapper deliberately retains HLOS RW

Linux's higher-level `qcom_tzmem_shm_bridge_create()` builds:

- `pfn_and_ns_perm = paddr | QCOM_SCM_PERM_RW`;
- `ipfn_and_s_perm = paddr | QCOM_SCM_PERM_RW`;
- `size_and_flags = size | (1 << 9)`;
- `ns_vmids = QCOM_SCM_VMID_HLOS`.

So the current Linux TZMEM use case deliberately establishes a bridge in which normal HLOS remains an RW participant.

This is exactly appropriate for QCOMTEE message/shared memory, where Linux retains the `tee_shm` kernel address, but it is the wrong protection class for E004bw's external protected camera sample.

## 5. Raw Linux SCM has the transport, but not a camera policy helper

Linux also exposes the lower-level:

`qcom_scm_shm_bridge_create(pfn_and_ns_perm_flags, ipfn_and_s_perm_flags, size_and_flags, ns_vmids, handle)`

which forwards all four packed arguments directly to the same MP SHM-bridge create command.

Thus Linux is not prevented by its SCM transport from expressing something more specialized than TZMEM's fixed HLOS wrapper.

But the current kernel has no camera-specific helper that authoritatively constructs the Windows-style arbitrary VMID/permission form, and there is no source authority defining the valid camera bridge ACL.

Using the raw call with guessed packing would therefore be mechanism-driven rather than oracle-driven.

## 6. SHM bridge and memory ownership assignment are separate firmware operations

Linux makes this separation explicit:

- SHM bridge create/delete use MP commands `0x1e` / `0x1d`;
- `qcom_scm_assign_mem()` uses separate MP command `QCOM_SCM_MP_ASSIGN = 0x16`.

The QcTrEE MemShare implementation likewise contains no `AssignMemoryToSocDomain`, CP_CAMERA, or memory-assignment call.

This explains why E004bt and E004by cannot be collapsed:

- **ASSIGN** controls memory ownership/VMID ACL state;
- **SHM BRIDGE** registers/shares a physical region with secure world and returns a bridge lifetime handle.

A protected camera backend might eventually need both classes of primitive, but their composition must be proven rather than assumed.

## 7. What the opaque bridge handle can and cannot represent

The SHM-bridge handle has a real create/delete lifetime and is therefore a plausible **backend resource handle**.

It is not by itself the E004bw external sample identity because the bridge API carries no Windows-equivalent:

- request ID;
- allocated versus captured extent distinction;
- serialized metadata extent;
- pixel payload offset;
- trusted-worker object identity;
- consumer-facing secure sample identity.

Those remain separate contract state even if a future provider internally uses a bridge handle.

## 8. Windows parity boundary remains unchanged

The actual Windows external camera sample is an **IUM VTL1 secure section** created by the Windows media stack/FsIso path and opened by the SecureISP VTL1 trustlet.

SecureISP does not use QcTrEE MemShare for that object.

Therefore E004bz does not reinterpret MemShare as the Windows camera provider. It only establishes which lower-level Qualcomm primitive Linux already has available if a future Linux provider is proven to need it.

## Architectural consequence

We can now separate four mechanisms cleanly:

1. **protected sample abstraction** — E004bw contract;
2. **memory ownership ACL** — SCM MP ASSIGN;
3. **secure-world sharing registration** — SCM MP SHM BRIDGE;
4. **trusted execution/object transport** — QTEE SMCINVOKE.

All four mechanisms exist in some form. None by itself supplies the missing camera provider authority.

The useful result is that the Linux implementation does **not** need a new proprietary transport layer. It needs a provider/policy binding over already-existing primitives, but only after the correct signed camera authority is identified.

## What remains forbidden

Do not yet:

- create a raw SHM bridge with custom VMIDs;
- interpret omission of HLOS from a bridge list as memory protection;
- combine SHM bridge and `qcom_scm_assign_mem()` experimentally;
- use CP_CAMERA or TZ VMIDs by guess;
- enable QCOMTEE;
- register a secure-video-record heap;
- activate protected camera runtime.

## Next gate

The next highest-value gate is **E004ca — external VTL1 secure-section protection semantics versus Linux primitives**, static first.

Return to the Windows oracle and answer the missing provider question from the side that actually owns the sample:

1. trace the FsIso/MFPlat/IUM external secure-section creation contract beyond identity/lifetime into its protection attributes;
2. determine whether the IUM secure section is VTL1-only, shared with a named trustlet/scenario, or backed by another domain policy;
3. identify what operation makes it inaccessible to ordinary VTL0 CPU code;
4. distinguish secure-section scenario authorization from physical-page ownership assignment;
5. compare that protection shape against Linux's ASSIGN, SHM-bridge and protected DMA-BUF primitives without executing them;
6. only then decide whether Linux needs a new provider implementation or can compose existing primitives under a proven policy.
