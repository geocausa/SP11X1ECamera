# E003i-FP — Windows R4–R18 Tintless/LSC oracle PASS

Status: **CONSUMED ONE-SHOT WINDOWS PASS / GOLDEN RETURN PASS.**

FP extended FI's accepted request-labelled Tintless/trigger/final-staging oracle from R15 through R18 using the same proven DeviceMFT hooks and fail-closed Tintless layout checks.

Exactly one Windows front-camera stream was started. The holder reached WAIT_START before CDB attached, both breakpoints were armed against the single FrameServer QcDeviceMFT8380.dll process, then START.GO was created once. The holder reported START_STATUS=Success, STOP_PASS and exited 0. CDB captured R4..R18, emitted FP_CAPTURE_COMPLETE R=18, detached and exited 0.

Capture completeness:
- 15 Tintless stats dumps, each 0x12bec bytes
- 15 trigger dumps, each 0x100 bytes
- 15 final LSC staging dumps, each 0x18a0 bytes
- 15 entry hooks + 15 post-stage hooks
- bank parity 1,0,1,0,1,0,1,0,1,0,1,0,1,0,1

Native clean-room replay through the production Tintless/DX DynamicLsc state machine is 15/15 byte-exact for LSC0/LSC1/LSC2/GIC through R18.

The actual-used Windows holder additionally removed any stale START.GO marker before initialization. That is now canonical in this stage; oracle.cmd, entry.cmd and post.cmd matched the committed FP capture scripts exactly.

Raw evidence archive:
/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fp/windows-r4-r18-20260911

Windows evidence ZIP SHA256:
f20d931b92cabb2533aaeea9cd205b63af21ee9cbc7791c91a07a52961393197

No Linux camera runtime was performed by FP. The machine returned to protected Golden Linux after the one Windows stream.
