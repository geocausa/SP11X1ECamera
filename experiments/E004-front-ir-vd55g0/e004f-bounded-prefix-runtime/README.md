# E004f — one-shot VD55G0 Surface patch/boot prefix runtime

E004f packages the verified E004e DTB and prefix module into one disposable boot.

Acceptance contract:

- exact model 0x3047 and physical CUT1 revision 0x1111 must pass before the first write;
- exactly 552 Surface patch writes plus PATCH_SETUP and BOOT = 554 sensor-data writes;
- all four Windows-derived polls must pass with 6 / 28 / 6 / 4 ms loop bounds;
- final state must reach software standby;
- Windows's final 43 configuration writes are not executed;
- therefore the sensor GPIO1 strobe selector is not configured;
- CAMSS, V4L2, streaming and external illumination remain absent;
- one attempt only, marked consumed before manual `insmod`;
- sensor must power off before module unload;
- immediately reboot to Golden and retire the candidate.

The runtime package itself is committed and pushed before installation or arming.
