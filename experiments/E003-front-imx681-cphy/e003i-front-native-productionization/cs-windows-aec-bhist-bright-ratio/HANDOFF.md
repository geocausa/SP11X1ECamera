# Handoff after CS

CS is a static/offline ownership checkpoint. It proves ordinary `Bank4:6` (`SaturateStatsRatio`) is fixed calculator 4 `BrightRatio` API5 output lane 1 over the tuned BhistY value interval `[255,256]`, and pins the shared histogram/CDF consumption path.

CS deliberately does **not** claim the producer of the per-bin float32 value/luma axis at stats-record `+0x40`. No linear raw-bin-to-luma mapping is assumed.

## Next checkpoint

**CT — Windows AEC BHist value-axis provenance / native stats replay**

Resume by tracing the producer of stats-record `+0x40` used by `0x1803ea478`, then close the exact BHIST replay needed for Bank4 `{7,8,19}` and BrightRatio Bank4:6. Prefer static/offline work first; a one-shot Windows oracle is authorized if it materially shortens the proof. Do not start a new Linux camera runtime until the raw-stat → Bank4 adapter is verified offline.

## Durable state at handoff

- Parent CR commit before CS: `1ba395b`.
- Branch: `experiment/e003-front-imx681-cphy`.
- Golden kernel: `7.1.5-sp11-render-parity-v4+`.
- GRUB saved entry remains `sp11-audio-fullio-v19c`; `next_entry` is empty.
- No camera module load, STREAMON, sensor write, MMIO, or reboot was performed by CS.
