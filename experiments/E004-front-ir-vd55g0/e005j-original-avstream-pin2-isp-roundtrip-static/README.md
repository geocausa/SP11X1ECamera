# E005j — original Windows AVStream pin2 → ISP request/completion roundtrip static source lock

Parent Git `27e2c5206f5b13b57a2c11b4b9ab06bd33b6ae12`. SP11 Golden Linux; Windows system volume mounted read-only. Original `surfacecamavs8380.sys` SHA256 `b97c4338c7c8868b9f3b73a34f6aea338ae6ab2a773bfd65f3b8fd31941577ed`.

E005h already established physically, in a fresh original Windows rear session, that KS **pin 2 is the NV12 3840×2160 VideoRecord streaming pin** and that its exact returned pin handle issues real `IOCTL_KS_READ_STREAM` calls. E005j does not repeat that live experiment. It source-locks what the original Qualcomm/Microsoft Surface AVStream driver does around its video-pin request and ISP completion paths.

The exact original ARM64 source/log/vtable map establishes the request half:

`CVideoPin::HandleExtBuffer (0x8fd30)` → `CCaptureFilter::TriggerStart (0x80ef0)` → `CCaptureFilter::SubmitPendingPackets (0x7fa8)` → `CCaptureFilter::SendPacketInternal (0x9b18)` → `IfeNode::ProcessRequest (0x96a10)`.

The original `CVideoPin` vtable at RVA `0x2fab8` contains inherited `CPin::ValidateBuffer` at slot `+0x68`, `CPin::Process` at `+0x78`, the video-specific `CVideoPin::HandleExtBuffer` at `+0xa0`, `CPin::CompleteFrame` at `+0xb8`, and `CPin::NotifyFrameCompleted` at `+0xc0`.

The completion half is likewise source-locked:

`CDispatchHandler::IspWorkerThreadProc (0x8a8d0)` → notification wrapper → `CDispatchHandler::OnIspNotification (0x17428)` → both `GetIspNotification (0x17798)` and `CCaptureFilter::ProcessIfeFrame (0x5488)`. The original dispatcher contains the `IFE_MSG_ID_GROUP0_IMAGE` path and calls `ParseIFEMessage (0x8a988)`, whose original logging includes `Frame Done IFE -%requestId`. `ProcessIfeFrame` loads pin virtual slot `+0x68` (the `ValidateBuffer` slot) and later `+0xb8` (the `CompleteFrame` slot). `CPin::CompleteFrame` itself loads slot `+0xc0`, which the same video-pin vtable resolves to `CPin::NotifyFrameCompleted`.

This closes a source-level AVStream request/return loop around the real VideoRecord pin role: user-mode E005h pin2 feeds the original video-pin path, the driver submits through the IFE request graph, and ISP notifications are validated/completed back through the pin completion machinery.

**Boundary:** this is static original-driver source binding plus the already-published E005h user-mode physical pin identity. It does NOT dynamically bind one pin2 `IOCTL_KS_READ_STREAM` to one kernel object/requestId, does NOT prove that a particular live pin2 frame used GROUP0 rather than another graph branch, and does NOT establish same-frame FIFO8 group8 → non-null WM16 identity, independent WM16 IRQ/ACK, DMA/IOMMU quiescence, or six-group safe stop. E005i separately proves BF is one member of original GROUP3_STATS, not a video-buffer DMA fence. Native processed rear ISP remains DENIED.

Run `PYTHONDONTWRITEBYTECODE=1 python3 verify.py` on SP11 Golden Linux with the Windows volume mounted read-only at `/mnt/sp11-win-ro`.
