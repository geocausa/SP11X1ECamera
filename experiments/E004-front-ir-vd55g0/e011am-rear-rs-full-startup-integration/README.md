# E011AM RS integration — zero remaining offline differences

Parent6dba79a3da24274e7e34f11154a72b8f97eb5e95. A portable integer L4 RS producer and detached L2 binder now remove the seven remaining RS_STATS14 differences in the four-phase startup comparison. This is offline parity conditional on independent semantic input records; deterministic bootstrap and live Linux rear ISP capture remain separate open gates.

Inputs are E011AK pre-adjustment RS counts, color-conversion flag, inclusive crop and pixel-format width policy. The earlier normal AFD count producer remains open. This slice supports an explicit whole-frame, zero-offset caller policy; it does not port stripe offsets or a color matrix. Color conversion is separate from module enable: the bounded original RS pack path enables the module independently.

The original CheckDependenceChange first derives region dimensions by crop/count division. AdjustROI clamps width2..8192 and even height2..16, reduces counts when minimum regions exceed the remaining frame, and computes shift as max(0,bit_length(region_width*region_height)-4). Pixel-format1 halves crop width before division. The producer accepts bounded positive caller inputs and rejects unsupported domains before changing output.

Private execution of unchanged original ARM64 AdjustROI matches4,387 cases/35,096 fields per compiler. Those include3 captured input cases,3,360 systematic edge cases and1,024 synthetic cases. All21 observed RS pack count/color/region/offset fields match; all3 pack-option shifts match the original module shift at+0x130. This closes the sampled shift binding that E011AK left open.

Only clean C outputs enter the binder. It validates three source identities, all geometry/flag/shift values and every caller startup tag before mutation. All70 binder negatives preserve the entire base array;14 producer negatives preserve output. Caller tags and other modules remain unchanged. Source schedule0/1/2/2 follows cold request1, first normal request1, second normal request2 and the observed stable request3 input; packet3 emits no RS registers.

The actual full E008o/E008l/E007y replay now has zero semantic register differences in every phase. All12 present RS register instances match. Prior BG geometry/threshold, weight/quad, scalar, BF ROI/gamma, BPC and LSC/GTM/GIC comparisons remain exact. GCC and Clang ASan/UBSan each pass509,829 assertions.

A fresh isolated ARM64 W=1 build passes with zero warnings. Module SHA85c318c424d5b3380f884c2e28893dbe28d49c233c4d0874de9a95cd058a3d25; never installed or loaded. Its build identity is consumed; never rerun build-once.py.

Validation on SP11: python3 native-private.py and python3 verify-private.py. See ARITHMETIC-SAFE.json, INTEGRATION-SAFE.json, BUILD-SAFE.json and RESULT.json. Proprietary originals, input records, process pointers, raw transcripts and packet bytes remain private on SP11. No Linux camera, boot, sleep, MMIO, DMI or RT-CDM runtime action occurred.

Next: replace the remaining observed caller-policy inputs with source-backed deterministic initialization: cold BG weights/quad, normal RS/AFD count selection and whole-frame offset authority. Explicit inactive cold BF gamma policy and independent WM16 same-generation IRQ/DMA/IOMMU retirement also remain open. Zero offline differences do not authorize a live camera run. Preserve Golden FullIOv19c, accepted front native capture and rear RAW/software fallback.
