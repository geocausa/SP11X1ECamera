# E007y — complete rear startup offline materializer

Status: **COMPILE-ONLY PASS**.

## Goal

Close the E007r complete four-packet startup request assembly gate without submitting anything to hardware.

E007y composes all four rear selector-2 startup block-list vectors:

- packet 0: 0x4 / 0xF1C / 0x4 / 0x3C
- packet 1: 0x4 / 0xEBC / 0xC / 0x4 / 0x10 / 0x14
- packet 2: 0x4 / 0xA00 / 0xC / 0x4 / 0x10 / 0x14
- packet 3: 0x4 / 0x658 / 0xC / 0x4 / 0x10 / 0x14

The MAINs are generated from E006k symbolic command topology, not copied from Windows buffers. All symbolic register-value and DMI-address holes begin at zero and generated skeleton hashes must equal E006k normalized hashes.

## Value ownership

Startup register values come from E007d with E007w packet-aware PERIOD_CFG. Normal DMI payloads come from the final clean E007v chain. Packet-0 BHist selector1/selector2 zero priming comes from E007x. DMI, MAIN and wrapper IOVAs are caller-supplied aligned nonzero Linux-owned 32-bit addresses.

request_id is explicit and is not derived from the startup packet number. The request-tagged LSC/GTM handoffs validate their own identity. The large dynamic DMI scratch object is caller-owned rather than kernel-stack local.

## Rear wrapper source locks

The rear-specific companion values are independently grounded: CSID1 IPP parity/crop/format values match E004ns/E004nq; the packet1..3 VFE 0x1E0C = 0x00190004 write matches rear WM16/BAF geometry from E004nu; 0x37C/0x380 are CSID IPP IRQ subsample pattern/period; and the final 0x18 write is CSID RUP_AUP_CMD. validate-private.py compares these semantic constructions against the retained private E006a records without committing private bytes.

## Safety boundary

The generated include is allocation-free and unreachable. It contains no MMIO, FIFO submission, module-init/probe hook, DMA allocation, firmware call, camera activation or RT-CDM submit function. On composition failure it zeroes caller-owned output/scratch buffers.

A compile pass does not authorize rear native ISP runtime. The next gate is structural/ownership review of the completed request plus output/completion/retirement and safe-stop invariants before any fresh single-use native rear experiment.

## Build result — PASS

The complete accepted E006/E007 dependency chain through E007y was injected into
a fresh isolated CAMSS copy and compiled W=1 against the protected Golden
headers.

- successful build identity: e007y-rear-full-startup-offline-materializer-build-v2
- qcom-camss.ko: 13,897,320 bytes
- SHA-256: 5da4809d2b70811701c7a767c49120ac9a234040269cf9374624c314061dde59
- vermagic: 7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64
- W=1 warnings/errors: 0
- retained symbols: e007y_rear_materialize and e007y_rear_startup_recipe
- install/load/camera/DMI/RT-CDM submission: none

The first isolated build identity was consumed by a generator formatting defect:
literal backslash-n/backslash-t text was emitted into the generated C array
source and the compiler rejected it before any module existed. The generator was
fixed, regenerated deterministically, and the fresh v2 identity passed. No
runtime action occurred in either attempt.
