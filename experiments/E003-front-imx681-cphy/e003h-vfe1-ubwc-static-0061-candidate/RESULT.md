# E003h 0061 result

The exact Windows SP11 VFE1 BUS common `UBWC_STATIC_CTRL=0x00001046` is now achieved on Linux, versus `0x00000006` in consumed 0060. This parity correction is real but noncausal for the remaining failure: raw VFE1 BUS status1 Epoch0 remains absent, QC10C remains absent, CSID1 remains healthy at 3840x2160 with no line/ECC/CRC errors, RT-CDM completes 25 FIFO submissions without fault, and all nine BUS clients retain valid address-status relations.

Next gate: same-machine Windows dynamic lifecycle trace of VFE1 BUS CGC override `+0xc08`, which the active start callback writes `0x1ff` but successful stable-live Windows reads as zero.
