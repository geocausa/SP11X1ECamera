# E001 — Windows oracle map

Goal: recover an implementation-grade SP11 camera hardware/lifecycle map from the exact Windows installation before modifying Linux DT or kernel behavior.

Scope:
- front SONY0681 / IMX681 (MSHW0490)
- rear OVTID858 / OV13858 (MSHW0491)
- IR SMO55F0 / VD55G0 (MSHW0492)
- Qualcomm camera platform MSHW0495

No runtime Linux camera changes are permitted in E001.

## Static-oracle checkpoint

Mechanically established from the exact installed Windows package:
- exact D0/D3 power/resource sequences for front/rear/IR;
- sensor probe addresses and chip IDs;
- RAW10 transport mode lists;
- sensor stream-on/off and group-hold lifecycles;
- IMX681 front is CSI-2 **C-PHY** (`0x0111=3`), not an assumption;
- rear OV13858 is the first Linux transport target so C-PHY support cannot block common CAMSS bring-up.

Remaining E001 work is dynamic Windows host-side mapping: CCI/CSIPHY/CSID assignment, host PHY parameters and privacy-LED lifecycle.
