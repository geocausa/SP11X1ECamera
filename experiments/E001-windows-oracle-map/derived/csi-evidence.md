# E001 static oracle — CSI evidence

## IMX681 front: C-PHY is mechanically proven

The exact installed Windows IMX681 sensor package's init register set writes:

- sensor register `0x0111 = 0x03`
- per-mode `0x0110 = 0x00`
- `0x0112 = 0x0a`
- `0x0113 = 0x0a`
- `0x0114 = 0x00`

In the exact Linux kernel source used by the deployed SP11 baseline, `drivers/media/i2c/ccs/ccs-regs.h` defines:
- `0x0111` = CSI signalling mode
- `2` = CSI-2 D-PHY
- `3` = CSI-2 C-PHY
- `0x0112` = CSI data format
- `0x0114` = CSI lane mode

Therefore the SP11 front IMX681 is configured by Windows for **CSI-2 C-PHY**. This is local machine-derived evidence, not a copied community assumption.

`0x0114 = 0` is consistent with one C-PHY trio under CCS lane-mode semantics (`lanes - 1`), but we keep the host-side trio count as **high confidence / dynamically confirm** until the Windows CSI receiver configuration is observed.

## Rear/IR
- rear module `laneAssign = 0x3210`, combo mode disabled
- front/IR module laneAssign fields are zero; this is not enough by itself to derive the receiver wiring
- all three sensor-package streams use RAW10 DT 0x2b and VC0

## Implementation consequence
The deployed X1E CAMSS source has no obvious `V4L2_MBUS_CSI2_CPHY` / `PHY_TYPE_CPHY` path in the Qualcomm CAMSS driver. Therefore:
1. prove common Denali camera infrastructure with **rear OV13858 D-PHY first**;
2. keep front IMX681 C-PHY as a separate PHY-extension milestone;
3. do not let front C-PHY work contaminate or block the first rear RAW capture.

## Still unknown after static oracle
- exact CCI controller per sensor
- exact CSIPHY/CSID receiver assignment per sensor
- host PHY rate/settle values
- dynamic privacy LED timing/ownership
- whether any host routing differs across Windows camera profiles

Those are E001 dynamic-oracle targets.
