# E004cp — CPZ provider port contract

## Result

**PASS: a CPZ-capable protected-camera provider can now be represented at the CAMSS boundary without selecting or executing a backend. The compile-only contract requires all seven authority properties needed to turn E004co's vendor architecture into a parity-safe provider, and the resulting CAMSS module has byte-identical executable `.text` to the untouched baseline.**

No CPZ process, FastRPC control, mem-buf lend, SCM call, DT change, module load or camera runtime occurred.

## Why this gate exists

E004co proved a mechanically coherent vendor architecture:

`camera protected allocation`
→ HLOS-excluding protected camera/compute ownership
→ secure FastRPC import classification
→ CPZ-designated secure context bank
→ CDSP CPZ protected process.

But Golden does not yet contain the downstream host binding. The correct next engineering move is therefore not to call those APIs; it is to encode the exact conditions that must all be true before any runtime binding is permitted.

## Seven mandatory capabilities

The CPZ provider contract requires:

1. **camera + protected-compute co-owned internal target** — the camera hardware and trusted worker can access the same internal target;
2. **HLOS excluded from that target** — ordinary HLOS CPU access is not retained as a shortcut;
3. **privileged process-type authority** — the protected worker process class is selected by an authorized host path, not an arbitrary client;
4. **secure context import** — protected backing reaches the worker through an appropriate protected context-bank mapping;
5. **external protected sample import** — the separate consumer-facing protected sample is also visible to the trusted worker;
6. **reclaim ordering resolved** — protected ownership/mappings are torn down in a proven order before backing release;
7. **no HLOS fallback** — no ordinary CPU memcpy path may silently replace the trusted transfer.

All seven form `CAMSS_CPZ_PROVIDER_REQUIRED_CAPS = 0x7f`.

The contract deliberately leaves `runtime_binding_authorized` as state to be proven later. Merely naming CPZ or discovering the vendor APIs does not make the provider ready.

## External sample remains a separate gate

The internal capture-target side now has strong Qualcomm authority from E004co. The external protected sample is still a separate object, just as Windows keeps its external VTL1 sample distinct from the SecureISP internal CP_CAMERA target.

Therefore the port contract explicitly requires:

- `external_sample_provider_resolved`;
- `external_sample_hlos_excluded`;
- `CAMSS_CPZ_CAP_EXTERNAL_SAMPLE_IMPORT`.

A future implementation cannot declare parity-ready by solving only the internal camera buffer.

## No concrete runtime implementation in the contract

The new compile header contains no call to:

- Qualcomm SCM ownership functions;
- mem-buf lend/reclaim;
- FastRPC session control;
- dma-heap allocation;
- DT property parsing;
- QTEE/QSEE/Gunyah APIs;
- any ioctl or runtime selector.

It contains no concrete VMID numbers or CPZ process-type numeric value.

The only production C modifications are:

- include `camss-protected-cpz-provider.h`;
- call `camss_cpz_provider_compile_contract()`.

That inline function consists only of compile-time assertions.

## Mechanical zero-runtime proof

Production preimage:

- `camss-video.c` SHA-256 `2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4`;
- `camss-video.h` SHA-256 `69fdbb6364a772d5b9fe50114878bbc7a1a1ffc61e62af1e71c79fd16e94c982`.

Baseline and scaffold both build against the Golden runtime-v4 headers with vermagic:

`7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`

Executable `.text` is identical in both modules:

`fa5a8000207830a11d34fb46301cfd1b38f312a7666f6726bc170e2d0597e45e`

No module was installed or loaded.

## Safety boundary

Golden FullIO v19c remained active throughout. No protected ownership transition, DSP process creation, protected heap registration, camera module load or stream occurred.

## Next gate

Proceed to **E004cq — external protected-sample CPZ visibility authority**, static first.

The remaining architectural hole is now precise: find a Qualcomm/Linux mechanism that can provide the **separate external sample** with:

- HLOS CPU access absent;
- CPZ worker write visibility;
- stable per-sample identity/lifetime;
- reclaim before backing release;
- no requirement that the external sample also be a CAMSS hardware target.

Search vendor camera/mem-buf/FastRPC and same-machine Windows evidence first. Do not create a CPZ PD or perform a protected ownership transition until that external-sample contract is mechanically proven.
