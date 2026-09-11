# E003i-GM — live-capable R5–R27 producer integration

Status: **PASS OFFLINE / live-capable path preserved / no GM camera runtime.**

GM is mechanically derived from GK's closed R25–R27 offline producer. It re-enables the preserved live CLI path and changes only manifest/console identity. The V4L2 control shim remains byte-identical to the accepted GG/GA shim.

Acceptance requires R5..R24 to reproduce consumed GI live capsules 20/20 byte-exact, R25..R27 to match GK closed hashes, and two independent runs to be deterministic. GL supplies the compiled G1..G24 gain publisher.
