# E008c — rear complete stop and release contract

Parent Git: `bdf12243` (E008b owner/completion/quiescence integration PASS).

Status: **BUILD-ONLY PASS / NO RUNTIME CALL SITE**.

## Goal

Define the complete successful rear teardown ordering at which the E007z evidence
ledger and E005y shared VFE1 owner may finally be released.

This is still unreachable source. It does not authorize a native rear run.

## Source-locked ordering

Two independent existing sources constrain the prefix:

- same-SP11 OEM ISP E004oe statically proves the stop-like manager branch orders
  its per-core calls **CSID -> IFE -> CDM**. E004oe does **not** prove that a
  particular live rear 4K session selected the branch or that the calls had
  physically drained DMA;
- the accepted native front PIX runner independently uses
  **CSID1 -> BUS/IFE -> RT-CDM**, then CSIPHY -> sensor, and releases software /
  pipeline power only when teardown stayed safe.

E008c does not turn either observation into a Windows-runtime claim. It uses
them only as conservative stop ordering after E007z/E008a already provide the
missing per-buffer and IRQ/BUS retirement evidence.

## Complete successful path

`e008c_rear_complete_stop_release()` requires a fully active successful rear
session contract and then:

1. runs E008b, proving all ten exact consumed IOVAs plus CSID1 quiescence and
   VFE1 BUS/IRQ stop under one unchanged REAR owner epoch;
2. invokes the accepted RT-CDM1 stop/close and verifies IRQ0 mask == 0 and
   Linux `irq_armed == false`;
3. stops CSIPHY and sensor through the accepted V4L2 subdevice stream helper,
   attempting both even if the first fails;
4. on any failure before release, faults/pins the shared owner and leaves the
   E007z ledger intact;
5. only after all producers are stopped, releases the E007z evidence ledger,
   drops media-pipeline PM, and releases the E005y REAR owner as teardown-safe.

The ledger release clears only E007z bookkeeping; E008c itself performs no DMA
free/unmap or VB2 requeue. Actual runtime buffer ownership remains a later
runner-integration responsibility.

## Fail-closed behavior

A CSID/VFE failure is already pinned by E008b. RT-CDM verification or outer
stream-off failure calls the same pin/fault path. A ledger-release failure pins
the owner. Pipeline power and safe owner release occur only after all preceding
checks succeed.

## Remaining boundary

After this compile gate, the teardown *contract* is mechanically closed but
there is still no rear runtime caller, real rear native processed frame, or
live proof that the new startup/request producer executes correctly on
hardware. The next decision is whether the source/build evidence is sufficient
for a fresh, bounded, one-shot rear candidate or whether a Windows dynamic
oracle is still needed for a specific unresolved runtime field.

## Build result — PASS

The complete E005y + E007z + E008a + E008b + E008c composition built in a fresh
isolated CAMSS tree against the protected Golden-v4 headers.

- PiMaster verifier chain: PASS;
- independent Fabric verifier/hash/vermagic check: PASS;
- W=1 warnings/errors: 0;
- qcom-camss.ko: 13,708,376 bytes;
- SHA-256: `453714c533c65c79a35f33e0cba01de428d2f498247fd9202a3345deba5fe675`;
- vermagic: exact Golden `7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64`;
- no install/load/camera/DMA free/VB2 requeue/runtime call site.

This closes the teardown/release contract at build time only.
