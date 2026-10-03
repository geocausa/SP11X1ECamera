#!/usr/bin/env python3
"""Read-only accepted E011DK evidence/source integrity and scope check."""
from pathlib import Path
import hashlib
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]

def verify():
    result = json.loads((HERE / "RESULT.json").read_text())
    source = json.loads((HERE / "SOURCE-SAFE.json").read_text())
    assert result["experiment"] == source["experiment"] == "E011DK"
    assert result["status"] == source["status"] == "PASS_BOUNDED_ORIGINAL_RS_METADATA_COPY_AND_C_INPUT_DECODER"
    for relative, digest in result["source_locks"].items():
        path = (ROOT / relative).resolve()
        assert path.is_relative_to(ROOT)
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest, relative
    assert source["original_reader_RVA"] == "0x740e70"
    assert source["original_reader_bytes"] == 1792
    assert source["RS_query_slot"] == 5
    assert source["source_property_table_RVA"] == "0x17a30e0"
    assert source["destination_record_offset"] == "0x2c50"
    assert source["metadata_record_bytes"] == 132
    r = source["reader"]
    assert r["cases"] == 96
    assert r["cases_by_record_state"] == dict(present=32, absent=32, fallback=32)
    assert r["original_instruction_visits_including_original_frame_helpers"] == 39904
    for key in ("all132_RS_bytes_exact",
                "entire_owned_heap_unchanged_except_expected_RS_record",
                "source_records_immutable",
                "incoming_SP_and_callee_saved_registers_preserved",
                "stack_redzones_unchanged", "original_executable_bytes_unchanged",
                "API_registry_settings_TLS_lock_objects_are_owned_fixtures",
                "runtime_property_tag_vector_is_an_owned_fixture",
                "upstream_query_helper_registry_publication_AFD_policy_not_executed"):
        assert r[key] is True, key
    assert {x["compiler"] for x in source["compiler_runs"]} == {"gcc", "clang"}
    for c in source["compiler_runs"]:
        assert c["atomic_negative_cases"] == 21
        assert c["observed_source_records_decoded"] == 3
        assert c["input_and_original_RS_output_fields_exact"] == 42
        assert c["ASan_UBSan_stderr_empty"] is True
    assert len(source["observed_fixture_pins"]) == 3
    assert source["initial_RS_origin_reused"] == "E011M"
    assert source["RS_numerical_producer_reused"] == "E011AM"
    for key in ("upstream_AFD_normal_count_policy_closed",
                "metadata_query_helper_or_actual_runtime_registry_qualified",
                "runtime_property_tag_vector_initialization_qualified",
                "complete_deterministic_source_bootstrap_closed",
                "native_rear_runtime_allowed", "new_kernel_build",
                "private_bytes_exported"):
        assert source[key] is False, key
    assert source["new_camera_starts"] == source["new_reboots"] == 0
    assert source["whole_frame_zero_offset_scope_only"] is True
    assert result["latest_factory_enumeration_checkpoint"] == "E011DI"
    assert result["next_experiment"] == "E011DL"
    assert result["qualification_transport"] == "PiMaster SP11 Linux run_script"
    assert result["qualification_exit_code"] == 0
    assert result["independent_enabled_output_retirement_proven"] is False
    print("PASS_E011DK_96_ORIGINAL_RS_COPY_CASES_39904_INSTRUCTIONS_"
          "GCC_CLANG_42_FIELDS_21_ATOMIC_NEGATIVES_UPSTREAM_POLICY_OPEN_RUNTIME_DENIED")

if __name__ == "__main__":
    verify()
