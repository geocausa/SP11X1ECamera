# E003f R2 preflight after first receiver fault

The first E003f receiver-only harness attempt was rejected at runtime before any C-PHY table execution.
`csiphy_set_power()` enabled the receiver supplies/clocks, then `csiphy_reset()` faulted on its first
X1E common-register write at `csiphy->base + 0x1000`.

Mechanical evidence in `RUNTIME-FAULT-1.txt` proves the cause:

- fault VA was the first page beyond the mapped `csiphy2` parent CAMSS resource;
- `/proc/iomem` mapped `0x0ace8000-0x0ace8fff` (4 KiB) as `acb7000.isp csiphy2`;
- the live parent CAMSS `reg` property encoded `csiphy2` size `0x1000`;
- the already-existing X1E child `phy@ace8000` node encodes size `0x2000`;
- same-machine Windows mapped/dumped the CSIPHY2 block as 8 KiB and uses offsets through `0x1054`.

R2 changes only the parent CAMSS `csiphy2` resource size from `0x1000` to `0x2000`.
Decompiled accepted-E003d DTB vs R2 DTB is exactly one removed line / one added line, with only that
size cell changed. R2 DTB SHA-256 is `e9fd13a29b6580955d2662c27377dbd1caba14f7f89613510b5e23bd6c266293`.

The receiver harness also gains a no-hardware preflight that requires the platform `csiphy2` resource
to be at least `0x2000` before it can call `.s_power`. R2 harness SHA-256 is
`d5ba9f8a7c3851b5fe253faf9011a908158ac3ec1441f4ebfa43b6bd902c6e78`; 13/13 imported symbol CRCs
match Golden. It still contains no CCI/I2C/sensor write path.

R2 initrd is reproducible A/B at
`467fad49cab05315dbb9a116580952507437aae2e6ce0c5b859a276d71c225b4`.

No R2 runtime has occurred when this file was written. Golden is running and remains saved default.
