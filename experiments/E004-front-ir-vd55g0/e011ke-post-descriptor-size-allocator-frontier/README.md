# E011KE — post-descriptor size to allocator frontier

PASS. E011KE resumes with function return `0` and descriptor size `0xA4`, rejects the return-one and zero-size exits, reuses E011DS authority for caller `x19=RVA 0x17A4230` and `x19+0x20=0`, computes allocation size `0x1480`, and stops before `0x5B82C8 -> 0xCAE740`.

NEXT E011KF reuses the already-qualified process-heap allocator contract to allocate exactly `0x1480` bytes and stops before the result branch at `0x5B82D0`. No new camera Start, reboot, rear runtime, or kernel build is used.
