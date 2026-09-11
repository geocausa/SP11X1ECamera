# E003i-FI — Windows R4–R15 Tintless/LSC oracle

Status: **STAGED / UNARMED / NO FI WINDOWS STREAM YET.**

FI extends accepted ED's exact request-labelled Tintless/trigger/final-staging oracle from R12 through R15. It uses the same proven DeviceMFT hooks, the same fail-closed Tintless layout checks, and the same single-stream gated holder.

The holder initializes but does not call StartAsync until both debugger hooks are armed. Entry and post-stage dumps are explicit decimal requests R4..R15. The R15 post hook writes the final staging, emits FI_CAPTURE_COMPLETE, clears breakpoints, closes the debugger log and detaches.

Acceptance after Windows capture is sequential clean-room replay R4..R15 through the existing native Tintless/DX LSC state machine and byte-exact comparison of LSC0/LSC1/LSC2/GIC to Windows staging.

Safety: direct Windows BootNext is one-shot. Persistent GRUB Golden remains unchanged. One Windows front-camera stream maximum for FI.
