# E003h 0073 — Demux/BLS dGain closure

Status: **accepted offline closure**. No Linux request6 was run.

A fresh read-only Windows stream captured the exact IFE `sensorData.dGain` at the primary IQ setup return for frames 4–6. Request6 used raw `0x3f8024b7` = `1.0011204481124878`.

The exact Surface Demux141 common calculation at RVA `0x998e70`, the Titan680 packer at `0xb42840`, and the decoded IMX681 default Demux/BLS14 region close the two remaining true scalar registers. For Bayer0 the decoded black-level terms are `602, 593, 592, 596` and the four channel terms are `1.0`. The calculation is `round(1024 × dGain × channel × 16383/(16383-BLS))`, with the exact per-channel Bayer0 ordering recovered from the binary.

For request6 this produces Q10 `1064,1064,1064,1064`, hence `0x3b70=0x04280428` and `0x3b74=0x04280428`. The independently captured same-stream request6 main contains exactly those values.

This closes all **8/8** genuinely calculated steady scalar fields. The scalar side is closed. Subsequent exact-binary proof in `GIC-WIRE-ALIAS-CLOSURE.md` reduces the independent changing Windows wire-LUT producer work to LSC and GTM; the Windows GIC DMI payload is an LSC alias. Bank-select/update fields remain separate state parity, not IQ math.

Raw Windows bytes/logs remain local/untracked. Derived oracle SHA-256: `6750e4d872f5d987ba3f7599b5dc4903d22d860d8104cd896498ef0739708539`.
