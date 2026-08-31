# E003h 0062r1 result — CGC release parity achieved, noncausal

The diagnostic retry boot succeeded under multi-user mode. The exact 0062 camera payload ran once. Removing the private VFE1 BUS `+0xc08=0x1ff` write produced live `cgc=0x00000000`, matching successful Windows, while UBWC stayed `0x00001046`. VFE BUS status remained zero, the Windows BUS Epoch0 latch remained absent, RT-CDM completed FIFO 25 without fault, CSID remained healthy at 3840x2160, all nine BUS client address-status relations remained valid, and QC10C remained absent.

Therefore CGC override retention was a real parity mismatch but is noncausal for the remaining stall. Keep `c08` released; move the investigation to generation/qualification of BUS status1 bit21 rather than BUS common configuration.
