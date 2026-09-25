# E005f — original Windows rear4K user-mode FrameServer/KS IOCTL trace

Parent native Linux Git `92b05e1ae610afcdef0eb841cecea7d9c0abd899`. New experiment identity; never replay any consumed E005C/D/E work.

## Hard safety boundary

SP11 is remote-only during this stage. **Do not use KD, local kernel debugging, kernel breakpoints, kernel WinDbg attach, or any operation that can halt the Windows kernel.** Do not change BCD debug transport/settings. WinDbg/CDB may attach only to ordinary **user-mode camera processes** (camera client, FrameServer/DeviceMFT user-mode host where attach is permitted). Breakpoints must auto-continue and may only pause that user-mode process. Non-halting ETW/WPP and read-only static OEM analysis are allowed. If a trace requires kernel-stop semantics, abort it.

No camera frame/pixel payload, kernel pointer, DMA/IOVA, proprietary OEM binary or raw private debugger log enters Git.

## Evidence objective

Use a fresh finite Surface Camera Rear / Color / VideoRecord / NV12 3840x2160 session and user-mode tracing to identify the real user-mode camera host/device handle and KS DeviceIoControl control-code sequence associated with the 4K pin. Existing FrameServer evidence already identifies pin 2 as NV12 3840x2160@30 and the QCOM_AVStream_8380 camera symbolic-link family.

This stage may source-lock which user-mode handle/control path corresponds to the selected 4K stream. It **cannot by itself prove** FIFO8 non-null WM16 identity, hardware IRQ/ACK, DMA/IOMMU quiescence or safe native rear buffer retirement. Native rear hardware ISP remains DENIED.

## Actual E005f result (2026-09-25)

Fresh original-Windows rear Color/VideoRecord/NV12 3840x2160 session ran 20,049 ms and returned 203 valid frame handles with StartAsync/StopAsync success. ARM64 CDB attached only to the user-mode Windows Camera FrameServer svchost, with auto-continue CreateFileW/DeviceIoControl logpoints. No KD, no kernel debugger, no kernel breakpoint and no BCD debug-setting change occurred.

Private FrameServer trace SHA256 d8859976d0b1f1a5ed9dfd8760dc485656c8bd225872a2aded7053075fdb6d75 contains 4,598 observed user-mode DeviceIoControl calls. Microsoft SDK ks.h source-maps 0x002f0003 to IOCTL_KS_PROPERTY (1,599 calls), 0x002f4017 to IOCTL_KS_READ_STREAM (1,225 calls across exactly two user-mode pin handles, with per-handle counts 922 and 303), 0x002f0007 to IOCTL_KS_ENABLE_EVENT (18), 0x002f000b to IOCTL_KS_DISABLE_EVENT (4), and 0x002f000f to IOCTL_KS_METHOD (2). FrameServer opened the QCOM_AVStream_8380 filter and loaded QcDeviceMFT8380.dll and ksuser.dll in the same session. Raw handles/pointers and private CDB output remain Windows-private.

This establishes a real user-mode -> KS streaming boundary but does not yet prove which of the two IOCTL_KS_READ_STREAM handles is VideoRecord pin 2. Therefore it does not prove FIFO8/non-null WM16 identity or hardware DMA completion. Next gate: user-mode KsCreatePin/KsCreatePin2 PinId -> returned handle correlation, then bind the selected 4K pin to the original OEM queue path. Rear native ISP remains DENIED.

## Planned bounded trace

1. Confirm no stale camera/debugger processes or traces.
2. Start/identify the Windows Camera FrameServer and DeviceMFT user-mode host.
3. Attach ARM64 user-mode CDB/WinDbg only. Use auto-continue logpoints around user-mode `CreateFileW` and `DeviceIoControl` where possible.
4. Start one new finite rear4K WinRT capture, count only frame handles, no pixel serialization.
5. Stop capture, detach debugger, verify camera host and debugger exit.
6. Reduce private logs to control-code counts, selected device symbolic-link identity and source-backed scalar facts only.
7. Return normally to persistent Linux-first Golden and verify camera overlap guard.
