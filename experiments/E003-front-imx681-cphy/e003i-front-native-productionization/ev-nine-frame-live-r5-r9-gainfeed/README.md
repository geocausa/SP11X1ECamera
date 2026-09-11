# E003i-EV — fresh nine-frame R5-R9 live successor with six-generation gain publisher

Status: **STAGED OFFLINE / NO EV CAMERA RUNTIME YET.**

EV is the fresh successor to consumed ET. ET proved startup, STREAMON, G1..G3 AEC, R5/R6 live submission and six completed frames, then exposed a stale C gain-feed publisher validation bound: the helper requested G1..G6 publication but the copied publisher rejected G4+.

EV keeps ET/ES nine-frame transport, the closed EN/EP producer/content path, CW IMX681 control, R4 bootstrap, and the three-write sensor schedule. The only functional correction is that helper builds source gain-feed.c and gain-feed.h from EU, whose compiled C proof accepts G1..G6, rejects G7, and preserves request = generation + 3 and the 24-byte ABI.

EV additionally prints the actual DQBUF index/bytesused/sequence before pinning on any ordering mismatch so a transport failure cannot hide its observed tuple.

One candidate boot may perform at most one camera stream attempt. Any failure pins/archives and requires a whole-machine reboot to Golden with no same-boot retry. A PASS remains bounded nine-frame integration, not unrestricted continuous AEC.
