# E003i-L — deferred live IQ ingress

This static productionization checkpoint fixes the timing mismatch between the already-proven V4L2 IQ control and a genuinely adaptive per-request producer.

The previous E003i-D contract required R4/R5/R6 to be queued before STREAMON and the worker dequeued/materialized all three before pipeline power-on. That is correct for fixed regression capsules but cannot consume state learned while the stream is running.

This checkpoint changes **timing/ownership only**:

- STREAMON requires exactly one pre-queued capsule: request4.
- The existing standard `X1E Front IQ Capsule` V4L2 control remains the only producer ingress; no private ioctl or sysfs path is added.
- STREAMON schedules the existing camera worker and returns. While that worker is live, the same exclusive fd may submit request5 and request6 through `VIDIOC_S_EXT_CTRLS`.
- Request5/request6 remain strict monotonic provider entries.
- The worker no longer dequeues R5/R6 before hardware start.
- At each already-proven steady Epoch0 gate the runner consumes the corresponding queued capsule **without sleeping across an Epoch0 boundary**, parses it, and materializes only its steady payload.
- If the required request is not ready at its gate, the runner fails closed with `-EAGAIN` and performs the existing safe unwind.
- The previous upfront `capsule_next/capsule_next_next` runner mode remains supported for non-live compatibility callers.
- Unsafe teardown still returns before materialized DMA is released, preserving the existing pin-until-reboot ownership rule.

## V4L2 lock proof

Linux 7.1.5 `VIDIOC_STREAMON` is `INFO_FL_QUEUE` and therefore uses `vb2_q.lock`; CAMSS sets that to `video->q_lock`. `VIDIOC_S_EXT_CTRLS` is a control ioctl and resolves to `vdev->lock`; CAMSS sets that to the distinct `video->lock`. The live worker itself is asynchronous. Thus later IQ control writes do not deadlock behind STREAMON's queue mutex.

## Intended bounded sequence

`configure/QBUF x4 → submit R4 → STREAMON → derive/submit R5 → derive/submit R6 → DQBUF six frames → STREAMOFF`

This checkpoint does **not** authorize camera runtime. It also does not yet define continuous request7+ behavior. The next producer gate is live Linux request-state acquisition (Tintless statistics/config and TMC/ADRC/3A state) feeding the already-clean LSC/GTM/scalar/bank backends.
