# Windows CSID1 RUP_DONE IRQ ownership

This checkpoint answers the exact post-0050 ownership question against the installed same-SP11 `qccamisp8380.sys` SHA-256 `64463b4d78894fdeee01ce87b51e3153662243e3fdf16f87596579b58617c21c`.

The fail-closed Capstone extractor pins the IRQ reader (`RVA 0x1b5f0..0x1b7c8`) and handler (`RVA 0x1b840..0x1bdc8`). The reader's direct CSID MMIO stores are exactly IRQ clear/ack offsets `+0x84,+0xa4,+0x94,+0xb4,+0xd4,+0x14`; IPP status is read at `+0xac` and written back to IPP clear `+0xb4`. There is no direct store to `REG_UPDATE_CMD +0x18`.

The handler reloads IPP status as `w24` at RVA `0x1b8b0`. Its complete condition set on that field tests bit12, error mask `0x3c1c6004`, bit1, bit4 and bit3. It never tests bit23 `RUP_DONE`; the error mask also excludes bit23. The handler contains no direct CSID MMIO store. Therefore normal Windows handling of an IPP IRQ carrying RUP_DONE acknowledges the IRQ but does not issue a follow-up update/zero command at `+0x18`.

This closes a Linux ownership mismatch exposed by 0050. The SP11 front IPP RUP/AUP update is already submitted by RT-CDM as exact `+0x18=0x01f501f5`. Linux's generic `csid_reg_update_clear()` path currently clears its software shadow and then writes that shadow to `+0x18` when RUP_DONE is observed. For the X1E80100 front IPP path that second MMIO write is not Windows behavior. The smallest justified Linux representation is to retain software-shadow bookkeeping but suppress the post-RUP `+0x18` MMIO write only for this fail-closed front IPP path; legacy RDI/non-front behavior must remain unchanged.
