# E003i-AA — AEC/AWB trigger reconstruction oracle

Status: **Windows fixture acquisition PASS; clean Linux replay/reconstruction remains**.

Z proved live Linux AEC_BE/BHist/AWB_BG transport paired exactly to TL_BG source identity. AA used one direct Windows oracle boot to close the next semantic boundary with request-labelled fixtures from the same SHA-pinned Surface `QcDeviceMFT8380.dll` (`c241b7fb...41c35`). SP11 was then returned to persistent Golden.

The AEC oracle produced two useful fixtures. The first fresh `0x14000` AEC_BE raw dump is SHA `c44c57ec...633f7` and the immediately following AEC frame-control publication is Windows request **4**, with `AECLuxIndex` bits `0x4365acdd` = **229.6752472**. A later complete raw+parsed pair is raw SHA `dac4a912...52331`, parsed `0x70008` SHA `e3e4bdf0...7dcc8`; its request-labelled publication is request `0xe45` (3653), Lux bits `0x43b5d064` = **363.6280518**.

The AWB oracle produced a complete `0x3c000` raw + `0x6a528` parsed pair: raw SHA `dca2454b...09638`, parsed SHA `5b9ae831...64d46`. Its frame-control publication is request `0x766` (1894), CCT **4452 K**, with RGB gains **1.6758220 / 1.0 / 2.1812174**. Request IDs are direct Windows labels and are not inferred from Linux source generation.

The BHist high-level parser RVA `0x5f3c60` was kept armed through front-stream intervals in which AWB, AEC and their publishers fired, but it produced **zero observed hits**. The follow-up BHist-only probe again saw an AEC publication but no BHist parser hit. This is useful negative evidence: BHist is not dynamically proven to participate at that parser boundary in this front stream. The first clean AEC reconstruction should therefore start from AEC_BE and only add BHist if another proven consumer boundary requires it.

Compact KD logs are tracked as `KD-ORACLE.log` and `KD-BHIST.log`; raw/parsed binary fixtures remain on SP7 and are SHA-pinned in `FIXTURE-MANIFEST.json`. `RESULT.json` is the semantic acceptance record.

Golden return was verified on kernel `7.1.5-sp11-render-parity-v4+`, saved entry `sp11-audio-fullio-v19c`, empty `next_entry`, and no camera modules loaded.

**Next:** reconstruct the Titan680 AEC/AWB parsed structures and the minimum clean algorithms needed to reproduce the request-labelled Lux/CCT fixtures offline. Only after replay matches should Linux G2/G3 live stats drive request5/request6 LSC selection. Dynamic R5/R6 substitution remains blocked.
