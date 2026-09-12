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

## Runtime outcome

The single authorized E004f attempt passed, then returned immediately to Golden and retired the candidate.

Observed result:

- model 0x3047 / physical revision 0x1111 CUT1 revalidated before writes;
- 552 Surface patch writes completed;
- PATCH_SETUP was write 553 and reached 0x0200==0 on the second poll read;
- BOOT was write 554 and reached 0x0200==0 on the second poll read;
- FSM SW_STBY 0x02 was observed on the first poll read;
- total sensor-data writes: exactly 554;
- final 43 Windows configuration writes: zero;
- sensor GPIO1 strobe selector: not configured;
- CAMSS/V4L2/stream/external illumination: absent;
- reset was asserted and sensor resources powered off before module unload.

The experiment therefore proves that the exact Surface Windows patch is accepted by this actual CUT1 sensor and that the Windows patch-setup/boot prefix reaches software standby under Linux with the same command ordering and bounded polls.
