# E003h second PIX diagnostic — abrupt reset before persistent stage result

The second diagnostic authorization was consumed exactly once. The candidate boot and pre-RUN checks passed with the pinned 0036+0037 CAMSS module, front-only PIX route, QC10C 2560x1440 format, two-buffer one-shot helper, and sensor/CAMSS suspended before trigger.

A preliminary non-root helper invocation could not open the owner-write-only trigger and therefore did not issue `RUN`; sensor/CAMSS remained suspended. The subsequent root invocation is treated as the one authorized `RUN` and is **not retried**.

The machine reset abruptly during/after that invocation. The next boot is Golden. Persistent evidence shows:

- previous candidate journal has no normal systemd shutdown/reboot sequence;
- the following Golden boot performs EXT4 orphan cleanup, establishing an unclean reset rather than an orderly reboot;
- the previous boot journal ends immediately after candidate CAMSS/IMX681 load/bind and contains no persisted 0036 stage-error line;
- `RUNTIME-PIX-DIAG2-RUN.txt` is empty and no QC10C output file exists;
- no pstore record is present;
- Golden returned byte-exact with empty GRUB `next_entry` and no candidate camera modules loaded.

Because the reset occurred before stage telemetry could be persisted, this run does **not** establish the last RT-CDM stage reached. The 0037 correction remains statically valid, but its relationship to this reset is unknown. The next runtime gate must first add a non-MMIO persistent observer path for the already-recorded RT-CDM stage state; no third PIX attempt is authorized by this result.
