# E008d — rear ten-WM Linux DMA/address provider

Parent Git: `0fb4cb3f` (E008c complete stop/release contract PASS).

Status: **BUILD-ONLY / NO ENABLE / NO RUNTIME CALL SITE**.

## Why this checkpoint exists

E007y constructs the complete rear startup command stream and E007z can retire
ten exact programmed image IOVAs, but neither owns the actual Linux DMA
allocations or installs those dynamic VFE addresses. E008d closes only that
gap and intentionally stops before WM enable or RT-CDM submission.

## Historical E004nu correction

Audit found that E004nu's old `vfe680_e004nu_rear_wm_prepare_disabled()`
contradicts its README: after writing `c->cfg & ~EN`, its source contains a
second `writel_relaxed(c->cfg, ...CFG)` that can set EN again.

E004nu was isolated/unreachable and never installed or loaded, so hardware was
not affected. Its ten-client data table remains independently verified against
the two rear Windows captures, but the old helper is **superseded and must not
be called**. E008d's verifier detects the historical defect and rejects the
same pattern in new source.

## Linux-owned allocations

For one candidate frame, WM0/1 use the proven E004nt coherent rear FULL
surface (0xFF6000 bytes). WM2/3/11/12/13/14/16/18 each receive a distinct
coherent Linux allocation sized directly from that WM's two-pass
rear-Windows-proven `FRAME_INCR`. Every complete DMA span must fit the VFE's
32-bit aperture. All allocations are zeroed; no Windows IOVA is copied or
inferred.

The eight auxiliary allocations total 0x373D00 bytes; together with FULL the
one-frame private hardware allocation budget is 0x1369D00 bytes.

## Disabled-only MMIO contract

`e008d_rear_prepare_addresses_disabled()` verifies all ten WMs disabled before
its first write, writes every source-locked rear static field with EN masked
off, writes ten Linux-owned IMAGE_ADDR values plus WM0/1 META_ADDR, executes
`wmb()`, then reads all addresses and all ten enable bits back. It succeeds
only with every WM still disabled.

There is deliberately **no enable helper**. The remaining startup-order
question therefore cannot be answered accidentally by this checkpoint.

## Remaining boundary

After E008d, Linux ownership/address programming and teardown safety are closed
without live camera access. The remaining decision is the exact startup
sequence from disabled/addressed WMs through E007y packet submission, WM
enable, CSID1/CSIPHY1/sensor start and first-frame completion. Use a new
bounded Windows dynamic oracle only if existing evidence cannot resolve that
sequence without assumption.

## Build result — PASS

Fresh isolated fix1 CAMSS build: 13,779,520 bytes, SHA-256
`59c66fa3ebc0e250c28e23488d3086f99627561eb398e42c9c16ccd2baebcb94`, exact
Golden vermagic, W=1 with zero warnings/errors. PiMaster verifier PASS and an
independent Fabric verifier/hash/vermagic check PASS. The first build identity
was consumed by a staging-script Python syntax error before compilation; no
module was produced from it. No module was installed or loaded and no camera,
WM enable or RT-CDM submission occurred.
