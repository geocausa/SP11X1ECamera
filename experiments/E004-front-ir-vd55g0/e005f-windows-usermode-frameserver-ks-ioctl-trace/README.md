# E005f — original Windows rear4K user-mode FrameServer/KS IOCTL trace

Parent native Linux Git `92b05e1ae610afcdef0eb841cecea7d9c0abd899`. New experiment identity; never replay any consumed E005C/D/E work.

## Hard safety boundary

SP11 is remote-only during this stage. **Do not use KD, local kernel debugging, kernel breakpoints, kernel WinDbg attach, or any operation that can halt the Windows kernel.** Do not change BCD debug transport/settings. WinDbg/CDB may attach only to ordinary **user-mode camera processes** (camera client, FrameServer/DeviceMFT user-mode host where attach is permitted). Breakpoints must auto-continue and may only pause that user-mode process. Non-halting ETW/WPP and read-only static OEM analysis are allowed. If a trace requires kernel-stop semantics, abort it.

No camera frame/pixel payload, kernel pointer, DMA/IOVA, proprietary OEM binary or raw private debugger log enters Git.

## Evidence objective

Use a fresh finite Surface Camera Rear / Color / VideoRecord / NV12 3840x2160 session and user-mode tracing to identify the real user-mode camera host/device handle and KS DeviceIoControl control-code sequence associated with the 4K pin. Existing FrameServer evidence already identifies pin 2 as NV12 3840x2160@30 and the QCOM_AVStream_8380 camera symbolic-link family.

This stage may source-lock which user-mode handle/control path corresponds to the selected 4K stream. It **cannot by itself prove** FIFO8 non-null WM16 identity, hardware IRQ/ACK, DMA/IOMMU quiescence or safe native rear buffer retirement. Native rear hardware ISP remains DENIED.

## Planned bounded trace

1. Confirm no stale camera/debugger processes or traces.
2. Start/identify the Windows Camera FrameServer and DeviceMFT user-mode host.
3. Attach ARM64 user-mode CDB/WinDbg only. Use auto-continue logpoints around user-mode `CreateFileW` and `DeviceIoControl` where possible.
4. Start one new finite rear4K WinRT capture, count only frame handles, no pixel serialization.
5. Stop capture, detach debugger, verify camera host and debugger exit.
6. Reduce private logs to control-code counts, selected device symbolic-link identity and source-backed scalar facts only.
7. Return normally to persistent Linux-first Golden and verify camera overlap guard.
