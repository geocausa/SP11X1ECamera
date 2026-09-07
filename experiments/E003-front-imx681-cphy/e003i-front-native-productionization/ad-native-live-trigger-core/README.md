# E003i-AD — native live Lux/CCT trigger core

Status: **PASS (offline differential/deadline proof; no camera runtime).**

Stage AC closed the clean request-local AWB/CCT model, but the Python implementation takes roughly 29 ms for G2/G3 on SP11. Combined with Stage X's arbitrary-trigger LSC path that is too close to or above the 33.33 ms frame budget. AD translates only the already-closed hot trigger path to strict C: AEC_BE measured-luma, Algorithm001 Lux, AWB P01/P03/P04/P05/P09 and AGW fresh XY/CCT.

The native code does not contain the proprietary P03 engine/anchor blobs or P04/P05 leaf tables. The differential harness supplies the local SHA-pinned Stage-AC fixtures at runtime. It builds with `-fno-fast-math -ffp-contract=off -Wall -Wextra -Werror`.

## Bounded baseline contract

Algorithm001 requires a dynamic history Lux baseline. The accepted six-frame Linux runtime does not issue per-frame sensor exposure/gain controls; IMX681 gain is programmed once by the mode table. For the **bounded** R4/R5/R6 integration proof, AD therefore seeds the history baseline from the authoritative W request4 Lux (`0x43b302c7`) and keeps that exposure-history reference fixed while G1/G2/G3 are evaluated. This is deliberately not a claim of a complete continuous AEC implementation.

## Differential result

Using the retained Z generation-tagged Linux 3A snapshots, every native output field is bit-exact to the committed AB/AC Python oracle for G1..G6: measured luma, Lux, AGW X/Y, fresh CCT, accumulated weight, P01 count and valid count. Under the bounded seed, G2/G3 fresh CCT are about 5150.35 K / 5139.10 K.

The accepted G2/G3 trigger timing is orders of magnitude below one frame. See `RESULT.json` for exact p95/p99 numbers. This leaves the deadline dominated by the already-proven Stage-X native Tintless/LSC path.

## Safety/classification

- source generation is not a request ID;
- W mapping remains R5<-G2 and R6<-G3;
- no kernel ABI is added;
- no camera runtime is executed here;
- continuous dynamic AEC is not authorized by this checkpoint;
- next gate is one bounded producer -> existing deferred V4L2 IQ FIFO integration proof.

Reproduce on Golden Linux with readable copies of the six Z snapshots:

```sh
./prove-native-trigger-core.py --snapshot-dir /tmp/e003i-live3a-bench --baseline-bits 0x43b302c7
```
