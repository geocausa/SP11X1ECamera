# E003h 0068 result — first actual slot reuse / third V4L2 frame

0068 succeeded in one authorized ordinary V4L2 session. Three queued QC10C buffers returned as DQBUF sequences 0, 1 and 2, each 7,778,304 bytes and each a complete 1440-line Y + 720-line C surface with a distinct SHA256. After 0067-proven five-group retirement freed slot0, Linux rebound slot0 to buffer2, performed the Windows-proven nine-client BUS refill and replay3/request3, and received a complete third frame. RT-CDM advanced from FIFO30 to FIFO35, stopped with error=0/faulted=0, and the machine returned cleanly to Golden.

This proves actual two-slot hardware reuse, but not continuous V4L2 requeue: all three buffers were queued before STREAMON and the bounded runner still tears hardware down before STREAMON returns.
