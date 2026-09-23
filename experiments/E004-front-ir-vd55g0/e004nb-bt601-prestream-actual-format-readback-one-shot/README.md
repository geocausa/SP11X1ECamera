# E004nb: fresh opt-in BT601 pre-stream real V4L2 S_FMT / G_FMT numeric readback

The distinct prior consumed E004na boot FAILED before sensor STREAMON:
front virtual NV12 output format returned a non-identical colour
metadata tuple but only a generic mismatch was logged. It captured
ZERO frames, was retired after automatic protected Golden return.
Root cause and which fields the V4L2 loopback driver returns were
UNKNOWN. Never rearm E004na or prior consumed identities.

E004nb is a NEW separately source-locked guarded single-use candidate.
Its sole material change is a metadata-only pre-stream scalar readback
of the exact requested S_FMT, returned S_FMT, and independent G_FMT
values for front/rear; no photo/pixel/tile/thumb/hash exported. The
strict existing failure gate remains unchanged: do NOT automatically
accept an unknown or 709-tagged consumer stream as correct BT601.
On mismatch the publisher exits before native sensor streaming,
original guarded runner records FAIL and single-use identity is
consumed; preserve numeric evidence and automatically return Golden.
If all fields really echo, require full original front1080/rear4K
ordinary UID1000 app/color caps/29fps each gain window/final neutral
GPU/Golden checks. Any captured private photos stay ONLY SP11
geoca0700/photos0600; none expected if same pre-stream failure.
Normal Golden camera/IR/nonnative DSP configuration unchanged.
