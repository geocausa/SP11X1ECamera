# E011AL Bayer-grid weight and quad integration

Parent c8742eb070b69a5a35f67c0d5fd9484ab2962ab7. This slice implements portable L4 weight conversion and a detached integer L2 binder for AEC luminance weights and the AWB quad flag. There is no runtime camera caller.

Independent inputs come from E011AK: cold semantic consumers, normal AEC engine frame-control weights, and the normal AWB IO quad field. The cold initialization policy remains open. This slice proves conversion and composition conditional on those caller-owned inputs; it does not provide a complete deterministic cold seed.

The producer accepts finite nonnegative IEEE754 binary32 weights in0..1 and boolean quad. Integer significand/exponent arithmetic gives the same Q4 result as exact weight scaling by16 and ARM64 FRINTA (nearest, ties away). It handles zero, negative zero, subnormals and every half-integer boundary without an FPU. Invalid domains reject before changing output.

Private differential validation executes the unchanged original AEC and AWB pack functions in owned emulated objects. GCC and Clang each match2,164 original function cases/8,656 fields: two input cases and1,080 synthetic cases through both functions. Synthetic cases include one ULP below/at/above every Q4 half-integer boundary. Original register images are comparison outputs only; they never become producer inputs or committed bytes.

The binder validates both source identities, all result domains and all four caller startup tags before mutation. It changes only AEC Q4 weights and AWB quad; geometry, thresholds, black levels, AEC quad, AWB weights and unrelated state remain untouched. All35 binding negatives preserve every base byte;22 producer negatives preserve output. Source schedule0/1/1/1 is detached design state: packets2/3 do not emit these Bayer-grid ranges.

The actual full E008o/E008l/E007y replay matches all four formerly different weight/quad register instances. Remaining differences fall11->7, by phase1/3/3/0, all RS_STATS14. Prior36 BG geometry/threshold,26 scalar register instances, BF ROI/gamma, BPC and LSC/GTM/GIC comparisons remain exact. Both ASan/UBSan compilers pass509,582 assertions.

A fresh isolated ARM64 W=1 build passes with zero warnings; module SHA1b510b04dd119bd5c1e978b54829794bf02e7f0447c79f960e3e829cc0934f10. The module was not installed or loaded. The one-use build directory is consumed; never rerun build-once.py.

Validation commands on SP11: python3 native-private.py; python3 verify-private.py. See ARITHMETIC-SAFE.json, INTEGRATION-SAFE.json, BUILD-SAFE.json and RESULT.json. Originals, semantic input bytes, process addresses, raw transcripts and generated packet bytes remain private on SP11.

Next: source-close RS normal count policy and shift-field binding, implement the portable RS producer, and remove the remaining seven differences. Cold weight/quad initialization authority, explicit inactive cold gamma policy, complete source-produced E008o startup and independent WM16 same-generation IRQ/DMA/IOMMU retirement remain open. Native rear ISP runtime remains denied. Golden FullIOv19c, front native capture and rear RAW/software fallback are protected.
