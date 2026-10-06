# E011KD — native +0xC0 function descriptor frontier

PASS. E011KD executes the native-qualified `0x5B828C -> 0x5BA820` function with `x0=caller SP+0x60`. The non-null branch writes descriptor pointer RVA `0x1624140` and size `0xA4`, returns `w0=0`, and resumes at `0x5B8290`, where execution stops.

NEXT E011KE consumes that return and descriptor size, qualifies the post-call branches, and stops before `0x5B82A8` reads restored caller `x19+0x20`. No new camera Start, reboot, rear runtime, or kernel build is used.
