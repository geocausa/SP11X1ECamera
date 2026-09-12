# E004e — bounded Linux Surface-patch/boot prefix authority

Status: **PASS target is offline only until verifier succeeds and a separate one-shot runtime package is checkpointed.**

E004e implements only the same-machine Windows InitialConfig prefix proven by E004d, stopping at VD55G0 software standby before Windows's final 43 configuration writes.

The private DT compatible is `microsoft,sp11-vd55g0-prefixprobe`. The E004e DTB is derived byte-deterministically from E004b and changes only that compatible string.

The prefix module requires the already-proven physical identity (model BE 0x3047, revision 0x1111 CUT1) before any sensor-data write. It then performs:

1. poll `0x002c == 1` for up to 6 one-millisecond attempts;
2. write the exact 552-byte Surface Windows patch, one 16-bit-address/8-bit-data transaction per register;
3. write `0x0200 = 2`;
4. poll `0x0200 == 0` for up to 28 one-millisecond attempts;
5. write `0x0200 = 1`;
6. poll `0x0200 == 0` for up to 6 one-millisecond attempts;
7. poll `0x002c == 2` for up to 4 one-millisecond attempts;
8. stop and power off.

A successful attempt therefore performs exactly **554 sensor-data writes**.

The Surface patch bytes are not committed. `generate_surface_patch_header.py` extracts them from the exact local Surface package at build time and refuses to proceed unless package and patch hashes match E004a/E004d. The generated header is ignored by Git.

E004e deliberately does **not** perform Windows's final 43 configuration writes. In particular it does not write the Windows-observed GPIO-control block `1,2,1,1`, so the sensor GPIO1 strobe selector is not configured. CAMSS, V4L2, streaming and external illumination remain absent.

Run:

```
python3 experiments/E004-front-ir-vd55g0/e004e-linux-prefixprobe-authority/verify_e004e.py
```

Only after that offline gate and a separate committed one-shot package may a single live prefix attempt be armed.
