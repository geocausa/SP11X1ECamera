# E003d pre-runtime result

Status: **BUILD IN PROGRESS / runtime not yet performed**.

Already proven:
- exact Windows X1E C-PHY table boundary: 121 records at local driver raw offset `0xf650`;
- 118/118 unique final register values match both independent KD live snapshots;
- Linux translation preserves all ordered writes, zero writes, duplicates and delays;
- one-trio lane mask is `0x02`, matching Windows live common CTRL5;
- Windows live/common CTRL7 is `0x7a`; X1E C-PHY Linux path carries that value while D-PHY retains `0x02`;
- DT adds only the symmetric IMX681 ↔ CSIPHY2 C-PHY one-trio graph and intentionally no link-frequency.

No E003d boot has been installed or armed at this checkpoint.
