# E011AH — request AF rectangles through full startup integration

Parent: `2f35a08454e7322ee29db88143d216a4b444351d`.

Status: **DETACHED REQUEST AF/BF ROI LOWERING + FULL PROVIDER PRIVATE PARITY + ISOLATED ARM64 BUILD PASS.**

Linux slice: **L4 caller AF rectangle → L2 offline BF ROI adjustment/materialization**. Client/profile: rear Color VideoRecord NV12 3840×2160. Evidence: S for the existing E008z/E009c/E008x/E008t source expressions, prior P for E009e's independently observed AF input and the private E006b validation corpus, D for the new detached Linux handoff. No new camera session occurred.

## Change

The new kernel-compatible include consumes three caller-owned, phase/request-tagged AF rectangles and updates only geometry in normal startup packets 1–3. It lowers E009c's supported interior BAF adjustment and E008x's selected zero-overlap 5×5 BF validation branch using integer arithmetic. It leaves packet 0 byte-for-byte unchanged and preserves ROI IDs/flags, gamma, registers, every other DMI family, request IDs and readiness.

Every packet identity and all three normal rectangle domains are validated before any change. A wrong tag, repeated caller identity, ready/sealed packet, unsupported geometry, missing ROI/gamma state or alias rejects without partial mutation, including errors in the last phase. Caller-owned objects must be valid, disjoint and serialized; bind detached bases before sealing/materializing/exposing commands. No runtime call site exists.

The kernel include takes the final L4 rectangle; it does not put floating point or AF policy in CAMSS. The host replay uses the existing E008z source helper, pinned HAF fractions .25/.25 and E009e's measured first-normal zoom float32 0x3f7f3f0f, then zoom1.0. These are explicit replay inputs. This does **not** newly prove the zoom's upstream calculation or a directly tagged live AF→RT-CDM packet identity; E009e's packet association remains based on established startup order and final shape.

## Validation

The new checks extend the source-locked actual E011AG harness, without modifying that historical checkpoint. Actual recursive E008o validation, actual E008l arena/layout and complete E007y materialization run, with the existing actual BPC/LSC/GTM binders.

GCC and Clang C11 ASan/UBSan each pass **508,760 assertions**, the **32 existing composition negatives** and **61 new AF handoff negatives**. The integer map is checked against E008x's independent float reference over 18,157 odd/even rectangles. All 16,385 integer dimensions from 0 through 16,384 prove that the bounded float32 one-fifth multiply/truncation equals integer division by five. This is a bounded-domain lowering, not a general float replacement.

| Phase | BF ROI selector 1 | BF gamma selector 2 |
| --- | --- | --- |
| 0 | 300/300 bytes, all 25 records exact | Absent |
| 1 | 300/300 bytes, all 25 records exact | 128/128 bytes |
| 2 | 300/300 bytes, all 25 records exact | 128/128 bytes |
| 3 | 300/300 bytes, all 25 records exact | 128/128 bytes |

Total BF comparison: **1,200 ROI bytes and 384 gamma bytes**, all exact through the complete four-packet composer. The independent neutral first-zoom control still matches only **250/300** phase-1 ROI bytes, so a settled first-normal rectangle is rejected by parity evidence.

All 2,268 register-write positions and 46 DMI identities still match corpus shape. Source BPC remains 21/21 present startup words; source LSC/GTM/GIC propagation remains 4/4/3 slots. Other semantic register differences remain 11/27/11/2 by phase; their neutral-scalar/statistics fixture seams are not claimed closed.

## ARM64 build

A fresh one-use isolated build copies source-locked E011AG and adds the exact integer-only AF binder. CAMSS W=1 passes with zero warnings against protected Golden headers. Both the binder/recipe and full composer/recipe are retained. No runtime call site was added.

- Module: 14,749,232 bytes.
- SHA-256: `9f1de3bb49cbc47b8a8a8b52e8d8a59c97ea511781cd98107e0006aaa6ccf760`.
- Exact Golden `7.1.5-sp11-render-parity-v4+` ARM64 vermagic.
- BUILD-SAFE.json records source/module locks.
- Module was not installed, loaded, booted or submitted.
- `build-once.py` is a consumed historical build identity; never rerun it.

## Remaining gates

Lower the already source/live-closed E011X neutral scalar and E010Z/E011A–R statistics handoffs into independent portable bases, preserving cold/normal transitions and keeping captured outputs validation-only. Recover original E011X inputs privately on SP11 if needed. Do not redo closed provenance experiments.

The cold packet still has hardware BF gamma disabled and no selector2. Generic validation eagerly requires complete gamma state; the inherited host-only unused completion remains explicit and is not a Windows cold producer/runtime policy. Normal AF input selection and request association remain the caller's responsibility.

**Complete source-produced E008o startup composition remains OPEN. Independent VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle remains OPEN. Native rear Linux ISP remains denied.**

SP11 stayed on idle Golden boot `208d6c65-0103-40e2-8ff4-fa25395f2534`. No camera, module, MMIO, submission, sleep, boot or persistent platform change occurred. Raw authority, packets and diagnostics stay private on SP11.

## Rechecks

`verify.py` checks committed counts/source/build locks. `verify-private.py` requires SP11 private authority, replays the original upstream BPC/tuning inputs and both real-provider sanitizer paths, and compares generated BF payloads privately. It emits only derived aggregates; generated bytes stay in a private temporary directory. Failed diagnostics remain private.
