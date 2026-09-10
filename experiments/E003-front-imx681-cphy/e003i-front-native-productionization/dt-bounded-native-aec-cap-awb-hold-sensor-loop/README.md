# E003i-DT — bounded native AEC cap + AWB hold live candidate

Status: **PASS LIVE SIX-FRAME CAP AEC + AWB HOLD; GOLDEN RETURN PASS; CANDIDATE RETIRED.**

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

## Attempt 1 result

The one-shot executed once and passed all six generations with DQBUF sequences 0..5, three group-held sensor writes, producer-derived R5/R6, helper rc=0 and clean STREAMOFF. DS took the DQ/DR Windows-valid HOLD_PREVIOUS branch on G1..G3 and kept XY `0x3f1129ca/0x3f00e486`, published CCT 4999. Native AEC reached the DN-capped tuple `FLL=7116, exposure=7108, analogue=960, digital=1471` at G3 and remained valid through G6. The machine returned to Golden and the consumed candidate was retired. See `LIVE-PASS-ATTEMPT1.txt` and `RESULT.json`.

DT itself does not infer optical latency from the scene-dependent luma sequence. CY already provides the dedicated one-step sensor visibility measurement; the follow-on DU proof combines CY's N→N+2 measured boundary with DT's release points. Residual ISP gain remains unapplied, so continuous/full AEC parity is not claimed.
