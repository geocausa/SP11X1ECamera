# Bounded live producer protocol

The single front PIX fd remains the session owner.

1. Configure the already-proven front graph and QC10C format; allocate and queue four buffers.
2. Generate and submit request4 through `V4L2_CID_QCOM_CAMSS_X1E_IQ_CAPSULE`.
3. Call `VIDIOC_STREAMON`. The driver accepts only `depth=1,last_enqueued=4,last_dequeued=3`, schedules the live worker and returns.
4. Once request5 producer state is available, generate its 41,088-byte capsule and submit it through the same control. The monotonic provider requires request5 next.
5. Before the request5 steady gate, the capsule must already be queued. The runner takes it without waiting, materializes only the steady section and submits at the existing request5 Epoch0 site.
6. Repeat for request6.
7. Complete the existing bounded six-frame lifecycle and STREAMOFF.

Submitting R5/R6 before STREAMON makes the STREAMON preflight fail (`depth != 1`). Missing R5/R6 at the gate fails closed. A closed provider is never auto-reopened while streaming.
