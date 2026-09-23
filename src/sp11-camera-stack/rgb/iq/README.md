# Full-precision RAW10 pixel interpretation (offline only)

The accepted front and rear RAW-to-NV12 publishers currently extract
only the first four (upper-eight) bytes of each MIPI RAW10 five-byte
group. E004mc/E004md therefore could not verify what the discarded
2-bit planes contain or whether an uncalibrated optical black level
removes the little remaining visible scene signal.

`raw10_unpack.h` is a stand-alone, strict, 10-bit row-pixel primitive
for both front 3840x2160 pRAA and rear 4076x2806 pgAA. It preserves
the low two bits, validates group/stride limits and never opens a device
or changes the accepted output path. Use it as the basis for a fresh
source-pinned, bounded in-memory per-channel source/black-level and
RAW-to-NV12 analysis; do not infer black level, lens occlusion or colour
accuracy from upper-8-bit percentiles alone. No existing Golden or
one-shot live publisher is modified by this offline component.
