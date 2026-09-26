# E006z — rear clean scalar + bank providers

Parent Git: `70c62db3` (E006y AWBBGStats17 compile PASS).

Status: **STAGED / COMPILE-ONLY**. No module install/load, camera access, reboot, MMIO write or RT-CDM submission is part of this experiment.

## Goal

Reduce the 61 non-startup-only register contracts that remained after E006y without mistaking register closure for full camera-stack parity.

This checkpoint implements **24 register providers** whose packing/state rule is already cleanly closed:

- 16 Titan680 bank selectors;
- Demux/BLS141: 0x3B70, 0x3B74;
- PDPC311: 0x3D78, 0x3D7C, 0x3D80, 0x3D84;
- WB201: 0x456C, 0x4570.

No observed rear register value is embedded.

## Rear bank-state rule

Private rear E006a data is validation only. It proves two distinct rules:

- startup: every present bank selector is `startup_phase & 1`;
- rear steady regular group (PDPC, GIC, BPC/ABF, DSX): `(request_id + 1) & 1`;
- rear steady inverse group (LSC, GTM, Gamma): `request_id & 1`.

Rear LSC belongs to the inverse steady group. This intentionally differs from the older front proof grouping, so the front bank rule was not copied mechanically.

## Scalar semantic boundary

Pinned Surface/Titan680 analysis source-locks the same hardware generations used by the clean front calculations:

- IFEDemuxBLS141Titan680 common calculation `0x998E70`, packer `0xB42840`;
- IFEPDPC311Titan680 common calculation `0x9C07C0`, packer `0xB3C7D0`;
- IFEWB201Titan680 common calculation `0x995E60`, packer `0xB560C0`.

The compile-only C provider accepts the already-quantized common-calculation outputs. Live rear post-sensor gain, BLS tuning/interpolation, AWB gains and predictiveGain remain explicit upstream state-production work. This avoids kernel floating point and does not treat front tuning as rear authority.

## Private validation

`validate-private.py` decodes retained E006a packets locally and checks startup bank parity, rear steady regular/inverse bank rules across the retained corpus, and exact pack/unpack round trips for the eight scalar fields.

Only aggregate PASS counts are written to `PRIVATE-VALIDATION-SAFE.json`; no captured register values or packet bytes are committed.

## Coverage on compile PASS

- startup-only remains **184/184 (100%)**;
- concrete startup register providers become **677/714 (94.8%)**;
- non-startup-only register contracts remaining: **37**.

Those 37 are exactly:

- VFE680 PERIOD_CFG: 1;
- BPC/ABF411 non-bank words: 7;
- BFStats25: 29.

This does **not** mean 94.8% overall camera-stack parity. DMI/live-state work remains for LSC/Tintless, GTM, PDPC modes, BPC/ABF, Gamma and DSX, in addition to BFStats25 and PERIOD_CFG.

## Runtime gate

Native rear Linux ISP and RT-CDM submission remain **DENIED**. This checkpoint is compile-only producer closure.

Next: BPC/ABF411 seven-word calculation and BFStats25/transport-state closure, while continuing rear DMI/live-state production in parallel.
