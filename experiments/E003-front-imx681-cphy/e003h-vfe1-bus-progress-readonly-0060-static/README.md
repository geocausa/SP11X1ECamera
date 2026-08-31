# E003h 0060 — VFE1 BUS progression read-only telemetry

Static-only diagnostic. Starting from accepted 0059 source, add timeout-path reads for VFE1 BUS common CGC/UBWC/power/debug state and all nine Windows-active BUS clients' configuration, current image address, four address-status registers and debug status. No MMIO write or camera programming/order change.

The immediate discriminator is Windows `BUS +0x58 = 0x00001046` (VFE680 UBWC static control) plus whether Linux client address-status registers show the same address-consumption relation as successful Windows.

Runtime remains unauthorized until a separate package and authorization checkpoint.
