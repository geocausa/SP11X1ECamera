# E003i-GR — continuous scheduler/helper integration

Status: **PASS OFFLINE compile/integration / no camera runtime / not live-authorized.**

GR integrates GQ's two-slot continuous scheduler into the exact consumed GO 27-frame helper source without changing transport, statistics collection, AEC, IQ producer ordering, sensor-control ioctl contents, or the exact DQBUF timing gate.

The integration changes the release range from only target G2..G4 to every target G2..G27. In a hypothetical 27-frame continuous-write run that means sources G1..G26 would be released after completed G2..G27, with G27 remaining pending for the next boundary. Effects G28/G29 are outside GO's evidence window and are not claimed as proven.

Most importantly, the existing fail-closed boundary rule is preserved byte-for-byte in substance: a release is refused if the completed generation has already passed the intended boundary, and a sensor ioctl that overlaps the next completion returns a hard timing failure.
