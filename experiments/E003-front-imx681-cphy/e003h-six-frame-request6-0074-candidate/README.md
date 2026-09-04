# E003h 0074 bounded request6 runtime candidate

Disposable one-shot extension of accepted E003h 0072.

The accepted startup/priming, front IMX681 mode, CSIPHY/CSID/VFE programming, two-slot ownership, RT-CDM lifecycle and Golden-return policy are unchanged. The candidate substitutes the 0074 CAMSS module, the six-frame V4L2 helper, and the fresh atomic Windows-derived request4/request5/request6 capsules.

Expected output order is exactly `[0,1,2,3,0,1]`. Buffer0 is requeued immediately after sequence0 and buffer1 immediately after sequence1. Request5 and request6 must traverse the owned monotonic IQ FIFO in exact order `5 -> 6`. There is one helper invocation, no loop, no same-boot retry, and any ambiguity consumes the one-shot and requires external return to persistent Golden.
