## Consumed and retired; do not retry04

Allocation passed. Final teardown log contains an MCLK enable warning, also
found retrospectively in02/03; warning-free unload remains unqualified.
Evidence docs/UPSTREAM-MMAP04-20261014.json. Corrected retirement helper
spelling matches the actually used private worker; original boot sources
remain in commit e801147b and the pinned private runtime directory.

# Candidate28 MMAP allocation/release only — fresh04

Reuses retired probe03 recovery/module-isolation harness. Distinct04 identity;
03 and all earlier identities stay retired. Targets VFE1 RDI0 video output by
media identity. Three cycles of three MMAP buffers: request, query, map without
accessing bytes, unmap, release and close. Imported DMA-BUF request must be
rejected. Only QUERYCAP, G_FMT, REQBUFS and QUERYBUF ioctls are allowed in the
helper; no QBUF, STREAMON, STREAMOFF, sensor or media-link changes.

Checks sensor remains suspended, rail users/MCLK zero and reset low, then
camera module unloading succeeds. This checks actual allocation-reference
creation/cleanup; it does not prove physical DMA or hardware stream/fault
behavior. PHY release-error contract still blocks hardware streaming.

Private copied module root substitutes qualified module28 under kernel26 ABI.
Golden default/assets/global module installation remain intact. Headless boot
uses retained 180-second independent return timer and ExecStopPost; no OS sleep.
Assets/observer/helper/units must be committed, pinned and qualified before
one-use arming. No captured data or image contents are accessed or exported.
