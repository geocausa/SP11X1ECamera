# DK handoff

DK is offline evidence hardening for the next bounded DB diagnostic candidate.

Before another live run: commit/push DK + DB attempt3 evidence, require a clean-tree full root prearm, reinstall/arm the disposable DB candidate, and repeat candidate identity/load/prepare gates. Launch `invoke-once.sh` as a persistent PiMaster job, not a finite-time execute command.

If G4 again returns `-142`, do not retry. Require `TLBG-FAIL-G4.bin` and `STATS3A-FAIL-G4.bin`, archive/hash them, then reboot normally to Golden. Only after Golden return should the exact G4 pair be replayed offline to determine the Short-T681 target and upstream state responsible for the overflow.

## Consumed diagnostic retry

Attempt4 executed via persistent PiMaster job and saved the G4 pair successfully. Golden return and candidate retirement passed. Continue at ../dl-native-aec-g4-failure-replay/HANDOFF.md; do not repeat the consumed DB candidate.
