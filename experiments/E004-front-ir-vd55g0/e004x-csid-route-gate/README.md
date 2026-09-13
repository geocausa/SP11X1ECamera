# E004x — IR CSID route gate

E004x freezes what is known and, equally importantly, what is **not yet proven** about the front-IR path downstream of CSIPHY0.

## Proven before this gate

E004w closed the receiver stage on the real VD55G0 path:

- native sensor exact Windows state: 596 writes;
- sensor returned to runtime suspend;
- CSIPHY0 D-PHY, one data lane, 420 MHz link;
- E004k receiver programming executed;
- 96/96 modeled CSIPHY0 registers matched same-machine Windows;
- receiver powered back off;
- no sensor stream, CSID stream, VFE stream, capture or illumination.

## Deterministic Linux CSID candidate

Current X1E CAMSS source gives a unique RDI0 register model **if** the IR route is CSIPHY0 -> CSID0 RDI0.

Enabling the CSIPHY0->CSID0 sink link establishes:

- `csiphy_id = 0`;
- one data lane;
- D-PHY;
- lane assignment 0.

Enabling CSID0 source pad1 establishes RDI0 / VC0. The native sensor's Y10 bus format maps to MIPI RAW10, CSI data type `0x2b`.

For that exact tuple, Linux CSID680 computes:

- wrapper IO_PATH_CFG0(CSID0): `0x00000101`;
- CSID0 RX_CFG0 +0x200: `0x00100000`;
- CSID0 RX_CFG1 +0x204: `0x00000001`;
- RDI0 CFG0 +0x500 after enable: `0x802bf000`;
- RDI0 CTRL +0x504 after resume: `0x00000001`;
- RDI0 CFG1 +0x510: `0x000081f5`;
- IRQ subsample pattern +0x548: `0x00000001`;
- IRQ subsample period +0x54c: `0x00000000`.

These values are a deterministic Linux candidate, **not yet an IR Windows parity claim**.

## Windows boundary

The existing E003g same-machine Windows route oracle is explicitly for `Surface Camera Front / Sony IMX681`. It proves RGB uses:

`IMX681 -> CSIPHY2 -> CSID1 -> IFE1/VFE1`

and therefore cannot prove the IR CSID instance.

The existing E004 Windows IR oracle proves VD55G0, CSIPHY0, D-PHY one lane, RAW10/VC0 transport and exact CSIPHY0 state, but it did **not** capture CSID/VFE MMIO.

Therefore E004x intentionally leaves the Windows IR CSID instance/path unresolved.

## Power-domain note

Linux `csid_set_power(1)` acquires its parent VFE power domain before powering/resetting CSID. That is a hardware power dependency, not a VFE stream request. Any later receiver/CSID-only runtime gate must distinguish parent-domain power from actual VFE `.s_stream()`, which remains prohibited.

## Next authority required

Acquire a dedicated same-machine Windows IR route oracle while explicitly running `Surface IR Camera Front`. Capture at minimum:

- CSID wrapper;
- CSID0, CSID1 and CSID2 full 8 KiB windows;
- enough VFE/IFE state to identify the active output instance;
- preferably IDLE -> LIVE1 -> POST -> LIVE2 -> POST2 as in E003g.

No Linux CSID runtime is authorized until that capture identifies the Windows IR route.
