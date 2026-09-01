# E003h 0067 — five-group slot lifetime validation

Static-only checkpoint based on the successful 0066 two-frame V4L2 session. 0067 adds no hardware operation. It counts Windows-proven CSID BUF_DONE bits 0/4/5/6/9 from the register value the ISR already reads, waits for all five completion generations, and retires the existing independent ownership FIFOs so slot0/slot1 must be reusable before the same proven teardown.

A later candidate may reuse a slot only if this exact validation succeeds at runtime.
