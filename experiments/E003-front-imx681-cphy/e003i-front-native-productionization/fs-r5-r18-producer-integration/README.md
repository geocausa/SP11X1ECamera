# E003i-FS — live-capable R5–R18 producer integration

Status: **offline candidate / no FS camera runtime.**

FS extends FL's exact live-capable producer loop from G1..G12 to G1..G15. The production scheduler, control shim, gain-feed path, dynamic AWB, Tintless/LSC state machine, IQ composer, deadline-sensitive live submission path, and failure evidence path are otherwise preserved.

Offline acceptance requires:

- R5..R15 reproduce the real FN live capsules 11/11 byte-exact with key metadata.
- R16..R18 match FQ-authorized capsule hashes exactly.
- two independent offline runs are deterministic.
- FR supplies the real compiled G1..G15 gain publisher.

No camera runtime is performed by FS itself.
