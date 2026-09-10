# CX handoff

Parent: `b767514` (`camera: make IMX681 request controls atomic`).

Closed offline:
- Windows packet `F` ordinary hdrMode1 selection occurs at current SOF request `F-1`;
- selected packet is synchronously walked into KMD I²C submission before consumed-request bookkeeping;
- CW Linux output is one four-control `0x0104` group-held transaction;
- no additional software request queue has been identified after the selected apply call.

Still open:
- exact IMX681 group-hold release → first optically affected frame/generation.

Recommended next gate: clone AP's consumed-safe one-shot discipline into a fresh candidate using CW, perform exactly one mid-stream exposure step immediately after DQBUF sequence 0, retain paired 3A/BHist generations 1..6 plus QC10C frames and transaction timestamps, then return Golden without same-boot retry. Treat the run as diagnostic only; do not enable continuous AEC from it.
