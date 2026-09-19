#!/usr/bin/env python3
"""Verify the completed E004ft single-boot live-pattern HLOS result offline."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json
import re

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
E = HERE / "evidence"
HASHES = {
    "RUNTIME-RESULT.json": "ac21b914751f821b0110c26e93c1698b047fc29e89f7fd38276b55c1b35b7d6a",
    "CAPTURE.txt": "d0533f8ebc3481f6131a5fc2b7f3783cb05eda107091e835f89cca6304e87a2e",
    "KERNEL.txt": "be3757175bc9a9c38694e749accdacc14e66d60fcf872ad99c951fca9494efa3",
    "ARMED.json": "986c0c2f6c7e458f9e824b663c1bba39b234d699d93ebb9105a1ce08f5af8f30",
    "CONSUMED.json": "52569a3757c8696328bbf586576669565cd2cb03cfc7493932960cab6613388f",
    "RETIRED.json": "7b59a5b0950c65a119784556738ebf51e85d6d0119207ce97ba89035eedca3b6",
    "POSTBOOT.txt": "b266aa3547bf4f48e7c447992147eb5a00b24c9feb5d52f01fd1123fd639ab4d",
}


def require(test: bool, reason: str) -> None:
    if not test:
        raise ValueError("E004FT_EVIDENCE_FAIL " + reason)


def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    for name, expected in HASHES.items():
        p = E / name
        require(p.is_file() and digest(p) == expected, "missing/drifted " + name)
    runtime = json.loads((E / "RUNTIME-RESULT.json").read_text())
    armed = json.loads((E / "ARMED.json").read_text())
    consumed = json.loads((E / "CONSUMED.json").read_text())
    retired = json.loads((E / "RETIRED.json").read_text())
    hlos = json.loads((E / "HLOS-BINARIES.json").read_text())
    capture = (E / "CAPTURE.txt").read_text()
    kernel = (E / "KERNEL.txt").read_text()
    post = (E / "POSTBOOT.txt").read_text()

    require(armed["head"] == "f091282f091d32e3597d73ea53f8a532197e5b6d",
            "incorrect checkpoint at arming")
    require(len({armed["golden_boot"], consumed["boot"], retired["boot"]}) == 3,
            "one-shot and Golden return boot identities not distinct")
    require(retired["status"] == "GOLDEN_RESTORED_CANDIDATE_RETIRED"
            and retired["boot"] in post, "Golden return or candidate retirement unverified")
    require("sp11-audio-fullio-v19c" in post and "next_entry=\n" in post
            and "BootOrder: 0005,0004,0000,0001,0002,0006" in post
            and "OVERLAP_GUARD=PASS" in post, "Golden boot or camera-idle check absent")
    for marker in ("CANDIDATE_BOOT_ABSENT=YES", "CANDIDATE_ENTRY_ABSENT=YES",
                   "CANDIDATE_FIRMWARE_ABSENT=YES", "CAPTURE_RAW_ABSENT=YES"):
        require(marker in post, "cleanup missing: " + marker)
    require(runtime["status"] == "PASS_LIVE_PATTERN_HLOS_16FRAMES",
            "live pipeline did not pass")
    for key in ("gpio_outputs", "protected_runtime", "protected_worker_used",
                "native_ir_illumination_enabled", "kernel_fault_or_warning",
                "raw_capture_payload_retained"):
        expected = "disabled" if key == "gpio_outputs" else False
        require(runtime[key] == expected, "unexpected safety state: " + key)
    for key in ("hlos_pipeline_verified", "processed_pattern_verified",
                "sensor_stream_confirmed", "sensor_stop_confirmed",
                "status_snapshots_verified", "applied_controls_verified",
                "digital_gain_verified", "monochrome_tuning_selected",
                "gain_helper_bound"):
        require(runtime[key] is True, "capture/processing health failed: " + key)
    require(runtime["frames_requested"] == 16 and runtime["stream_attempts"] == 1
            and runtime["sequences"] == list(range(16)), "one-shot frame sequence")
    frames = [(int(n), int(sz)) for n, sz in
              re.findall(r"cam0-stream0 seq:\s+(\d+) bytesused:\s+(\d+)", capture)]
    require(frames == [(n, 1169344) for n in range(16)],
            "raw capture log sequence or buffer length mismatch")
    require(runtime["captured_bytes"] == 16*1936*604
            and runtime["hlos_processed_bytes"] == 16*644*604*3//2
            and runtime["hlos_frames_processed"] == 16,
            "frame extent or worker count mismatch")
    require(runtime["input_capture_sha256"] ==
            "33dce2a2a6edacd608c998734e2635d7a9230c39d0f0fa27767dfa8b514918c3"
            and runtime["hlos_processed_sha256"] ==
            "ea414ce89d3fdcf25f834baa3f8d13a1d04b25289ff34dba844a57986db655df",
            "live capture/processed hashes differ from reported result")
    require(runtime["frame_sha256"] ==
            ["baf8aef482c894c21c0c3f6dd818bce6181b9cb1dff78ff4a497ccf5cfd99b28"]*16,
            "generated pattern frames differ")
    require(all(v == [15, 212] for v in runtime["frame_gray_ranges"]),
            "unexpected grayscale range")
    require(runtime["sensor_pm"] and all(v == "suspended"
            for v in runtime["sensor_pm"].values()), "sensor not suspended after capture")
    require("native RAW10 stream started; GPIO outputs disabled" in kernel
            and "native test pattern verified: Horizontal greyscale" in kernel
            and "name=STOP_STANDBY" in kernel, "kernel capture/stop evidence missing")
    require(hlos["status"] == "OFFLINE_PREPARED_NOT_INSTALLED",
            "HLOS build was not offline prepared")
    for name, expected in hlos["sources"].items():
        require(digest(REPO / name) == expected, "HLOS source drift: " + name)
    for name, expected in hlos["binaries"].items():
        require(digest(Path(name)) == expected, "HLOS binary drift: " + name)
    require(not (HERE / "runtime/frames.bin").exists(), "raw test-pattern buffer retained")
    require(not Path("/boot/sp11-7.1.5-camera-e004ft-native-ir").exists(),
            "candidate boot still installed")
    require(not Path("/etc/grub.d/99zzzzzz_sp11_camera_e004ft_native_ir").exists(),
            "candidate entry still installed")

    result = {
        "experiment": "E004ft",
        "status": runtime["status"],
        "identity_consumed": True,
        "same_boot_retry": False,
        "capture_type": "live native Linux VD55G0 generated grayscale sensor pattern",
        "frames_captured": 16,
        "frames_processed_with_ordinary_linux_hlos_worker": 16,
        "capture_sha256": runtime["input_capture_sha256"],
        "processed_sha256": runtime["hlos_processed_sha256"],
        "processed_bytes": runtime["hlos_processed_bytes"],
        "camera_stream_stop": "PASS",
        "sensor_runtime_pm": runtime["sensor_pm"],
        "kernel_fault_or_warning": False,
        "native_ir_emitter": "OFF",
        "protected_worker_used": False,
        "golden_boot_return": retired["boot"],
        "candidate_retired": True,
        "raw_capture_retained": False,
        "evidence_sha256": HASHES,
        "caveat": ("Sensor-generated grayscale test pattern, not a useful optical image, "
                   "illumination proof, facial identity matching, liveness or login."),
        "next_gate": ("Live ordinary unilluminated optical capture and separately verified "
                      "IR emitter pulse/current/independent timeout authority."),
    }
    (E / "RESULT.json").write_text(json.dumps(result, indent=2) + "\n")
    print("E004FT_RESULT=PASS LIVE_PATTERN_FRAMES=16 HLOS_PROCESSED=16")
    print("GOLDEN_RETURN=PASS CANDIDATE_RETIRED=YES IR_EMITTER=OFF")


if __name__ == "__main__":
    main()
