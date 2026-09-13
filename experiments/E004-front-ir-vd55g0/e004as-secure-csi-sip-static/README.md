# E004as — secure CSI SIP static decode

## Result

**PASS: the Windows SecureISP CSI lane-protection request has been reduced to a standard Qualcomm SIP/SCM-shaped call without executing it on Linux.**

E004z established that CameraSecureISP sends a QcTrEE PassThrough request before protected START and the inverse request after STOP. E004as resolves the previously opaque request header by combining the exact SecureISP KMD bytes, the QcTrEE PassThrough implementation, and Linux's Qualcomm SCM/SMCCC ABI definitions.

Linux SecureISP runtime remains **NOT AUTHORIZED**.

## QcTrEE ownership

Static analysis of the installed same-machine `QcTrEE.sys` shows:

- the PassThrough service dispatches its SIP request to `PassThroughServiceSipSyscall`;
- the first two request dwords are separated from the payload and forwarded as the first two low-level SIP call fields;
- the remaining request bytes are forwarded as the call arguments;
- the ARMv8 SIP path serializes the request and submits it to the platform secure-call interface.

This means the PassThrough service is a raw secure-call bridge for this request, not a camera-specific implementation itself.

## Exact SecureISP request shape

The installed `qccamsecureisp8380.sys` contains an 8-byte constant request header:

- dword 0: `0x02001807`
- dword 1: `0x00000002`

`ConfigSecureCamera()` then appends exactly two 64-bit values:

1. the protect/unprotect boolean;
2. the computed CSI lane-protection bitmask.

The second dword therefore matches the Qualcomm SCM two-value argument descriptor `QCOM_SCM_ARGS(2)`.

## SMCCC / Qualcomm decode

Linux's ARM SMCCC definitions decode `0x02001807` as:

- standard call;
- 32-bit SMC convention bit;
- owner 2 = SIP;
- function number `0x1807`.

Linux's Qualcomm SCM ABI splits the 16-bit function number with `SCM_SMC_FNID(service, command)`, giving:

- Qualcomm service `0x18`;
- command `0x07`.

The current 7.1.5 tree does not contain a symbolic service-0x18 definition or an in-tree wrapper for this service/command pair.

## Linux interpretation

The missing secure-lane operation is no longer an unknown Windows IOCTL semantic. It is an unmodeled Qualcomm SIP call carried by QcTrEE on Windows.

That narrows the Linux work substantially: a future parity implementation would need a camera-specific host bridge using the existing Qualcomm SCM machinery, but the service/command must remain dormant until runtime is separately authorized and a reversible test gate is designed.

E004as deliberately does **not** add or execute such a wrapper.

## Evidence

- `evidence/SMC-DECODE.txt` — exact installed-binary request bytes and SMCCC/Qualcomm field decode.
- `evidence/QCTREE-PASSTHROUGH-DECOMP.txt` — targeted QcTrEE PassThrough/SIP decompilation.
- `evidence/SECUREISP-CONFIG-DECOMP.txt` — targeted SecureISP `ConfigSecureCamera()` request construction.
- `evidence/LINUX-SCM-ABI.txt` — current Linux SMCCC and qcom_scm ABI references and negative service-0x18 wrapper search.

## Boundary

No qcomtee module was loaded, no `/dev/tee` object was opened, no secure call was issued, no camera memory was reassigned, and no CSI protection state was changed.

The next static gate is the SecureCompanion/trustlet addressing path: determine how Windows identity 4096 maps, if at all, to the Linux-visible trusted-application/service namespace. That remains independent from this SIP lane-control path.
