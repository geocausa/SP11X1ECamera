#!/usr/bin/env python3
import hashlib
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
EXPECTED_HASHES = {
    "windows-evidence/E003I-AQ-FINAL-LIVE-EVIDENCE.txt": "ea742dbb36d9f89fd52a1cfc19a49659678eeef0b7160f48c1d1c9cd3ed72250",
    "windows-evidence/E003I-AQ-SelectedTableScan.ps1": "b3054394f9ac02ff2ec092aa68cd5ec39df71e6209590cd6df4c1bc27e654e3c",
    "windows-evidence/E003I-AQ-FinalHolder90.ps1": "7a0a618117b250f7e6dedad1aa0bf256a831f72e5671468f7d7aacffeb9ded31",
    "E003I-AQ-aec-arbitration-replay.py": "40523cea10aee14122559c7f721048674e90150462f0172aff27d0125c3aa482",
    "E003I-AQ-REPLAY-RESULT.txt": "ad949c61b89e5c5ecca814014a55bab74aedde6ad394f3d08e5fdcece78a87cf",
}


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def main():
    for rel, expected in EXPECTED_HASHES.items():
        actual = sha256(ROOT / rel)
        require(actual == expected, f"sha mismatch {rel}: {actual} != {expected}")
    print("AQ_HASH_PINS=PASS")

    evidence = (ROOT / "windows-evidence/E003I-AQ-FINAL-LIVE-EVIDENCE.txt").read_text(encoding="ascii")
    require("E003I_AC53_STATUS=Success" in evidence, "Windows holder did not report StartAsync success")
    require("DEBUGGER_MODE=none" in evidence, "final evidence was not debugger-free")
    require("DEBUGGER_PROCESS_COUNT=0" in evidence, "debugger process guard failed")
    require(evidence.count("PID=5588 TABLES=5") == 2, "expected two matching live selector scans")
    require(evidence.count("T5 hdr=") == 2, "T5 missing from one selector scan")
    require(evidence.count("name=DefaultExpTable knees=4 dbrefs=3 hrefs=1") == 2,
            "T5 active-reference signature not stable across both scans")
    for n, knees in [(1, 2), (2, 4), (3, 3), (4, 2)]:
        require(evidence.count(f"T{n} hdr=") == 2, f"T{n} missing from one selector scan")
        require(evidence.count(f"name=DefaultExpTable knees={knees} dbrefs=1 hrefs=0") >= 2,
                f"T{n} passive-reference signature missing")
    print("AQ_LIVE_SELECTOR_TABLE681=PASS")

    fixture = json.loads((ROOT / "TABLE681.fixture.json").read_text())
    require(fixture["tuned_blob"]["active_symbol_id"] == 681, "wrong active symbol")
    require(fixture["tuned_blob"]["sha256"] == "2c1c7fd9090e0bf338f44bd9de785509c1fbebc975facc5286f12865cf675f1d",
            "wrong tuned-blob pin")
    require(fixture["device_mft"]["sha256"] == "c241b7fbb2ec54e439752a1ea7ad25da10ca740012a54bd0e7a87ea94a141c35",
            "wrong DeviceMFT pin")
    expected_knees = [
        {"increment_priority": 1, "gain_f32": 1.0, "exposure_time_ns": 37516},
        {"increment_priority": 1, "gain_f32": 67.0, "exposure_time_ns": 33333333},
        {"increment_priority": 1, "gain_f32": 67.0, "exposure_time_ns": 66666666},
        {"increment_priority": 0, "gain_f32": 92.0, "exposure_time_ns": 66666666},
    ]
    require(fixture["decoded_knees"] == expected_knees, "decoded table 681 knees changed")
    require(fixture["truncated_knee_products"] == [37516, 2233333311, 4466666622, 6133333272],
            "table 681 products changed")
    print("AQ_TABLE681_FIXTURE=PASS")

    replay = subprocess.run(
        [sys.executable, str(ROOT / "E003I-AQ-aec-arbitration-replay.py")],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    stored = (ROOT / "E003I-AQ-REPLAY-RESULT.txt").read_bytes()
    require(replay.stdout == stored, "fresh replay output differs from pinned result")
    text = stored.decode("utf-8")
    require("FUZZ_CASES 100017 SEGMENTS {1: 36133, 2: 36635, 3: 27249} PASS" in text,
            "100017-case regression marker missing")
    require("OBSERVED_PAIR_CHECK 0x40e7b95b 33333332" in text,
            "live output-pair corroboration marker missing")
    require("AQ_REPLAY_SELFTEST=PASS" in text, "replay self-test marker missing")
    print("AQ_REPLAY_REPRODUCIBLE=PASS")
    print("AQ_VERIFY=PASS")


if __name__ == "__main__":
    main()
