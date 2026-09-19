#!/usr/bin/env python3
"""Prepare E004fu standalone ordinary-Linux user-space binaries (offline only)."""
from hashlib import sha256
import json
from pathlib import Path
import subprocess

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
HLOS = REPO / "src/sp11-camera-hlos-worker"
CORE = REPO / "src/sp11-camera-protected-worker"
BUILD = HERE / "build"
BUILD.mkdir(exist_ok=True)
SOURCES = [
    "experiments/E004-front-ir-vd55g0/e004fu-unilluminated-optical-hlos/optical_stats.py",
    "src/sp11-camera-hlos-worker/sp11-ir-rgb888-to-nv12.c",
    "src/sp11-camera-hlos-worker/sp11-hlos-ir.c",
    "src/sp11-camera-protected-worker/sp11-parity-worker.c",
    "src/sp11-camera-protected-worker/sp11-parity-worker.h",
    "src/sp11-camera-protected-worker/sp11-swabf-reference.c",
    "src/sp11-camera-protected-worker/sp11-swasf-reference.c",
    "src/sp11-camera-protected-worker/sp11-swasf-windows-tuning.c",
    "src/sp11-camera-protected-worker/sp11-swasf-helpers.c",
    "src/sp11-camera-protected-worker/sp11-swasf-c230.c",
    "src/sp11-camera-protected-worker/sp11-swasf-c3e8.c",
    "src/sp11-camera-protected-worker/sp11-swasf-cd90.c",
]
def sha(path):
    return sha256(path.read_bytes()).hexdigest()
for script in ("test-offline.sh", "test-capture-integration.sh",
               "test-multiframe-offline.sh", "test-bridge16-offline.sh"):
    subprocess.run(["bash", str(HLOS/script)], check=True, stdout=subprocess.DEVNULL,
                   timeout=130)
flags = ["clang", "-std=c11", "-O2", "-Wall", "-Wextra", "-Werror"]
bridge = BUILD / "sp11-ir-rgb888-to-nv12"
worker = BUILD / "sp11-hlos-ir"
subprocess.run(flags + [str(HLOS/"sp11-ir-rgb888-to-nv12.c"), "-o", str(bridge)],
               check=True, timeout=50)
subprocess.run(flags + [str(HLOS/"sp11-hlos-ir.c")] +
               [str(REPO/path) for path in SOURCES if path.endswith(".c") and "protected-worker" in path] +
               ["-o", str(worker)], check=True, timeout=65)
record = {
    "status": "OFFLINE_PREPARED_NOT_INSTALLED",
    "source_experiment": "E004fe previously completed and retired",
    "source_capture_type": "native libcamera unilluminated optical scene, test pattern disabled; no IR emitter",
    "sources": {p: sha(REPO/p) for p in SOURCES},
    "binaries": {str(p): sha(p) for p in (bridge, worker)},
    "system_install": False,
    "retains_raw_optical_frames": False,
    "face_authentication": False,
}
(HERE/"evidence/HLOS-BINARIES.json").write_text(json.dumps(record,indent=2)+"\n")
print("E004FU_HLOS_PREPARED=PASS BINARY_COUNT=2 CAMERA_ACTIVATED=NO")