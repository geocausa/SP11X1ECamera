# E003h 0069 — unarmed bounded four-frame first-steady candidate

One ordinary V4L2 STREAMON session with four buffers queued before start. The only new hardware actions beyond accepted 0068 are one existing nine-client BUS retarget to proven-reusable slot1 and one existing five-BL steady `0x958/request4` submission. No post-DQBUF QBUF requeue, fifth frame, asynchronous STREAMON, same-boot retry, new MMIO primitive or new register value is authorized. Golden remains the saved default and candidate boots are one-shot only.
