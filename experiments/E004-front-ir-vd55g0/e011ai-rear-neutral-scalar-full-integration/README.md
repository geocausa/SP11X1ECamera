# E011AI — portable neutral scalar production through full startup integration

Parent: `6dded7a85953782c6c05b943b34889e4159be671`.

Status: **CLEAN L4 SCALAR PRODUCER + FULL PROVIDER PRIVATE PARITY + ISOLATED ARM64 BUILD PASS.**

Linux slice: **L4 portable scalar arithmetic → L2 detached startup binding/materialization**. Client/profile: rear Color VideoRecord NV12 3840×2160. Evidence: prior P E011X original input trace; S original arithmetic/source differential; D detached Linux phase handoff. No new camera session occurred.

## Original authority recovered

The original E011X-1412A trace, holder log, samples and comparison records were recovered privately from SP11's own Windows partition. The raw trace, holder and corpus hashes exactly match the committed E011X evidence. The partition was mounted read-only, copied only within SP11 and unmounted.

The new parser reads the 32 numeric events directly, checks every original input bit pattern against the archived eight samples, checks coherent PDPC/WB AWB inputs and exact event order, and proves the pre-request-1 calculation followed by request-1/request-2 recalculation and request-3 hold. It does not choose inputs by the captured output match matrix. Source IDs 0/1/2 and schedule [0,1,2,2] are explicit; materializer IDs 100/101/102/103 remain separate fixtures.

## Portable producer

`scalar-producer.h` is independently written C11 user-space code with no camera or Windows dependency. It produces four Demux Q10 values, four PDPC Q12 ratios and WB B/R Q10 values from caller-owned semantic gain/BLS/channel/AWB/predictive inputs.

The admitted branch is the source-audited Titan680 rear Bayer enum2 and ordinary WB quantization. Other Bayer policies and optional WB normalization remain outside this slice. Inputs/intermediates are bounded and finite. Separate binary32 operations are preserved without FMA; roundf implements the source FRINTA ties-away boundary. Demux applies source 14-bit normalization and maximum-gain rescaling; PDPC applies its minimum/maximum limits and near-zero denominator rule.

The private source differential caught and corrected an edge case before integration: PDPC's near-zero AWB denominator produces the **minimum 128**, not unity4096. This correction is proved by the exact source branch and original arithmetic.

The original three common-calculation routines execute only in local private Unicorn memory with synthetic owned dependency/region/reserve blocks. The PDPC differential covers its scalar ratio outputs, not the complete PDPC map producer; WB uses the ordinary branch with optional normalization explicitly inactive. No process, driver or OS is invoked.

GCC and Clang sanitizer builds each match **1,038 cases / 10,380 scalar fields** against original ARM64 arithmetic. Cases include all eight recovered live inputs, 1,024 reproducible synthetic inputs (gain normalization, channel variation and predictive-gain variation), and six epsilon/clamp controls. Full integration consumes the **clean C results**, after comparison passes; original/native outputs and captured command words remain comparison-only.

## Kernel handoff and complete composition

The integer-only binder checks source IDs/domain, unique caller IDs, startup phase/request tags, readiness and aliasing before changing any base. It updates only the ten scalar fields, preserving all other fields and tags. Packet3 receives source2's held state. Invalid source values or late packet tags preserve every base.

The source-locked E011AH harness is extended without modifying historical checkpoints. It still runs actual E008o recursive validation, E008l allocation/layout, E007y materialization, E011AE BPC, E011Z adaptive and E011AH AF ROI binders.

GCC and Clang ASan/UBSan each pass **509,118 assertions**: 32 inherited composer negatives, 61 AF handoff negatives, 69 new scalar binder negatives and 69 finite/domain producer negatives. Last-source/last-packet failures prove atomic preservation. Invalid producer inputs preserve output.

| Phase | Present scalar register instances | Exact clean-source comparison | Remaining other semantic differences |
| --- | ---: | ---: | ---: |
| 0 | 8 | 8 | 3 |
| 1 | 8 | 8 | 19 |
| 2 | 8 | 8 | 3 |
| 3 | 2 | 2 | 0 |

All **26** scalar register instances now match the retained Windows startup corpus through the complete composer. Remaining semantic register differences fall from **51 to25**, exclusively in statistics families. These differences are implementation work, not reopened provenance gates.

BF ROI/gamma still match all four/three emitted payloads; source LSC/GTM/GIC propagation remains4/4/3 slots; BPC remains21 present exact words. Register positions2,268, DMI identities46 and emitted DMI payload36,152 bytes remain unchanged.

## ARM64 build

A fresh consumed one-use build copies source-locked E011AH and adds only the integer scalar binder. The user-space float producer is not copied into kernel source. CAMSS W=1 passes with zero warnings against protected Golden headers; scalar binder/recipe, AF binder and full composer are retained. No runtime call site was added.

- Module: 14,758,008 bytes.
- SHA-256: `be35b2da4905b63549a4fef65f89f0299f46f4bc79404c7a720a278648113c5b`.
- Exact Golden `7.1.5-sp11-render-parity-v4+` ARM64 vermagic.
- No install, load, boot, MMIO, DMI or RT-CDM submission.
- `build-once.py` is a consumed identity; never rerun it.

## Next falsifiable gate

Lower the already source/live-closed E010Z/E011A–R statistics geometry/threshold/weight/black-level/RS handoffs into independent portable bases and require full private register/DMI parity. Original E011X authority is now available privately on SP11; do not repeat that hardware session.

The cold BF gamma completion remains explicitly host-only, unused, hardware enable0 and selector2 absent. AF first-normal zoom remains an explicit existing measured replay input, with its upstream calculation and directly tagged packet identity not newly proved. No complete AE/AWB/AF algorithm or metadata publisher is ported by this slice.

**Complete source-produced E008o startup composition remains OPEN. Independent VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement/lifecycle remains OPEN. Native rear ISP remains denied.**

SP11 stayed on idle Golden boot `208d6c65-0103-40e2-8ff4-fa25395f2534`; no camera, sleep or boot action occurred. Raw authority, generated bytes and failed diagnostics remain private on SP11. The failed first read-only mount used an unsupported ntfs3 option; the successful ntfs-3g read-only mount performed no recovery/write.

## Rechecks

`verify.py` checks committed aggregates and source/build locks. `authority-private.py` validates recovered input provenance without printing inputs. `native-private.py` compares clean C production with original arithmetic privately. `verify-private.py` runs both full sanitizer paths and private retained corpus comparisons, writing only safe aggregates. Generated packet bytes are held in a private temporary directory. Source arithmetic/domain changes require rerunning both private differential and integration; kernel changes require a fresh build identity.
