# E004lm — libcamera Simple native RGB guarded-route integration (offline)

Date: 2026-09-22. Parent project 67b3689f8aad9edde84332f8fbd53b3bf3db41ca, after E004ll native physical route PASS. Clean pinned libcamera v0.7.0 commit b7854fd07d42168f099b5ce30d1702e0e0875bf5 was extracted from the local reference repository using git archive; the dirty reference checkout was never edited. Apply E004lh 0001-sp11-rgb-path-filter.patch, E004lm 0002-sp11-guarded-simple-native-session.patch and the independent src/front-imx681/libcamera/0001-imx681-gain-helper.patch (SHA-256 19e5f2537fa73213dac6cbb6cc528efc9435d6b5eba520201e1975bc4362468a), then copy six maintained sp11-*.h headers from src/sp11-camera-stack/libcamera into the pinned Simple handler directory. There is no production installation or live libcamera run.

Integration candidate: guarded root-only and exact one-shot kernel-command-line admission is checked before Simple CAMSS sensor discovery; ordinary Golden Linux refuses before opening a sensor or changing any link. Only the two exact RGB sensor/path matches from E004lh enter the candidate. Both existing SimpleCameraData::init and configure setupLinks use the E004lj native fresh MEDIA_IOC_G_TOPOLOGY + MEDIA_IOC_SETUP_LINK transaction instead of cached MediaLink::setEnabled. During camera discovery, each successfully initialized RGB route returns neutral before camera registration. On successful configuration the route is parked neutral while the app is idle and re-enabled only through guarded beforeStream, and afterStream disables it again. All failure paths that cannot establish a safe transition poison the native controller and require the outer one-shot runner to retire the candidate. Simple's unguarded ActiveFormat subdevice resetRoutingTable is blocked for CAMSS nodes that report supportsStreams; no claim of correct alternate active routing is made.

New maintained headers: sp11-libcamera-route-gate.h and sp11-libcamera-experimental-lease.h; E004lm C++ lifecycle, denial and source mutation-boundary tests live in src/sp11-camera-stack/libcamera/tests/. The lease is a strictly experimental cooperative lockf media-device owner with exact dynamic three-sensor suspended-state checks, not OS-enforced exclusivity over uncooperative external clients; the *future* one-shot launcher must separately refuse other open video/subdev users and abort/reboot on any failed neutral shutdown. The guard is only armed for root on a future distinct boot carrying sp11_camera_e004lm_libcamera=1 and the matching sp11_entry marker. This source-only marker is NOT a boot prepared or armed in this experiment. E004lm does not reuse E004lk/E004ll consumed identities.

Validated on protected camera-free SP11 Golden ARM64: initial pinned libcamera 0.7.0 native build 357/357 targets, followed by a successful 15/15 incremental rebuild after applying the independently verified IMX681 gain helper, and the final 77-test suite with 45 OK (including libcamera:imx681-helper), 1 expected failure, 31 skips and 0 unexpected failures. Native C++ -Wall -Wextra -Werror -pedantic ASan+UBSan gate test passes front/rear/idle-neutral parking, rejects IR, invalid sensors, wrong-camera start, simultaneous route switching, absent owner/quiescence and failed link writes. Golden experimental-lease denial executable PASS; 11 existing Python route tests PASS; static patched Simple mutation-boundary smoke test PASS. The second patch passes git apply --check against clean E004lh baseline. These are OFFLINE and camera-free proofs, not ordinary app capture, kernel module changes or parity validation.

**Remaining gates before ANY E004lm physical/libcamera activation:** establish genuinely exclusive, current cross-process camera ownership and verified all-camera-streams-stopped proof; use E004ln's separate live-kernel read-only evidence that all 28 SP11 subdevices advertise CAP_STREAMS=0 (the candidate still deliberately rejects active reset); design a fresh, uniquely staged fail-closed service/boot with durable error exit, native neutral cleanup and Golden automatic return; inspect libcamera's real sensor metadata/configurations and chosen front/rear format; then separately prove application frames through the expected front 1080p/rear 4K output bridge. No claim of libcamera registration, STREAMON, production service, Windows ISP image-quality parity or protected IR. Dark nighttime scenes are not evidence of a defective image pipeline.

## Source-only subdevice capability audit

See HASSTREAMS-SOURCE-AUDIT.txt: the pinned V4L2 core derives SUBDEV_CAP_STREAMS
from the driver's SUBDEV_FL_STREAMS flag; exact camss/front/rear/standby-IR
camera sources have no literal uses of that flag. This is consistent with the
blocked libcamera active routing reset not being needed on the source tested,
but is NOT actual live VIDIOC_SUBDEV_QUERYCAP evidence. A future fresh
one-shot must query real dynamically enumerated subdevices and fail closed on
unexpected stream capabilities before enabling any camera manager.

## Subsequent independent hardware prerequisite — E004ln

E004ln (separate fresh one-shot, later consumed and retired) matched all
28 real SP11 /dev/v4l-subdev* device numbers to the verified qcom-camss
Media Controller interface topology and queried VIDIOC_SUBDEV_QUERYCAP.
All returned CAP_STREAMS=0, including both RGB sensors and standby IR.
This closes the *specific tested-kernel* hasStreams/ACTIVE reset question;
E004lm itself remains a source-only libcamera build with no CameraManager
enumeration/registration, no frames and no production ownership proof.

## Subsequent guarded libcamera registration evidence — E004lo

An independent, consumed one-shot first registered real OV13858 through
the guarded Simple adapter but rejected IMX681 at CameraSensor
construction due to absent mandatory V4L2_CID_HBLANK/PIXEL_RATE on
the canonical IMX681 module. It returned to Golden and did not stream.
This does not alter E004lm's OFFLINE native build PASS, nor prove a
dual-RGB libcamera stack. The E004ld/E004le fixed metadata/clock
module pair has separately recorded real sustained RGB success;
revalidate that exact pinned pair, and independently seal compiled
IPA/config paths, in a NEW unique candidate before another live test.
