"""Offline regression for E004md stale-string failure; NEVER starts hardware."""
import importlib.util
import pathlib
import tempfile
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
MOD = ROOT / "tools/camera-validator-contract.py"
spec = importlib.util.spec_from_file_location("camera_validator_contract", MOD)
contract = importlib.util.module_from_spec(spec)
spec.loader.exec_module(contract)
BASE = ROOT / "experiments/E004-front-ir-vd55g0"


class ContractTests(unittest.TestCase):
    def test_historical_e004mc_pair_matches(self):
        stage = BASE / "e004mc-guarded-raw-vs-nv12-rgb-source-probe-one-shot"
        status = contract.verify(stage / "run-once.sh", stage / "paired_source_validator.py")
        self.assertEqual(status, "PASS_BOUNDED_REAL_PAIRED_SOURCE_RAW8_VS_NV12_SCALAR_FRAMES")

    def test_consumed_e004md_mismatch_detected_before_boot(self):
        stage = BASE / "e004md-guarded-rgb-sensor-gain-response-one-shot"
        with self.assertRaisesRegex(ValueError, "STALE_RUNNER_RESULT_CONTRACT"):
            contract.verify(stage / "run-once.sh", stage / "paired_source_validator.py")

    def test_missing_guard_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "run-once.sh"
            p.write_text("echo PASS\n")
            with self.assertRaisesRegex(ValueError, "MISSING_OR_DUPLICATE"):
                contract.required_status(p)

    def test_duplicate_or_ambiguous_validator_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            p = pathlib.Path(d) / "validator.py"
            p.write_text("def validate():\n    if True: return {\"status\": \"PASS_A\"}\n    return {\"status\": \"PASS_B\"}\n")
            with self.assertRaisesRegex(ValueError, "AMBIGUOUS_OR_MISSING"):
                contract.declared_status(p)


if __name__ == "__main__":
    unittest.main()
