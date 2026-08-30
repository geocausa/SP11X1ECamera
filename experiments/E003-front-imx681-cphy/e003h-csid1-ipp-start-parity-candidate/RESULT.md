# E003h CSID1 IPP 0042 bounded runtime result — 2026-08-30

## Result

The separately authorized one-shot was consumed exactly once. The helper entered the retained bounded PIX runner, completed the same 13 pre-CSID RT-CDM FIFO0 submissions with no RT-CDM fault, started IMX681 transmission, and timed out waiting for VFE1 raw Epoch0. No QC10C buffer was produced. There was no same-boot retry. The wrapper archived evidence and rebooted immediately; FullIO v19c Golden is restored with empty `next_entry` and no candidate camera modules loaded.

## New localization from 0042 telemetry

The failure is **not** lack of sensor or CSI traffic.

At the Epoch0 timeout CSID1 reported:

- wrapper route `0x00000101`;
- RX status/mask `0x00000017 / 0x019fb800`;
- RX config `0x11300000 / 0x00000001`;
- 37,016 received CSI packets (`0x9098`);
- ECC errors `0`;
- CRC errors `0`;
- IPP control `1`;
- IPP config `0x802b2000 / 0x00007241`;
- IPP mask `0x3cbc601c`;
- exact zero writes `+0x324=0`, `+0x330=0`;
- epoch config `0x00130013`;
- Windows-matched crop/drop/format-measure state;
- `+0x340 = 0x48000a08`, matching the accepted Windows live readback.

The Linux IPP IRQ status was `0x00011e00`. Using the exact CSID680 register-layout reference already pinned by E003g, those set bits decode to:

- `INFO_INPUT_EOF`;
- `INFO_INPUT_EOL`;
- `INFO_INPUT_SOL`;
- `INFO_INPUT_SOF`;
- `VCDT_GRP1_SEL`.

No CSID680 path error bit is set. Thus complete sensor frame boundaries are entering the IPP parser cleanly.

The accepted same-machine Windows live IPP IRQ status is `0x00e11ff8`. Relative to Linux, Windows additionally has the critical path-progress events:

- `CAMIF_EOF`;
- `CAMIF_SOF`;
- `CAMIF_EPOCH0`;
- `CAMIF_EPOCH1`;
- `RUP_DONE`;

plus latched frame-drop status bits. Linux has no status bit that Windows lacks.

This localizes the current failure to **after clean CSI packet/input-frame ingress and before CSID CAMIF/RUP/Epoch output progression into VFE1**.

## RUP/AUP implementation clue — not yet parity proof

Qualcomm's public CSID680 implementation at commit `0f16924ff6a7f9bb56a7e958016da2ed8a174f2f` identifies:

- common `RUP_AUP_CMD` offset `+0x18`;
- IPP `rup_aup_mask = 0x00010001`;
- stream-on behavior that writes the accumulated RUP/AUP mask before enabling CSI2.

The current Linux CAMSS source already has the same IPP mask in `reg_update_ipp()` (`BIT(0) | BIT(16)`), but the custom E003h PIX runner bypasses the ordinary VFE stream path that normally causes `ops->reg_update()` / `camss_reg_update()` to issue it.

This is strong implementation evidence, but **not yet same-machine Windows behavioral proof**. Patch 0042 correctly did not synthesize this write from upstream alone.

## Next gate

Do not repeat Linux PIX runtime. Recover exact same-machine Windows CSID1 RUP/AUP command value and lifecycle order, preferably by a bounded KD write oracle on physical `CSID1 +0x18` during a normal front-camera start, corroborated by exact `qccamisp8380.sys` control flow. Only after that proof may a native Linux RUP/update delta be represented and statically inspected.

## Evidence identities

- `RUNTIME-CSID1-0042-RUN.txt`: `7278407c3dddacec05a3deb1acb1f8258680109e5ed40ef85aef76810eab7db8`
- `RUNTIME-CSID1-0042-POST.txt`: `d53c198e9b856f00735eb01b5220aff0c26f67595733eeadd46f416ab1f97f58`
- `RUNTIME-CSID1-0042-DMESG.txt`: `32b2236f38977564936e9f69942c5892008375a45e3e87328eec2ca50538d201`
- `RUNTIME-CSID1-0042-RTCDM-STAGES.txt`: `3371d2b9645223c4de47cdd54d4dc3939c75a5d43532b1586475ef7944a28e8e`
- `extract-runtime-0042.py`: `422353f55d100de55abca035f91dbc192ee9d7d8db3e67df17fe7a63b67f5aa4`
- `runtime-0042-analysis.json`: `83e6945ca44402e6aaea1974cedc52d9f843216c08e69a6da02e389181f9df8c`
