# Stable front-IMX681 IQ runtime

`live-iq-producer.py` is the GM R5..R27 producer with **path binding only** relocated into this stable tree. The live V4L2 shim is byte-identical to GM.

HG adds a miniature vendored source root and an explicit SHA-pinned authority-cache contract. `prepare-authority-cache.py` copies the 79 required repo-local data inputs plus the one local IMX681 tuning blob into an ignored cache after verifying every byte. The cache is **not committed**, and the proprietary tuning blob remains local.

After cache provisioning, two independent offline replays reproduce R5..R27 23/23 byte-exact and `strace` proves the producer opens no project-local path outside this stable IQ root. This makes the runtime path-relocatable, but not yet a fully redistributable clean-room package. HH will reduce the local cache to clean decoded/derived runtime authority.
