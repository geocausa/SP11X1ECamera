# E003i-FA — Windows R12 AWB GainAdj same-request oracle

Status: **PASS — one Windows stream captured R4–R12; Golden return complete.**

FA extends the same-machine Windows AWB GainAdj/publication oracle through request R12. The holder performed exactly one front-camera stream; it initialized successfully, started once, stopped normally, and exited 0. CDB emitted extra R13–R18 command-file lines after the R12 terminal marker, but those were debugger control-flow artifacts from the same holder stream, not additional camera streams. The compact oracle deliberately keeps only paired R4–R12 rows.

The longer capture exposed a real historical EL limitation rather than a GainAdj mesh failure. EL had fixed EJ's slot-0/high reciprocal calibration because that was sufficient for the older EG sequence. Static reconstruction in FB recovered Windows' CAWBCtrlV1-to-CSFStatDistV1 calibration-slot selector from the pinned DeviceMFT and shipped tuning. The accepted same-run sequence is:

- R4: calibration slot 3, EJ high factor.
- R5–R12: calibration slot 5, EJ midpoint factor.

With that dynamic selector, FB replays EG 8/8 and FA 9/9 bit-exact for triangle/vertices, barycentric weights, nested CCT multiplier, final GainAdj RGB and published RGB. Published integer CCT remains recorded as observed output; it is not conflated with the internal GainAdj CCT trigger.

Safety/result: no register or IQ injection, no second Windows stream, normal holder stop, reboot to Golden Linux, persistent Golden GRUB unchanged, camera modules/nodes absent afterward. Raw Windows evidence is preserved outside Git under /home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fa/windows-r12-20260911.
