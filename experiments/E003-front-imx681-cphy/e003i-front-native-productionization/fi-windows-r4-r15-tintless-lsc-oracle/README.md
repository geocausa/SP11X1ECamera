# E003i-FI — Windows R4–R15 Tintless/LSC oracle

Status: **PASS_WINDOWS_ORACLE / CLEANROOM R4–R15 12/12 BYTE-EXACT / GOLDEN RETURN PASS.**

FI extended accepted ED's request-labelled Tintless/trigger/final-staging oracle from R12 through R15 using the same proven DeviceMFT hooks and fail-closed Tintless layout checks.

Exactly one Windows front-camera stream was performed. The holder initialized, waited for both debugger hooks, started once, stopped normally and exited 0. CDB attached to the sole FrameServer process hosting QcDeviceMFT8380.dll, captured R4..R15, emitted FI_CAPTURE_COMPLETE at R15, detached and exited 0.

Each request captured:
- 0x12bec-byte Tintless stats object
- 0x100-byte trigger block
- 0x18a0-byte final IFELSC411 staging

Sequential clean-room replay through the existing native Tintless core + DX DynamicLsc state machine is **12/12 byte-exact** for LSC0, LSC1, LSC2 and GIC. Bank parity is exactly 1,0,1,0,1,0,1,0,1,0,1,0.

R13, R14 and R15 therefore close the post-R12 Tintless/LSC differential-authority gap. No Linux camera runtime occurred in FI.

Windows evidence archive:
/home/geoca/Documents/SP11-PROJECT/00-RE-archive/e003i-fi/windows-r4-r15-20260911

Sealed Windows ZIP SHA256:
8650b0834832a7a95f3c70a5990361660f9ddc0b79ba49b691b2e92c97ffdac3

Final Linux archive MANIFEST.sha256 file SHA256:
eda7b5339be0788c0505be7ae77f530f7f73475ca56579efd7f1c3f20296242d

Tracked RESULT.json SHA256:
21ae1b2d67f8228c7247419dc6ef1f179d193ecb9358a94f281030ae94610293

Golden-return SHA256:
99d92d778f8d16d2cbfe094d81d3c8f121907285ff6511c05a25b87cd48b87c1

This stage proves bounded Windows differential parity through R15. It does not claim unrestricted continuous AEC.
