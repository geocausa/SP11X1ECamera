# E004cz — integrated Golden protected-provider build closure

## Result

**PASS: the previously separate Golden protected-memory, dma-buf state, CPZ FastRPC import and secure-CB9 topology pieces now compile together and resolve their internal link edges in one ARM64 relocatable object. The integrated candidate remains fail-closed by construction: CB9 is disabled, SCM/FastRPC registration is absent, production Golden sources are unchanged, and the external protected-sample/transfer side is still contract-only.**

This is a compile/link checkpoint, not a runtime provider activation.

## 1. Integrated compile set

E004cz stages the already-proven pieces together:

1. E004ct Qualcomm SCM multi-region ownership API;
2. E004ct SG batching helper;
3. E004cu system-heap protected ownership state machine;
4. E004cv CPZ process-type and protected FastRPC import gate;
5. E004cr CAMSS protected-provider/external-sample contracts;
6. E004cy X1E secure compute-cb@9 topology, still disabled.

A small compile-only glue object references the system-heap lifecycle and protected-query APIs and instantiates the CAMSS compile-time contracts. It has no runtime registration entrypoint.

## 2. Real cross-component link edges now close

Before the partial link, the staged objects have the expected unresolved internal dependencies:

- SG owner -> `qcom_scm_assign_mem_regions`;
- protected system heap -> `sp11_cpz_assign_sg`;
- FastRPC -> `sp11_cpz_dma_buf_is_protected`;
- provider proof -> lend/active/detach/reclaim/query APIs.

After `aarch64-linux-gnu-ld -r`, every one of those integration edges is resolved inside `sp11-protected-stack-e004cz.o`.

The integrated object directly defines:

- `qcom_scm_assign_mem_regions`;
- `sp11_cpz_assign_sg`;
- `sp11_cpz_dma_buf_is_protected`;
- `sp11_cpz_system_heap_lend`;
- `sp11_cpz_system_heap_mark_active`;
- `sp11_cpz_system_heap_mark_detached`;
- `sp11_cpz_system_heap_reclaim`.

No `sp11_cpz_*` or `qcom_scm_assign_mem_regions` integration edge remains unresolved.

## 3. Provider-authoritative protected dma-buf query is now concrete

E004cv previously compiled against an intentionally unresolved query:

`sp11_cpz_dma_buf_is_protected(dmabuf)`

E004cz implements that query inside the staged system heap. It reports protected state only while the buffer is in one of the non-HLOS ownership states:

- transition;
- lent;
- active;
- detached;
- poisoned/ownership-uncertain.

It does not report the initial HLOS or successfully reclaimed state as protected.

That lets FastRPC consume the system-heap state machine as the authority rather than trusting user attributes such as legacy `SECUREMAP`.

## 4. Registration is deliberately removed

The full SCM source naturally contains a normal platform-driver init path. E004cz removes that registration from the compile-only staged copy and retains only a `__used` compile-proof function which returns `-EPERM`.

The integrated object contains no:

- `init_module`;
- `cleanup_module`;
- initcall registration.

The E004cv FastRPC staged source already has its own driver registration removed.

Therefore the integrated object cannot become a live replacement driver merely by existing on disk.

## 5. Secure CB9 still compiles but stays disabled

The same disabled X1E node from E004cy is compiled as part of this checkpoint:

- logical FastRPC context 9;
- SMMU SID `0x0c09`;
- flags/mask `0x20`;
- `pd-type = <6>` (`CPZ_USERPD`);
- `status = "disabled"`.

The topology harness compiles with zero warnings. The live kernel still has no `compute-cb@9` node.

## 6. Production Golden sources are byte-stable

The production Golden source hashes remain exactly the previously recorded values:

- `qcom_scm.c` — `9937c995...67c33`;
- `system_heap.c` — `56b0db19...1856d`;
- `fastrpc.c` — `e2410813...dcb2`.

All E004cz changes exist only under the experiment directory.

## 7. Why this is not parity-ready yet

The **internal** protected-target host path now closes at compile/link level:

system heap backing
→ HLOS exclusion / CP_CDSP(+CP_CAMERA) ownership
→ provider-authoritative protected state
→ CPZ typed FastRPC import
→ recovered secure context-bank topology.

But the **external protected sample** is still only a contract. There is no runtime implementation yet for:

- external backing creation;
- CP_CDSP-only protected ownership lifecycle;
- trusted worker import/reference lifetime;
- payload completion;
- trusted detach;
- ownership reclaim before free;
- protected source-to-external transfer.

Therefore `runtime_binding_authorized` remains false and CAMSS must not expose a protected queue.

## Safety boundary

SP11 stayed on Golden FullIO v19c. No module/object was loaded, no DTB/overlay was installed, no context bank was probed, no SCM ownership call ran, no FastRPC ioctl ran, no CPZ process was created, and no camera or Linux SecureISP runtime was invoked.

## Next gate

**E004da — external CPZ protected-sample backing implementation, compile-only first.**

Implement the missing external-sample side as a staged system-heap-backed object while preserving the already-proven separation from the internal camera target:

1. external backing is generic system-heap dma-buf;
2. ownership destination is CP_CDSP only — never CP_CAMERA;
3. HLOS CPU access is revoked before trusted import;
4. worker reference is retained through payload completion;
5. FastRPC protected import must see the external dma-buf as protected;
6. detach must precede reclaim;
7. reclaim to HLOS must precede final dma-buf release;
8. no runtime registration or live ownership transition.
