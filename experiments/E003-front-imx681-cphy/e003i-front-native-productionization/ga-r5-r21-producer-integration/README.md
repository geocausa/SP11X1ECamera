# E003i-GA — live-capable R5–R21 producer integration

Status: **PASS OFFLINE / live-capable path preserved / no GA camera runtime.**

GA is mechanically derived from FV's closed R19–R21 offline producer. It re-enables the already-preserved live CLI path and changes only the manifest/console identity. The V4L2 control shim is byte-identical to FS.

Offline acceptance requires:

- R5..R18 reproduce the consumed FU live capsules 14/14 byte-exact;
- R19..R21 match FV's closed deterministic capsule hashes exactly;
- two independent runs are deterministic;
- the producer maps G2..G18 to R5..R21;
- FZ supplies the compiled G1..G18 gain publisher;
- the GA Python source normalizes exactly back to FV after removing only the live-mode/identity delta.

No camera runtime is performed by GA itself.
