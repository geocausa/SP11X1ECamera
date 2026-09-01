# E003h 0071 — bounded live V4L2 requeue static proof

Base: accepted 0070R1 five-frame/request5 runtime at `67154ffe9ba2c866b3b5a972de3cde542dbce701`.

0071 changes only Linux vb2 ownership/timing. Four buffers are queued before STREAMON. STREAMON schedules the bounded five-frame runner and returns. After sequence0 completes with all five CSID completion groups retired, vb2 returns index0 to userspace; userspace immediately re-QBUFs index0. The existing replay3 and request4 paths continue on initial indices2/3. Before the existing request5 BUS refill, the worker requires the pending buffer to be the same index0 object and uses it for sequence4. No request6, continuous loop, new MMIO, new IRQ programming, new BUS recipe, or new RT-CDM recipe is introduced.

Front-PIX QBUF is explicitly software-only in this candidate so it cannot enter generic VFE680 one-WM programming while the private nine-client path is live.
