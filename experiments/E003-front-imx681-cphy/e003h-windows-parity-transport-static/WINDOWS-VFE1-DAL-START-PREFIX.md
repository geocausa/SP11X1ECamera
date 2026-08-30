# E003h Windows VFE1 DAL_ife_start prefix / Linux 0047

0046 proved that the X1E VFE1 BUS clients and Linux-owned FULL addresses are programmed correctly, but all VFE TOP/BUS IRQ masks remain zero at the Epoch0 timeout. Exact qccamisp8380 reversal closes the missing lifecycle action.

For the active VFE680 callback family, IFE context slot `+0x6b690` selects RVA `0x1d2b0`. That routine writes TOP IRQ masks `0x0007f051/0` and BUS IRQ masks `0xd0000000/0`. The optional BUS `+0x08=0x0fffffff` write is separately guarded by context `+0x6b6f0 != 0` and is not authorized for this SP11 use case. Slot `+0x6b698` selects RVA `0x1d820`, which writes VFE TOP `+0x24=0`.

The normal first-start path in `DAL_ife_start` checks context `+0x3488`, invokes `+0x6b690`, then `+0x6b698`, then calls `DAL_ife_bus_start`. Existing same-machine dynamic cross-order independently places BUS static config/enable/initial addresses between IFE startup packets 1 and 2. Each of the four captured startup packets writes VFE1 `+0x24=0x6000`, so Windows performs the exact transition `packet1 leaves 0x6000 -> DAL_ife_start writes 0 -> BUS start -> packet2 restores 0x6000`.

Linux 0047 therefore adds one private VFE helper containing only those five proven writes and calls it immediately before the existing `vfe680_x1e_pix_runtime_bus_prepare()` in the already-proven packet1/BUS/packet2 split. Captured RT-CDM bytes/order, BUS programming, CSID, sensor lifecycle, and the optional BUS `+0x08` path remain unchanged. This is a static checkpoint only; no hardware runtime is authorized.
