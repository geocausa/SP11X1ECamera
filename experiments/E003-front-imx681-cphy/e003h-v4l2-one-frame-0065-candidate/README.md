# E003h 0065 — bounded ordinary V4L2 one-frame candidate

Golden-safe one-shot candidate. Camera/ISP hardware programming is byte-for-byte the already-proven 0064 path. The only new behavior is software ownership: two real vb2 MMAP buffers are QBUF'd, STREAMON hands them to the proven bounded runner, slot0 is completed through vb2, DQBUF returns the full QC10C frame, and STREAMOFF flushes slot1 without a second hardware stop.

This is diagnostic-arm-only, exactly one helper invocation, no same-boot retry. Any teardown-unsafe condition pins DMA ownership until mandatory reboot.
