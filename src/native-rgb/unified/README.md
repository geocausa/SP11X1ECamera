# Unified SP11 camera stack (front + rear in one boot)

One camss module and one libcamera build drive both RGB cameras; two on-demand
bridges expose them to every application as ordinary webcams.

| Piece | What it is |
| --- | --- |
| `merge-unified.py` | 3-way merge of the front line (build 46: native queue, robust queue, AE/AWB metadata, LSC/ABF) and the rear line (daily 65: rear generation queue, 30 fps statistics) against their common ancestor (build.py at 84425426). Clean, no conflicts. |
| `build-kernel48.py` | Unified module 48 = merge + the shared-node fixes: the VFE1 statistics node offers both layouts (front QXS1, rear QXR1) and S_FMT selects one; VFE1 PIX output geometry follows the request (exact 4K NV12 = rear, otherwise front 2560x1440); the front parameter-queue gate no longer blocks the rear. W=1 -Werror. |
| `build-lib21.py`, `build-lib21.sh` | libcamera 21 = front tree 20 + rear pipeline/IPA. Each handler selects its statistics layout; the rear registers without requiring 4K as the node default; the rear AEC decoder counts saturated (uncounted) samples at saturation instead of rejecting bright frames (daylight stopped the rear stream before). Builds the bridge too. |
| `sp11-webcam.cpp` | Bridge: one libcamera camera -> one v4l2loopback device, 1920x1080 YUYV 30 fps, bilinear scaling from 2560x1440 (front) or 3840x2160 (rear). Runs the camera only while a reader has the device open; restarts a failed or stalled stream. |
| `setup-daily2.py`, `install-daily2.sh` | Boot entry `SP11 Golden + Cameras` (id `sp11-camera-daily2`): the Golden kernel, initrd and command line plus the camera device tree (a pure superset of the Golden tree). Golden stays the GRUB default. Private firmware is read through `firmware_class.path`; nothing goes into /lib/firmware. |
| `test-webcams.py` | Reads the webcam devices like an application and reports frame rate and picture scalars. |
| `fit-look.py`, `verify-look.py`, `capture-natives.sh`, `looks/` | Rendering ("look") per camera, fitted against a same-scene Windows capture: tone table, chroma gain and neutral offset, cored unsharp mask, motion-adaptive temporal filter. The bridge applies it. |
| `make-daily-dtb.py`, `vaf/` | Rear lens supply: a camera-only RPMh provider node for PM8550 LDO16 (2.9 V) plus a `regulator-output` consumer, added to the camera device tree. The provider module is loaded by the camera boot and votes only while the rear camera streams. (Defining LDO16 in the Golden PM8550 provider hung the boot.) |

Applications see `SP11 Front Camera` (/dev/video50) and `SP11 Rear Camera`
(/dev/video51), also through PipeWire. Both cameras share CSID1/VFE1, so one
streams at a time; the other bridge retries until the hardware is free.

Verified 2026-10-11 (daylight): alternating rear/front/rear/front sessions,
300 frames each, 29.9 fps at the application, no kernel warnings.

Rear autofocus (2026-10-11): the bridge drives the DW9800 actuator (0x0c on the
rear CCI bus) with contrast autofocus on the native 4K frames: coarse sweep
380..900 in steps of 48, fine sweep +-48 in steps of 12, three frames per
position, then hold; a lasting sharpness or brightness change re-runs it. The
SP7 screen at about 40 cm focuses at code ~560 in about 3 s. Without power the
lens rests near infinity.

Against a same-scene Windows capture (daylight, bridge output vs Windows scaled
the same way): front tone within 1-4 codes, chroma 43-45 vs 42, temporal noise
2.0-2.5 vs 2.0, edge strength 90-95 %; rear tone within 5-10 codes, chroma 47
vs 45, noise 2.8 vs 3.1, edge strength 89 % (59 % before autofocus).

