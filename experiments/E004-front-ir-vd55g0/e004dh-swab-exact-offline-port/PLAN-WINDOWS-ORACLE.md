# E004dh bounded Windows oracle plan

Question: what exact SWABF (`0x22`) and SWASF (`0x804`) tuning payloads does the shipping Windows stack deliver to the SecureISP trustlet for the SP11 FaceAuth IR path?

Method:

1. boot Windows once using the existing `Boot0006` direct oracle entry;
2. attach the already-established SP7 KDNET debugger read-only;
3. break only at `qccamsecureisp8380!FUN_140004a90` / SecureISP task-send;
4. when `x0 == 9`, dump `x2 .. x2+0x22`;
5. when `x0 == 10`, dump `x2 .. x2+0x804`;
6. run the accepted E004AQ FaceAuth + SecureMode IR controller script for one bounded stream;
7. stop cleanly and reboot directly back to Golden Linux;
8. preserve exact dumps and compare repeat occurrences for stability before porting.

No writes, no breakpoint-side mutation, no trustlet patching, no firmware patching.
