# E002b-r3f result — Windows-exact OV13858 identity transfer

Status: **SAFE BUS-LEVEL FAILURE / electrically clean**

## Runtime result

The one-shot candidate booted successfully and remained stable. It used:

- Golden kernel byte-for-byte;
- accepted r3d DTB byte-for-byte (`4eca2b3fb7f6793d780cc7d9e3642bf9f3a4703b7db011a6650f4857a2b12233`);
- accepted camera-only RPMh provider;
- r3f probe module `939cc97d40e33eaec82f28c219b71cfe7a03a9bfc91c9871b481e0d5ef16d0ac`;
- reproducible initrd `0ed680055bdf5359478a29451e167679f2cba2b7c4f8b0ba30841046a453dbb2`.

The probe reproduced the accepted rail/reset/MCLK path and changed only the sensor identification transaction to the exact Windows/QTI schema:

- CCI0/master1;
- 400 kHz FAST mode;
- Linux 7-bit address `0x10`;
- 16-bit register address `0x300b`;
- 16-bit read expecting `0xd855`.

The transaction still returned `-ENXIO` (`-6`). Teardown then disabled LDO16_B, LDO5_M, LDO1_M and LDO6_M cleanly.

No panic/oops/pstore record occurred. The temporary network disappearance observed by SP7 was normal reboot/network transition, not a crash. Wi-Fi, MultiMedia1 playback, MultiMedia3 capture, CAMSS `/dev/media0`, and sixteen VFE video nodes were healthy after boot.

## New physical boundary

The live TLMM state revealed an important omission:

- CCI0/master1 pins GPIO103/GPIO104 are claimed by `ac15000.cci` with function `cci_i2c`;
- all X1E `cam_mclk` capable pins GPIO96..GPIO99 remain **UNCLAIMED**, func0/GPIO;
- the rear probe node has no MCLK pinctrl state;
- `cam_cc_mclk1_clk` can therefore be enabled internally without Linux selecting a physical `cam_mclk` output pad.

This is now a stronger explanation for the NACK than address, CCI master, bus speed, or ID transaction format.

Linux also runtime-resumes the CCI node through `CAM_CC_TITAN_TOP_GDSC` during transfer, so a substantial portion of Windows's common camera-domain preamble is already represented by runtime PM. Do not add duplicate manual GDSC control without evidence.

## Next gate

Before another powered Linux probe, determine the **board-specific physical pad for Windows `cam_cc_mclk1_clk`**. X1E pinctrl exposes `cam_mclk` on GPIO96..GPIO99, but do not infer the MCLK1-to-pad mapping solely from numbering.

Preferred evidence: one-shot Windows boot, observe TLMM GPIO96..GPIO100 mux state before and during rear-camera D0 using SP7 KD and/or the Windows endpoint. Once the pad is proven, make the next Linux experiment a DT-only MCLK pinctrl correction while keeping r3f's exact transaction, accepted rails, reset, and CCI routing unchanged.
