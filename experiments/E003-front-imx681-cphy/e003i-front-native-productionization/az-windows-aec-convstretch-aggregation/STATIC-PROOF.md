# AZ static proof anchors

## Request-local type-12 lookup
- `0x1803b5bb4`: controller `+0xdf50`.
- `0x1803b5bbc`: request-key lookup helper `0x1803d4968`.
- `0x1803b5bd4`: result -> convergence `+0x2f8`.

## ComputeTargetStretchOutput (`0x1803cecc8`)
- `0x1803ced04`: ConvStretch `+0x14` active count.
- `0x1803ced10`: zero convergence `+0x128` batch head.
- `0x1803ced58`: entry stride `0x30`.
- `0x1803ced60`: entries pointer ConvStretch `+0x20`.
- trigger descriptors: entry `+0x04,+0x0c,+0x14` via `0x1803d2da8`.
- `0x1803cedac`: entry `+0x18` stretchType.
- `0x1803cf484..5cc`: interpolated core -> runtime `0x14` record.
- runtime record: Weight `+0`, FinalOff `+4`, Comp `+8`, tempWeight `+c`, sign `+10`.
- inline constants `0x1803cf9f8=0x33d6bf95`, `0x1803cf9fc=0x3f83d70a`.

## AggregateStretchOutput (`0x1803cfa00`)
- ConvStretch `+0x28` aggregation type (`0x1803cfa38`).
- ConvStretch `+0x14` count (`0x1803cfa3c`).
- ConvStretch `+0x10` direction mode (`0x1803cfb58`).
- aggregation type compared with 5 at `0x1803cfbd4`; >=5 invalid diagnostic.
- mode 0 weighted accumulation: `0x1803cfd78..da8`; normalization `0x1803cfddc..e0c`.
- modes 1/2 vs 3/4 comparator field selection: `0x1803cfe28..eb8`.
- full qword/sign record swaps: `0x1803cfec8..f14`.
- selected record copy to output: `0x1803d0194..1a0`.
- fallback: `0x1803d01a8..1b4` -> offset 0, comp 1, tempWeight .5.

## Post-aggregate / lanes
- history(1) previous delta `+0x17c`: `0x1803cf6d4..6e0`.
- weighted temporal filter: `0x1803cf6f0..700`.
- `FRINTA` quantizer call `0x1803cf75c -> 0x1800014d0`.
- negative-stretch predictive gain pow path: `0x1803cf76c..784`.
- Short update: `0x1803cf830..840`, convergence `+0xa0`.
- Safe update: `0x1803cf844..84c`, convergence `+0xb0`.
- `predGain,shortStretch -> +0xd8,+0xdc`: `0x1803cf850`.
- final log call loads Short from `+0xa0`, then stack ABI orders Safe from `+0xb0`, Long from `+0xa8`.
