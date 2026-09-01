# E003h 0069 — bounded four-frame first-steady proof

Static-only continuation of accepted 0068. Four V4L2 buffers are queued before STREAMON. After frame2 retires slot1's five Windows-proven completion groups, the next CSID Epoch0 generation rebinds slot1 to buffer3, performs one existing nine-client BUS update, then submits the already-materialized five-BL first steady `0x958` batch with Windows-proven requestId 4. No post-DQBUF QBUF requeue, fifth frame, asynchronous STREAMON, new MMIO primitive or new register value is authorized.

The disposable request4 capsule remains local/untracked; it differs from the exact successful 0068 capsule only at request-id byte offset `0x2c` (`2 -> 4`). Its hash and hash-only manifest are recorded here.
