# E004lg RGB route-policy offline acceptance

Self-contained src/sp11-camera-stack/routing includes the byte-identical accepted119-edge graph contract plus explicit RGB path admission and a transaction engine. Eleven tests cover all240 shortest paths across three sensors, nine phase transitions, topology/flag asymmetry, invalid targets/pads, missing exclusive/quiescent ownership, every write-failure position (including uncertain success), stale graph before each write, no-effect writes, cancellation and lost ownership.

All admitted camera changes pass through neutral with downstream-first disconnect and upstream-first connect. Full graph structure and enabled flags are checked before/after every mutation. Failures poison the controller and permit no retry or speculative rollback.

No OS/device backend exists. Tests use memory graph snapshots derived from E004le metadata; no physical experiments repeated, no installs or boot changes. This is not libcamera integration or runtime safety certification. A native adapter must provide fresh kernel reads, current-boot/session identity and actual exclusive/quiescent ownership. Libcamera cached MediaLink flags cannot substitute for those reads.
