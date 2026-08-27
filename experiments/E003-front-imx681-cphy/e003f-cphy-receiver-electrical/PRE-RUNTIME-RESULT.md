# E003f pre-runtime result

Status: **READY FOR ONE-SHOT / receiver electrical test not yet executed**.

## New receiver bug caught statically

The accepted E003d X1E C-PHY code carried the exact 121-record Windows table, but generic CAMSS logic immediately followed the table by zeroing common CTRL11..CTRL21. On X1E these are offsets `0x102c..0x1054`, and the same-machine Windows oracle requires all 11 to remain non-zero.

Mechanical final-state simulation proves the old runtime would have exactly 11 mismatches:

`0x102c,0x1030,0x1034,0x1038,0x103c,0x1040,0x1044,0x1048,0x104c,0x1050,0x1054`.

E003f gates the generic IRQ-mask zeroing away only for X1E80100 + C-PHY. D-PHY and non-X1E behavior are unchanged. The modeled final X1E C-PHY state then matches both independent Windows KD live snapshots at all 121 expected offsets: `post_fix_mismatches=0`.

## Candidate binaries

Patched CAMSS:
- SHA-256 `e1c8dcb099ee872ffd8bac263576b8f2db85cef104077df80d29a2916f47f308`;
- srcversion `1D2912B8FF127D1F3D94704`;
- exact Golden vermagic;
- 140 imported symbols / 0 Golden CRC mismatches.

Receiver-only harness:
- SHA-256 `631c1d1c86b7ed132f3086acb25583437067272421186e92f891cee8d3a50780`;
- srcversion `ECA36450A292CAE56ACD0B9`;
- exact Golden vermagic;
- 12 imported symbols / 0 Golden CRC mismatches.

The accepted E003e IMX681 module is unchanged at SHA-256 `6a1939aae15fea062bd893ae6d5c60f6a8f7985c391ea289ddb82195e3d8233c`.

## Harness safety boundary

The test module contains no CCI/I2C write path and no MODE_SELECT reference. It directly locates CAMSS/CSIPHY2 and performs only:

`CSIPHY2 power-on -> CSIPHY2 stream-on -> 121-offset MMIO compare -> CSIPHY2 stream-off -> CTRL5/6 zero check -> CSIPHY2 power-off`.

It never calls the IMX681 stream callback. IMX681 must remain runtime-suspended, reset-low, with MCLK4 and front rails off.

## Reproducible initrd

Base is accepted R3 initrd SHA-256 `dfcc8a0d53391b80ef418ff7b3c40df2ccbc0d8aeb43ffe6a8e7abb5aabf7e15`.

Two independent E003f builds are byte-identical:

`4c353be73e3bca787f91d0f07ce3f287098cf300206d01c29d246f3d159dcf02`.

Semantic delta count is exactly 11: ORDER, E003f loader, E003f module directory, patched CAMSS, accepted E003e IMX681, manual receiver harness, and five existing media dependencies. The loader dynamically discovers the IMX681 client and explicitly does not execute the harness.

No E003f boot has been installed or armed at this checkpoint.
