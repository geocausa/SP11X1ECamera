# E004lf libcamera route-admission audit

Pinned libcamera v0.7.0 b7854fd07d42168f099b5ce30d1702e0e0875bf5, SimpleCameraData constructor, searches for the first shortest sensor-to-video path without requiring links to be enabled or matching the project's approved route. SimpleCameraData::init calls setupLinks before format probing; setupLinks disables competing links and enables the selected path. Therefore ordinary CameraManager/cam enumeration is not graph-read-only.

Replay against the archived E004le complete neutral graph finds80 equal-length routes per sensor, with only one accepted front RAW route and one accepted rear route. All80 IR routes are inadmissible under the RGB safety contract. Preserving fixture link order selects front via CSID0/VFE0, which the complete119-edge guard rejects. This is static replay, not proof of actual libcamera kernel-enumeration order or a physical route attempt.

Do not run unrestricted cam enumeration on the camera-capable system. New integration must restrict discovered cameras and candidate paths to the approved front CSIPHY2→CSID1→VFE1 RDI0 and rear CSIPHY1→CSID0→VFE0 RDI0 routes, enforce whole-graph neutral/exclusive transitions, and exclude IR before any setupLinks mutation. Shortest path alone is not admission authority. Existing kernel mandatory controls and gain helper do not close this integration gate.

This audit is camera-free and repeats no physical experiment. E004le remains the latest physical proof; Golden remains restored. Selection/crop metadata, sensor delays, calibrated AEC/AWB/black level and PIX acceptance also remain incomplete.
