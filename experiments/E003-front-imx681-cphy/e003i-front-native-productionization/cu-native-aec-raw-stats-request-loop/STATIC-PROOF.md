# CU static / mechanical proof

## 1. Producer envelope

The existing `z-live-3a-runtime/e003i-z-six-frame-stats.c` defines and validates the same ABI consumed by CU:

- `STATS3A_HEADER_BYTES = 64`;
- `STATS3A_AEC_BYTES = 0x14000`;
- `STATS3A_BHIST_BYTES = 0x1000`;
- `STATS3A_AWB_BYTES = 0x3c000`;
- `STATS3A_MAGIC = 0x54534133`;
- raw offsets `0`, `0x14000`, `0x15000`;
- valid bit 0;
- generation/source sequence nonzero and slot `<2`.

`native-stats3a.c::e003i_stats3a_open()` reproduces those structural checks before exposing plane pointers. CU additionally owns the cold-loop association `generation == source_seq == frame_id+1`, preventing a stale producer snapshot from advancing CP state.

## 2. AEC_BE measured-luma authority

AB already proved the normal front path live/bit-exact against Windows:

`AEC_BE 32x32 -> CAECXCoreGridStatsOut::ComputeLuma -> checkerboard -> FrameLumaBE16x16 -> FrameSA analyzer 2 -> 2-D meter bank 1 Equally Weighted`.

Pinned AB facts consumed by `native-stats3a.c`:

- input grid 32x32, output 16x16;
- input bit depth 18, output bit depth 8;
- 1980 pixels/channel;
- RGB coefficient bits `3e991687 / 3f1645a2 / 3de978d5`;
- scale bits `3504655e`;
- selected mask intersects FrameLuma descriptor `0x10` and not the other descriptor `0x02`;
- selected parity `(row+column)%2==0`;
- 512 selected cells, two per output bin;
- producer bin update is float32 incremental mean;
- FrameSA reduction is sequential float32 weighted sum then float32 divide.

CU differential-generates twelve AEC_BE grids and compares the native C output to AB's committed replay function bit-for-bit.

## 3. Raw BHist → Bank4 authority

Parent CT commit `9a3b9fa` owns:

- parser mask `0x01ffffff`;
- exact 1024-entry BhistY value axis;
- ARM CDF reciprocal/Newton instruction semantics;
- Bank4:6 BrightRatio CDF mass;
- Bank4:7 SatPrevHighPCTLLuma;
- Bank4:8 DarkPrevLowPCTLLuma;
- Bank4:19 ShortSatPrevHighPCTLLuma;
- runtime flags `{6:1,7:1,8:1,19:0}` at their producers;
- ordinary source tag `3 = S1`;
- history cap law using delayed Safe/S1/PredGain;
- synthetic-start `PredGain=+0.0f -> flag1 scale +0.0f` behavior.

CU calls CT directly on the BHist plane and does not approximate or translate the value axis.

## 4. CR startup-domain extension

CT makes Bank4:7/:8 exact zero a valid ordinary startup state. The prior CR guard was stricter than Windows and rejected those values before its already-proven formulas ran.

CU changes only that domain guard:

- `sat_prev_high_pctl_luma >= 0` is accepted;
- `dark_prev_low_pctl_luma >= 0` is accepted;
- negative values remain rejected;
- `short_sat_prev_high_pctl_luma` remains strictly positive.

The CR reference model naturally reproduces the zero case using IEEE float32 division. Its differential verifier now includes the CT-proven startup vector in addition to the existing 28 boundary and 8192 random positive-domain cases.

## 5. CP delayed-history seam

CP already owns the exact history selection logic in its private `history_get_offset()` implementation. CU adds only a public copy accessor:

`e003i_request_loop_get_history_offset(state,current_frame,offset,out)`.

The accessor:

- requires the caller's frame to equal CP's `next_frame_id`;
- delegates to the existing selector;
- copies the selected entry to caller storage;
- does not advance, modify, or commit recurrence state.

CU asks for offset 3 and passes the returned `Safe/S1/PredGain` directly to CT plus delayed Short directly to CR's Illuminance input.

## 6. Mechanical composition

For each accepted frame CU performs, in order:

1. validate STATS3A and generation ownership;
2. select CP delayed history offset 3;
3. derive measured luma from AEC_BE;
4. derive CT Bank4 `{6,7,8,19}` from BHist and the same delayed history;
5. derive the current FrameSA target from CP's current Lux trigger;
6. run CR with measured luma, frame target, delayed Short and CT Bank4;
7. copy CR's non-Frame analyzers into CP request input;
8. run CP, which alone commits the new recurrence state.

The verifier independently executes the same primitive calls outside the wrapper and requires byte-identical intermediate outputs and final `e003i_request_loop_state` across four generated frames.

## 7. Pinned four-frame integration fixture

The deterministic fixture uses BHist bin 700 with total count 2,073,600 and AEC uniform-sum sequence:

`101375995, 93265916, 91200000, 90000000`.

Pinned outputs are:

| F | measured luma bits | Bank4 6/7/8/19 bits | Lux in | next Lux | retained Short / Safe / S1 |
|---|---|---|---|---|---|
| 0 | `42480000` | `00000000 00000000 00000000 423c8081` | `4365b24a` | `4365b24a` | `197890639 / 211553009 / 197890639` |
| 1 | `42380000` | `00000000 423c807f 423c8080 423c8081` | `4365b24a` | `43926342` | `315897325 / 347299339 / 315897325` |
| 2 | `4233ecaa` | `00000000 423c807f 423c8080 423c8080` | `43926342` | `4392c441` | `504230670 / 563178231 / 504230670` |
| 3 | `42318ea5` | `00000000 423c807f 423c8080 423c8080` | `4392c441` | `4392fd9b` | `723655354 / 820289070 / 723655354` |

PredGain is `0x3f800000` on all four CP outputs.

## 8. Failure atomicity and safety

The verifier snapshots the complete CP state and requires byte equality after deliberate failures for wrong frame, wrong snapshot size, stale generation, bad AEC counts, and empty-BHist/CR rejection.

CU has no CQ dependency and no code path that opens a V4L2 node or writes IMX681 controls. It is therefore safe to verify on Golden Linux without loading or starting the camera stack.
