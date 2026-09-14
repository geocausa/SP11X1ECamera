# E004co — CDSP CPZ protected-process authority

## Result

**PASS: the missing Qualcomm Linux-side protected-worker bridge is now mechanically identified. A protected camera dma-buf lent to `{CP_CAMERA, CP_CDSP}` loses HLOS-exclusive ownership; Qualcomm downstream FastRPC recognizes that state as secure memory and routes it to a CPZ-designated secure context bank. The exact SP11 CDSP firmware contains the matching CPZ protected-process/mapping machinery. Golden Linux lacks this downstream host binding, and Windows DeviceMFT explicitly uses ordinary unsigned CDSP PD instead of CPZ.**

This is a static/read-only authority checkpoint. No new DSP process, FastRPC invocation, ownership transition, camera runtime, SecureISP runtime or Windows boot occurred.

## 1. CPZ is a real protected CDSP process class

Static Hexagon analysis of the exact Golden CDSP firmware proves a dedicated CPZ path, including:

- `HLOS_PHYSPOOL_CPZ` creation;
- a one-CPZ-PD runtime constraint;
- CPZ migration with physical backing information;
- explicit acquire/release ownership diagnostics;
- `fastrpc_invoke_mmap_get_cpz_phys`.

This is separate from ordinary signed/unsigned FastRPC process creation.

## 2. Qualcomm downstream FastRPC exposes the host CPZ contract

A Qualcomm-derived downstream FastRPC change adds a remote process-type ABI with `CPZ_USERPD = 6`, session-info control and PD-typed context banks.

The security boundary is explicit: a request coming from an untrusted delegated client is allowed to select ordinary `USERPD` only; privileged process types such as CPZ are rejected for that caller class.

For a secure dma-buf, the driver allocates a secure-memory session. When PD-typed context banks are enabled, that allocation is normalized to `CPZ_USERPD` and matched against a context bank carrying the corresponding `pd-type`.

So CPZ is not a guessed flag or a filename convention. It is a real host↔DSP process/context-bank contract.

## 3. mem-buf proves the no-HLOS ownership transition

Qualcomm mem-buf source resolves the crucial ownership ambiguity.

`mem_buf_lend()` requires the current VM to be absent from the target ACL. `mem_buf_share()` is the operation that retains the current VM.

The vendor camera path uses **lend**, not share, for protected buffers. For `CAM_MEM_FLAG_PROTECTED_MODE | CAM_MEM_FLAG_CDSP_OUTPUT`, the target ACL is:

- `CP_CAMERA` RW;
- `CP_CDSP` RW.

After successful lend, HLOS is no longer the untouched exclusive owner. Downstream FastRPC tests exactly that state through `mem_buf_dma_buf_exclusive_owner()` to decide whether the imported dma-buf needs a secure context bank.

## 4. The camera-to-CPZ bridge is now mechanical

The independently recovered pieces compose without inventing a new security model:

`protected camera allocation`
→ `mem_buf_lend({CP_CAMERA, CP_CDSP})`
→ `HLOS no longer exclusive owner`
→ `FastRPC secure buffer classification`
→ `secure context bank`
→ `CPZ_USERPD context-bank selection`
→ `CDSP CPZ physical-map/migration machinery`.

This architecture has the required shape for a Linux protected frame worker: camera hardware plus protected compute access without leaving ordinary HLOS CPU access to the frame backing.

## 5. Golden does not implement that bridge yet

Golden's current mainline FastRPC driver contains no CPZ process type, session-info ABI, mem-buf ownership query or PD-typed context-bank selection.

Its existing `FASTRPC_ATTR_SECUREMAP` is a different mechanism that deliberately retains HLOS RW and therefore cannot be called parity.

The live X1E CDSP FastRPC DT also has no CPZ `pd-type` policy and no `qcom,vmids` owner binding.

Therefore this checkpoint proves **implementation feasibility and upstream/downstream authority**, not runtime readiness.

## 6. Windows remains the oracle, and it does not use CPZ for protected IR

Exact SP11 DeviceMFT reversing closes a potential false lead.

Its only `remote_session_control` caller is the BitML engine constructor. That call selects CDSP domain 3 and enables FastRPC control request 2, with its own error text identifying the operation as switching to **unsigned PD**.

The BitML and DSP-streamer clients therefore demonstrate ordinary camera CDSP acceleration, not the protected IR trusted-worker lifetime.

Windows protected IR remains the already-proven architecture:

`internal protected target`
→ `VTL1 SecureISP CPU worker`
→ `external VTL1 protected sample`.

CPZ is a Linux parity implementation candidate because it can reproduce the *security/execution shape*; it is not being substituted as a claim about Windows internals.

## Safety boundary

No runtime ownership change or protected-camera action was performed. Golden FullIO v19c remained active; no camera nodes/modules were enabled.

## Next gate

**E004cp — CPZ provider port contract, compile-only.**

Encode only the minimum Linux interfaces that a future protected CAMSS backend would need:

- explicit CPZ-capable provider capability;
- protected dma-buf / no-HLOS ownership proof;
- remote process type and secure-context-bank selection abstraction;
- camera target remains `{CP_CAMERA, CP_CDSP}`;
- reclaim/release ordering is explicit;
- no ordinary HLOS transfer fallback.

Do not add live DT `pd-type`, create a CPZ PD, perform `mem_buf_lend()`, call SCM, or enable camera runtime. Build-only/zero-text verification first.
