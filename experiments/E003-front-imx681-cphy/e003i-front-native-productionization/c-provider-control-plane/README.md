# E003i-C — provider-owned front PIX control plane

This static productionization checkpoint removes the disposable E003h control plane from the proven front PIX executor. The hardware runner itself is not rewritten.

Production contract:

- request4, request5 and request6 capsule bytes are all owned by the monotonic provider FIFO;
- fixed `request_firmware_direct()` seeding is removed;
- the `e003h_pix_runtime_arm` module parameter and E003h sysfs trigger/diagnostic attributes are removed;
- the old global irreversible one-shot latch is removed;
- normal front VB2 STREAMON is the only executor entry and fails with `-EAGAIN` before scheduling hardware unless the provider is open at request4 and has primed R4/R5/R6;
- safe completion/error closes and purges provider ownership; unsafe hardware teardown deliberately pins provider bytes with DMA ownership until reboot.

This checkpoint deliberately has **no producer ingress yet**. Therefore the production front path is fail-closed and cannot start from userspace until E003i-D supplies the real producer interface. No Linux camera runtime is authorized by this checkpoint.
