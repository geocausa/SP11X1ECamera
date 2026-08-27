# E002h-r1 — CSIPHY1 MMIO window correction

Single-variable correction after the first E002h STREAMON Oops.

Change only integrated CAMSS `reg` tuple named `csiphy1`:

- before: `<0 0x0ace6000 0 0x1000>`
- after:  `<0 0x0ace6000 0 0x2000>`

Rationale: X1E integrated CSIPHY sets a 0x1000 internal register offset, and Denali's own standalone CSIPHY1 node maps 0x2000 bytes. This correction makes the driver's first reset write mapped without altering any behavioral programming.
