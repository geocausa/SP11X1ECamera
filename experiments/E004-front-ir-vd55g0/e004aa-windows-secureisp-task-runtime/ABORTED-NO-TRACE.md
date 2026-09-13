# E004aa — aborted pre-trace Windows one-shot

Status: **ABORTED BEFORE ACCEPTED TRACE / NO RUNTIME EVIDENCE**

This directory contains only the Linux preboot and Windows BootNext arming records from an attempted SecureISP dynamic task trace.

The chat/tool session became unstable before a valid IR Secure Companion task trace was captured. A stale KD process on SP7 left the Windows target paused. During chat handoff recovery:

1. SP7 stale KD was killed.
2. KD was reattached on `net:port=50005,key=1.2.3.4`.
3. SP11 Windows was deliberately broken into KD.
4. `.reboot` was issued.
5. The Windows one-shot fell back to protected Linux Golden.
6. Golden was verified:
   - kernel `7.1.5-sp11-render-parity-v4+`
   - BOOT_IMAGE FullIO v19c
   - saved entry `sp11-audio-fullio-v19c`
   - empty `next_entry`
   - no camera/CAMSS modules
   - no media/video nodes

No E004aa task trace, task ordering, payload values, frame evidence, or SecureISP runtime result is accepted from this attempt.

If the dynamic task trace is still needed, start a fresh one-shot experiment rather than trying to resume this attempt.
