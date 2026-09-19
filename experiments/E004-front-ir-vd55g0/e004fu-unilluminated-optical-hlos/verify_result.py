#!/usr/bin/env python3
"""Verify E004fu's bounded optical-to-HLOS test without retaining optical pixels."""
from hashlib import sha256
from pathlib import Path
import json
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E = HERE / "evidence"
NON_IMAGE_SHA256 = {
    "RUNTIME-RESULT.json": "71202e04f095217a3ddeeb1a44cf2e1b7d459d7e1415fc2d173fa5c6ef67f0af",
    "CAPTURE.txt": "242eed05675b1fc9de8cdcd7196f95beb19f14660f397818314962ee76f050fa",
    "KERNEL.txt": "9fde51456ecf6cc39d51b2e49221aab93208746bbd1aaa9f11c72df622d174a1",
    "ARMED.json": "3611b1b5bed8cf85f09963cd1252751a6a93a7e8d0fc527397e1cc0458bc36df",
    "CONSUMED.json": "4bf5d8e5d1e79f36ca31209e411c781e7f934a3bf7c3a85a64713684be45376e",
    "RETIRED.json": "93ab4b44644602672e85b392f30b38a5aa1db8070d692330df43061728282efc",
    "PATTERN-CONTROL.txt": "afc46ea5b42279a35b4190777efb172fd3370d0a20915b5e6f6d71f5b30d816f",
    "POSTBOOT.txt": "8f5f4f2bca7aa09c87926364ded304cf03dc736d7e2bee79fe4b18fede8172b5",
}

def require(test, problem):
    if not test:
        raise ValueError("E004FU_EVIDENCE_FAIL " + problem)

def sha(path):
    return sha256(path.read_bytes()).hexdigest()

