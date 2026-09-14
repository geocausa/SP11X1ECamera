# E004df — parity worker admission alternatives, architecture closure

## Result

**PASS / ARCHITECTURE CLOSED: among the locally proven SP11 mechanisms, CPZ/SecurePD remains the only architecture that satisfies the protected camera memory/worker shape without exposing pixels to HLOS. Its memory, mapping, context-bank and worker habitat are now mechanically bounded, but the exact camera-parity worker cannot be admitted under the production trust policy with the credentials/material available to this project. Other candidate trusted habitats fail earlier on camera ownership, DMA/IOMMU authority, loader/service identity or boot-chain coupling.**

This does not abandon the CPZ design. It freezes runtime activation and separates two tasks cleanly:

1. keep the parity worker implementation source-controlled and testable **offline**;
2. require a legitimate production admission route before any protected runtime.

## 1. CPZ is still the technically correct target

The CPZ route now has uniquely strong same-machine authority:

- camera internal memory can be owned by `CP_CAMERA + CP_CDSP`;
- external sample can be owned by `CP_CDSP` only;
- HLOS can be excluded;
- X1E secure FastRPC CB9/SID is recovered;
- FastRPC protected dma-buf map/unmap lifetime is bounded;
- SecurePD provides trusted CPU mappings/threads/mailboxes;
- the production shell has a real CPZ migration path.

No other Linux-side habitat currently closes all of those planes.

## 2. Why the other trusted habitats do not replace CPZ

### pKVM

pKVM gives us source-controlled EL2 CPU code, but the blocker is not CPU execution anymore. The missing authority is trusted camera DMA/IOMMU mapping equivalent to the Windows protected device-GPA plane. Golden protected mode is also inactive. Building more nVHE copy code would not solve camera visibility.

### Gunyah

Same-machine QHEE/Gunyah supports memory parcels and trusted VMs, but its ACL/rule analysis does not authorize `CP_CAMERA` with the trusted VM classes we recovered. No camera-to-trusted-VM device binding is known.

### FF-A / QTEE / QSEE

The transport primitives exist, but no reusable camera secure service/partition or arbitrary project-worker loader was found.

### HypX

HypX is part of the authenticated Windows Hyper-V boot chain. Static work found no post-boot runtime module-loading surface that Linux can use as a camera worker.

### HLOS

Post-processing after reclaim would be easy, but the protected pixels would become visible to HLOS. That fails the core Windows security contract and is not accepted as parity.

## 3. Manufacturer/development signing route was not found locally

A direct scan of the exact SP11 firmware/packages found no usable SecurePD signing credential, `oemconfig.so`, testsig package or development certificate/private key.

Windows FastRPC INF policy contains host SID allow-lists for signed callers. That is a Windows access-control layer, not a DSP module-signing mechanism and cannot admit a new CPZ ELF.

So there is currently no legitimate “flip this switch and load our worker” path in the material we possess.

## 4. Runtime activation is intentionally frozen

At this point, enabling CB9 or starting CPZ with a Gaussian/example module would prove infrastructure we already know exists while still leaving the real camera worker unavailable.

It would also cross the protected-runtime safety boundary without advancing the 1:1 goal.

Therefore:

- secure CB9 stays disabled;
- no CPZ process is created;
- no protected ownership transition is attempted;
- no verification policy is weakened.

## 5. Productive work can continue offline

Worker **admission** is blocked, but worker **implementation** is not.

E004cf already recovered the Windows execution contract: once both trusted mappings exist, the worker is ordinary CPU memory processing with direct copy/SWAB/synthetic-fill behavior plus geometry/payload metadata.

That means the next useful engineering task is to implement a tiny source-controlled Hexagon parity worker offline, compile it, and test its algorithms only against synthetic host-side vectors. This gives us a ready worker artifact and exact ABI without pretending it is trusted or loadable today.

If a legitimate Qualcomm/Microsoft/OEM signing/admission route later becomes available, the worker can be admitted without redesigning the protected memory stack.

## Safety boundary

SP11 remains Golden FullIO v19c. No CDSP trust policy, firmware, CB9, FastRPC, ownership, CPZ, camera or Linux SecureISP runtime state was changed.

## Next gate

**E004dg — source-controlled parity worker implementation, offline compile/test only.**

Implement the smallest worker ABI reproducing the Windows-proven operations:

- bounded source→destination copy;
- payload offset handling;
- synthetic/tail fill where required;
- SWABF/SWASF-equivalent transformation from the exact E004cf oracle;
- strict extent/stride/geometry validation;
- completion status suitable for E004db's “complete before MEM_UNMAP” lifetime.

Build/test with synthetic buffers only. Do not sign, install, load, migrate CPZ, or touch protected buffers.
