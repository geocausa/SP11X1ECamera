# Experimental libcamera RGB path filter

sp11-rgb-paths.h selects only the verified IMX681→CSIPHY2→CSID1→VFE1 RDI0 and OV13858→CSIPHY1→CSID0→VFE0 RDI0 paths. Dynamic I2C bus numbers are normalized with exact addresses; pads are checked. IR and alternate paths are excluded before sensor construction.

E004lh carries the Simple pipeline patch for clean libcamera v0.7.0 b7854fd07d42168f099b5ce30d1702e0e0875bf5. It is an SP11-only experimental build: its qcom-camss discovery restriction is not suitable for general upstream deployment.

This closes path-selection ambiguity only. It does not integrate the E004lg graph transaction engine or provide fresh graph snapshots, exclusive ownership, neutral cleanup and failure retirement. Do not install or run this candidate on a camera-capable boot until those guards are connected. No live libcamera support is claimed.

## E004li/E004lj offline native graph and transaction candidates

sp11-media-topology.h reads full Media Controller v2 topology from an exact
CAMSS fd and validates it independently of cached libcamera MediaLink flags.
sp11-rgb-graph.h and sp11-native-session.h implement a fail-closed native RGB
route transaction with freshly mapped entity/pad IDs and ioctl writes; native
ASan/UBSan mock-kernel tests are in tests/test_media_topology.cpp and
tests/test_native_session.cpp. The NativeSession ownership and idle callbacks
are not an independent OS-backed session/stream-liveness implementation.

These headers are NOT wired into SimplePipelineHandler or installed. Existing
SimpleCameraData::setupLinks and resetRoutingTable may mutate the graph;
unrestricted cam/CameraManager activation on a camera-capable boot is still
prohibited. Verify live v2 layout and integrate real exclusive/quiescent
ownership, all mutation sites and failure retirement before live admission.
