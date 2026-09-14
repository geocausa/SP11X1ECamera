# E004cs — Golden CPZ host-port source delta

## Result

**PASS: the minimum Golden-side CPZ host port is now bounded, and two concrete source pieces compile against the existing 7.1.5 Golden ABI without being loaded: (1) the CP_CAMERA/CP_CDSP ownership transition core using Golden's existing `qcom_scm_assign_mem()`, and (2) an inert FastRPC PD-type/session-selection stage derived from Qualcomm's designated-context-bank design. A full mem-buf/Gunyah backport is not required for CP_CAMERA/CP_CDSP. The remaining major source gap is protected dma-buf ownership/lifetime plus scalable scatter-gather assignment.**

No live kernel source was modified. The compile products were built in the experiment/temp tree only and were never installed or loaded.

## 1. Golden already has the low-level contiguous ownership primitive

Golden 7.1.5 exports:

`qcom_scm_assign_mem(phys_addr, size, source-owner-mask, destination-vmperm-array, count)`.

This API can mechanically encode both E004cq/E004co transitions:

- external sample: `HLOS -> CP_CDSP`;
- internal target: `HLOS -> {CP_CAMERA, CP_CDSP}`;
- teardown: current protected owner set -> `HLOS`.

E004cs includes a standalone compile proof with those three helpers. They are retained in the built module, and the module has a real unresolved dependency on Golden's exported `qcom_scm_assign_mem` symbol. The module init function performs no ownership operation.

This means we do **not** need a new secure-world transport for the first host port.

## 2. CP_CDSP does not require Gunyah

Qualcomm mem-buf classifies `CP_CAMERA` and `CP_CDSP` as fixed peripheral VM classes with no Gunyah API requirement.

The mem-buf path performs the Qualcomm ownership assignment first; its Gunyah memparcel layer is needed only when one of the selected VM classes explicitly requires the Gunyah API (for example a trusted/OEM guest VM).

Therefore the previously missing local `drivers/virt/gunyah` stack is **not a blocker** for the camera CPZ path.

That removes a large and unnecessary porting dependency.

## 3. The important ownership API mismatch is SG versus contiguous

Golden's `qcom_scm_assign_mem()` serializes one physical range.

Qualcomm's newer `secure_buffer/hyp_assign_table()` accepts a scatter-gather table and batches multiple physical ranges through the newer public:

`qcom_scm_assign_mem_regions()`.

Golden already contains the same internal SCM memory-region and permission descriptor layouts, but does not export that multi-region function or the public helpers.

Consequences:

- a contiguous protected backing can use Golden's API today;
- the vendor generic system-heap path cannot be ported verbatim because system-heap dma-bufs may contain multiple physical extents;
- the scalable final port should either backport the batched multi-region API or deliberately use a protected contiguous heap.

Current Golden boots with `cma=128M`, but normal desktop runtime leaves little CMA free. So **CMA-only is a useful first compile/bring-up shape, not yet a justified final capacity design**.

## 4. FastRPC PD-type selection has a small safe first stage

Golden FastRPC currently chooses the first free valid context-bank session. It has no process type on the session or client object.

E004cs stages only the structural part of the Qualcomm design:

- the known PD-type vocabulary including CPZ user PD;
- `pd_type` in the session and per-open client state;
- session allocation can require a matching PD type;
- every existing context bank and client defaults to `DEFAULT_UNUSED`;
- no ioctl or DT property can set a nonzero type yet.

The staged FastRPC source builds successfully as a module against the Golden headers. Since every live-configurable value remains zero, this stage does not provide a path to create/select CPZ even if someone mistakenly loaded the experimental binary. It is a source-port checkpoint, not a runtime feature.

## 5. What must still be ported before protected runtime exists

The remaining minimum host-side pieces are now explicit.

### Protected dma-buf ownership wrapper

We still need the mem-buf semantics that make a dma-buf's ownership state authoritative:

- refuse HLOS-excluding lend while HLOS CPU mappings/pins exist;
- record active owner/perms;
- deny HLOS `mmap`/`vmap` after lend;
- classify a non-HLOS-owned dma-buf as protected for FastRPC;
- reclaim ownership before heap backing is freed;
- retain/leak safely if reclaim fails rather than freeing unknown-owned memory.

### Protected heap/exporter

The first runtime-capable provider should be separate from ordinary Golden heaps. Do not mutate `system` or `default_cma_region` globally just to obtain camera protection semantics.

A protected-only exporter can start with contiguous backing while the SG API is being ported.

### FastRPC secure import split

Golden currently has `FASTRPC_ATTR_SECUREMAP`, but that is a user-supplied attribute and its old ownership path intentionally retains HLOS. It cannot be the parity security signal.

Protected mapping must instead be selected from the dma-buf's proven ownership state, then use a CPZ-typed secure context bank.

### Authorization / DT

The vendor session-info control and `pd-type` context-bank policy are deliberately not exposed yet. They need a separate authority gate and caller restrictions before CPZ can be selected.

## 6. Compile evidence

### Contiguous owner shim

The E004cs owner module builds with Golden vermagic:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`.

Its exported compile-proof functions are:

- `sp11_cpz_lend_external`;
- `sp11_cpz_lend_internal`;
- `sp11_cpz_reclaim_hlos`.

The built object retains `qcom_scm_assign_mem` as an unresolved kernel dependency, proving the concrete ownership calls were compiled rather than dead-code-eliminated.

### FastRPC PD-type stage 1

Both untouched Golden FastRPC and the staged source build successfully. The stage adds only 32 bytes to `.text` in this external-module build (`22396 -> 22428` bytes), while leaving the selection value at `DEFAULT_UNUSED` and exposing no new user/DT control.

Neither module was loaded.

## Safety boundary

Golden FullIO v19c remained active with no one-shot armed. No protected buffer was allocated, no SCM ownership call was executed, no CPZ process was selected, no FastRPC call was made and no camera/SecureISP runtime occurred.

## Next gate

**E004ct — Golden scatter-gather ownership backport**, static/compile-only first.

Backport just enough of Qualcomm's `qcom_scm_assign_mem_regions()` / secure-buffer batching model to the Golden SCM API in a temporary source tree and prove it compiles without changing runtime. Then decide mechanically whether the final protected external/internal backing can use system-heap SG buffers or whether a dedicated contiguous heap remains necessary.

Do not load the modified SCM/FastRPC code or perform an ownership transition.
