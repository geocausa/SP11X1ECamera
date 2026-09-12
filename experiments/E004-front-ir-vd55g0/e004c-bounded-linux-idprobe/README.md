# E004c — bounded Linux VD55G0 identity/revision runtime

E004c is a disposable one-shot wrapper around the verified E004b DTB and write-free ID probe.

Contract:

- protected Golden kernel/initrd/default are never replaced;
- the E004b DTB is copied only to a separate candidate boot directory;
- qcom_camss, RGB sensor drivers and the custom ID probe are blacklisted from autoload;
- CCI may load only to expose the inert I2C client at 0x60;
- the verified custom probe module is loaded manually with `insmod` exactly once;
- the attempt is marked consumed before `insmod`;
- success requires model BE=0x3047, a captured revision, exact clock/rail checks, the write-free marker and confirmed power-off;
- no retry is authorized in the same boot;
- no patch, sensor boot/configuration, stream, V4L2 or illumination is permitted;
- after the attempt, reboot immediately to Golden and retire the candidate.

The package must be committed and pushed before installation/arming.
