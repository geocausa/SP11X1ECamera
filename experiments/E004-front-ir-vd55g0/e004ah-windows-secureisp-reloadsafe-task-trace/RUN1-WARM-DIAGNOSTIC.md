# E004ah run 1 — warm dynamic diagnostic

Status: **VALID DIAGNOSTIC / NOT ACCEPTED AS THE REQUIRED SECUREISP TASK TRACE**

Same-machine Windows IR holder completed two independent warm cycles:

- Surface IR Camera Front
- source kind Infrared
- stream VideoPreview
- subtype NV12
- 644x604 @ 60/1
- StartAsync = Success
- 12 TryAcquireLatestFrame() frames in each cycle
- normal gate release
- StopAsync PASS in each cycle

While cycle 1 was held live after the 12 real frames, SP7 KDNET showed no loaded
qccamsecureisp8380.sys; instead WinDbg listed it in unloaded modules at the last
observed range:

    fffff800a8090000 - fffff800a80cb000 qccamsecureisp8380.sys

Cycle 2 again delivered 12 real frames without a new SecureISP KMD load event.

Therefore the missing SecureISP KMD task activity is not in the ordinary repeated
warm frame loop. The KMD is short-lived earlier in boot/first-use setup. This
explains why prior absolute-RVA breakpoints became stale after relocation.

No class-1 task sequence, lane-mask transaction, or payload values are accepted
from run 1. Linux SecureISP runtime remains NOT AUTHORIZED.
