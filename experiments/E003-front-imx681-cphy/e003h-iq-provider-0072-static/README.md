# E003h 0072 static IQ-provider FIFO

Static-only bridge after accepted 0071 live V4L2 requeue.

- Adds a software-owned, bounded FIFO for steady IQ capsules beginning at request5.
- Copies/owns provider bytes and enforces strict monotonically increasing request IDs.
- Existing request5 firmware is used only as a compatibility producer and is dequeued through the FIFO before the unchanged runner sees it.
- Request4 bootstrap/startup remains unchanged.
- No new MMIO, IRQ programming, BUS update, RT-CDM submission, sensor/CSID/VFE operation, request6, or userspace injection entrypoint.
- Runtime is not authorized by this static checkpoint.
