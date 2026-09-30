# E011AS — explicit inactive cold BF gamma

Parent e73c4ff38221a28b4bf7995581e756a1f607a9a1.
Status: PASS_OFFLINE_AND_ARM64_BUILD. The bounded inactive cold gamma gate is closed; native rear hardware runtime remains DENIED.

E008s/E008t source authority disables BF gamma in cold packet0. The independently pinned startup recipe emits BF selector1 ROI but no selector2 gamma table in packet0; packets1–3 enable and emit gamma. The inherited generic dynamic materializer eagerly produced every family and the full host harness therefore supplied a dummy valid gamma table even when cold gamma was unused. This checkpoint removes that completion.

Four additive derivatives of the existing clean providers introduce:
- explicit gamma_inactive semantic state, distinct from gamma_valid;
- selected dynamic preparation that skips the gamma producer when inactive;
- a separate bf_gamma_materialized output flag, so an inactive dynamic object cannot satisfy a gamma slot;
- recursive validation rejecting inactive+valid, nonzero inactive LUT data, missing normal gamma and packet/register activity disagreement.

The original generic E006g entry point still requires active gamma. Its selected preparation zeros the dynamic object on every producer failure, including the first LSC callback. Direct BF selector2 encoding rejects inactive state before writing. Normal gamma arithmetic and emitted bytes are unchanged.

The new kernel-compilable e011as_rear_mark_cold_gamma_inactive producer validates cold startup phase/request identity, gamma hardware disabled, gamma_valid false and a zero semantic LUT before setting the only activity flag. Every rejection preserves the entire packet. It leaves ROI and all other modules unchanged. There is no inferred cold numeric gamma curve: zero unused semantic storage is a chosen deterministic Linux absence policy; source authority supplies disable/no-selector behavior.

The actual full host path now uses the original E008t BF seed followed by this new producer. The dummy-table completion is removed. E011AR's exact preflight function then materializes the four independently owned packets using the real provider chain. The kernel build includes the four derivative providers and the standalone cold-policy producer, while E008t's older host-only bootstrap wrapper is not a kernel input. No complete BF/AE/AWB/AF algorithm port is claimed.

Validation on SP11:
- GCC and Clang ASan/UBSan: 510,371 assertions each and zero semantic register differences in all four phases.
- All existing BF ROI/normal gamma, BPC, LSC/GTM/GIC and statistics comparisons remain exact.
- Nine packet/register/activity negatives; 38 atomic cold-policy negatives; all32 unused LUT words individually rejected when nonzero; nine injected dynamic-producer failures leave zero output.
- Inactive selector2 rejection preserves destination bytes; active legacy preparation still calls gamma and normal output matches the real encoder.
- Fresh isolated ARM64 W=1 v2 build: zero warnings/errors, module14,832,288 bytes, SHA41d169f5d5d9f24cf429a6e922eca49899a5c60b9034965ea9810da97935959e. Exact Golden vermagic; separately confirmed through Fabric.
- Read-only audit proves parent providers, E011AR runner and all unrelated base sources are preserved.

The first build identity stopped during preparation before compiler invocation because the archived E008t host-only seed was absent from the kernel base. A separate v2 identity passed; both identities are consumed. One added negative test initially used zero as a non-startup enum, but STARTUP is zero; the fixture was corrected to a distinct value and final tests pass. These were offline preparation/test failures, with no hardware action.

No module installed/loaded, Linux camera activation, DMA/MMIO/submission, reboot or sleep occurred. Golden remains idle on bootc0e263ed-7319-4f69-8f10-4d51f20cd1a1. Originals and private replay packet bytes remain on SP11.

Run verify.py for immutable source/build/replay checks; verify-private.py repeats the private full comparison on SP11. prepare.py, build-once.py and build-once-v2.py are consumed and must not be rerun.

Remaining gates: deterministic cold AEC weights/AWB retained BG initialization, normal RS count/whole-frame offset authority, final complete bootstrap/preflight, and independent same-generation WM16 IRQ/consumed-IOVA/DMA/IOMMU retirement proof. Runtime authorization remains -EOPNOTSUPP. Do not activate either candidate or wire an ordinary V4L2/autostart path.
