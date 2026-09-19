#!/usr/bin/env python3
"""Reproduce E004fv's source-level evidence (never a hardware approval)."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json
import subprocess

from generate_patch import BASE, PATCH, WIN, source_pair

HERE = Path(__file__).resolve().parent
original, candidate = source_pair()
assert PATCH.is_file()
r = subprocess.run(["python3", str(HERE / "test_timer_patch.py")],
                   text=True, capture_output=True, check=False, timeout=75)
if r.returncode:
    raise SystemExit("E004FV_TEST_FAILURE " + r.stdout + " " + r.stderr)
assert "E004FV_ACTUAL_PATCHED_C=PASS WINDOWS_PARITY_REQUESTS=1271" in r.stdout
assert "STANDALONE_ASAN_UBSAN=PASS" in r.stdout
build = subprocess.run(["python3", str(HERE / "test_isolated_kernel_build.py")],
                       text=True, capture_output=True, check=False, timeout=165)
if build.returncode or "E004FV_ISOLATED_KERNEL_MODULE_BUILD=PASS" not in build.stdout:
    raise SystemExit("E004FV_BUILD_FAILURE " + build.stdout + " " + build.stderr)
assert sha256(PATCH.read_bytes()).hexdigest() == (
    "430953b2eade6a9ac08a1c2689982b5685fceb61b30222f02a79ce98cec62de9"
)
windows = json.loads(WIN.read_text())["timer_handler"]
assert windows["flash_helper_enabled_request_ms"] == 1270
assert windows["flash_helper_enabled_register_value"] == 254
assert windows["used_by_type0_stream_proven"] is False
samples = {}
for ms in (0, 10, 11, 19, 20, 40, 100, 1260, 1270, 1280):
    previous = 0 if ms == 0 else 0x80 | min(ms // 10, 127)
    new = 0 if ms == 0 else 0x80 | ((ms - 10) // 10)
    samples[str(ms)] = {
        "original_linux_hex": f"0x{previous:02x}",
        "candidate_and_windows_handler_hex": f"0x{new:02x}",
    }
assert samples["10"] == {"original_linux_hex": "0x81",
                         "candidate_and_windows_handler_hex": "0x80"}
assert samples["1270"] == {"original_linux_hex": "0xff",
                           "candidate_and_windows_handler_hex": "0xfe"}
assert samples["1280"] == {"original_linux_hex": "0xff",
                           "candidate_and_windows_handler_hex": "0xff"}
result = {
    "experiment": "E004fv",
    "status": "PASS_OFFLINE_WINDOWS_HANDLER_ENCODING_PARITY_SOURCE_PATCH_ONLY",
    "source_sha256": sha256(BASE.read_bytes()).hexdigest(),
    "windows_static_result_sha256": sha256(WIN.read_bytes()).hexdigest(),
    "patch_sha256": sha256(PATCH.read_bytes()).hexdigest(),
    "patched_source_sha256": sha256(candidate.encode()).hexdigest(),
    "sample_timer_encodings": samples,
    "windows_reported_handler_formula": windows["enabled_value"],
    "original_linux_formula": "0x80 | min(floor(timeout_ms / 10), 127)",
    "candidate_formula": "0x80 | floor((timeout_ms - 10) / 10) for 10..1280 ms; zero disables",
    "nonzero_requests_below_ten_ms_rejected": True,
    "arming_with_disabled_timer_rejected": True,
    "windows_parity_valid_requested_intervals_tested": 1271,
    "invalid_interval_count_tested": 9,
    "paired_channels_tested": [0, 3],
    "kernel_module_built_offline_against_golden_headers": True,
    "address_and_undefined_behavior_sanitizers": "PASS",
    "patched_module_installed": False,
    "flash_source_replaced_in_golden": False,
    "emitter_activated": False,
    "physical_timer_duration_measured": False,
    "physical_led_strobe_shutdown_verified": False,
    "actual_pmic_timer_register_readback_verified": False,
    "optical_current_and_irradiance_limit_verified": False,
    "emitter_enable_authorized": False,
    "next_gate": "Actual read-only timer register evidence and independently verified electrical/optical shutoff before any active emitter test.",
}
evidence = HERE / "evidence"
evidence.mkdir(exist_ok=True)
(evidence / "RESULT.json").write_text(json.dumps(result, indent=2)+"\n")
print("E004FV_RESULT=PASS HANDLER_ENCODER_PARITY=1271 ISOLATED_BUILD=PASS")
print("INSTALLED=NO EMITTER_ENABLED=NO PHYSICAL_TIMER_AUTHORITY=NO")
