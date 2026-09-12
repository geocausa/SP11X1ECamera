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

## Runtime outcome

The one authorized attempt passed and the candidate was immediately returned to Golden and retired.

Observed sensor identity/revision:

- model raw bytes: `30 47`;
- model big-endian: `0x3047`, exact Windows/QTI expected ID;
- model little-endian: `0x4730`;
- revision raw bytes: `11 11`;
- revision: **`0x1111` (CUT1)**.

The module verified MCLK=19.2 MHz and Linux rail setpoints 1.800/1.152/2.800 V, performed no sensor-data writes, then asserted reset and powered all sensor resources off before unload.

Combined with E004a, this proves an important Surface-specific fact: the actual CUT1 sensor on this SP11 is initialized by Windows with the captured 552-byte Surface patch (`5c07088c...26b321`), not the public ST generic CUT1 patch. Any future Linux parity path must therefore be reconstructed from the same-machine Windows transaction rather than substituting the ST CUT1 blob.
