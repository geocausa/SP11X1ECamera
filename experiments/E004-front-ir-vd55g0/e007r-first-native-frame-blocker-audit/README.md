# E007r — first native rear processed-frame blocker audit

Parent Git: a43a9129 (E007q clean GTM/TMC request-tagged handoff PASS).

Status: **OFFLINE AUDIT PASS / NO RUNTIME**.

## Purpose

Stop broad parity burn-down and identify only what still prevents a complete,
non-submitting rear native startup/request from being assembled safely enough
to justify a first guarded Titan680 processed-frame attempt.

## Already closed for the first-frame path

- all 714 startup register materialization contracts are concrete and integrated;
- BFStats25 register packing, DMI encoding and materializer binding;
- rear lower-AEC LSC/Tintless clean producer plus request-tagged selectors 1/2;
- GIC exact alias derived from current LSC bytes;
- rear TMC141 clean producer;
- clean GTM wire generation and request-tagged 2048-byte GTM handoff.

The later steady 0x658 MAIN variant itself requires only GTM + BFStats DMI,
which are already closed. The startup sequence is stricter and still includes
the stable DMI identities below.

## Stable-DMI audit

The rear E006b corpus and the accepted front native/static authority were
compared by payload identity only. All remaining stable identities are
byte-identical across front and rear in the exercised modes. Therefore none is
a rear sensor-adaptive producer.

### Bind-only

**PDPC 0x3D08/1, 512 B**

The rear payload is all zero and is identical across startup/steady variants and
the accepted front authority. A clean zero provider is sufficient for this
validated mode.

**LSC 0x4308/3, 884 B**

The rear selector-3 payload is all zero and cross-sensor identical. E007h's
clean LSC runtime also emits the third selector, but E007i deliberately handed
only dynamic selectors 1/2 into E006g. No new LSC algorithm is required.

### Actual stable-payload generator blockers

**BPC/ABF 0x4908/1, 256 B**

Nonzero, invariant, and byte-identical front/rear. It is therefore shared
hardware-mode state rather than rear adaptive state, but the project does not
yet have a clean generator for this DMI table. E007a closes calculated
registers only.

**Gamma 0x5F08/1,2,3, 1024 B each**

All three selectors are identical; the same payload is invariant across
front/rear. The bank rule is closed, but clean LUT generation is still missing.

**DSX 0xA008/1,2 (768 B) and 0xA208/1,2 (384 B)**

Each selector pair is identical and the same payloads are shared by front/rear.
The register/bank rules are closed; clean payload generation remains open.

Cross-sensor equality means no additional rear Windows oracle is justified for
these three families. The next work should source-lock their Titan680
packers/generators and reproduce the common payloads from semantic/default
hardware-mode state.

## Transport blocker

PERIOD_CFG at 0x008C is still an upstream transport-state dependency.

E007c closes the packet-aware materialization boundary and proves the mapping:

- packet 0 -> logical value 0;
- packets 1/2/3 -> shared logical value 1.

Windows proves qccamisp does not derive or mutate these values. The current
Linux front code likewise treats them as opaque caller inputs. A Linux-owned
upstream producer/stream-state derivation is therefore still required before a
parity startup request can be considered complete. Captured Windows values must
not be frozen.

## What is not a first-frame blocker

The following remain parity work but do not need to precede a single guarded
processed frame once the startup request is complete:

- upper-AEC rear LSC authority;
- long-run live AEC/AWB/AF convergence;
- broad scene/mode coverage;
- image-quality tuning corner cases.

## Gate to first native rear frame

Before any rear ISP submission:

1. close clean shared BPC/ABF, Gamma and DSX stable payload generators;
2. bind PDPC-zero and LSC-selector3 stable providers;
3. close Linux-owned PERIOD_CFG upstream state;
4. assemble the complete four-packet startup + first request offline;
5. patch only Linux-owned DMA/IOVA addresses;
6. validate DMI selectors/banks, register writes, packet ordering and lengths
   against the accepted Windows structure without copying Windows addresses;
7. verify output-buffer routing, completion/retirement, timeout and safe-stop;
8. only then prepare a single-use guarded native rear processed-frame runtime.

No Windows boot is required by the blocker audit itself.