def main():
    for name, digest in NON_IMAGE_SHA256.items():
        path = E / name
        require(path.is_file() and sha(path) == digest, "evidence changed: " + name)
    runtime = json.loads((E / "RUNTIME-RESULT.json").read_text())
    armed = json.loads((E / "ARMED.json").read_text())
    consumed = json.loads((E / "CONSUMED.json").read_text())
    retired = json.loads((E / "RETIRED.json").read_text())
    post = (E / "POSTBOOT.txt").read_text()
    capture = (E / "CAPTURE.txt").read_text()
    kernel = (E / "KERNEL.txt").read_text()
    hlos = json.loads((E / "HLOS-BINARIES.json").read_text())
    require(armed.get("head") == "43800a04de7e62cdfa598db9e1bf600dfe2236d1",
            "wrong source checkpoint at arming")
    require(len({armed["golden_boot"], consumed["boot"], retired["boot"]}) == 3,
            "one-shot identity or return boot reused")
    require(retired["status"] == "GOLDEN_RESTORED_CANDIDATE_RETIRED" and
            retired["boot"] in post, "Golden return not verified")
    for marker in ("saved_entry=sp11-audio-fullio-v19c", "next_entry=",
                   "BootCurrent: 0005", "BootOrder: 0005,0004,0000,0001,0002,0006",
                   "OVERLAP_GUARD=PASS", "CANDIDATE_BOOT_ABSENT=YES",
                   "CANDIDATE_ENTRY_ABSENT=YES", "CANDIDATE_FIRMWARE_ABSENT=YES",
                   "RAW_OPTICAL_FRAMES_ABSENT=YES"):
        require(marker in post, "postboot/cleanup not verified: " + marker)
    require(runtime["status"] == "PASS_LIVE_UNILLUMINATED_OPTICAL_HLOS_16FRAMES",
            "live optical transport/HLOS pipeline did not pass")
    for key, expected in (
        ("protected_runtime", False), ("protected_worker_used", False),
        ("native_ir_illumination_enabled", False), ("gpio_outputs", "disabled"),
        ("kernel_fault_or_warning", False), ("raw_capture_payload_retained", False),
        ("optical_signal_sufficient_for_face_auth", False),
        ("raw_or_processed_optical_hashes_recorded", False),
    ):
        require(runtime[key] == expected, "safety/privacy mismatch: " + key)
    for key in ("test_pattern_disabled", "hlos_pipeline_verified",
                "sensor_stream_confirmed", "test_pattern_verified",
                "sensor_stop_confirmed", "applied_controls_verified",
                "status_snapshots_verified", "digital_gain_verified"):
        require(runtime[key] is True, "capture/health mismatch: " + key)
    require(runtime["frames_requested"] == 16 and runtime["stream_attempts"] == 1
            and runtime["sequences"] == list(range(16))
            and runtime["hlos_frames_processed"] == 16, "capture frame sequence/count")
    require(runtime["captured_bytes"] == 16*1936*604
            and runtime["hlos_processed_bytes"] == 16*644*604*3//2,
            "capture/processed payload sizes differ")
    frames = [(int(n), int(length)) for n, length in
              re.findall(r"cam0-stream0 seq:\s+(\d+) bytesused:\s+(\d+)", capture)]
    require(frames == [(n, 1169344) for n in range(16)], "libcamera frame record mismatch")
    require("test_pattern: 0 (Disabled)" in (E / "PATTERN-CONTROL.txt").read_text()
            and "native test pattern verified: Disabled" in kernel
            and "native RAW10 stream started; GPIO outputs disabled" in kernel
            and "name=STOP_STANDBY" in kernel, "unilluminated mode or stop not verified")
    require(runtime["sensor_pm"] and
            all(value == "suspended" for value in runtime["sensor_pm"].values()),
            "sensor did not suspend")
    metrics = runtime["optical_frame_metrics"]
    require(len(metrics) == 16, "optical aggregate measurement count")
    require(all(row["frame"] == i and row["nonuniform"] is True
                and 0 <= row["min"] <= row["mean"] <= row["max"] <= 255
                and 0 <= row["p99"] <= 255 and 0 <= row["fraction_above_32"] <= 1
                for i,row in enumerate(metrics)), "invalid optical statistics")
    require(all(38 <= row["mean"] <= 40 for row in metrics[2:]),
            "captured steady-frame brightness does not match bounded evidence")
    forbidden = {"frame_sha256", "input_capture_sha256", "hlos_processed_sha256",
                 "hlos_nv12_sha256", "raw_image", "face_template"}
    require(not (forbidden & runtime.keys()), "raw/processed optical fingerprint retained")
    for name, expected in hlos["sources"].items():
        require(sha(ROOT / name) == expected, "HLOS source drift: " + name)
    for name, expected in hlos["binaries"].items():
        require(sha(Path(name)) == expected, "HLOS binary drift: " + name)
    require(not (HERE / "runtime/frames.bin").exists(), "optical images still on disk")
    require(not Path("/boot/sp11-7.1.5-camera-e004fu-native-ir").exists(),
            "camera candidate boot remains installed")
    result = {
        "experiment": "E004fu",
        "status": "PASS_LIVE_UNILLUMINATED_OPTICAL_HLOS_16FRAMES",
        "identity_consumed_and_retired": True,
        "frames_captured_and_processed": 16,
        "exposure_test_pattern": "Disabled",
        "illumination": "OFF; GPIO outputs disabled",
        "sensor_runtime_pm": runtime["sensor_pm"],
        "steady_frame_mean_grayscale_range": [
            min(row["mean"] for row in metrics[2:]),
            max(row["mean"] for row in metrics[2:]),
        ],
        "steady_frame_max_gray": max(row["max"] for row in metrics[2:]),
        "initial_frames_dark": True,
        "optical_signal_sufficient_for_face_auth": False,
        "protected_worker_used": False,
        "image_or_image_hashes_retained": False,
        "raw_optical_frames_absent": True,
        "camera_stop_and_golden_return": "PASS",
        "golden_return_boot": retired["boot"],
        "evidence_non_image_sha256": NON_IMAGE_SHA256,
        "interpretation": "Live ambient optical frame transport and HLOS processing work, but low contrast is not proven useful for facial identification; no IR emitter or biometric login was tested.",
        "next_gate": "Independent IR illumination timing/current/fault-shutdown authority, plus actual usable optical quality before face matching.",
    }
    (E / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print("E004FU_RESULT=PASS LIVE_UNILLUMINATED=16 HLOS_PROCESSED=16")
    print("LOW_CONTRAST=YES FACE_AUTHENTICATION=NO IR_EMITTER=OFF GOLDEN_RESTORED=YES")

if __name__ == "__main__":
    main()
