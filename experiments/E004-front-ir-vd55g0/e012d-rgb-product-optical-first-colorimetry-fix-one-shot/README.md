# E012D — corrected RGB product optical-first one-shot

E012D is the fresh retry after E012C failed closed before its first optical frame. E012C proved the product route/daemon could select front, but the maintained publisher exited before frame 1. The corrected maintained publishers now validate the loopback's independently read-back **effective** BT.601 semantics, accepting the V4L2-defined DEFAULT (zero) optional enc/range/xfer fields only when they map to SMPTE170M/601/limited/709. The product installer also carries the route parser dependency explicitly.

This identity is fresh and single-use. Its first live gate remains exactly two root-private current-product renders: front 1920x1080 and rear 3840x2160. No repeated switch soak is allowed before both images are visually inspected.
