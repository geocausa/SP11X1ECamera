# E003i n — Titan680 Tintless-BG raw parser

This static/offline checkpoint closes the raw VFE Tintless-BG format used by the Surface X1E/Titan680 path.

The exact SHA-pinned `QcDeviceMFT8380.dll` contains `CamX::TitanStatsParser::ParseTintlessBGStats`. Its config helper at RVA `0x5f07b8` recognizes hardware version `0x60800` (Titan680), forces parsed flags `3`, and the special parser helper at RVA `0x5f23a0` consumes exactly `0x50` raw bytes for each Tintless region. Front geometry is 32×24 = 768 regions, so one required raw client-13 parser snapshot is exactly **`0xF000` bytes (61,440)**. Later handoff text accidentally wrote `0x25800`; `PARSER-PROOF.json` and the parser implementation always retained the correct 61,440-byte authority.

`prove-titan680-tlbg-parser.py` constructs a deterministic raw preimage from each bounded Windows parsed x2 fixture, runs the clean parser forward, and requires byte-exact recovery of all `0x12bec` captured bytes for requests 4/5/6. Missing bytes beyond the historical bound in the final parsed record are validation-only unknowns and are zero only in the synthetic inverse fixture; production parsing always emits the full parsed object.

No camera runtime, module load, STREAMON, MMIO, or reboot is performed by this checkpoint.
