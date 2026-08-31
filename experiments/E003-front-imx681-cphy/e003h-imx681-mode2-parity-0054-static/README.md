# E003h 0054 — Windows-selected IMX681 mode2 static parity

Same-machine Windows KD capture proved that stock Windows Camera selects IMX681 firmware resolution index 2, 3840x2160@30. This static checkpoint converts Linux from the previously used 3840x2640 record 0 to that exact Windows-selected record without adding speculative CSID programming.

## Proven sensor delta

The current Windows sensor blob is SHA-256 `f7dd81be64153fd3f0da8e6288ee1b9906b7bf51b773a98496934d76dc96a45c`. Its mode0 and selected mode2 register sequences contain the same 68 addresses in the same order. Only seven values differ: `0347 00->f0`, `034a 0b->0a`, `034b 4f->5f`, `040e 0a->08`, `040f 50->70`, `034e 0a->08`, `034f 50->70`. The generated Linux mode2 table equals all 68 address/value pairs from the captured Windows packet. MODE_SELECT is absent from the table.

Mode2 remains RAW10, one-trio C-PHY, 6752 line length, 3554 frame length, 548.57 MHz pixel rate and 1.2 GHz V4L2 C-PHY link frequency. Its sensor output and digital-crop size are 3840x2160.

## CAMSS delta

CAMSS changes only three front-path eligibility/validation height checks from 2640 to 2160: the CSID1 special-path predicate, RT-CDM input validator and bounded front-runner validator. No CAMSS MMIO write is added and no CSID programming value changes. Existing Windows-derived CSID vertical crop/expected-frame programming already targets 3840x2160.

## Static acceptance

`0054-static-inspection.json` is fail-closed and accepted. It requires the exact Windows oracle SHA, 68/68 packet equality, the exact seven sensor changes, exactly three CAMSS geometry substitutions, zero new CAMSS writes, exact forward/reverse Git patch application, and Golden vermagic for both built modules.

Built locally on Golden ABI `7.1.5-sp11-render-parity-v4+`:

- IMX681 module SHA-256 `a12693a18bf2e4108dd309af68da189a2ea394a734a0c6a3c1d624ac44dea3dc`
- CAMSS module SHA-256 `0dc8e3a3318a4b68fc968ce6ff3c68e93bf2931502063b4469ed093cb0002be1`
- static inspection SHA-256 `19f6fddf77d323507bfe4ad390c5f1ae3e70ed983dd574a6ecfec0bd83645231`
- sensor patch SHA-256 `57ff4b43d9e1ab4a73c0a973c7f9e02f01129214ef82841a481c4facdccdbfa2`
- CAMSS patch SHA-256 `98512b72a1c164f6d49fd999465164378442b4ed1b16ad7268febb2b695e3165`

Runtime is **not authorized** by this checkpoint. Next gate is a separate unarmed bounded 0054 one-shot package, followed by an independent authorization review before any camera hardware execution.
