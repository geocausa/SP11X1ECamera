# E011AG — full real-provider offline startup integration

Parent: `361518ec4aca187cce49f131747ecca89042228b`.

Status: **FULL PROVIDER INTEGRATION + ISOLATED ARM64 BUILD PASS; COMPLETE SOURCE-PRODUCED STARTUP BASES STILL OPEN.**

Linux slice: **L2**, offline rear CSI/ISP startup composition, with explicit L4 caller semantic inputs. Profile: rear Color VideoRecord NV12 3840×2160. Evidence: D for the integration design and host allocator; S for source-produced BPC/LSC/GTM/CST and existing providers; previously P-bound Windows upstream inputs and retained validation corpus. There was no new camera session.

## What changed

Earlier E011AE and E011Z compile checks used simplified E008o shapes. This checkpoint includes **34 actual provider/contract files**, the actual recursive E008o validator, actual E008l allocation/layout code, and the complete E007y packet materializer. Only kernel allocation and target predicates are replaced by clearly marked host shims; these allocate ordinary process memory and synthetic 32-bit IOVAs. No fake E008o validation or fake DMI production is used.

The new caller-owned composer accepts four distinct base objects, three source BPC states, two source LSC states, one startup GTM payload, a separate work object and an allocated, unsubmitted command arena. It preserves caller packet IDs; the host uses 100/101/102/103, independently of BPC source request IDs 0/1/2.

Composition checks aliasing, exposure/submission state and the exact E008l buffer layout before changing anything. It then binds BPC [0,1,2,2], binds LSC [0,1,1,1] and flat startup GTM, validates the complete register-family union for every packet, and materializes every real packet. An accepted-domain semantic or production failure clears all four command slabs, dynamic scratch, block lists and semantic readiness/sealing. Invalid/exposed arenas and aliased input objects are rejected without altering an existing valid set. Caller allocation metadata/descriptor arrays must be valid owned objects, preparation must be serialized, and arena backing must not alias semantic inputs.

The existing E011AF private verifier can now return its source states **after all original checks**, without printing private values. This allows integration to consume the already-verified upstream calculation instead of captured register outputs.

## Validation

GCC and Clang C11 builds pass `-Wall -Wextra -Werror` with AddressSanitizer and UndefinedBehaviorSanitizer. Each run passes **1,872 assertions and 32 negative cases**. Negative tests cover wrong phases/request tags, missing period/ROI/gamma state, source BPC domain errors, invalid ROI production, aliased input/output, oversized DMI descriptors, exposed arenas and already-submitted packets. A late packet-3 production failure verifies clearing of earlier successful packets.

| Phase | Actual register writes | Actual DMI slots |
| --- | ---: | ---: |
| 0 | 714 | 17 |
| 1 | 705 | 16 |
| 2 | 504 | 10 |
| 3 | 345 | 3 |

All **2,268 register-write positions and 46 DMI slot identities** match the private startup corpus shape. Total emitted DMI payload is 36,152 bytes. The three present BPC blocks match all **21 retained Windows words** after full integration. Source-produced payload propagation is exact for **four LSC selectors, four GTM selectors and three GIC aliases**. Phase 3 holds BPC state 2, but has no BPC register block; no fourth captured block is invented.

Source-derived rear CST12 and disabled BC101 settings match through the full provider path. PERIOD_CFG comparison uses its source-defined low-five-bit semantic mask; preserved Windows upper stack bits are not a Linux policy.

## Explicit incomplete inputs

Neutral scalar and some statistics base fields still use **host caller fixtures**, rather than the previously established E011X and E010Z/E011A–R producer handoffs. Their semantic mismatches are mapped by family in INTEGRATION-SAFE.json: 11/27/11/2 instances by phase. These are a map of work still to implement, not a reopened source/live provenance gate or an accepted bootstrap policy. Normal BF ROI in the host fixture also still needs the accepted E009c/E009e/E011T–V request-specific input/adjustment path and full DMI comparison.

The cold packet disables BF gamma and does not emit BF gamma selector 2. The generic recursive validator nevertheless requires a valid gamma state because dynamic preparation builds every family. The harness supplies a clearly marked valid **unused host-only completion**, keeping hardware gamma enable zero and emitting no cold gamma table. This does not infer a Windows cold gamma producer or authorize native runtime. A final producer must make the inactive-state completion explicit.

The flat pre-valid-TMC GTM curve has zero slope at every point, so its packed result is independent of interpolation coordinates. E011Z replay now uses the clean packer with a canonical monotonic grid, verifies equality with an irregular grid, and checks the existing exact startup hash. This removes an unnecessary missing private normal-TMC domain-file dependency from static startup replay. Normal adaptive GTM is unchanged.

## Actual ARM64 driver build

A fresh one-use isolated CAMSS source build includes the exact new composer and existing BPC/adaptive binders, using the source-locked previous E008o build. W=1 passed with **zero warnings** against protected Golden headers. Both composer and recipe symbols are retained; no runtime call site was added.

- Module: 14,734,568 bytes.
- SHA-256: `6ed7738dcc2ba1a197e162e8b4cff1ca5fb98492ed90bde98703799ce9f4d488`.
- Vermagic: exact `7.1.5-sp11-render-parity-v4+ ... aarch64`.
- Source lock and build evidence: BUILD-SAFE.json.
- Do not rerun consumed `build-once.py`; use a new audited build identity for changed kernel source.

## Next falsifiable gate

Lower the already source/live-closed neutral scalar and statistics producer expressions/handoffs into portable independent base objects, preserve cold/normal transitions, apply the proven request-specific AF ROI adjustment, then require full semantic register/DMI comparison through this real integration harness. Recover the archived E011X input authority on SP11 if needed; never invert the E006a outputs into inputs. Keep all raw authority and generated packet bytes on SP11.

**Complete source-produced E008o startup composition remains OPEN. Independent VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle remains OPEN. Native rear ISP remains denied.**

SP11 remained on idle Golden boot `208d6c65-0103-40e2-8ff4-fa25395f2534`; no module install/load, camera access, MMIO, DMI submission, RT-CDM submission, sleep or boot change occurred.

## Rechecks

`verify.py` checks committed aggregates and source/build locks without private authority. `verify-private.py` replays private upstream authority and both sanitizer integrations on SP11; generated packet bytes stay in a private temporary directory and only aggregates are committed. Failed runtime diagnostics are retained privately. `build-once.py` is historical single-use build evidence.
