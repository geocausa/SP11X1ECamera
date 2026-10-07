# Front public libcamera lifecycle qualification

Fresh native-lifecycle-20261007-02 uses corrected audit26 and qualified libcamera build03.
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
