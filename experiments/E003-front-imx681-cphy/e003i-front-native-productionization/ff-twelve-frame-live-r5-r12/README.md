# E003i-FF — fresh bounded twelve-frame R5–R12 live candidate

Status: **STAGED OFFLINE / UNARMED / NO FF CAMERA RUNTIME.**

FF is the fresh successor to consumed EZ. It combines FE's twelve-frame transport, FC's compiled G1..G9 gain-feed publisher, FD's corrected R5..R12 producer with FB dynamic AWB calibration-slot selection, CW IMX681 controls, the unchanged R4 bootstrap, and the unchanged three-write delayed sensor schedule.

Safety contract: install unarmed; protected Golden remains persistent; exactly one candidate boot and at most one twelve-frame stream attempt; no same-boot retry; preserve evidence and reboot to Golden on either PASS or failure. This stage does not claim continuous/unrestricted AEC.
