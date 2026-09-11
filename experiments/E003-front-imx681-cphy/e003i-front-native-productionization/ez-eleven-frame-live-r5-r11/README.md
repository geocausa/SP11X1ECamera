# E003i-EZ — fresh bounded eleven-frame R5-R11 one-shot candidate

Status: **STAGED OFFLINE ONLY / NO EZ CAMERA RUNTIME YET.**

EZ combines only already-proven fresh stages: EY's eleven-frame transport, EW's real compiled G1..G8 CQ gain publisher, EX's R5..R11 producer, CW IMX681 controls, the unchanged R4 bootstrap, and the unchanged three-write delayed sensor schedule.

Offline authorities before arming are strict: EY must remain PASS with CAMSS W=1 and helper Werror; EW must accept G1..G8 and reject G9; EX must reproduce EV R5..R9 5/5 and deterministically compose R10/R11 from EV's actual G7/G8 Linux state. No new Windows stream is needed because EB/ED cover GTM/LSC through R12 and EL/EG cover AWB/GainAdj through R11.

One candidate boot may perform at most one camera stream attempt. Any failure is archived and requires whole-machine Golden return. A PASS proves bounded eleven-frame integration only, not unrestricted continuous AEC.
