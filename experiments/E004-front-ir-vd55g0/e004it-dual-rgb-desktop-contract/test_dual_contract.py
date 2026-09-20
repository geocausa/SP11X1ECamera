#!/usr/bin/env python3
"""E004it: fail-closed FRONT+REAR ordinary desktop readiness contract tests."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
STATUS=ROOT/"tools/camera-desktop-status.py"
CONTRACT=ROOT/"src/sp11-camera-stack/rgb-desktop-output-contract.json"
SPEC=importlib.util.spec_from_file_location("sp11_dual_rgb_status",STATUS)
MOD=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MOD)

class DualRGBTests(unittest.TestCase):
    def test_both_source_profiles_faithful(self):
        c=MOD.load_rgb_contract()
        self.assertEqual(c["rear"]["sensor"],"OV13858")
        self.assertEqual(c["rear"]["capture_frame_bytes"],14321824)
        self.assertEqual(c["rear"]["accepted_v4l2_fourcc"],"pgAA")
        self.assertEqual(c["front"]["sensor"],"IMX681")
        self.assertEqual(c["front"]["capture_frame_bytes"],7778304)
        self.assertEqual(c["front"]["accepted_v4l2_fourcc"],"Q10C")
        self.assertFalse(c["front"]["may_treat_qc10c_as_linear_nv12"])
        self.assertEqual(c["common_desktop_target"]["frame_bytes"],3110400)

    def test_json_status_both_camera_endpoints_unverified(self):
        cp=subprocess.run([sys.executable,str(STATUS),"--json"],
                          capture_output=True,text=True,timeout=35)
        self.assertEqual(cp.returncode,0,cp.stderr[-450:])
        data=json.loads(cp.stdout)
        self.assertFalse(data["activation_performed"])
        self.assertFalse(data["camera_opened"])
        self.assertEqual(set(data["rgb_cameras"]),{"rear","front"})
        self.assertEqual(data["rgb_cameras"]["rear"]["offline_real_colorbar_to_nv12"],
                         "PASS_UNCALIBRATED_PROTOTYPE")
        self.assertEqual(data["rgb_cameras"]["front"]["real_linear_nv12_or_qc10c_decode"],
                         "NOT_VERIFIED")
        self.assertEqual(data["rgb_cameras"]["front"]["live_desktop_device"],
                         "NOT_VERIFIED")
        self.assertEqual(data["rgb_cameras"]["rear"]["live_desktop_device"],
                         "NOT_VERIFIED")
        self.assertEqual(data["rear_front_live_app_switching"],"NOT_VERIFIED")
        self.assertEqual(data["application_capture"],"NOT_TESTED")

    def test_human_readable_names_both_not_available(self):
        cp=subprocess.run([sys.executable,str(STATUS)],
                          capture_output=True,text=True,timeout=35)
        self.assertEqual(cp.returncode,0,cp.stderr[-450:])
        self.assertIn("Rear RGB (OV13858)",cp.stdout)
        self.assertIn("Front RGB (IMX681)",cp.stdout)
        self.assertIn("Front/rear app switching: NOT_VERIFIED",cp.stdout)

    def reject_mutated_contract(self,callback):
        with tempfile.TemporaryDirectory(prefix="sp11-e004it-fixture-") as root:
            f=Path(root)/"contract.json"
            c=json.loads(CONTRACT.read_text())
            callback(c)
            f.write_text(json.dumps(c))
            with mock.patch.object(MOD,"DUAL_RGB_CONTRACT",f):
                with self.assertRaises(ValueError):
                    MOD.load_rgb_contract()

    def test_reject_rear_wrong_bayer_geometry(self):
        self.reject_mutated_contract(lambda x: x["rear"].update(capture_stride_bytes=5095))

    def test_reject_rear_unverified_bridge_claim(self):
        self.reject_mutated_contract(lambda x: x["rear"].update(offline_previous_real_colorbar_to_nv12=False))

    def test_reject_front_wrong_format(self):
        self.reject_mutated_contract(lambda x: x["front"].update(accepted_v4l2_fourcc="NV12"))

    def test_reject_qc10c_being_treated_as_linear_nv12(self):
        self.reject_mutated_contract(lambda x: x["front"].update(may_treat_qc10c_as_linear_nv12=True))

    def test_reject_qc10c_being_treated_as_bayer(self):
        self.reject_mutated_contract(lambda x: x["front"].update(may_treat_qc10c_as_bayer=True))

    def test_reject_unsupported_rear_app_endpoint(self):
        self.reject_mutated_contract(lambda x: x["rear"].update(device_advertisable_to_applications=True))

    def test_reject_unsupported_front_app_endpoint(self):
        self.reject_mutated_contract(lambda x: x["front"].update(live_desktop_nv12_device_verified=True))

    def test_reject_unproven_dual_camera_switching(self):
        self.reject_mutated_contract(lambda x: x["common_desktop_target"].update(selectable_front_rear_live_devices=True))

    def test_reject_wrong_desktop_output_size(self):
        self.reject_mutated_contract(lambda x: x["common_desktop_target"].update(frame_bytes=7778304))

    def test_reject_premature_default_install(self):
        self.reject_mutated_contract(lambda x: x.update(default_install_authorized=True))

    def test_reject_drifted_historical_rear_evidence(self):
        with tempfile.TemporaryDirectory(prefix="sp11-e004it-evidence-") as root:
            f=Path(root)/"evidence.json"
            proof=json.loads(MOD.REAR_BRIDGE_EVIDENCE.read_text())
            proof["source_sha256"]="0"*64
            f.write_text(json.dumps(proof))
            with mock.patch.object(MOD,"REAR_BRIDGE_EVIDENCE",f):
                with self.assertRaises(ValueError):
                    MOD.load_rgb_contract()

if __name__=="__main__": unittest.main(verbosity=2)
