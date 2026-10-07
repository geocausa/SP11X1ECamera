# Native front queue qualification

This optional diagnostic composes after the cold linear-NV12 and consumed-owner
overlays. All three module flags default false; ordinary and rear streaming are
unchanged. The front startup path enters a two-slot loop after its third fully
retired frame. Every refill consumes the next queued buffer and request, waits
for Epoch0, retargets BUS, and verifies five CDM BL_DONE receipts. Commands and
DMI memory are recycled only after the prior slot has fully retired. Every
completion checks the IRQ-latched consumed addresses, sequence and stream epoch.
STREAMOFF wakes the worker; hardware producers stop before buffers or commands
are returned or freed. Failed stop keeps ownership pinned until reboot.

Fresh identity native-queue-20261007-01 targets 80 sequential NV12 frames using
four reusable vb2 buffers. The first returned pair is requeued in reverse order,
and the probe checks that changed order in delivered frames. It submits fixed
manual IQ requests ahead of use, with all 16 DMI bank selectors generated from
the existing qualified scalar source. R4 must remain byte-identical to its local
private authority. This measures queue cadence and cancellation, not live 3A,
image quality or a final parameters API. Raw capsules remain a private diagnostic
interface; the product still needs typed parameters/statistics and libcamera IPA.
All fixtures stay private on SP11. No optical pixels leave SP11.

Preparation checks exact source/module hashes, Golden refusal, clean repository,
protected Golden assets and a fresh one-use identity. install.py prepares only.
After a hardware attempt the identity must be consumed, returned to Golden and
retired; never rearm it.
