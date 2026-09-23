#!/usr/bin/env python3
"""Only synthetic scalar evidence; fail closed before any native control."""
import copy
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

p=Path(__file__).resolve().parents[1]/"exposure_envelope.py"
spec=importlib.util.spec_from_file_location("offline_exposure_envelope",p)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def synthetic():
    trials={}
    samples={}
    for camera in ("front","rear"):
        bounds={"exposure":{"min":4,"max":16777210 if camera=="front" else 3206,
                             "step":2 if camera=="front" else 1},
                "analogue_gain":{"min":0,"max":960 if camera=="front" else 8191,"step":1},
                "digital_gain":{"min":256 if camera=="front" else 0,
                                "max":3840 if camera=="front" else 16384,"step":1}}
        trials[camera]=dict(camera=camera,
            correct_RGB_subdevice=True,
            driver_supported_v4l2_controls_only=True,
            raw_registers_directly_written=False,
            illumination_or_ir_enabled=False,os_system_sleep_used=False,
            pixel_files_saved=False,
            baseline_controls=m.EXPECTED[camera]["baseline"].copy(),
            modified_controls=m.EXPECTED[camera]["trial"].copy(),
            restored_controls=m.EXPECTED[camera]["baseline"].copy(),
            advertised_sensor_control_bounds=bounds)
        samples[camera]={}
        for stage in ("baseline","gain"):
            low=64 if stage=="baseline" else 73
            high=(70 if camera=="rear" else 112) if stage=="baseline" else (140 if camera=="rear" else 254)
            samples[camera][stage]={c:dict(p01=low,p50=low+1,p95=high-1,p99=high,
                                p99_minus_p01=high-low,p50_minus_p01=1)
                               for c in m.CHANNELS}
    selector={"status":"PASS_REAL_OPT_IN_RGB_SELECTOR_UID1000_FRONT1080_REAR4K",
              "gain_trials":trials}
    scalars={"identity":"E004mp",
             "original_images_or_hashes_exported_or_committed":False,
             "optical_scene_uncontrolled_and_unmatched_windows":True,
             "raw10_same_source_sparse_four_bayer_channels":samples}
    return selector,scalars


class ExposureEnvelopeTests(unittest.TestCase):
    def test_verified_controls_still_do_not_license_an_ae_write(self):
        sel,raw=synthetic()
        d=m.analyze(sel,raw)
        self.assertFalse(d["approved_to_raise_gain_or_exposure"])
        self.assertFalse(d["may_infer_optical_black_from_p01"])
        self.assertFalse(d["approved_to_enable_live_auto_exposure_or_tone_mapping"])
        self.assertEqual(d["cameras"]["rear"]["remaining_exposure_lines_at_same_frame_timing"],6)
        self.assertEqual(d["cameras"]["front"]["remaining_exposure_lines_at_same_frame_timing"],4)
        self.assertEqual(d["cameras"]["rear"]["raw10_channel_quantile_differences"]["G0"]["p01_change"],9)

    def test_rejects_misread_as_different_camera_or_ir(self):
        sel,raw=synthetic()
        sel["gain_trials"]["rear"]["correct_RGB_subdevice"]=False
        with self.assertRaisesRegex(ValueError,"RGB_SOURCE_SAFETY"):m.analyze(sel,raw)
        sel,raw=synthetic()
        sel["gain_trials"]["rear"]["illumination_or_ir_enabled"]=True
        with self.assertRaisesRegex(ValueError,"RGB_SOURCE_SAFETY"):m.analyze(sel,raw)

    def test_no_unproven_timing_expansion(self):
        sel,raw=synthetic()
        sel["gain_trials"]["rear"]["advertised_sensor_control_bounds"]["exposure"]["max"]=65000
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_ACTIVE_FRAME"):m.analyze(sel,raw)
        sel,raw=synthetic()
        sel["gain_trials"]["rear"]["modified_controls"]["exposure"]=3207
        with self.assertRaisesRegex(ValueError,"NATIVE_CONTROL_CHANGE"):m.analyze(sel,raw)

    def test_readback_and_gain_are_exact(self):
        sel,raw=synthetic()
        sel["gain_trials"]["rear"]["restored_controls"]["analogue_gain"]=256
        with self.assertRaisesRegex(ValueError,"NATIVE_CONTROL_CHANGE"):m.analyze(sel,raw)
        sel,raw=synthetic()
        sel["gain_trials"]["rear"]["modified_controls"]["analogue_gain"]=8191
        with self.assertRaisesRegex(ValueError,"NATIVE_CONTROL_CHANGE"):m.analyze(sel,raw)

    def test_quantiles_do_not_become_a_black_reference(self):
        sel,raw=synthetic()
        raw["raw10_same_source_sparse_four_bayer_channels"]["rear"]["gain"]["G0"]["p01"]=73
        raw["raw10_same_source_sparse_four_bayer_channels"]["rear"]["gain"]["G0"]["p99_minus_p01"]=140-64
        with self.assertRaisesRegex(ValueError,"INCONSISTENT_RAW"):m.analyze(sel,raw)
        sel,raw=synthetic()
        raw["raw10_same_source_sparse_four_bayer_channels"]["rear"]["gain"]["G0"]["p99"]=68
        with self.assertRaisesRegex(ValueError,"NONMONOTONIC_FULL10_RAW"):m.analyze(sel,raw)

    def test_incomplete_or_false_privacy_flags_rejected(self):
        sel,raw=synthetic()
        raw["original_images_or_hashes_exported_or_committed"]=True
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_IMAGE_PRIVACY"):m.analyze(sel,raw)
        sel,raw=synthetic()
        raw["identity"]="E004mh"
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_OR_FAILED"):m.analyze(sel,raw)


if __name__=="__main__":
    unittest.main()
