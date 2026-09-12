# E003i-HW — production boot-bundle + fail-closed activation preparation

Status: **installed / unarmed / no runtime**.

HW is the first production-style boot bundle built on the HV current-Golden DTB. The exact candidate is now installed under `/boot/sp11-7.1.5-camera-e003i-hw-prod-activation` but remains unarmed (`next_entry` empty). The candidate preserves the protected Golden kernel and initrd byte-for-byte and preserves the Golden kernel command line in order, changing only `sp11_entry` and adding the explicit camera-module blacklist plus fresh one-shot activation token. Unlike the historical disposable candidates it does **not** use `firmware_class.path=`.

The production package is current HR/HS authority (manifest `57aa9cc2...66a5a757`) while CAMSS and IMX681 modules remain exact HN binaries. Boot is fail-closed: camera modules are blacklisted, and `runtime-preflight.sh` requires the fresh token, candidate boot image, clean Git/origin, empty `next_entry`, exact installed HV DTB and intact package before `load.sh` may insert private modules.

If later authorized by the checkpoint sequence, `load.sh` is limited to module binding plus dynamic production topology discovery. **It does not stream.** There is no same-boot activation retry authority. Golden return and candidate retirement helpers are prepared in advance.
