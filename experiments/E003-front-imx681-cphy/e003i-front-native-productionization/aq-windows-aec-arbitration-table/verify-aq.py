#!/usr/bin/env python3
import hashlib
import json
import pathlib
import subprocess
import sys
import struct

ROOT = pathlib.Path(__file__).resolve().parent
EXPECTED_HASHES = {
    "windows-evidence/E003I-AQ-FINAL-LIVE-EVIDENCE.txt": "ea742dbb36d9f89fd52a1cfc19a49659678eeef0b7160f48c1d1c9cd3ed72250",
    "windows-evidence/E003I-AQ-SelectedTableScan.ps1": "b3054394f9ac02ff2ec092aa68cd5ec39df71e6209590cd6df4c1bc27e654e3c",
    "windows-evidence/E003I-AQ-FinalHolder90.ps1": "7a0a618117b250f7e6dedad1aa0bf256a831f72e5671468f7d7aacffeb9ded31",
    "E003I-AQ-aec-arbitration-replay.py": "45a4da2f993e7c5e224fd8592602a3226fc6bbad54936aab87c110fd60fff068",
    "E003I-AQ-REPLAY-RESULT.txt": "3d8db95a02bad1e4eb032fdd57f4eafd7af062b5935d0714d78d00e426dae4a5",
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

    # 2026-09-10 same-machine read-only recapture closes the controller range
    # that the original selector-only AQ checkpoint deliberately did not pin.
    rr = ROOT / "windows-evidence/range-recapture-20260910"
    range_hashes = {
        "E003I-CH-RANGE-RECAPTURE.zip": "809e7d58ba5605cbd5f98bcc2e2b41c12843dcc79e91cf2fd86e43647a9e8c67",
        "controller-plus-0100.bin": "333c0f41e7751bc154118f54539d139c165d82386468d82563a7f626760fa011",
        "controller-plus-0140.bin": "5561a3ddcc56563b1c16b857d0c469743060086178034223623dfceaaf52a9f8",
        "ORACLE.txt": "908d8b2cbcd76230b63ad6945179b52b63e8a6086af5c519dd62cf5487e17e50",
        "SelectedTableScan.txt": "b1b83d25ac4819834523fd81453fd4da121de67fa9cbbc72f264c4dd561dc0f8",
        "t5-db-header.bin": "88b08b4426667bd70386384a8fe85ad00d9c1cb7ce0772c90275974bc6dce0f0",
        "t5-knees.bin": "79ef9779ac9b5fb0761a3c0f6c1c07680cc6ef8900a2b59df2b4ce09d6d417f7",
    }
    for name, expected in range_hashes.items():
        require(sha256(rr / name) == expected, f"range recapture sha mismatch: {name}")
    scan = (rr / "SelectedTableScan.txt").read_text(encoding="utf-16")
    require("T5 hdr=0x160D5F18390 db=0x160D5F18380 name=DefaultExpTable knees=4 dbrefs=3 hrefs=1" in scan,
            "active T5 signature missing from range recapture")
    require("HREFS 0x160DA73A300" in scan, "active T5 controller header reference missing")
    ctrl = (rr / "controller-plus-0100.bin").read_bytes()
    require(len(ctrl) == 0xe0, "controller recapture length changed")
    require(struct.unpack_from("<f", ctrl, 0x28)[0] == 1.0, "min gain changed")
    require(struct.unpack_from("<Q", ctrl, 0x30)[0] == 37516, "min time changed")
    require(struct.unpack_from("<f", ctrl, 0x50)[0] == 92.0, "max gain changed")
    require(struct.unpack_from("<Q", ctrl, 0x58)[0] == 66666664, "max time changed")
    t5_hdr = struct.unpack_from("<Q", ctrl, 0x90)[0]
    require(t5_hdr == 0x160D5F18390, "controller +0x190 no longer points to recaptured T5")
    require(struct.unpack_from("<Q", ctrl, 0xa0)[0] == 0, "controller +0x1a0 policy changed")
    knees_raw = (rr / "t5-knees.bin").read_bytes()
    knees = [struct.unpack_from("<IfQ", knees_raw, i * 16) for i in range(4)]
    require(knees == [(1,1.0,37516),(1,67.0,33333333),(1,67.0,66666666),(0,92.0,66666666)],
            "live T5 knees changed")
    oracle_raw = (rr / "ORACLE.txt").read_bytes()
    oracle = oracle_raw.decode("utf-16") if oracle_raw.startswith((b"\xff\xfe", b"\xfe\xff")) else oracle_raw.decode("utf-8", errors="replace")
    require("CONTROLLER=0x160DA73A170" in oracle and "+0x1A0: q=0x0000000000000000" in oracle,
            "range oracle controller/policy identity missing")
    print("AQ_LIVE_PREVIEW_RANGE=minGain1,minTime37516,maxGain92,maxTime66666664,policy0")

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
