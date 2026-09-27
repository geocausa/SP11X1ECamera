# E007z — rear ten-WM consumed-IOVA retirement contract

Status: **BUILD-ONLY PASS**.

## Purpose

E007y closed complete offline startup command construction. E007z closes the next
lifetime layer without starting hardware: every one of the ten Windows-measured
rear VFE680 write masters must be bound to a Linux-owned span and a precise
programmed image IOVA, and a completion bit alone may never retire a buffer.

The physical VFE680 completion-group map for the measured rear WMs is:

- group 0: WM0, WM1, WM2, WM3
- group 4: WM11, WM12
- group 5: WM13
- group 6: WM14
- group 7: WM16 / STATS_BAF
- group 9: WM18

For shared groups, each WM is retired independently only after its own
ADDR_STATUS0 / last-consumed value equals its exact Linux-owned programmed image
IOVA.

## Address identity

The pinned Qualcomm packet parser stores fence-map image_buf_addr after adding
the per-plane image_buf_offset. The ISP context compares last_consumed_addr to
that shifted address before signaling success.

Therefore WM0/WM1 FULL UBWC bindings own their entire metadata+data subspans but
must match the image addresses, not the metadata bases:

- WM0 image offset: 0x11000
- WM1 image offset within its C-plane subspan: 0x9000

The other eight measured rear WMs have meta_cfg=0 in the accepted E004nu
contract, so their image offset is zero here.

## Safety model

E007z does not allocate, map, program, ACK, free, signal, requeue or submit
anything. The caller supplies all ten non-overlapping Linux-owned spans. Binding
fails closed on missing/duplicate WM IDs, undersized or overflowing spans,
misaligned addresses, overlap, or an incorrect image offset.

Observation consumes only an already-latched/ACKed CSID BUF_DONE status plus a
caller-provided last-consumed IOVA. Owner epoch and request generation must match.
A wrong consumed address faults the frame and prevents retirement.

Even after all ten matches, the ledger is retireable only if the caller separately
proves BUS stopped and IRQs drained. Runtime authorization remains denied.

Next after a build/test pass: integrate the E005y rear owner/CSID observer with
this ledger in a new source-only checkpoint, then prove the actual stop/drain
sequence before considering a one-shot native rear runtime.

## Build result — PASS

The complete accepted E006/E007 dependency chain through E007y plus E007z was
injected into a fresh isolated CAMSS copy and compiled W=1 against the protected
Golden headers.

- qcom-camss.ko: 13,921,008 bytes
- SHA-256: 1e1791d2b13465378c8500527132cdd909a2cf162cb4852fb1684e2a66d238b3
- vermagic: 7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64
- W=1 warnings/errors: 0
- retained symbols: e007z_rear_bind, e007z_rear_observe, e007z_rear_retirement_recipe
- install/load/camera/DMI/RT-CDM submission/retirement: none
