# E003h post-provenance candidate boot — pre-exec harness abort

Date: 2026-08-30

The authorized post-provenance candidate **boot** was consumed, but the hardware `RUN` was not executed.

Candidate preflight passed with the corrected five-entry CAMSS IOMMU domain including the Windows-proven RT-CDM1 requester SID `0x18a0`, exact front PIX route, pinned module/DT/capsule/helper hashes, and the persistent RT-CDM observer running from `idle`.

The attempted orchestration shell created the run evidence file through a privileged redirection and then a non-root shell later attempted to redirect into that root-owned file before invoking `sudo`. Shell redirection failed first with `Permission denied`, so the helper executable was never entered and the sysfs trigger was never written.

Mechanical evidence that no hardware trigger occurred:

- persistent RT-CDM observer remained `seq=0 stage=idle`, `irq_armed=0`, `faulted=0`;
- no IMX681 `MODE_SELECT=1` / transmission-start message;
- no QC10C output file;
- IMX681 and CAMSS remained runtime-suspended;
- Golden reboot/return completed with `saved_entry=sp11-audio-fullio-v19c` and empty `next_entry`.

This is a **pre-execution harness failure**, not a failed PIX hardware attempt. It does not consume a hardware `RUN`, but the one-candidate-boot authorization is treated as consumed. No same-boot retry occurred.

A corrected wrapper `run-postprovenance-pix-once.sh` creates its own run log as the invoking user before the sole privileged helper invocation, refuses reuse of an existing actual-run log, requires a ready persistent watcher and idle RT-CDM state, archives evidence, and reboots immediately to Golden after the helper returns.

A replacement candidate boot requires a fresh explicit one-shot authorization checkpoint before re-arming.
