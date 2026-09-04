# E003h 0076 long-poll helper diagnostic

Userspace-only diagnostic on the exact 0074 kernel/module/IQ assets.

Delta from the 0074 helper:
- DQBUF poll watchdog: 1000 ms -> 5000 ms.
- Add CLOCK_MONOTONIC timestamps around each poll.
- No V4L2 ordering, buffer count, requeue order, format, sensor, kernel, DT, or IQ change.

Purpose: determine whether A3's first-DQBUF failure was caused by the 1-second userspace watchdog while the 0074 kernel was still making bounded progress.
