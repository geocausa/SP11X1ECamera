# E005h — original Windows rear4K pin2 -> KS read-stream handle correlation

Parent Git: 5a8b06ca94785ff9a33e2c1ec273742348a1250f.

SP11 remained remote-only. This experiment used ARM64 CDB only against the ordinary user-mode Windows Camera FrameServer process. No KD, no kernel debugger, no kernel breakpoint, no BCD debug-setting change, and no kernel halt occurred.

## Source lock

Installed Windows ksuser.dll SHA256:
00baa6d3ad353ceb1547da8bd1e1aa913a7a26b27c0cf8deaed3adf4521bd369.

Microsoft SDK 10.0.26100.0 shared/ks.h defines KSPIN_CONNECT with PinId at offset 0x30 on ARM64 and declares KsCreatePin/KsCreatePin2. Installed ksuser.dll exports KsCreatePin at RVA 0x3ca0 and KsCreatePin2 at RVA 0x3ce0. Static ARM64 disassembly source-locks post-create points at KsCreatePin+0x254 (RVA 0x3ef4) and KsCreatePin2+0x3c0 (RVA 0x40a0). At those points the create has returned while the original KSPIN_CONNECT pointer and output PHANDLE remain available.

## Physical user-mode result

One fresh original Windows Surface Camera Rear / Color / VideoRecord / NV12 3840x2160 session ran 15,055 ms and returned 157 valid frame handles. StartAsync and StopAsync both succeeded.

The user-mode FrameServer trace observed successful KsCreatePin creation of pin IDs 0, 1, 2 and 3. In the same process/session, IOCTL_KS_READ_STREAM (0x002f4017) occurred 1,449 times across exactly two user-mode pin handles. Correlation against the same returned pin handles produced:

- pin 0: 0 read-stream calls
- pin 1: 0 read-stream calls
- pin 2: 361 read-stream calls
- pin 3: 1,088 read-stream calls

The exact handle values are deliberately not exported. The previously source-locked Windows FrameServer media-type evidence identifies pin 2 as the NV12 3840x2160 VideoRecord pin. Therefore E005h proves that the real rear-4K VideoRecord pin 2 is one of the two actual KS streaming handles and records 361 real IOCTL_KS_READ_STREAM calls on that exact handle in this bounded session.

Private evidence hashes:
- CDB log: 8a6aa06fac11f30a8b80105bf32be6e2eea34b3371b6c4e5f60fc6a4ab4972fe
- capture scalars: c2a99087bef8ba2ca050934e3d55bd5a3b9f89ec1dbd8ff306f5ed645dc7715d
- capture script: 3fdf8fb612578d205a0ed7f212f725809a8890a244c40766128bf7503aa90c55

## Boundary

This is a strong L0/L1 user-mode-to-KS identity result, not an ISP DMA fence. It does not yet prove which original kernel driver/device instance receives pin2 reads, a same-frame FIFO8 group8 entry, a non-null outstanding WM16 token/tag, hardware IRQ/ACK, DMA/IOMMU quiescence, or six-group safe stop. Native processed rear ISP remains DENIED.

Next gate: source-bind this exact pin2 KS read-stream path through the original QCOM_AVStream kernel stack into the selected OEM ISP device/queue path, then continue toward FIFO8/non-null WM16 and independent hardware completion.
