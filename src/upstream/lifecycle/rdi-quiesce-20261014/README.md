# Owned standard X1E RDI quiesce
Reuse audit: docs/UPSTREAM-RAW-PRIOR-SOLUTION-AUDIT-20261014.json.
Retained matched front CSID1/VFE1 RAW capture proves routing; native rear59
proves source-before-CSID shutdown ordering in its own bespoke pipeline.
Neither is hardware qualification of this standard backend.

This port drains only the finite programmed FIFO without refilling, pauses
the owned WM before retiring the last active buffer, stops PHY/sensor before
fresh acknowledged CSID reset, masks/readbacks IRQs and synchronizes handlers
outside the output lock. Any failure preserves PM, graph/module ownership
and independent DMA-SG mappings until reboot. Warm reopen restores CSID IRQs.
Starvation pauses the WM; restart programs the new DMA address before enable.
The standard mapping must have one DMA extent covering the entire plane,
with both endpoints inside the 32-bit WM address range. No first-SG shortcut.

Scope: exclusive X1E, one matched CSID/VFE RDI, MMAP; no PIX/DMABUF imports,
concurrent subdevice controls, shared RDI, bus/CDM PIX reset or full fault-matrix
hardware claim. The hardware qualification harness separately gates the exact
matched media graph. Mismatched route admission at the generic video prepare
hook remains a release prerequisite, not a supported caller configuration.

56 actual CAMSS/VB2 integration cases and 35 actual CSID/VFE/FIFO/DMA-admission
cases per GCC/Clang ASAN/UBSAN pass; ten compiled unsafe mutations are refused.
Deterministic IRQ/MMIO/wait adapters do not prove electrical or concurrency
behavior. Strict ARM64 module and patch replay/style checks pass.
Sensor31/current standard source offers 3840x2640; the old native 3840x2160
sample and its FPS do not describe this profile. Qualification uses negotiated
3840x2640 pRAA, 4800-byte stride, 12672000-byte plane, without any FPS assumption.

prepare.py refuses occupied destinations and detaches changed hardlinks.
build-worker.py uses fresh O=/MO= outputs and never installs system modules.
Pixels, image hashes and spatial statistics remain on SP11. Hardware status
is recorded separately; source qualification alone does not permit release.
