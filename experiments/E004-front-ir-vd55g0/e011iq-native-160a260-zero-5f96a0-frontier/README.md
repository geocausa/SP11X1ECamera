# E011IQ — native 0x160A260 zero to 0x5F96A0 frontier

PASS. The exact QcDeviceMFT8380.dll image is SHA-256 `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`. RVA `0x160A260` is file-static zero but resides in writable `.data`, so E011IQ used the Windows front-camera oracle rather than treating the file value as runtime authority. The qword was zero both after front-only initialization and after one successful NV12 1920x1080 front reader start. The original `0x5F968C` load therefore yields zero and `0x5F9690` takes the branch to `0x5F96A0`; execution stops before `0x5F96A0`.

One bounded Windows one-shot and one front reader Start were used. Rear runtime remained denied; no rear Start or kernel build occurred, and the machine returned to Golden Linux.

NEXT E011IR advances source-exactly from `0x5F96A0` through already-owned stack/buffer-backed publication state and stops at the first genuinely new dependency.
