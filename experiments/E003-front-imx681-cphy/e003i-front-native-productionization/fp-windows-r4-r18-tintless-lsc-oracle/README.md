# E003i-FP — Windows R4–R18 Tintless/LSC oracle

Status: **STAGED / UNARMED / NO FP WINDOWS STREAM YET.**

FP extends FI's accepted request-labelled Tintless/trigger/final-staging oracle from R15 through R18 using the exact same proven DeviceMFT hooks and fail-closed Tintless layout checks.

The holder initializes the Surface Camera Front but does not call StartAsync until both debugger breakpoints are armed. Entry and post-stage dumps are explicit decimal requests R4..R18. The R18 post hook writes final staging, emits FP_CAPTURE_COMPLETE, clears breakpoints, closes the debugger log, detaches, and exits.

Acceptance after Windows capture is sequential clean-room replay R4..R18 through the existing native Tintless/DX LSC state machine and byte-exact comparison of LSC0/LSC1/LSC2/GIC to Windows staging.

Safety:
- direct Windows BootNext is one-shot;
- persistent Golden GRUB remains unchanged;
- exactly one Windows front-camera stream maximum for FP;
- no Linux camera runtime is performed by FP.
