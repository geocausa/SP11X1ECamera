# E003h 0071 — bounded live V4L2 requeue candidate

Four buffers are queued before STREAMON. STREAMON returns while the bounded worker remains live. Sequence0/index0 is copied by userspace and immediately re-QBUF'd. The already-proven replay3/request4/request5 hardware sequence continues, and request5 must return the same index0 as sequence4. No request6 or continuous loop is authorized.
