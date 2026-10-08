# Rear cold linear NV12 qualification

Candidate21/sourcebuild26 is isolated diagnostic tooling. It keeps the proven
mode1 sensor, CSI route, tuning and startup order, 240MHz NoC floor, and eight
auxiliary outputs. FULL output becomes native hardware 3840x2160 NV12:
stride3840, Y offset0, UV offset8294400, image12441600 bytes,
page-rounded allocation12443648 bytes. FULL round/clamp8; DS remains10.

The overlay applies before any command is submitted. All10 write masters must
be disabled and FULL UBWC enable bits already clear. FULL compression controls,
metadata and loss registers/addresses are never written. Geometry, packer3,
stride, increments and22 round/clamp words are read back before enable.
Every WM completion requires its exact owned consumed IOVA. Both output
generations and complete source/CSID/BUS/RTCDM stops are required.

The default rear runtime remains denied. No public V4L2 buffer is exposed by
this diagnostic and no optical pixel is read. Exposed DMA, PM and shared owner
stay pinned until mandatory Golden return. This is no CPU pixel ISP or product
daemon. Windows optical parity and normal continuous libcamera capture remain
unproven. Front calibration stays deferred.

Source audit: docs/NATIVE-RGB-REAR-LINEAR-NV12-SOURCE-AUDIT-20261008.json.
Hosted tests exercise the actual staged layout, bus helper, round/clamp and
ten-WM ledger under GCC/Clang ASAN/UBSAN. Geometry fixture includes now resolve
the selected staged binder explicitly; both compressed and linear modes pass.
