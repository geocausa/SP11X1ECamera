# BA static proof anchors

- caller `0x1803b6740/0x1803b6750`: `GetExposureInfo(0/1)`.
- caller DRC diagnostic: `x7=+e8`, stack order `+f8,+f0` => Short/Safe/Long.
- `GetExposureInfo` destination: `0x1803d2104..2108`, `(type+0x1d)*8 = +e8+8*type`.
- aggregator VA `0x1803d2150`.
- `0x1803d217c..21a4`: `1.03^(Safe-DRCShort)` and `1.03^(Safe-Short)`.
- `0x1803d21b4`: policy from config `+0x30`.
- `0x1803d21ac..21c4`: DRC Long `+f0` -> normal Long `+a8` unconditionally.
- full DRC copy block begins `0x1803d227c` and maps `e8..118 -> a0..d0` in logical block order.
- policy-1 cascade: log of StretchRatio through shared reciprocal-log1.03 at `0x1803d23a4..23bc`, DRC Short minus that log at `0x1803d23f0..23f4`.
- diagnostics anchor policy branches: DRC-vs-stretch, predictive-gain consumption, cascade, stretch-only, DRC output, normal/predictive output.
