# E003h priming / CSID / MIPI cross-order oracle

Date: 2026-08-29

Two independent same-machine Windows front-camera starts close the two placement gaps left explicit by Linux `0030`.

Raw KD log: `E003H_PRIMING_MIPI_CROSSORDER_20260829.log`, 7,420 bytes, SHA-256 `06127e46dca5759cfded698b1a1a8dc0dcd40dd04ca271d515a54fbed42987ee`.
Extractor SHA-256: `ff4397b20f1019f52f7ff6d716236e055441d8b60bd2ee191151f196289b140b`.
Derived oracle SHA-256: `849687aaa5206c25484b9a6e015aba320d7d01610d5292a33df54605f20ae599`.

Both cycles reproduce the same start sequence:

`replay0 (0xe94) -> replay1 (0xe34) -> CSID1 start -> ISP_START_DONE -> MIPI/CSIPHY start enter -> MIPI/CSIPHY start done -> sensor MODE_SELECT=1 apply -> replay2 (0x904) -> replay3 (0x4e8) -> first steady 0x958 batch`.

The replay identities are recognized by the already-closed selector-2 main-list encoded lengths at the exact RT-CDM consumer. CSID start is the exact qccamisp DEVICE_START callsite; MIPI entry/completion and sensor apply reuse the previously SHA-pinned lifecycle anchors.

This proves replay0/1 precede CSID1 start, and replay2/3 occur only after MIPI start and sensor stream-on. It does **not** yet order replay0/1 against the already-proven host prefix `packet0 -> packet1 -> BUS prepare -> packet2 -> packet3`; all six events are known to precede CSID1 start but their mutual interleave is not yet captured. That is the remaining pre-start ordering question before a callable Linux PIX runner.

No Linux camera candidate was loaded during this oracle. The SP11 returned by normal reboot to saved/default Golden `sp11-audio-fullio-v19c` with empty `next_entry`.
