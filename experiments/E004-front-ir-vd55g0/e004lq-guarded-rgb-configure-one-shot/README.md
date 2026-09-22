# E004lq — guarded sequential real RGB libcamera configure-only experiment

Date: 2026-09-22. Fresh one-shot identity distinct from consumed E004lp/E004lo and all prior physical trials. Parent project commit 6d230d99d5fb5ca4130430be9c6bbcefed15e5ea. The goal is to establish whether the two real cameras registered under E004lp can each be acquired and configured for a RAW libcamera stream, in separate sequential sessions, without starting any video stream. This is NOT an application video or image-quality test.

The new source client src/sp11-camera-stack/libcamera/sp11-configure-only-probe.cpp accepts only root on this experiment's exact nondefault boot command line. It starts a CameraManager and matches real front IMX681 / rear OV13858 via exact camera Model property, explicitly excluding the four Virtual cameras. It acquires, generates and validates a single Raw-role configuration, calls Camera::configure(), independently reads the real /dev/media0 full v2 graph using READ-ONLY DEVICE_INFO/G_TOPOLOGY ioctls and requires a completely neutral graph after EACH configure, then releases the camera. Finally it requires neutral again after both releases and exits. It contains no Camera::start(), VIDIOC_STREAMON, frame allocation/queueing, image/pixel recording or IR illumination code. Any non-neutral graph, failed configuration or camera mismatch is a candidate failure and never retried with this identity.

The root-sealed libcamera 0.7.0 build starts from pinned b7854fd07d42168f099b5ce30d1702e0e0875bf5 with independent E004lh RGB route filter, E004lm native guarded Simple integration, E004lo uncertain STREAMOFF fail-closed change, and verified IMX681 gain-helper patch. The E004lq-specific lease is root-only, requires exact E004lq cmdline token and limits media node opening to /dev/media0; it validates root:root 0600 on 1 media / 16 video / 28 subdevice nodes before each native graph transaction. Real E004ln kernel QUERYCAP read-only evidence found CAP_STREAMS=0 on all 28 subdevices. E004lk/E004ll established real full-graph reads and link transactions; E004lp registered both physical cameras using the byte-identical E004le physically accepted HBLANK/PIXEL_RATE pair.

Build results (source-only until its one-shot result is archived): native pinned libcamera 368/368 targets, 77-test suite 45 OK / 1 expected failure / 31 skipped / 0 unexpected failures and gain-helper PASS. Byte-identical E004le IMX681 and CAMSS timing pair reproducibly built at the accepted historic Kbuild path: imx681.ko SHA 448bd926193c003cdf3c1407382c3de0af7ba0ebfdca7cb36d8c797797c0bc6c; qcom-camss.ko SHA 8aa3e7cb3ce790a0b37b6494f540e4075d78f8b3fed69ed415e81f4da5cfb75d. The unchanged canonical four-module authority manifest is ad96f706b5e0c5440707c0b9dc5d40a1376391b792f03d3d20bba5d23244f53c. Standby IR remains OFF.

The new one-shot runner consumes the identity BEFORE driver bind, verifies Golden's saved v19c default and blank next_entry, accepted hashes/source HEAD, suspended exact sensor set, no open camera node users, and seals the full 45-node camera namespace root:root 0600. It executes only the configure-only client for at most 35 seconds, verifies exactly one successful front/rear configuration and two separate neutral readbacks. On any failure it does not retry or guess a media-graph rollback; it reboots to protected Golden. A distinct 150-second systemd bound, nondefault one-shot GRUB entry and root-private source+IPA build path are required. Build directories and candidate boot/service/staging are removed after independent Golden return, with only numeric/non-image evidence archived.

Limitations: DAC root-only permissions exclude normal unprivileged camera users during the experimental boot but cannot protect against root-equivalent actors; this does not establish production multi-client exclusivity. Camera configuration may change subdevice formats and kernel controls but must not start streaming. Front/rear optically sustained 30 fps through a separate standard V4L2 software-publisher path in E004le; this new test does not establish libcamera app fps, full ISP parity, calibrated colour or frame capture. Nighttime darkness is irrelevant to the no-pixel configuration test. Never reuse E004lq once armed, even if it fails before opening a camera.

Status at preparation: compiled and staged source-only; no E004lq physical attempt until its unique consumed marker is written. RESULT.json/CONSUMED.json and guarded boot history supersede preparation status.

## Final physical result — PASS, consumed, retired

Fresh candidate boot 6bbe3993-d47a-402c-8c53-42cfd6cb5ab0 executed
exactly once under root-only camera node seal. OV13858 configured RAW
4076x2806 SGRBG10_CSI2P and IMX681 configured RAW 3840x2160
SRGGB10_CSI2P, each in independent acquire/configure/release sessions.
The separate read-only native Media Controller v2 graph auditor
accepted a FULL neutral graph after EACH configuration and after both
releases. There was no Camera::start, V4L2 STREAMON, frame allocation,
pixel recording or IR emitter. Root-owned libcamera/IPA configuration
remained pinned under /var/lib/sp11-e004lq-build; optional sensor crop
ENOTTY/defaulted rectangles and uncalibrated IPA still need work.
The oneshot reported rc0 and automatically returned to protected
Golden boot 0d41c33e-7536-4d61-84c6-c9556aa1012e, saved_entry v19c,
next_entry empty, no camera nodes or modules. Root-private build,
candidate stage, service and separate GRUB entry were retired after
independent Golden verification. See RESULT.json, CONSUMED.json and
evidence/ for non-image proof. This does NOT demonstrate libcamera
streaming, FPS, processed output, calibrated image quality or
production multi-client ownership. Never rearm E004lq.
