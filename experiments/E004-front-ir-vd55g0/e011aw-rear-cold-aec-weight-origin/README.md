# E011AW cold AEC weight origin — bounded offline audit

Parent: 8550c03b8c32eb74e58cfa734f5a4b80b72bd99a.
Hypothesis: the selected AEC statistics getter may generate the initial weight
triple. Result: the bounded getter field stores copy caller-owned cached words;
numeric initialization remains OPEN. No constant or captured weight was promoted
to a source-backed policy.

## Verified boundaries

The engine's static primary frame binding at call8528EC invokes GetParam
selector12 (AECAlgoGetParamBGStatsConfig), output type10, size92, into
frame+1A8. Hardware AEC_BE naming therefore does not establish an algorithm
BE-selector20 origin. A BE-only oracle would miss this primary source path.

Original GetParam372E40 accepts a typed output-descriptor list. The query has
its output-array pointer at+18 and count at+20 (hex); entries are24 bytes,
with payload pointer+0, allocated bytes+8 and type+10. Selector12 seeks type10;
selector20 seeks type21 (decimal). Forty-eight owned descriptor routes across
four object bases, three valid allocations and zero/two decoy entries reach
39EA40 with the intended manager, primary lane, payload pointer and requested92
bytes. Twenty-four wrong-type/undersized routes fail to reach that dispatch.
Execution stops before the dispatch call or its common diagnostic boundary:
no full callback return or zero-count diagnostic-path claim.

The original grid getter3A0DB0 reads its cache through object+18. Cache
weight words+14/+18/+1C become output+44/+48/+4C (hex). Across908 owned cases,
all2724 words match exactly, including walking bits, arbitrary u32 patterns,
NaNs and sign bits; source and checked neighbors are preserved. Execution
stops at3A0F18 before TLS-dependent diagnostics and the remaining tail.

The exact original primary statistics conversion fragment83E01C..83E034
copies frame+1EC/+1F0/+1F4 into primary statistics+30/+34/+38. Feeding the
getter's weight words through that separate owned frame fragment passes908
cases/2724 fields, with all other128 destination bytes preserved. This is
two bounded field-copy proofs, not execution of the whole engine between them.

ReadDefaultStatsConfig73B730 copies the default AEC statistics payload at
73C090 through original memcpyF5D480; the source-locked length is818(hex)
bytes. Earlier E011AN identifies its retained node destination+72A58.
This gives a precise cold-consumer boundary for a fresh oracle.

## Scope and incomplete exploration

No live cold selector, actual getter/cache object, first cache writer,
selected tuning policy or independent numeric weight initialization was proved.
The observed E011AK triple is one comparison case only. All synthetic words
are owned input, not retained output used as a policy.

Private attempts to reproduce the entire C++ dispatch manager did not
reproduce all its object/interface/TLS context. Initial direct-buffer and
descriptor-size assumptions were corrected before the successful bounded
route audit. That exploratory full-dispatch fixture remains INCOMPLETE;
it is not evidence of an original Windows driver defect and is not part of PASS.
The zero-output-count diagnostic path is also excluded.
Only the source-locked static frame binding is claimed; do not call it a
live cold invocation or claim full engine or getter returns.

All executable bytes are unchanged. Ghidra postprocessing was read-only.
Original DLL/decompiler text, exploration scripts and diagnostics remain
under ../private/E011AW* on this SP11. No Linux production C change,
new kernel build, install/load, camera access, reboot, MMIO, BCD, sleep or
submission occurred. Golden boot and all three protected payload hashes
are unchanged; NTFS is unmounted and camera idle.

The last full replay is E011AV: GCC/Clang ASan/UBSan each510374 assertions
and packet differences0/0/0/0 conditional on observed cold AEC/normal inputs.
E011AW does not replace those cold weights. Native rear ISP stays DENIED.
RS count/offset authority, full deterministic bootstrap and WM16
same-generation IRQ/consumed-IOVA/DMA/IOMMU retirement remain OPEN.

## Next smallest experiment

A fresh Windows original rear4K observer must qualify actual loaded code
before Start and bracket the earliest primary AEC BG query and grid-cache
getter during initialization/prepublish. Capture the selected cache's first
32 bytes through object+18 before the three copies, their output92 bytes,
the frame+1A8 output and the default AEC copy. Establish same invocation/
object/source lineage, then trace the writer of cache+14/+18/+1C upstream.
Do not assume AEC inherits AWB's callback slots, capture only BE selector20,
hardcode0.299/0.587/0.114, or repeat already verified AWB probes.
NEXT-OBSERVER.json records the bounded source-based plan; it is not armed.

Validation on SP11:
python3 experiments/E004-front-ir-vd55g0/e011aw-rear-cold-aec-weight-origin/source-private.py
python3 experiments/E004-front-ir-vd55g0/e011aw-rear-cold-aec-weight-origin/verify-private.py
