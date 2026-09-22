# E004ld IMX681 timing and CAMSS clock candidate
Source-only candidate based on E004lc. Not installed or physically validated.

Expose read-only HBLANK=2912 and pixel-array rate=719898240 Hz without changing the writable cluster or sensor programming. CAMSS uses the documented bus throughput calculation for sensors providing explicit C-PHY configuration: link*2*trios*16/(7*bpp), rounded up. D-PHY and missing-config legacy control paths are retained. Both VFE clock selection and checking pass the sink bits-per-sample.

For front RAW10, 1.2 GHz link and one trio give 548571429 bus samples/s; the PIX vote becomes 594 MHz instead of the current missing-control fallback of 727 MHz. This is a candidate clock reduction, not a validated optimization. The Windows output-clock metadata rounds to 548570000 Hz. Exposure timing remains 719898240 Hz. The patch does not alter CSI link frequency or extend the physical sensor mode list.

Runtime admission remains blocked until isolated candidate builds/tests and a fresh guarded physical experiment validate the new module pair. Never substitute modules into the accepted hash-pinned package or modify its accepted hashes to bypass validation.
