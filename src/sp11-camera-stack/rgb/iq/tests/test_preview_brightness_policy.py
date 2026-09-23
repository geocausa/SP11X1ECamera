#!/usr/bin/env python3
"""Camera-free hypothetical RGB observations only; no sensor/image I/O."""
import importlib.util
import unittest
from dataclasses import replace
from pathlib import Path

src=Path(__file__).resolve().parents[1]/"preview_brightness_policy.py"
spec=importlib.util.spec_from_file_location("preview_brightness_policy",src)
m=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=m
spec.loader.exec_module(m)


def make(camera="rear", seq=1,controls=None,p01=30,p50=35,p99=55,
         fps=30.,mono=None,**changes):
    if controls is None:controls=m.PROFILES[camera]["baseline"]
    if mono is None:mono=1000.+(seq-1)*33.333
    kw=dict(camera=camera,native_controls=controls,sequence=seq,
        monotonic_ms=mono,p01_y=p01,p50_y=p50,p99_y=p99,
        fraction_y_ge235=0.,native_source_fps=fps,
        source_sequence_gaps=0,neutral_IR_off=True,
        native_frame_timing_unchanged=True,
        native_sensor_bounds_readback_verified=True,
        exclusive_RGB_route_owner=True,ordinary_visible_app_uid=1000)
    kw.update(changes)
    return m.ScalarObservation(**kw)


def baseline_planner(cam="rear", p01=30,p50=35,p99=55):
    a=m.BrightnessPlanner(cam)
    for seq in range(1,31):
        result=a.observe(make(cam,seq,p01=p01,p50=p50,p99=p99))
    assert result.action=="TRIAL_ELIGIBLE"
    assert not result.eligible_for_live_control_write
    return a


