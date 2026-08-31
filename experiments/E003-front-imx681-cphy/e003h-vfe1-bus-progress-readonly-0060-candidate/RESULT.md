# E003h 0060 result

PASS as a consumed read-only diagnostic. Golden return is verified. All nine Windows-active BUS clients are enabled and reflect their programmed image addresses in ADDR_STATUS0/3 with zero debug status. The concrete remaining BUS-common delta is UBWC_STATIC_CTRL: Linux 0x00000006 versus successful Windows 0x00001046 (missing bits 0x00001040). This proves the mismatch, not its write ownership or causality. No programming write is authorized yet.
