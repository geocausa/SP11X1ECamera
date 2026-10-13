# E005 probe03: CAMSS module27 TPG classification

Hypothesis: the retained one-source-pad TPG, classified as a synthetic sensor
like the kernel VIMC generator, registers without the three warnings while
keeping all TPG links disabled and the physical IMX681 -> PHY2 link intact.

The sole camera source change is entity.function. Existing Image/DT/initrd
and sensor/PHY modules are the qualified front26 package. Corrected CAMSS27
is in a private copied module root selected explicitly with modprobe -d;
the installed front26 module tree is unchanged. Runtime code and all assets
are pinned before arming. No stream, capture, firmware, RAW or DMA operation.

Same temporary headless scope, exact boot token, consumed marker, observer
return and independent180-second timer as02. Golden stays saved default.
No OS sleep tests. Userspace return cannot recover a pre-userspace hard lock.

Expected: TPG0/1/2 classified Sensor with one source pad and no enabled links;
physical IMX681 link enabled/immutable to PHY2; zero TPG warnings, existing
identity/runtime PM/power-off checks and clean camera module unloading.
This does not validate TPG streaming, RAW timing or upstream acceptance.
Both private startup consumers/all14 release categories remain open.