class BrightnessSafety(unittest.TestCase):
    def test_rear_exact_native_trial_converges_without_using_untrusted_black(self):
        a=baseline_planner()
        gain=m.PROFILES["rear"]["trial"]
        for seq in range(31,61):
            p=a.observe(make(seq=seq,controls=gain,p01=125,p50=143,p99=161))
        self.assertEqual(p.action,"HOLD")
        self.assertIn("NO_PROOF_OF_SCENE_DETAIL",p.reason)
        self.assertFalse(p.eligible_for_live_control_write)
        self.assertFalse(p.optical_black_calibrated)
        self.assertEqual(a.baseline_p50,35)

    def test_front_trial_still_too_dark_revert_not_raise_more_gain(self):
        a=baseline_planner("front",30,35,37)
        for seq in range(31,61):
            p=a.observe(make("front",seq,controls=m.PROFILES["front"]["trial"],
                             p01=30,p50=34,p99=61))
        self.assertEqual(p.action,"REVERT_ELIGIBLE")
        self.assertEqual(p.control_profile,"baseline")
        self.assertFalse(p.eligible_for_live_control_write)

    def test_flat_or_occluded_rear_trial_does_not_force_brightness(self):
        a=baseline_planner("rear",18,19,20)
        for seq in range(31,61):
            p=a.observe(make(seq=seq,controls=m.PROFILES["rear"]["trial"],
                            p01=22,p50=24,p99=27))
        self.assertEqual(p.action,"REVERT_ELIGIBLE")
        self.assertIn("TRIAL_STILL_DARK_FLAT",p.reason)

    def test_bright_baseline_or_clipped_never_probes(self):
        for vals in (dict(p01=65,p50=100,p99=150),
                     dict(p01=20,p50=35,p99=230),
                     dict(p01=20,p50=35,p99=50,fraction_y_ge235=0.002)):
            a=m.BrightnessPlanner("rear")
            for i in range(1,65):
                p=a.observe(make(seq=i,**vals))
            self.assertEqual(p.action,"HOLD")
            self.assertFalse(a.probed_this_session)

    def test_trial_overexposure_reverts_immediately(self):
        a=baseline_planner()
        p=a.observe(make(seq=31,controls=m.PROFILES["rear"]["trial"],
                         p01=100,p50=155,p99=230))
        self.assertEqual(p.action,"REVERT_ELIGIBLE")

    def test_revert_readback_must_match_baseline_and_no_new_probe(self):
        a=baseline_planner()
        for i in range(31,61):
            a.observe(make(seq=i,controls=m.PROFILES["rear"]["trial"],
                           p01=125,p50=143,p99=161))
        p=a.observe(make(seq=61,controls=m.PROFILES["rear"]["baseline"]))
        self.assertEqual(p.action,"HOLD")
        self.assertIn("ALREADY_TRIED",p.reason)
        for i in range(62,90):
            p=a.observe(make(seq=i,controls=m.PROFILES["rear"]["baseline"]))
        self.assertEqual(p.action,"HOLD")

    def test_stable_window_cannot_be_accumulated_from_bright_and_dark(self):
        a=m.BrightnessPlanner("rear")
        for i in range(1,18):
            a.observe(make(seq=i))
        a.observe(make(seq=18,p01=75,p50=115,p99=195))
        for i in range(19,47):
            p=a.observe(make(seq=i))
        self.assertEqual(p.action,"HOLD")
        self.assertFalse(a.probed_this_session)
        self.assertEqual(a.observe(make(seq=47)).action,"HOLD")
        self.assertEqual(a.observe(make(seq=48)).action,"TRIAL_ELIGIBLE")

    def test_fps_below_29_is_safety_block_even_when_brightness_good(self):
        a=baseline_planner()
        p=a.observe(make(seq=31,controls=m.PROFILES["rear"]["trial"],
                         fps=28.85,p01=125,p50=143,p99=161))
        self.assertEqual(p.action,"BLOCKED")
        self.assertEqual(a.observe(make(seq=32)).action,"BLOCKED")

    def test_fail_closed_native_sensor_exposure_bounds_ir_and_uid(self):
        invalid=(dict(native_controls=(4000,512,2048)),
                 dict(native_controls=(3200,512,2049)),
                 dict(neutral_IR_off=False),
                 dict(native_frame_timing_unchanged=False),
                 dict(native_sensor_bounds_readback_verified=False),
                 dict(exclusive_RGB_route_owner=False),
                 dict(ordinary_visible_app_uid=0),
                 dict(source_sequence_gaps=1),
                 dict(p01_y=0),
                 dict(fraction_y_ge235=float("nan")),
                 dict(native_source_fps=29.0-0.001),
                 dict(native_source_fps=float("nan")),
                 dict(native_source_fps=None),
                 dict(native_controls=None),
                 dict(fraction_y_ge235=None))
        for values in invalid:
            a=m.BrightnessPlanner("rear")
            self.assertEqual(a.observe(make(**values)).action,"BLOCKED",values)
            self.assertEqual(a.observe(make(seq=2)).action,"BLOCKED",values)

    def test_nonmonotonic_or_gap_source_blocks_after_first_frame(self):
        for bad in (make(seq=3),make(seq=2,mono=1000.0),
                    make(seq=2,mono=1200.),
                    make(seq=2,mono=-1.)):
            a=m.BrightnessPlanner("rear")
            self.assertEqual(a.observe(make(seq=1)).action,"HOLD")
            self.assertEqual(a.observe(bad).action,"BLOCKED")

    def test_uncommanded_trial_and_unrecognized_camera(self):
        a=m.BrightnessPlanner("rear")
        self.assertEqual(a.observe(make(controls=m.PROFILES["rear"]["trial"])).action,"BLOCKED")
        with self.assertRaisesRegex(ValueError,"ONLY_FRONT_REAR_RGB"):
            m.BrightnessPlanner("ir")
        a=m.BrightnessPlanner("rear")
        self.assertEqual(a.observe(make(camera="front")).action,"BLOCKED")


if __name__=="__main__":
    unittest.main()
