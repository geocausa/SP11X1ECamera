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

## Host-routing checkpoint

The exact Windows platform PCFG parser has now been reversed sufficiently to recover per-sensor control/receive routing:
- rear OV13858: CCI0/master1 -> CSIPHY1;
- front IMX681: CCI1/master1 -> CSIPHY2;
- IR VD55G0: CCI0/master0 -> CSIPHY0.

The rear Windows transport is four-lane RAW10 at 1.1856 Gbit/s/lane (592.8 MHz DDR link frequency), with a Microsoft PLL profile different from mainline OV13858's stock 540/270 MHz profiles.

The one-shot Windows boot returned cleanly to FullIO v19c with `saved_entry=sp11-audio-fullio-v19c` and an empty `next_entry`. No Linux camera runtime change occurred in E001.

Remaining Windows-only observations (exact runtime settleTimeNS and privacy-LED transition timing) are useful parity follow-ups but no longer block the first rear D-PHY Linux experiment.
