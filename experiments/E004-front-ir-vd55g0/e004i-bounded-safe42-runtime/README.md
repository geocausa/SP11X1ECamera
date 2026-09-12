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

## Runtime outcome

The single authorized E004i attempt passed, then returned immediately to Golden and retired the candidate.

Observed result:

- model 0x3047 / physical revision 0x1111 CUT1 revalidated before writes;
- 554-write Surface patch/setup/boot prefix again reached SW_STBY;
- **before any of the 42 final configuration writes, register 0x0468 already read 0x02**;
- all 42 non-strobe Windows final writes completed and read back correctly;
- 0x0468 remained 0x02 afterward without ever being written by E004i;
- resulting GPIO control bytes were exactly Windows state 01,02,01,01;
- transport/timing readback matched Windows: 19.2 MHz external clock, 840 Mbps MIPI data rate, line length 1200, frame length 1955, ROI 644x604;
- total sensor-data writes: exactly 596;
- CAMSS/V4L2/stream/external illumination remained absent;
- sensor was reset and powered off before module unload.

This proves the physical CUT1 sensor reaches the Windows GPIO1 selector value 0x02 as part of the patch/boot path itself. The explicit final Windows 0x0468=0x02 write is therefore state-redundant on the observed SP11 path; final 43-register state parity can be reached without issuing that illumination-coupled write.
