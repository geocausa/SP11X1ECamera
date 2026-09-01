# E003h 0071 result

PASS: first live V4L2 DQBUF->QBUF requeue while front camera hardware remained streaming. Four MMAP buffers produced five complete frames; index0 returned as sequence0, was re-QBUF'd live, and returned again as complete distinct sequence4 through exact request5. No request6.
