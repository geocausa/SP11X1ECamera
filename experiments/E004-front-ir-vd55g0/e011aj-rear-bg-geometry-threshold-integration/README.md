# E011AJ rear Bayer-grid geometry and threshold integration

Parent: c5fab3f3066d69833aa02a23bc801bee47c10cf2.
Profile: rear Color VideoRecord NV12 3840x2160. Linux slice: L4 bounded caller-side statistics production -> L2 detached startup composition. Evidence: prior P source/live E011B/N/Q/M input semantics; S private original ARM64 arithmetic differential; D host and kernel build integration. Offline only.

## Result

Portable C11 produces AEC_BE and AWB_BG adjusted geometry and thresholds from upstream semantic records. The actual E011AG/E011AH/E011AI four-packet composer matches all36 present geometry/threshold register instances privately. Remaining register differences drop25->11, phases[3,5,3,0]. All prior scalar, BF ROI/gamma, BPC and adaptive DMI comparisons stay exact. This does not close complete startup production.

Both GCC and Clang ASan/UBSan pass509,427 assertions:32 composition,61 AF,69 scalar binding,69 scalar producer,90 BG binding and14 BG producer rejection cases. The independent original AEC/AWB geometry functions each match1,028 clean C cases, together2,056 cases/20,560 fields per compiler. The original hardware capability helper is shared by the AEC vtable and AWB helper; its original execution independently returns16..512 region limits,64x64 max grid and18-bit threshold max. Original executable bytes are unchanged in private Unicorn, with logging disabled in owned emulated data. No Windows runtime/driver invocation.

A fresh isolated ARM64 CAMSS W=1 build passes zero warnings. Module SHAa763e03440cf2fce81a89e338b90867cd3df5fbea4129492e8d8535e049bab71,14,765,856 bytes. It retains the BG binder/recipe and existing startup binders. It was not installed, loaded or called. Build directory /home/geoca/Documents/SP11-PROJECT/02-kernel/e011aj-rear-bg-geometry-threshold-build is consumed: never rerun build-once.py.

## Input boundary

E011B cold seed:64x48, zero origin, inclusive crop width/height minus floor(one tenth), threshold(1<<sourceBitDepth)-1. E011M active Titan680 capability independently supplies bit depth18. E011N request1 normal AEC engine frame control supplies32x32/fullcrop/four0x3e7ff thresholds through the previously closed E011C watched replacement. E011Q prerequest AWB supplies64x48/fullcrop/four0x3c3fe thresholds, downstream E011R request bridge already established.

The clean producer bounds the crop/ROI/grid, clamps the span against16..512 region limits, clips to crop, floors region dimensions even and revises grid counts only at the region limits. Thresholds clamp to the source bit-depth limit. Inputs and constants do not come from RT-CDM register inversion. Retained packets are comparison only.

Threshold gain policy is deliberately bounded to exact unity. The independent live binding of the original gain field request->trigger+0x44 remains OPEN; this slice does not establish that provenance or support its other scaling policies. Packet0 uses the cold result; later packet semantics hold the normal result. Only packets0/1 emit these BG register ranges, so packets2/3 BG holds are detached design state, not newly observed live publications.

The integer binder validates all source IDs, values, aliases and four caller tags/readiness before any write. It preserves weights, quad flags, black level, enable flags, every unrelated module, source objects and caller IDs. Input objects must be owned and serialized; this is not a concurrent runtime API.

## Remaining gates

Eleven register differences: AEC Q4 luminance weights(two instances), AWB quad synchronization(two), RS configuration(seven). The earlier E011H request+0x80 marker is color conversion according to the independently source-locked RS packer, separate from forced module enable; it is not evidence the RS module is disabled. Later RS source transitions remain to audit. No mismatched output is a license to back-solve an input.

Complete source-produced E008o startup composition, independent statistics gain binding, explicit inactive cold BF gamma policy and VFE1 WM16 same-generation IRQ/DMA/IOMMU retirement remain OPEN. Native rear ISP runtime remains DENIED.

Next falsifiable gate: independently recover/verify the AEC luminance weights, AWB quad flag and RS normal request producer records, lower them into the full composer and require the remaining11 differences to vanish. Independently verify the statistics gain field before claiming full source input closure. Do not reopen prior proven provenance gates or activate rear ISP based solely on offline byte parity.

## Verification and protection

verify.py checks committed aggregate/source/build locks. native-private.py compares clean production with original arithmetic privately on SP11. verify-private.py exercises the real full composer with both sanitizer compilers. Proprietary inputs, decompiler output and generated packet bytes stay private on SP11. A read-only NTFS inspection was unmounted without write/recovery. No new optical capture or Windows boot.

Golden boot208d6c65-0103-40e2-8ff4-fa25395f2534,7.1.5-sp11-render-parity-v4+, saved sp11-audio-fullio-v19c stayed idle. Protected Golden, accepted front27 frames and rear RAW/software fallback remain intact. No camera module/node/process, suspend/sleep, IR emitter, SecurePD weakening, MMIO, DMI or RT-CDM submission.
