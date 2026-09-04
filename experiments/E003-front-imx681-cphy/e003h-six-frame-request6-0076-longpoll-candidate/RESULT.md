# 0076 long-poll request6 result

PASS. Exact 0074 kernel/module/DT and atomic R4/R5/R6 completed six frames with V4L2 indices `[0,1,2,3,0,1]` and sequences `[0,1,2,3,4,5]`. RT-CDM stopped cleanly at userdata 6 with `error=0` and `faulted=0`.

The only functional change from A3 was the userspace DQBUF watchdog from 1 s to 5 s. This reclassifies A3 as a test-harness timeout: on that run the first completion missed the 1-second watchdog, the helper pinned, and therefore never requeued buffer0/1 for request5/request6.

The prior A3 interpretation based on the named `msm_vfe1` `/proc/interrupts` count is superseded; 0075a proved that counter can remain zero in a known-good runtime.
