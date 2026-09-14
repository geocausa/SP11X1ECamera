# E004dh Windows oracle — normative tuning state

**Authority rule:** live behavior captured from the shipping Windows SP11 camera stack is normative for E004dh. Decompiled code, Qualcomm source and firmware analysis are explanatory only. If any secondary source disagrees with Windows, Windows wins.

A bounded Boot0006 Windows run used the accepted Surface FaceAuth IR profile (`644x604 NV12 @ 60 fps`) with FaceAuthMode and SecureMode enabled. Twelve frames were acquired and the stack was stopped/disabled cleanly before returning to Golden Linux.

The live Camera Frame Server instance hosting the exact shipping `QcDeviceMFT8380.dll` was inspected read-only while that protected IR stream was active. Its SHA-256 was `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35` (file version `1.0.4258.7908`).

## SWABF

Windows selected:

- threshold = `128` (`0x43000000` as the cached float);
- weights = `2000,1990,1960,1911,1846,1670,1452,1213,973,750,556,395,270,177,142,112`.

The exact Windows packing routine converts these to 16 little-endian signed 16-bit weights followed by one signed 16-bit threshold. The resulting 0x22 payload is preserved as `oracle/windows-live/SWABF-derived-from-live-cache.bin`, SHA-256 `8443115a763d9f5e425cdf7415250f129bad6f028e1b1c18ade86c17a4f392aa`.

The live common CamX request block directly showed SWABF enable/change set, so these are not merely dormant/default tuning values.

## SWASF

Windows selected two 64-point source curves and final value `253.0f`. The shipping Windows `GetSWASF101Data` code expands those curves into two 256-dword tables. The exact resulting 0x804 bytes are preserved as `oracle/windows-live/SWASF-derived-from-live-cache.bin`, SHA-256 `6cc727315a8d640ab40211f031efdfe28f12e8f2be90f8c8a3a785bb63ccfc0c`.

A read-only scan of the live Frame Server found exactly one full byte-for-byte match for that 0x804 payload. The surrounding live `pInputData` block was also preserved and directly shows the SWABF values, SWABF change flag, SWASF table, SWASF final value and SWASF change flag in one request-local object.

This closes the tuning-value ambiguity. The remaining E004dh work is the SWASF pixel transform itself, not tuning selection.
