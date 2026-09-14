# E004cv — Golden CPZ FastRPC session/context-bank port

## Result

**PASS: the minimum CPZ FastRPC control/import path compiles against Golden and is privilege-gated, while remaining disabled by construction. A protected dma-buf can only enter the staged secure mapping path after CPZ process-type selection and a matching CPZ-typed session. Ordinary/delegated callers cannot select CPZ. Golden still has no CPZ-typed context bank, so the staged path fails closed and cannot become live.**

No FastRPC ioctl, DSP process creation, dma-buf import, SCM ownership transition, DT change, camera runtime, Windows boot or SecureISP runtime occurred.

## 1. Process-type control is now explicit

E004co proved Qualcomm's downstream ABI contains a remote process type and `CPZ_USERPD = 6`. E004cv ports the minimum shape into the Golden FastRPC source scaffold:

- session-info request structure;
- `CPZ_USERPD = 6` and ordinary `USERPD = 7`;
- per-open process type state;
- per-session process type state;
- process-type-aware session rebinding.

The ABI is present only in the staged build. Production Golden UAPI is untouched.

## 2. CPZ selection is privilege-gated

The staged control rejects CPZ unless all of these are true:

- the request comes from the same TGID that opened the FastRPC file;
- the caller has `CAP_SYS_ADMIN`;
- the secure FastRPC device was opened;
- the domain is CDSP;
- the request names CPZ_USERPD exactly.

A delegated caller can select ordinary USERPD only.

Once any process attach/create operation begins, session configuration is locked. The process type cannot be changed underneath an active or starting DSP process.

## 3. Typed context-bank binding is required

Selecting CPZ does not invent a session. `fastrpc_session_rebind_pd_type()` must find an already-valid unused context-bank session whose `pd_type` equals CPZ_USERPD.

E004cv deliberately adds **no DT `pd-type` parser**. The context-bank probe still initializes every session as DEFAULT_UNUSED.

Therefore on current Golden topology a CPZ selection cannot complete: the rebind returns `-ENODEV`.

This is the intended compile-first safety boundary.

## 4. Protected dma-buf import is provider-authoritative

The staged map path asks the E004cu provider boundary:

`sp11_cpz_dma_buf_is_protected(dmabuf)`

A protected dma-buf is rejected unless:

- legacy `FASTRPC_ATTR_SECUREMAP` is absent;
- the secure FastRPC device is used;
- the client is CPZ_USERPD;
- the bound session is also CPZ_USERPD.

For a protected import, FastRPC does not retain a host virtual address (`map->va = NULL`).

This keeps the E004cu ownership state machine authoritative and prevents the older HLOS-retaining SECUREMAP path from masquerading as protected parity.

## 5. Compile proof is nonzero but unreachable

Driver registration is removed from the staged source. There is no `module_init()`/`module_exit()` runtime path and no `init_module` symbol.

To prove the new code is genuinely emitted rather than optimized away, three compile-only roots are marked `__used`:

- protected dma-buf map/import gate;
- CPZ session authority gate;
- session-info copy/dispatch handler.

The resulting object contains **3432 bytes of `.text`** and retains unresolved dependencies on:

- `sp11_cpz_dma_buf_is_protected`;
- `capable`;
- dma-buf get/attach;
- user copy helpers.

Thus the control and import code has actually passed the Golden compiler, while the object has no runtime registration entrypoint and was never linked/loaded.

## 6. Production state remains unchanged

Golden FastRPC source/UAPI and live DT are unchanged. No CPZ process type or typed context bank exists in the booted kernel.

This checkpoint only proves that the missing host-side control/import logic can be ported in a bounded way.

## Safety boundary

Golden FullIO v19c remained active with no one-shot armed. No module was loaded, no FastRPC request was issued, no protected dma-buf was imported, no ownership changed, and no camera/SecureISP runtime was invoked.

## Next gate

**E004cw — CPZ typed context-bank authority and topology**, static first.

Resolve the last FastRPC host binding before considering any integrated build:

1. inventory the exact X1E CDSP FastRPC/SMMU context-bank topology;
2. find Qualcomm downstream DT bindings and production examples for `pd-type = CPZ_USERPD`;
3. determine whether CPZ requires a dedicated secure context bank/SID or may reuse an existing secure CDSP context;
4. prove the context bank's IOMMU visibility is compatible with CP_CDSP-owned dma-bufs;
5. do not modify live DT or create a CPZ process.
