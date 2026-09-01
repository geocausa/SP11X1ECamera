# E003h 0065 — bounded ordinary V4L2 one-frame bridge

0064 proved a complete Linux front-camera QC10C frame using the bounded diagnostic runner. 0065 changes no camera/ISP hardware programming. It connects the exact X1E VFE1 PIX QC10C vb2 path to that already-proven runner only when the diagnostic module is explicitly armed.

The runtime contract is deliberately one frame: userspace QBUFs exactly two MMAP buffers, STREAMON synchronously executes the proven 0064 lifecycle, slot0 is completed with `vb2_buffer_done(...DONE)`, DQBUF returns it, and STREAMOFF flushes the unused slot1. The generic VFE680 PIX one-WM `-EOPNOTSUPP` guard remains intact for all non-bridge paths.

If teardown is ever reported unsafe, the bridge pins DMA/buffer/power ownership and refuses normal stop/unprepare reuse until the mandatory candidate reboot.
