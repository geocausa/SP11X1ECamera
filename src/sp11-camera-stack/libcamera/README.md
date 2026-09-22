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

## E004lk/E004ll live kernel graph and guarded native link routing PASS

One-shot E004lk independently accepted real 44/44/84/163 Media Controller v2
topology, initially neutral. E004ll then proved exact native link transitions
neutral/front/neutral/rear/neutral with eight guarded writes, no STREAMON,
automatic Golden return and verified IR standby. Both are retired; no
unrestricted libcamera or ordinary app access was attempted.

## E004lm experimental libcamera Simple adapter (OFFLINE ONLY)

The maintained sp11-libcamera-route-gate.h and
sp11-libcamera-experimental-lease.h bridge E004lj NativeSession to the pinned
libcamera v0.7.0 Simple handler. Apply the E004lh RGB filter patch, then
E004lm 0002-sp11-guarded-simple-native-session.patch, and copy the maintained
sp11-*.h headers into the Simple source directory. libcamera builds/tests
pass in a private clean scratch checkout, including Golden admission-denial.
CAMSS setupLinks is intercepted for init+configure and existing ACTIVE
subdevice routing reset is denied; route is neutral after sensor enumeration,
after configure and after stop, and only the selected sensor can be routed
before streamOn. Boot token plus root and cooperative lockf are experimental
guards, NOT general OS-enforced exclusivity. There is no authorized
production install or live libcamera test; real hasStreams/active routing
requirements and independent cross-process ownership remain open. Do not
run unrestricted libcamera on a camera-enabled SP11 boot.
