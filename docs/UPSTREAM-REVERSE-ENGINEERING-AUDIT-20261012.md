# Reverse-engineering exclusion audit — 2026-10-12

The earlier C-PHY instruction to reject all private Windows tuning/deltas was
too broad if applied to independently reconstructed functional register behavior.
This audit corrects that instruction; it does not quantify lost progress.

The 121 ordered address/value pairs in our existing C-PHY configuration match
ooaklee's public runtime-observed configuration array exactly. The pinned public
header declares independently transcribed runtime MMIO observations, not copied
vendor source or an extracted binary payload. It is now retained with its
original GPL declaration/comments under src/upstream/phy/cphy-x1e-observed.

The legacy source labels its array as the exact Windows vendor table. That
legacy array is not relabeled or copied into the replacement. The independently
observed public source supplies the functional sequence. Identical tuples are
engineering evidence, not a way to change the origin of an old copy.

The match covers configuration addresses/values only. It does not establish
equivalence of delays, reset/common/IRQ/shutdown, clocks, power or retirement.
The public2.406-Gsymbol/s and project2.400-Gsymbol/s profiles still require
deliberate integration and fresh testing. Start the port from observed working
source plus existing project evidence; do not require all functional receiver
settings to be re-derived solely from generic public Qualcomm tables.

Independently reconstructed functional behavior and our measured/generated work
are eligible. Direct Windows calibration/vendor-table/tuning/blob copies remain
excluded. Array syntax is not the criterion: derivation is. Keep our qualified
sensor timing/controls, CSID/CDM facts, allocator/completion/ownership work and
independent calibration. Unknown origin requires a specific evidence finding,
not a blanket Windows-origin rejection.

Kernel MMIO documentation describes hardware reverse engineering as a purpose
of tracing. Kernel contributions also need compatible licensing, contributor
rights certification, reviewable patches, style and subsystem review.
Upstream drivers may request separately supplied firmware; this project's
no-proprietary-camera-startup-input target is stricter than a universal firmware
ban. No upstream acceptance or new hardware admission is claimed here.

Primary references:
- https://docs.kernel.org/trace/mmiotrace.html
- https://docs.kernel.org/process/license-rules.html
- https://docs.kernel.org/process/submitting-patches.html
- https://docs.kernel.org/driver-api/firmware/request_firmware.html

Evidence: UPSTREAM-REVERSE-ENGINEERING-AUDIT-20261012.json.
