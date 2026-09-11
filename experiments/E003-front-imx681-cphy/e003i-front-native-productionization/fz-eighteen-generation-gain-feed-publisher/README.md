# E003i-FZ — eighteen-generation gain-feed publisher

Status: **PASS OFFLINE G1..G18 publisher / no camera runtime.**

FZ extends FR by exactly one bounded validation change: the accepted generation upper bound moves from G15 to G18. The binary record ABI, little-endian float-bit publication, request identity law `request = generation + 3`, and all error handling remain unchanged.

Acceptance compiles and executes the real C source, requires G1..G18 to publish and decode correctly, requires G19 to reject with `-EINVAL`, and proves the source delta against FR is only the upper bound.
