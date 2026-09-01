# E003h 0066 result — PASS

0066 achieved two complete ordinary Linux V4L2 front-camera frames in one STREAMON session. Userspace QBUF'd two buffers, STREAMON succeeded, DQBUF returned index 0/sequence 0 and index 1/sequence 1 at 0x76b000 bytes each, and STREAMOFF succeeded. Both QC10C surfaces span all 1440 Y / 720 C lines and have different SHA256 values. No new camera/ISP hardware operation was introduced for 0066. RT-CDM stopped cleanly at FIFO 30 with no fault, and the machine returned to Golden.

Next boundary: continuous vb2 requeue/retarget while the hardware remains live, with the proven teardown moved to STREAMOFF rather than after the prequeued pair.
