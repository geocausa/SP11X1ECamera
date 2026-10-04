# E011EV: joined CC08E8 record claim to CreateFileW frontier

Status: **PASS_JOINED_CC08E8_CREATEFILEW_FRONTIER**.

E011EV executes original `0xCC08E8` against the E011EU source-qualified attach-time lowIO table. Under the inherited owned single-thread lock contract, global mutex 7 is acquired, record zero is acquired and marked active, the record keeps its invalid-handle sentinel, global mutex 7 is released, and `0xCC08E8` returns index zero. The record lock remains held. This is a bounded owned-fixture selection, not a claim about native Windows record selection or mutex bytes.

Original `0xCFD570` then continues to the exact `CreateFileW` boundary. The path pointer is the independently verified 76-byte UTF-16 output. Arguments are source-qualified as GENERIC_READ, FILE_SHARE_READ, a 24-byte SECURITY_ATTRIBUTES with null descriptor/inherit true, OPEN_EXISTING, normal attributes and null template. `CreateFileW` itself is not executed.

Four placements pass with 936 altered-contract rejections. No camera Start, reboot, kernel build, production-C or PM change was required.

NEXT **E011EW** resolves actual file/provenance/handle authority for this exact front-camera path, using bounded Windows/SP7 KD evidence when it is stronger than an owned assumption, then resumes the original function only if the handle result is qualified. Native rear runtime remains denied.
