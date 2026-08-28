# E003h Windows VFE1 FULL buffer layout

Date: 2026-08-28

Policy: same-machine Windows on this exact SP11 is the behavioral oracle. Qualcomm's public camera-driver source and the kernel's QC10C documentation are used only to name/decode the register and memory layout that Windows itself proves.

## Result

The Windows VFE1 FULL output is a 2560x1440 10-bit YUV420 TP10 UBWC surface. In Linux V4L2 terminology the corresponding opaque format family is `V4L2_PIX_FMT_QC10C`, not linear NV12 and not QC08C.

The proof is mechanical from the E003g same-machine VFE1 capture:

- FULL_Y client 0 `PACKER_CFG=0x0b`; Qualcomm VFE bus-ver3 defines value 11 as `PACKER_FMT_VER3_TP_10`.
- FULL_C client 1 has the same packer.
- Both clients have UBWC compression enabled (`MODE_CFG` has the published `BIT(1)` compression-enable bit set).
- FULL_Y `IMAGE_CFG_0=0x05a00a00` => 2560x1440.
- FULL_C `IMAGE_CFG_0=0x02d00a00` => 2560x720.
- Both use `IMAGE_CFG_2=0x0e00` => 3584-byte stride.

Standard TP10 UBWC geometry for 2560x1440 produces exactly the Windows values:

- stride = align((2560 * 4 / 3), 256) = 3584 = `0x0e00`;
- Y metadata = `0x6000`;
- Y TP10 data = 3584 * 1440 = `0x4ec000`;
- Y slice = `0x4f2000`, exactly the Windows FULL_Y frame increment;
- C metadata = `0x3000`;
- C TP10 data = 3584 * 720 = `0x276000`;
- C slice = `0x279000`, exactly the Windows FULL_C frame increment;
- total surface = `0x76b000` = 7,778,304 bytes.

Both independent Windows live phases also prove the address layout directly:

`Y_META -> Y_TP10_DATA -> C_META -> C_TP10_DATA`

For each phase:

- `Y_IMAGE - Y_META = 0x6000`;
- `C_META - Y_META = 0x4f2000` (exactly one Y slice);
- `C_IMAGE - C_META = 0x3000`.

Thus the FULL surface is one contiguous allocation. A Linux vb2 queue can represent it with one DMA buffer; the VFE driver must derive the four internal meta/data addresses from that base. Four separate V4L2 planes are not required by the buffer allocator.

## Linux consequence

Current CAMSS VFE680 cannot represent this path:

1. its v2 output allocator hard-codes one WM;
2. PIX still aliases to the RDI-only WM mapping;
3. its PIX format table is a TODO alias of the RDI table;
4. it has no QC10C/TP10 UBWC geometry or metadata-address programming;
5. it does not implement the Windows RAW-to-YUV/scaler configuration.

Mapping PIX merely to WM0/WM1 as linear NV12 would therefore be a false parity shortcut.

The buffer side is nevertheless representable without changing vb2's fundamental allocation model: one `QC10C` buffer can hold the exact contiguous Windows layout, and CAMSS can derive client-0/client-1 meta/data addresses from its DMA base.

## Remaining blocker

Qualcomm's public VFE680 driver explicitly notes that IFE top configuration is programmed via CDM. The static Windows `DEVICE_START` path likewise submits `0x803` initial configuration packets after IFE start and before CSID start. Those exact Windows packets must be captured/decoded before implementing the VFE1 RAW-to-TP10/scaler path.

Do not deploy or stream a VFE1 candidate until that command-packet oracle is resolved.
