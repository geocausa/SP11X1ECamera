# E003i-DT — bounded native AEC cap + AWB hold live candidate

Status: **PREPARED_UNEXECUTED.**

DT is a fresh disposable one-shot candidate after DP attempt1 exposed the previously uncaptured Windows AWB aggregate-zero behavior. It never reuses DP's consumed runtime identity.

Single live variable from DP attempt1: the helper, native AEC recurrence, DN internal CapExposure implementation, delayed three-write scheduler, atomic IMX681 control cluster, kernel modules, media setup and bootstrap are unchanged. The only producer change is AE -> DS. DS preserves previous AWB XY/CCT when DR reports DQ's Windows-proven zero-weight no-update condition.

Offline authority before arming:
- DN: 18 Windows cap pairs and 423 ARM64 arithmetic comparisons;
- DQ: pinned QcDeviceMFT8380.dll proves zero aggregate AGW weight -> (0,0) target -> previous AWB state retained;
- DR: six normal generations bit-exact to AD plus exact DP G1 HOLD_PREVIOUS;
- DS: normal R5/R6 capsule hashes unchanged, exact DP G1 held at XY 0x3f1129ca/0x3f00e486 and CCT 4999, hold path inside frame budget;
- CW IMX681 module hash/vermagic and inherited AI live safety gate must pass immediately before install/arm.

Safety boundary remains six ordinary front generations, at most three sensor writes behind exact DQBUF release gates, permanent fail-closed on any AEC/IQ/ownership/timing error, one helper invocation, no same-boot retry, and whole-machine Golden reboot after any post-STREAM failure. Golden remains the persistent GRUB default.

The purpose of DT is to get past DP's G1 producer abort and observe whether R5/R6 arrive in time while DN-controlled exposure evolves. It is still bounded evidence, not a claim of continuous automatic-exposure parity.
