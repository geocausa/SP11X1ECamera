# E003i-GS — continuous scheduler shadow live candidate

Status: **PREPARING / UNARMED / NO GS CAMERA RUNTIME YET.**

GS is a safety bridge between the consumed GO bounded PASS and real continuous sensor-control writes. It runs GQ/GR's continuous queue/release logic at every exact DQBUF boundary, but physically writes only the already-proven G1/G2/G3 controls. Sources G4..G26 are released and logged in **shadow mode** with no sensor ioctl.

Success therefore proves that the continuous scheduler can keep exact live boundary ownership across the full R27 stream without increasing physical sensor-write exposure beyond GO. It does not authorize continuous physical writes.

Safety contract: fresh identity, one candidate boot, one camera stream maximum, consumed marker before stream, no same-boot retry, archive first, immediate Golden return and retirement.
