# E003i-FH — recovered Windows R4–R18 AWB oracle

Status: **PASS — 15/15 bit-exact, no new Windows stream.**

FA's original extractor intentionally stopped its durable oracle at R12 even though the raw CDB log contained six additional complete same-stream GA/PUB pairs R13–R18. FH recovers those already-captured rows without changing FA history or running the camera again.

The pinned FA holder evidence proves exactly one Windows front-camera stream, normal START, normal STOP, and exit code 0. Its capture summary records requests 4..18, 30 raw GA/PUB rows, stream_count=1, and explicitly labels the post-R12 rows as same-stream CDB control-flow artifacts rather than additional streams.

FH treats the rows only as data already emitted at the real GainAdj/publication breakpoints. Replaying R4–R18 through FB's Windows-derived dynamic calibration selector and GainAdj implementation is 15/15 bit-exact for triangle/vertices, barycentric weights, nested CCT multiplier, final GainAdj RGB, and published RGB.

Result: AWB/GainAdj Windows differential authority now extends through R18 for this captured stream. No new Windows boot or camera stream was needed.
