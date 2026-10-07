# Native libcamera implementation checkpoint — 2026-10-07

The user accepted native Linux drivers plus the Qualcomm hardware ISP and standard
libcamera automatic controls. The earlier literal kernel-only boundary is
superseded. No bespoke camera service, software pixel ISP, loopback or AI/effects
is required by this architecture.

Implemented in src/native-rgb/libcamera: pinned clean libcamera staging,
repeatable build/test orchestration, IMX681 gain helper, all-or-nothing front
four-control adapter, generation/sequence-checked AEC metering, and rear neutral
scalar adapter preserving independently validated arithmetic. Retained algorithms
are reused unchanged apart from private statistics helper names in the staged
copy, which conflict with GNU math declarations.

Actual ARM64 build: libcamera base ff740913b1e8907a72fa703afbc1dc6c5536807a,
isolated source libcamera-native-rgb-20261007-03, build under 02-kernel of the same
name. Warnings are errors; zero compiler warnings. Eight selected tests pass;
control_info_map and control_list skip because platform/vimc.0 Sensor B is absent.
The new native helper test passes, including synthetic nonzero statistics,
malformed/stale identity rejection and unchanged outputs after errors.

Build evidence: NATIVE-RGB-LIBCAMERA-BUILD-20261007.json.
No module installation, hardware stream, reboot or quality claim accompanies
this build. This is not an implemented CAMSS pipeline or complete IPA.

## Current hardware gates

1. Front mode timing: distinguish CSI transport throughput from pixel-array
   timing. Hardware identity 02 captured 240 sequential front RAW frames at
   FLL 3554/7116 and HTS 6752; both support nominal 720 MHz, with 15.36 ppm
   between timestamp estimates. The isolated driver now exposes read-only
   PIXEL_RATE=720000000, HBLANK=2912 and LINK_FREQ=1200000000; identity 03
   will verify the live ABI. Selection/full native array geometry remains
   unproven. Retained exposure policy uses 719898240 as a nominal 30 fps model;
   the pipeline must use the sensor timing ABI rather than conceal this difference.
2. Native ordinary output: E004IK–IP already supplies NV12 negotiation and DMA
   plans. BUS-v3 NV12 packer/geometry is source-supported. Published start sets
   UBWC MODE_CFG bit 0 only when UBWC is enabled; its forced compression disable
   clears bit 1, which is not the same as selecting ordinary linear storage.
   Published stop disables WM CFG but does not clear MODE_CFG. Do not infer a
   compressed-to-linear transition from packer=3 or compression bit 1 alone.
3. Replace front manually expanded 27-frame runner with queue-driven operation,
   kernel parameters/statistics queues and generation-correlated completion.
4. Compose complete rear packet-isolated startup semantics and correct
   prepared-command handoff; prove completion and shutdown before runtime.
5. Connect libcamera pipeline/IPA, controls and metadata; then ordinary-app
   reopen/switch tests and measured Windows baseline optical quality.

References:
- https://docs.libcamera.org/master/libcamera_architecture.html
- https://docs.libcamera.org/master/sensor_driver_requirements.html
- https://docs.kernel.org/userspace-api/media/drivers/camera-sensor.html
- https://lkml.iu.edu/2609.2/21787.html
- Qualcomm camera-driver 82ac3a671a5b0a4e3b3ac4519208af1d37a93eb6,
  camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe_bus/cam_vfe_bus_ver3.c,
  camera/drivers/cam_isp/isp_hw_mgr/isp_hw/vfe_hw/vfe17x/cam_vfe680.h.

A separately published SP11 camera implementation uses RAW transport plus a
software ISP. It is useful sensor evidence, but does not establish this project's
hardware ISP/NV12 goal: https://github.com/karsies-wq/sp11-imx681-linux.
