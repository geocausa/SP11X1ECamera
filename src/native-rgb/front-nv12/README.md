# Native front NV12 cold-state trial

Fresh one-use identity: native-nv12-20261007-01. Never rearm after consumption.
This is diagnostic boot tooling; it installs no camera product service and
leaves protected Golden FullIO v19c as the saved default.

The optional `build.py --nv12-trial` overlay is separate from the ordinary
native builder. Its module parameter is false by default, and an atomic latch
permits one NV12 start attempt per module lifetime. It reuses the physically
exercised four-frame runner, CSID completion groups and stop/ownership path.

The FULL contract is 2560x1440 single-memory-plane NV12, 2560-byte Y/UV stride,
Y at offset 0, UV at 3686400, 5529600 bytes total. Ownership and all retargets
carry the format; mapped-SG coverage and the complete 32-bit span are checked.
FULL uses public BUS-v3 packer 3, line mode, UV half height and explicit
bandwidth-limiter disable. E1C is the VFE680 bandwidth limiter, not an inferred
burst-limit address.

Before any FULL configuration, all nine retained clients must be disabled
and both FULL UBWC MODE_CFG enable bits must already be clear. The trial
performs no compression-register/reset writes and rejects a previous
compressed state. It also reads back FULL geometry/packer/stride/increments
and every luma/chroma 8-bit round/clamp word before enabling the write masters.

The existing E006p semantic round/clamp packer matches all 44 FULL words in
startup packets 0/1. The actual command helper changes exactly twelve words
across those packets, preserving crop/scaler, DMI headers/payloads/addresses,
auxiliary paths and other IQ. Packet 2/3 and R4 steady contain no FULL or bus
writes. DMI binding remains owned by the pinned existing materializer. The
derived 41088-byte bootstrap stays private on SP11 and is not committed.

Validation: 170 synthetic C checks with ASan/UBSan; the actual local bootstrap
passes the same helper, with no file mutation/hardware access. Four source
composition tests pass. Kbuild uses W=1/-Werror. Builds 08–10 were uninstalled
preparation; only the final qualified audit11 is eligible for this candidate.

The private capture helper queues four buffers once, requests four frames,
checks sequence/payload/timestamp/errors, saves pixels at root-only local
paths and verifies STREAMOFF. It pre-fills each surface with a marker to reject
completely untouched Y/UV regions. Report only derived metadata. No software
pixel ISP, loopback, AI/effects, IR stream, Windows binary or bespoke product
daemon runs. Do not infer colour correctness, Windows quality, continuous
capture, repeated use or compressed-to-linear transitions from four buffers.

Public register/encoding authority: Qualcomm camera-driver
82ac3a671a5b0a4e3b3ac4519208af1d37a93eb6,
camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe_bus/cam_vfe_bus_ver3.c,
camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe680.h,
camera/drivers/cam_cdm/cam_cdm_util.{c,h}.
Retained semantic authority: camss-e006p-crop-roundclamp.inc (MIT).
