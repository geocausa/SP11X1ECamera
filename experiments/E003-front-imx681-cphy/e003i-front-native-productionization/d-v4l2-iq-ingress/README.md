# E003i-D — standard V4L2 IQ producer ingress

This static checkpoint connects the already-proven provider FIFO to the normal front PIX `/dev/video*` API without reintroducing sysfs, firmware seeding, or a private ioctl.

## ABI

The exact X1E front PIX node exposes one write-only, execute-on-write compound `V4L2_CTRL_TYPE_U8` control named **X1E Front IQ Capsule**. Its payload is exactly 41,088 bytes, the already-proven capsule ABI. The local control ID is `V4L2_CID_USER_BASE + 0x1240`.

Each successful `VIDIOC_S_EXT_CTRLS` write copies and validates one capsule into the existing provider FIFO. A closed provider auto-opens at request4. The FIFO then requires strict monotonic request5 and request6. Any parse/order/queue error closes and purges the partial sequence.

The front PIX node is single-open so one producer/capture session owns the FIFO. Open starts empty/closed; normal close purges safe state. A teardown-unsafe session remains pinned and blocks reopen until reboot.

STREAMON is still the standard VB2 operation and requires exactly three primed capsules: request4, request5, request6. The included `feed-x1e-iq.c` helper only demonstrates/compiles the control ABI and deliberately **does not issue STREAMON**.

No camera hardware runtime is authorized or executed by this checkpoint.
