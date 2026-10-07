# Fresh lifecycle04: actual signed threaded IPA lifetime qualification

Uses audit27/libcamera build06. The same public CameraManager and Camera capture
1 frame, restart for80 with the same configuration/app buffers, then release/
reacquire/reconfigure for80. This exercises actual IPA map/start/stop/unmap and
queued callbacks across kernel stream/profile resets in the signed threaded path.
Pipeline04 already proves the isolated path; this gate covers the normal trusted
opensource module path and repeated mapping lifetime. No automatic feedback.

Every app frame requires an actual IPA metering result with matching completion
time and a new stream identity per start. SensorTimestamp must be absent, since
buffer return time is not exposure time. All sensors suspend after each stop;
final release leaves neutral graph. Identity is fresh and one-use; keep pixels
private. Product quality and matched Windows lighting acceptance remain separate.

# Front public libcamera lifecycle qualification

Fresh native-lifecycle-20261007-03 uses corrected audit27 and qualified libcamera build03.
A small qualification application uses the public libcamera API; it is not a
product capture runtime. The same CameraManager and Camera object capture one
frame, restart with80 frames using the same configuration and application DMA
buffers, then release, reacquire, reconfigure and capture80 frames. No module
reload intervenes. Each finite capture must finish exactly, stop cleanly, carry
fresh stream identity and pair each hardware output with statistics. The kernel
must retire every owner group, reset its semantic FIFO and load a fresh profile
each start. No pixel data is processed or exported by this lifecycle test.

Protected Golden/default assets stay unchanged; the one-use service returns
Golden regardless of result. Consume and retire this identity after one attempt.
IPA/automatic3A, rear ISP and optical quality remain separate requirements.

Lifecycle01 passed the one-frame round then rejected the second start before
STREAMON: cached profile remained after its producer FIFO closed. Successful
STREAMOFF now retires stream-owned profile/FIFO after worker exit. Unsafe/pinned
paths keep their early returns. Lifecycle01 consumed/retired; never rearm.

Lifecycle02 verified profile/FIFO reinitialization but reached the legacy static
one-start-per-module NV12 guard. Profile mode now admits only inactive, unpinned
workers and retains the exact disabled-WM/linear-MODE cold-state readback gates.
The earlier diagnostic modes retain their one-start guard. Lifecycle02 consumed
and retired; never rearm.

Lifecycle03 physically passed161 app frames,880 owner checks/176 retirements,
185 typed requests and3 firmware loads; all three stops clean and all sensors
suspended after each. Original Golden hashes unchanged. All three lifecycle
identities consumed/retired. Pair timestamps are completion-time association;
SensorTimestamp first-row exposure/CLOCK_BOOTTIME semantics are not qualified.
