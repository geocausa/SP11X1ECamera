#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import runpy
import unittest
from pathlib import Path
analyze = runpy.run_path(str(Path(__file__).with_name("analyze.py")))["analyze"]


def fixture(delays=(2,1,3)):
    commands = [{"step":step,"sof":step*16} for step in range(1,19)]
    values = [0.5]*324
    for command in commands:
        start = command["sof"]+delays[(command["step"]-1)//6]
        values[start:] = [1.0 if command["step"]%2 else 0.5]*(324-start)
    return values,[10+(x-0.5)*12 for x in values[4:]],commands


class ResponseAnalysis(unittest.TestCase):
    def test_each_field_measures_its_own_delay(self):
        x,y,c = fixture()
        result = analyze(x,y,c,True)
        self.assertTrue(result["all_fields_response_timing_qualified"])
        self.assertEqual([f["observed_response_delay_frames"] for f in result["fields"]],[2,1,3])
        self.assertFalse(result["DelayedControls_parameters_qualified"])
        self.assertFalse(result["optical_quality_parity_proven"])

    def test_no_response_remains_unqualified(self):
        x,y,c = fixture()
        result = analyze([0.5]*324,[10.0]*320,c,True)
        self.assertFalse(result["all_fields_response_timing_qualified"])

    def test_restored_baseline_drift_is_rejected(self):
        x,y,c = fixture()
        for n in range(38,47):
            x[n] *= 1.3
        result = analyze(x,y,c,True)
        self.assertFalse(result["fields"][0]["response_timing_qualified"])
        self.assertIn("baseline changed across restored cycle",result["fields"][0]["reasons"])

    def test_gradual_transition_is_not_an_applied_frame(self):
        x,y,c = fixture()
        x[18:22] = [0.6,0.7,0.8,0.9]
        y = [10+(v-0.5)*12 for v in x[4:]]
        result = analyze(x,y,c,True)
        self.assertFalse(result["fields"][0]["response_timing_qualified"])

    def test_output_must_corroborate_statistics(self):
        x,y,c = fixture()
        result = analyze(x,[10.0]*320,c,True)
        self.assertFalse(result["all_fields_response_timing_qualified"])

    def test_association_change_blocks_all_fields(self):
        x,y,c = fixture()
        result = analyze(x,y,c,False)
        self.assertTrue(all(not f["response_timing_qualified"] for f in result["fields"]))

    def test_nonfinite_or_incomplete_samples_are_rejected(self):
        x,y,c = fixture()
        x[12] = float("nan")
        with self.assertRaises(ValueError):
            analyze(x,y,c,True)
        with self.assertRaises(ValueError):
            analyze([0.5]*323,y,c,True)


if __name__ == "__main__":
    unittest.main()
