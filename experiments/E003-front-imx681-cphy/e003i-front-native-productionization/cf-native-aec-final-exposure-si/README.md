# E003i CF — native final exposure SI publication

Status: **PASS (native/offline)**.

CF composes the CE ordinary/default final target producer with the Windows final analyzer publication rule. SafeAggSA, ShortAggSA and LongAggSA all use tuning `sourceType=3`, which Windows maps to the S1 source lane. Their positive phase-2 arithmetic publications are the already-proven float32 AdjRatios.

For each final lane Windows performs:

`qword exposure = FCVTZU(double(S1) * double(float32(AdjRatio)))`

The native API deliberately accepts S1 as `uint64_t`, matching the existing BK native request-state representation, then converts it to double only at this publication boundary. The verifier covers integer values around `2^53`, where uint64-to-double is no longer exact, so this is not merely a small-integer equivalence test.

The result is the ordinary DefaultSequence Short/Long/Safe qword target tuple that feeds the convergence path. No camera module load, stream, sensor write, MMIO, Windows boot or reboot is used.
