#!/usr/bin/env python3
"""Verify consumed one-shot PM8550 idle timer evidence OFFLINE; never re-read PMIC."""
from __future__ import annotations
from hashlib import sha256
from pathlib import Path
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
E = HERE / "evidence"
SOURCES = {
    "PREPARED.json": "9d898c443d8922f90fe751de5b1e7b4ba09b9b5d6e84d0726e2f97655079ae96",
    "CONSUMED.json": "dfb688867a1f31772f2e312cb5dbb8ba819581d92886e36e84a11c9fc721b559",
    "RESULT.json": "b2cbfeb4705937cca69609672fd1c4143135c82ee2aff8bcf82e33206daa093e",
    "POSTREAD.txt": "5c7ad77f77ae0664e4e5b0fbf30a527e3a39238cb5cd3ed281476f074e4d5a77",
}
MAPPING = ROOT / "experiments/E004-front-ir-vd55g0/e004fw-golden-pmic-flash-location-readonly/evidence/RESULT.json"
MAPPING_SHA = "4a7c333f39fa4d8fc0c3110fd8a131efaedba6bb62f77f1fdccaf6b1104c4c5b"
READ_SOURCE_SHA = "37e9458ef1d762c1692acaf7a00efd8b0755686891bc1108b5848a6ee8e52820"
WIN_TIMER = ROOT / "experiments/E004-front-ir-vd55g0/e004fl-ir-trigger-timing-authority/evidence/RESULT.json"
WIN_TIMER_SHA = "1d3ab98722a381c64f355b0b71da6cea84c4f569f81da1ebde262f51ea4348ef"

def need(ok: bool, reason: str) -> None:
    if not ok:
        raise ValueError("E004FX_OFFLINE_EVIDENCE_FAIL " + reason)

def digest(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()

def main() -> None:
    for name, expected in SOURCES.items():
        p = E / name
        need(p.is_file() and digest(p) == expected, name + " evidence changed")
    for p, expected in (
        (MAPPING, MAPPING_SHA), (HERE / "read_once.py", READ_SOURCE_SHA),
        (WIN_TIMER, WIN_TIMER_SHA),
    ):
        need(p.is_file() and digest(p) == expected, "pinned observer/authority changed")
    prepared = json.loads((E / "PREPARED.json").read_text())
    consumed = json.loads((E / "CONSUMED.json").read_text())
    result = json.loads((E / "RESULT.json").read_text())
    mapping = json.loads(MAPPING.read_text())
    post = (E / "POSTREAD.txt").read_text()
    win_timer = json.loads(WIN_TIMER.read_text())["timer_handler"]

    need(prepared["status"] == "PREPARED_SINGLE_PASSIVE_READ_NOT_CONSUMED",
         "not the prepared identity")
    need(consumed["status"] == "ONE_PASSIVE_READ_CONSUMED_BEFORE_IO"
         and consumed["attempt_count"] == 1, "read attempt not uniquely consumed")
    need(consumed["prepared_sha256"] == SOURCES["PREPARED.json"],
         "consumed marker references a different preparation")
    need(result["status"] == "PASS_SINGLE_PASSIVE_IDLE_TIMER_READ"
         and result["read_once_identity_consumed"] is True, "read result not passed")
    need(result["boot"] == prepared["golden_boot"] == consumed["boot"] ==
         "c4172e14-03ca-4e99-adbb-ddfb102cbe27", "Golden boot identity mismatch")
    need(prepared["target_seek_bytes"] == 548910
         and prepared["target_read_bytes"] == 36
         and result["requested_debugfs_pread_bytes"] == 36, "unbounded read extent")
    need(mapping["flash_pmic_sid"] == 1 and mapping["flash_dt_status"] == "disabled"
         and prepared["pmic_spmi"] == result["pmic_spmi"] == "0-01",
         "SPMI target or disabled flash mapping not pinned")
    target = [f"0xee{x:02x}" for x in (0x3e, 0x3f, 0x40, 0x41)]
    need(prepared["target_addresses"] == consumed["addresses"] ==
         result["target_addresses"] == target, "unexpected PMIC register set")
    bytes_observed = result["idle_timer_register_bytes"]
    need(list(bytes_observed) == target
         and all(bytes_observed[reg] == "93" for reg in target),
         "idle register readback changed")
    need(all(result["idle_timer_enable_bits"][reg] is True for reg in target),
         "timer byte enable bit mismatch")
    for marker in (
        "E004FX_GOLDEN_POSTREAD",
        prepared["golden_boot"], "FLASH_DT_STATUS=disabled",
        "saved_entry=sp11-audio-fullio-v19c", "next_entry=\n",
        "BootCurrent: 0005", "BootOrder: 0005,0004,0000,0001,0002,0006",
        "nodes=no modules=none active_processes=no", "OVERLAP_GUARD=PASS",
    ):
        need(marker in post, "post-read Golden/flash/camera verification missing: " + marker)
    for key in ("kernel_module_loaded_or_flash_driver_installed",
                "spmi_register_write_requested", "emitter_activation_requested",
                "physical_led_wiring_verified", "physical_timer_interval_measured",
                "independent_stuck_trigger_shutdown_verified",
                "safe_optical_irradiance_verified", "emitter_enable_authorized",
                "timer_state_during_windows_capture_proven",
                "emitter_on_time_limit_proven"):
        need(result[key] is False, "unjustified physical/activation conclusion: " + key)
    need(win_timer["enabled_value"] == "0x80 | floor((requested_ms - 10) / 10)"
         and win_timer["used_by_type0_stream_proven"] is False,
         "Windows static encoding evidence differs")
    requested = 10 + (int(bytes_observed[target[0]], 16) & 0x7f) * 10
    need(requested == 200, "conditional nominal Windows-handler decoding drift")
    verified = {
        "experiment": "E004fx",
        "status": "PASS_SINGLE_GOLDEN_IDLE_TIMER_REGISTER_SNAPSHOT",
        "identity_consumed": True,
        "read_only_values_from_spmi_0_01": bytes_observed,
        "register_timer_enable_bit_set": True,
        "windows_software_handler_conditional_nominal_ms": requested,
        "conditional_decode_only": True,
        "actual_hardware_timer_duration_measured": False,
        "flash_controller_enabled_on_golden": False,
        "physical_ir_led_emission_observed_or_requested": False,
        "windows_streaming_timer_state_known": False,
        "autonomous_stuck_trigger_shutdown_verified": False,
        "safe_irradiance_and_current_verified": False,
        "illumination_authorized": False,
        "golden_postread_pass": True,
        "evidence_sha256": SOURCES,
        "next_gate": (
            "Identify disabled idle module/channel enable and trigger configuration "
            "in a SEPARATE passive experiment; independently measure pulse/current/"
            "optical safety and host-failure cutoff before illuminated capture."
        ),
    }
    (E / "VERIFIED.json").write_text(json.dumps(verified, indent=2) + "\n")
    print("E004FX_RESULT=PASS FOUR_IDLE_TIMER_BYTES=0x93 GOLDEN=PASS")
    print("CONDITIONAL_WINDOWS_ENCODER_MS=200 PHYSICAL_DURATION=UNVERIFIED")
    print("EMITTER_AUTHORIZED=NO HARDWARE_REREAD=NO")

if __name__ == "__main__":
    main()
