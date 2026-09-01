# E003h 0065 result — first ordinary V4L2 front frame

0065 succeeded on its single authorized candidate boot. Userspace used the standard V4L2 sequence `QBUF(2) -> STREAMON -> DQBUF -> STREAMOFF`; no sysfs RUN trigger was invoked. `DQBUF` returned slot0 with 7,778,304 bytes and sequence 0.

The returned QC10C surface is complete: 1440/1440 luma lines and 720/720 chroma lines, with every expected metadata/data page populated. RT-CDM stopped normally at FIFO 30 with error=0/faulted=0. No camera IOMMU/SMMU fault, Oops, SError, or kernel panic was recorded. Golden return is verified.

This validates ordinary vb2 ownership for one front-camera frame. The next boundary is continuous multi-frame streaming: keep the proven pipeline alive, retire each CSID BUF_DONE video generation to userspace, retarget the nine BUS clients to the next queued vb2 surface, then use the already-proven teardown only at STREAMOFF.
