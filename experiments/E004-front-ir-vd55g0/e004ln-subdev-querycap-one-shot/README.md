# E004ln — actual SP11 V4L2 subdevice QUERYCAP, read-only one-shot

Date 2026-09-22. Unique unused E004ln identity, not E004lk/E004ll. Starting canonical project parent 3e769f0d974fad31d035a67e12f5961c756c6163. Protected Golden v19c Linux must remain the GRUB saved default with empty next_entry, no camera modules, node users, or duplicate experiment/service/boot assets.

Hypothesis: the 28 V4L2 subdevices belonging to the exact accepted SP11 qcom-camss Media Controller v2 topology do not advertise V4L2_SUBDEV_CAP_STREAMS. This directly checks the E004lm source-only audit and libcamera Simple's need to reset ACTIVE subdevice routing during enumeration. It does not validate format negotiation, per-sensor control metadata, real frame capture, or Windows parity.

Build: independently rebuild SHA-pinned accepted canonical camera hardware package at /tmp/sp11-e004ln-hardware and compile maintained src/sp11-camera-stack/libcamera/sp11-subdev-caps-probe.cpp with -O2 -std=c++17 -Wall -Wextra -Werror -pedantic. The diagnostic requires root, the distinct exact experimental boot token and /dev/media0; reads verified full kernel v2 graph using only MEDIA_IOC_DEVICE_INFO and MEDIA_IOC_G_TOPOLOGY and refuses any nonneutral initial route. Resolves each subdevice node by matching actual major/minor numbers to 28 verified media-interface links. Each node is opened O_RDONLY|O_NOFOLLOW|O_NONBLOCK and queried with VIDIOC_SUBDEV_QUERYCAP only. It refuses duplicates, missing/foreign devices, ioctl errors, unknown flags, or any subdevice advertising CAP_STREAMS. No STREAMON, media link writes, formats, pixel recording, application CameraManager, IR lighting or PMIC control.

An exact SHA-locked, root-private, newly named candidate module/diagnostic staging directory is installed only in a separate one-shot nondefault GRUB candidate with automatic Golden return. The 120-second systemd service writes an irreversible consumed marker before module binding and invokes the query program under a 15-second timeout. Both native and runner use fail-closed errors, no retry; the unit requests reboot to protected saved Golden on normal or failed completion. The conditional service remains inactive on Golden. On boot failure independent recovery may be needed; the script does not promote an experimental default. Verify boot ID, GRUB saved/next state, absence of active camera nodes and actual result before retiring and archiving numeric evidence.

The E004lm guarded libcamera adapter is NOT installed or launched. This is read-only metadata evidence, not a claim of production-safe exclusive ownership; dark nighttime images are irrelevant because no images are captured. Never rearm E004ln once attempted.

## Final physical result — PASS, consumed and retired

The unique candidate boot b504661b-d157-4a51-8e18-be921a5cebe7 loaded
the accepted modules and queried the 28 actual subdevice nodes, matched by
major/minor to their verified Media Controller v2 interfaces. All 28
returned VIDIOC_SUBDEV_QUERYCAP without CAP_STREAMS; none advertised
CAP_RO_SUBDEV. Actual sensors IMX681, OV13858 and standby VD55G0 were
included. The initial graph was complete and neutral; no media links,
formats, video streams, IR emitter or image data were changed/recorded.
Systemd completed successfully and returned automatically to protected
Golden boot 1545dc5d-6483-443b-a715-6c96aaf7d023. The unique root-private
candidate, service and GRUB entry were retired after independently confirming
the saved default, no pending boot and camera-free Golden. Numerical results
and standby IR kernel evidence are preserved in RESULT/CONSUMED/evidence.
Never rearm E004ln. This is a read-only metadata proof for this tested
kernel/device set, NOT actual libcamera registration or general OS-enforced
ownership of an ordinary multi-client camera stack.
