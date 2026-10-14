# CDM2.1 owned single-program submission

Candidate34 is a dormant kernel integration step after hardware-qualified RAW33.
It reuses native FIFO commit and exact-command receipt design, corroborated by
the pinned public Qualcomm GPL writer. The prior-work audit is
docs/UPSTREAM-PROCESSED-PRIOR-REUSE-AUDIT-20261014.json.

The parent supplies a coherent immutable allocation and independent retention
callback. Under power then CDM locks, the backend admits one bounded REG_CONT
program, requires fresh successful reset/exact2.1 revision/exclusive FIFO state,
retains allocation/mapping/module/device dependencies, submits BASE/LEN/STORE
and polls finitely with IRQ banks masked. Unknown/stale/other-bank status,
timeout, late error, pending FIFO or failed cleanup quarantines the instance.
Receipt publication requires BL_DONE, final masking/IRQ drain, pause readback,
zero FIFO observations and cleared status.

No return path releases the command hold. Even success requires separately
proven parent retirement before free/rewrite/power removal/unbind/unload.
Software sequence/request binding is not a hardware tag. Pause readback and
BL_DONE are not AXI drain or DMA-release authority. DMI/jumps/indirect commands
remain excluded. Register authority belongs to typed compilers and the future
parent constructor; there is no userspace register programming interface.
The retained independent minimum compiler feeds a1204-byte program, but its
CFA/precision/bypass/optical domains and complete PIX/CSID/BUS startup remain
hardware unqualified.

prepare.py and build-worker.py reuse sparse immutable-parent zero-fuzz replay
and exact kernel26 configuration/symvers strict ARM64 W=1/Werror MO builds.
test-submit.py executes actual provider/power-wrapper bodies with hosted
MMIO/ownership/time adapters and rejects six compiled unsafe mutations.
test-reset-regression.py reuses the retained reset fixture and its later
binding-suite stale-IRQ correction. test-public-fifo.py executes the actual
pinned public writer as oracle. Models do not prove physical IRQ concurrency,
coherent DMA/address translation or AXI retirement.

The mapped span now includes FIFO3_CFG (0x360 bytes minimum). No runtime parent
caller, installed/loaded payload, hardware attempt, firmware reader or
proprietary initialization dependency exists. Next reuse/implement parent
coherent-DMA/resource constructor and detach/retirement gates, complete the
independent PIX startup and qualify a bounded physical CDM transaction before
standard params/stats/IPA admission.

Public definitions come from Qualcomm GPL-2.0-only camera-driver revision
3f5ef25e12b501a518d2d4f4a870288e9bb127a0, with original notices preserved in
the pinned reference. The adaptation derives from retained GPL native work;
no vendor profile bytes were copied. Whole-series provenance/attribution,
author signoff, bindings, generic API design and upstream review remain open.
