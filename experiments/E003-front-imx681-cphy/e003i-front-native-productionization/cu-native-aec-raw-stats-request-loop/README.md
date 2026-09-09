# E003i CU — native raw STATS3A → AEC request loop

CU closes the first raw-stat-to-request seam for the ordinary front IMX681 path without touching the sensor.

The accepted input is one generation-tagged `STATS3A` snapshot. CU validates its 64-byte producer envelope, derives the Windows-equivalent FrameSA measured luma from the raw AEC_BE grid, replays CT's BhistY statistics, runs CR's effective analyzers, and hands those candidates to CP's self-contained request recurrence.

The composed path is:

`STATS3A -> {AEC_BE, BHist} -> measured_luma + Bank4 {6,7,8,19} -> CR -> CP`

CQ/IMX681 control synthesis is deliberately **not** invoked by CU.

## STATS3A ABI

CU consumes the existing generation-tagged producer ABI already used by the bounded front runtime:

- total bytes: `331840` (`64 + 0x51000`);
- header magic: `0x54534133` (`3AST` little-endian on the wire);
- version `1`, header bytes `64`;
- AEC_BE plane: offset `0`, bytes `0x14000` within the raw payload;
- BHist plane: offset `0x14000`, bytes `0x1000`;
- AWB plane: offset `0x15000`, bytes `0x3c000`;
- valid flag bit 0 must be set;
- generation and source sequence must be nonzero, slot must be 0 or 1.

For this cold-owned uninterrupted loop, request frame `F` accepts producer `generation == source_seq == F+1`. A mismatched/stale generation is rejected before recurrence state changes.

## AEC_BE → measured luma

`native-stats3a.c` ports the AB path exactly:

`AEC_BE 32x32 -> ComputeLuma -> even checkerboard -> FrameLumaBE16x16 -> equally weighted mean`

The implementation pins the AB/Windows constants and operation order:

- R/G/B coefficient bits `0x3e991687`, `0x3f1645a2`, `0x3de978d5`;
- scale bits `0x3504655e`;
- 34-bit raw sum mask;
- `1980` pixels per channel;
- `(row+column)%2==0` source-cell selection;
- exactly two selected source cells per 16x16 output bin;
- float32 incremental bin mean;
- sequential float32 final weighted sum/divide.

The CU verifier generates twelve deterministic AEC_BE grids, including nonuniform random grids, and requires the native C result to match AB's already-Windows-backed `replay-measured-luma.py` float32 bits exactly. No local-only raw fixture is required for this differential.

## BhistY and cold-start zero domain

CT supplies the raw BHist replay and exact value axis. The CP-selected delayed history record supplies `Safe`, `S1`, and `PredGain` to CT.

CT proved a subtle startup rule: the synthetic start record has `PredGain=+0.0f`; Windows' flag-1 BhistY cap calculation therefore reaches `+inf` and then an exact `+0.0f` cap. Bank4:7 and Bank4:8 can consequently be exact zero on the first request.

CR's native input guard is extended in this checkpoint to accept zero (but not negative) values for those two Windows-valid inputs. Its arithmetic already has the correct behavior: SatPrev saturates through its method-2 mapping after the divide-by-zero path, while DarkPrev applies its configured `0.25f` luma floor. Existing positive-domain CR differential coverage is unchanged.

## CP history ownership

CU does not reimplement the Windows F-3 selection rule. CP now exposes `e003i_request_loop_get_history_offset()`, a non-mutating copy accessor around CP's existing private selector. CU requests offset 3 before calculating CT BhistY values.

CP's full verifier proves the accessor does not mutate state and that all existing 2,304 composed request cases remain byte-exact.

## Composition verification

The verifier generates four complete deterministic STATS3A frames. It executes each frame twice:

1. once through `e003i_raw_request_loop_process()`;
2. once as independent calls to `stats3a_open -> frame_luma -> CP history accessor -> CT -> FrameSA target -> CR -> CP`.

For every frame it requires byte equality of Bank4 output, CR target input, CP request output, and the complete post-request recurrence state. Key float32/qword outputs are also pinned, so a wiring change cannot pass merely because both paths share a helper.

The four-frame fixture is synthetic and chosen to remain within the proven T681 table. It is an integration fixture, not a claim that historical AP G1/G2/G3 captures form an AEC-controlled continuous sequence.

## Failure atomicity

CU verifies that recurrence state is unchanged when rejecting:

- a non-sequential request frame;
- wrong STATS3A byte count;
- generation/source-sequence mismatch;
- invalid AEC_BE channel counts;
- an empty BHist that cannot produce CR's required ShortSatPrev input.

## Safety boundary

CU is entirely offline. It does not open camera devices, stream, load camera modules, write sensor controls, invoke CQ, alter GRUB, or change the Golden boot state.

Next: join the accepted CU request output to CQ's IMX681 control adapter **offline first**, and prove request-to-control generation ownership before any new live camera run.
