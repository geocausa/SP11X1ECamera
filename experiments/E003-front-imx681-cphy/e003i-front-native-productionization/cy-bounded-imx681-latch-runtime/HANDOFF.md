# CY handoff

Status: READY / UNEXECUTED / UNARMED.

Parent facts:
- AP: live group-held IMX681 controls and paired generations 1..6 passed, Golden return passed.
- CW: one four-control atomic cluster, exact Windows register bytes, full verifier passed.
- CX: Windows packet F is selected at SOF F-1 and synchronously walked into I2C submit; optical label remains open.

Runtime protocol:
1. install candidate while Golden and unarmed;
2. commit/checkpoint candidate scripts before arming;
3. arm exactly once with `arm-once.sh`, reboot;
4. on candidate boot: `load.sh`, `prepare.sh`, `invoke-once.sh` exactly once;
5. archive evidence; do not retry on the same boot;
6. reboot to saved Golden and run `golden-return-check.sh`;
7. only then interpret `runtime-output/LIVE-RESULT.json` together with CX.

Control step: sequence0 completed -> one atomic S_EXT_CTRLS -> FLL3554 / exposure1000 / again64 / dgain272.
