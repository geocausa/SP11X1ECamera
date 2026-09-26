# E007i — rear LSC DMI handoff

Parent Git: `cca26cc5` plus E007h clean rear userspace LSC/Tintless producer.

Status: **COMPILE-ONLY PASS**.

E007h proves a production-shaped rear userspace producer that emits the two dynamic 884-byte LSC selector payloads byte-exactly for the validated OV13858 lower-AEC domain. E007i closes the corresponding kernel/materializer ownership boundary without moving adaptive IQ math into kernel space.

The handoff state contains an explicit request ID, selector-1 bytes, selector-2 bytes, and a two-bit validity mask. Materialization requires the state request ID to equal the caller's expected request; stale request data returns `-EPROTO`, incomplete selectors return `-EAGAIN`, and unsupported selector numbers fail.

E007i binds those selector bytes into E007f's LSC callback. E006g continues to derive the 512-byte GIC alias from the already-proven LSC byte ranges. BFStats25 remains bound through E007e. GTM/TMC and stable-family providers stay separate upstream dependencies and remain fail-closed.

## Build result — PASS

The complete E006/E007 provider chain, E007h clean rear userspace producer proof, and E007i request-tagged LSC handoff compiled in an isolated accepted CAMSS source copy.

- E007h producer proof: 15/15 requests byte-exact;
- selector-1 / selector-2 handoff: 884 bytes each;
- stale request IDs are rejected before dynamic materialization;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,760,912 bytes;
- SHA-256: `521a644e7f7556c0af11b247791285bce99fe0b3d099efb53ec3a060c846a0fd`;
- exact Golden vermagic;
- no install/load/camera/DMI/RT-CDM submission.

This is a compile-only ownership/integration checkpoint. It does not add a live camera path. Live rear TLBG/3A correlation and request scheduling remain open.
