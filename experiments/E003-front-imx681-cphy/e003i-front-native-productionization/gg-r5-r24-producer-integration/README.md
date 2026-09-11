# E003i-GG — live-capable R5–R24 producer integration

Status: **PASS OFFLINE / live-capable path preserved / no GG camera runtime.**

GG is mechanically derived from GE's closed R22–R24 offline producer. It re-enables the preserved live CLI path and changes only manifest/console identity. The V4L2 control shim remains byte-identical to GA.

Acceptance requires R5..R21 to reproduce the consumed GC live capsules 17/17 byte-exact, R22..R24 to match GE's closed hashes, and two independent runs to be deterministic. GF supplies the compiled G1..G21 gain publisher.
