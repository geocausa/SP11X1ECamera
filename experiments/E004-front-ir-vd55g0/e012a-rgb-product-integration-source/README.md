# E012A — RGB product-integration source pivot

PASS, source/offline only. The project stops treating complete OEM DLL archaeology as a prerequisite for the normal camera product. Further Ghidra/KD/Windows-oracle work is demand-driven by concrete front/rear RGB failures.

The new `src/sp11-camera-stack/rgb/product/` layer reuses the already physically accepted RGBSession, exact 119-edge route controller and front1080/rear4K RAW10→NV12 publishers. It adds a pre-release systemd daemon, video-group control socket, exact product/stack asset admission, publisher units, STREAMOFF-bound stop proof, fail-safe Golden recovery, and a Golden-safe unactivated installer. Runtime remains opt-in and bounded to four hours until a fresh product-boot soak passes.

Offline validation: 42 existing service tests, 14 new product tests and 11 route-policy tests pass; the broader RGB source suite passes. Product-compiled front/rear publishers refuse execution on current Golden because the dedicated product boot token is absent. No camera Start, reboot, kernel build, service activation or ENABLE contract occurred.

Product source tree SHA-256: `407ce4be04b32a734194ac27b160c601897ee13330b234467f929fdb3536525b`. NEXT E012B performs only the inactive Golden installation/verification.
