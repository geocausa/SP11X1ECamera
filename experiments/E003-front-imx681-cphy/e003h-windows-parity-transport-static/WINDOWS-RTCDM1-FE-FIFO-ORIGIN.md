# E003h same-machine Windows RT-CDM1 FE/FIFO positive-origin oracle

This checkpoint closes the previous `FE_CFG` / `FIFO0_CFG` ownership ambiguity without turning negative static evidence into a reset-default claim. No Linux RT-CDM MMIO, IRQ arm, FIFO submission, sensor transmission, or frame occurred.

## Exact sources

- exact installed `qccamisp8380.sys`: 376,560 bytes, SHA-256 `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`
- raw same-machine KD log: `raw/E003H_FEFIFO_ORIGIN_20260828.log`
  - 18,444 bytes
  - SHA-256 `4d54bca3a1c8d2c542b6b09361e9cdee50a4e85175cb0667f0b8dd10c92076bb`
- extractor: `extract_rtcdm_fe_fifo_origin.py`
  - SHA-256 `16f283a084152c8998f1b222dd681fdf7257998ce29c311af97e734d4e7b4243`
- derived JSON: `windows-rtcdm1-fe-fifo-origin-oracle.json`
  - SHA-256 `7ab8eab8867393639d1a034d15bcd361e8773d64a5346a9de5f764f0a0a8ea3b`

## Exact software boundary

Static disassembly pins the front RT-CDM1 object lifecycle:

- resource getter call: RVA `0x18494`;
- returned MMIO pointer stored into CDM object `+0x48`: RVA `0x1849c`;
- pre-first-MMIO boundary: RVA `0x187a0`;
- first CDM-object RT-CDM MMIO write: RVA `0x187a8`, `IRQ0_MASK +0x30 = 1`;
- reset command: RVA `0x187b4`, `RST_CMD +0x10 = 9`;
- `CORE_CFG +0x18 = 0x11f`: RVA `0x18814`.

The capture samples RT_CDM1 at map-return, immediately before the first CDM-object MMIO write, after the reset wait, and after `CORE_CFG` programming.

## Two-cycle same-machine proof

Two independent native `Surface Camera Front` WinRT reader cycles completed `StartAsync=Success`, normal stop, and dispose in the same Windows boot.

After cycle 1 teardown, the first `0x80` bytes of the retained RT_CDM1 mapping were uniformly `0x80000000`, proving the powered-off interval before cycle 2.

On cycle 2, **at the resource-map return itself and before the front CDM object performed any RT-CDM MMIO write**, RT_CDM1 already contained:

- `HW_VERSION +0x00 = 0x20010000`
- `FE_CFG +0x20 = 0x07ff000f`
- `FIFO0_CFG +0x5c = 0x01000000`

The complete sampled `0x80`-byte map-return image equals the immediately-pre-first-MMIO image. The two target literals remain unchanged after the Windows reset wait and after Windows writes `CORE_CFG=0x11f`.

After cycle 2 teardown, the same `0x80` bytes again return uniformly to `0x80000000`.

## Ownership conclusion

This is positive same-machine timing evidence, not merely absence of a software store:

`powered-off sentinel -> platform/session power-up -> RT-CDM map return already has FE_CFG/FIFO0_CFG -> first CDM-object MMIO write`

Therefore the accepted Windows front CDM object does **not** program those two values. They are restored by the pre-CDM-object platform/power-up/hardware layer. This oracle intentionally does **not** claim whether the ultimate source is firmware, hardware reset logic, or another platform mechanism.

## Linux consequence

Linux must not synthesize or write `FE_CFG` or `FIFO0_CFG` merely to imitate the live register image. The parity-safe behavior is:

1. activate the proven-equivalent platform/power ownership layer;
2. before the first RT-CDM MMIO write, read-only validate:
   - `HW_VERSION = 0x20010000`
   - `FE_CFG = 0x07ff000f`
   - `FIFO0_CFG = 0x01000000`
3. if any value differs, fail closed **without** performing RT-CDM writes;
4. only after that validation may the exact Windows open/init sequence begin.

This closes the FE/FIFO ownership/timing blocker for static Linux architecture. It does not authorize runtime.
