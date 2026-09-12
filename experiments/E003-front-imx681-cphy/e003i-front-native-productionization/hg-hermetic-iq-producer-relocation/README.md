# E003i-HG — relocatable IQ runtime with local authority cache

Status: **PASS OFFLINE / no camera runtime.**

HF froze the exact GM producer source but it still imported the experiment tree directly. HG moves the live/offline IQ runtime onto `src/front-imx681/userspace/iq/` and gives it a miniature vendored source root. The stable producer differs from GM only in root/path binding; the live V4L2 shim remains byte-exact.

A successful original GM offline run was traced to close the real runtime dependency set. That revealed 79 repo-local data inputs plus one external SHA-pinned IMX681 tuning blob. HG does **not** commit those local/proprietary bytes. `prepare-authority-cache.py` verifies every input by size/SHA and copies them into an ignored local cache underneath the stable IQ root. After provisioning, `strace` proves the producer opens no project-local path outside the stable IQ root.

Two independent stable-producer replays reproduce **R5..R27 23/23 byte-exact** against the accepted GM authority, including R5..R24 live regression and GK-authorized R25..R27 continuation. No camera device is opened.

This is deliberately not yet called a fully redistributable clean-room package: the ignored cache still includes the local proprietary tuning blob and local oracle-derived data. HH should collapse that cache into the minimum clean-room runtime authority (decoded constants/derived state only) before production launcher/install work.
