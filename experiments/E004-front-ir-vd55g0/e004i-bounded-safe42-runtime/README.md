# E004i — one-shot VD55G0 safe-42 configuration runtime

E004i packages the verified E004h DTB and module into one disposable boot.

Acceptance contract:

- exact model 0x3047 / physical revision 0x1111 CUT1 before the first write;
- replay the already-proven 554-write Surface patch/setup/boot prefix;
- read GPIO1 selector register 0x0468 before final configuration;
- execute exactly 42 Windows final-configuration writes, excluding 0x0468;
- read 0x0468 afterward and require it to be unchanged;
- read back Windows transport/timing/exposure/ROI configuration and GPIO0..3;
- require GPIO0/2/3 = 1 and GPIO1 equal to its pre-write value;
- total successful sensor-data writes = 596;
- stay in software standby;
- no CAMSS, V4L2, stream, strobe-selector write, or external illumination;
- one attempt only, marked consumed before manual insmod;
- power off before module unload;
- reboot immediately to Golden and retire the candidate.

The package is committed and pushed before installation or arming.
