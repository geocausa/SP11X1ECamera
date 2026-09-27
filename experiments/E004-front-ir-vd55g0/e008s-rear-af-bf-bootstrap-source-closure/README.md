# E008s — rear AF/BF bootstrap source closure

Parent Git: `a5d4b2c404549890e8d8127e20205c1e3a348909` (E008r).

Status: **STATIC AF/BAF BOOTSTRAP SOURCE-CLOSURE PASS / NO RUNTIME**.

## Purpose

E008q source-locked the normal rear BF gamma/filter/coring tuning state and
E008r source-locked BFStats25/Titan680 ownership, bank policy and field
producers. Four upstream request-side items remained:

1. packet0's distinct filter/coring state;
2. the two numerical IIR shift values;
3. the accepted 25-ROI semantic seed;
4. packet-phase validity/enable policy.

E008s closes those items from the pinned DeviceMFT and selected rear tuning.
The private Ghidra workspace and Windows corpus remain off-repo. This
checkpoint contains only source locations, semantic conclusions and aggregate
validation counts.

Pinned authorities:

- `QcDeviceMFT8380.dll`, SHA-256
  `c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35`;
- `com.surface.tuned.rfc_ov13858`, SHA-256
  `4858ccb297eeecbc8e9b6d673f7ab4b0ead559adf16e3fe717eea9e40ccef635`.

## Pre-request AF/BAF path

`CAFStatsProcessor::GetDefaultConfigFromAlgo` (RVA `0x8274E0`) asks AF for
BAF stats/filter configuration plus ROI configuration before ordinary request
processing.

The AF GetParam path and normal AF request path converge on the same producer
and BAF logic:

- AF GetParam dispatcher: RVA `0x615EA0`;
- shared AF producer: RVA `0x628AB0`;
- BAF `SetTuningData`: RVA `0x62E698`;
- BAF `CheckConfigureUpdate`: RVA `0x62EC00`;
- BAF `MapStatsConfigure`: RVA `0x62F040`;
- BAF `MapROIConfigure`: RVA `0x6301C8`.

Pre-request and normal processing use twin BAF driver instances but the same
selected rear BAF tuning family. There is no separate hidden packet0 BAF
tuning table.

## Packet0: IFENode hardcode fallback

The missing packet0 producer is upstream of BFStats25.

`IFENode::Get3AFrameConfig` (RVA `0x741570`) checks the published BF ROI
count. For an early request whose BF configuration has zero ROIs it takes the
explicit **"Invalid BF config use hardcode"** branch, invokes:

- hardcoded BF semantic helper RVA `0x7635A8`;
- hardcoded ROI helper RVA `0x7637D8`;

and saves the resulting configuration as the previous BF configuration for
later invalid requests.

The hardcoded semantic helper owns packet0's unique filter state. Its embedded
float block begins at RVA `0x763788` and, after the same Q14 conversion and
Titan ordering source-locked in E008q/r, reproduces the retained packet0
filter coefficients exactly in private validation.

The same helper sets:

- input/luma configuration valid;
- gamma disabled;
- scale configuration invalid/disabled;
- both hardware BF filter objects valid;
- FIR enabled in the hardcode profile;
- both BF IIR groups enabled;
- first IIR shift = **-3**;
- second IIR shift = **0**;
- the packet0 coring threshold/tail profile.

Private validation gives one exact packet0 match for filter, shifts and both
coring tails. No captured values are emitted here.

This also rules out BFStats25/Titan initialization as the producer:
`BFStats25::Create` (RVA `0xA1CD70`) zero-initializes its object and the
Titan680 register configuration is separately zero-initialized.

## Packet0 ROI seed

The hardcoded ROI helper constructs the first valid 25-ROI semantic set
directly from CAMIF dimensions.

For each axis, cell size is approximately 5% of the active dimension, rounded
down to an even value. Five cells are centered on each axis, giving a **5 x 5
grid = 25 valid ROIs**. Each ROI receives a sequential index and valid flag.

Equivalently, the hardcoded grid spans approximately the centered 25% x 25%
window. This is semantic AF/IFE state; Titan680 only packs the already-created
ROI set.

## Packet1+ normal AF/BAF state

The rear BAF `configure` table selects **Default / configure index 0** first.
All four rear configure modes carry the same two IIR shifts, so the normal
packet1+ values are source-closed as **3 / 3**.

The selected normal state is:

- input/luma valid;
- gamma preset 0 enabled;
- scale configuration valid, scale itself disabled;
- both hardware BF filter objects valid;
- FIR preset 0 disabled;
- both selected IIR filters enabled;
- IIR shifts 3 / 3;
- E008q filter block 1 and coring record 0.

The rear HAF default/grid tuning block contains a centered 25%-scale default
window, enabled sub-grid, 0.2 / 0.2 normalized grid dimensions and zero
overlap. The AF producer computes horizontal and vertical counts as
`int(1 / ratio)` before passing them to the BAF ROI mapper, yielding the
normal **5 x 5 = 25 ROI** policy.

The exact packed selector-1 ROI payload is intentionally not claimed to be
byte-identical across requests: private startup/steady validation sees three
distinct selector-1 payload hashes. E008s closes the semantic ownership and
seed policy, not a captured DMI byte replay.

## Packet-phase validity evidence

Private DMI validation sees a 300-byte BF selector-1 payload on each of five
checked startup/steady captures, exactly 25 x 12-byte ROI entries.

Packet0 has no BF selector-2 gamma payload. Packet1, packet2, packet3 and the
checked steady record each have the 128-byte selector-2 gamma LUT. This
independently matches the source-derived phase policy:

- packet0 hardcode: gamma disabled;
- packet1+: normal BAF Default: gamma enabled.

## Closure

E008q + E008r + E008s now source-close the BF portion of the four-packet
semantic bootstrap:

- packet0 hardcoded filter/coring/shifts;
- packet1+ normal tuning filter/coring/shifts;
- 25-ROI ownership and packet-aware seed policy;
- packet-aware gamma/scale/filter validity and enables;
- downstream LUT-bank and Titan680 packing policy.

No Windows reboot is justified by this BF gate.

The next checkpoint may materialize these packet-aware BF semantics into the
still-unreachable E008o bootstrap model. It must remain detached from ordinary
V4L2/probe/autostart and from native rear submission until the larger semantic
bootstrap gate is closed.

## Safety

Static/private analysis only. No module build/load, MMIO, DMA, RT-CDM submit,
camera activation, reboot, V4L2 attachment, probe integration or autostart
change.
