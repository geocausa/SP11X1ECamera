#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Response gates with synthetic illumination, wrong-channel and no-effect cases."""
import copy,runpy,unittest
from pathlib import Path
evaluate=runpy.run_path(str(Path(__file__).with_name("gamma-response.py")))["evaluate"]
def fixture():
    base=[{"green_median":1000+100*j,"Y_median":30+10*j,"U_median":128.0,"V_median":128.0} for j in range(6)]
    streams=[copy.deepcopy(base) for _ in range(5)]
    for index,(dy,du,dv) in enumerate(((5,-2,8),(10,-6,-8),(2,8,-1)),1):
        for p in streams[index]:p["Y_median"]+=dy;p["U_median"]+=du;p["V_median"]+=dv
    return streams
class Response(unittest.TestCase):
    def test_independent_channel_response(self):self.assertTrue(evaluate(fixture())["qualified"])
    def test_no_output_response(self):
        s=fixture();s[1]=copy.deepcopy(s[0]);self.assertFalse(evaluate(s)["qualified"])
    def test_swapped_red_blue(self):
        s=fixture();s[1],s[3]=s[3],s[1];self.assertFalse(evaluate(s)["qualified"])
    def test_raw_scene_shift(self):
        s=fixture()
        for p in s[2]:p["green_median"]*=1.1
        self.assertFalse(evaluate(s)["qualified"])
    def test_baseline_colour_shift(self):
        s=fixture()
        for p in s[4]:p["V_median"]+=10
        self.assertFalse(evaluate(s)["qualified"])
    def test_only_one_plateau(self):
        s=fixture()
        for i in (1,2,3):
            for j in range(1,6):s[i][j]=copy.deepcopy(s[0][j])
        self.assertFalse(evaluate(s)["qualified"])
    def test_small_linear_drift_accepted(self):
        s=fixture()
        for i in range(5):
            for p in s[i]:p["green_median"]*=1+i*0.002;p["Y_median"]+=i*0.05
        self.assertTrue(evaluate(s)["qualified"])
    def test_bad_size(self):
        with self.assertRaises(ValueError):evaluate(fixture()[:4])
    def test_nonfinite(self):
        s=fixture();s[2][0]["Y_median"]=float("nan")
        with self.assertRaises(ValueError):evaluate(s)
unittest.main()
