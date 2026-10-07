#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import importlib.util
from pathlib import Path
import unittest
spec=importlib.util.spec_from_file_location("analysis",Path(__file__).with_name("analyze.py"))
a=importlib.util.module_from_spec(spec);spec.loader.exec_module(a)
def sample():
    out=[]
    for seq in range(320):
        step=min(seq//16,18)
        delta=0.02 if step%2 else 0
        out.append({"sequence":seq,"channels":[{"phase":ch,"samples":31654,
            "mean":64+ch+delta+((seq%3)-1)*0.0001,"variance":1,
            "zero_fraction":0,"storage_saturation_fraction":0} for ch in range(4)]})
    return out
class Tests(unittest.TestCase):
    def test_small_response_large_pedestal(self):
        r=a.analyze(sample())
        self.assertTrue(all(f["all_four_phases_repeatable"] for f in r["fields"].values()))
        self.assertFalse(r["sensor_application_delay_qualified"])
    def test_variance_response_without_mean_change(self):
        s=sample()
        for f in s:
            step=min(f["sequence"]//16,18)
            for c in f["channels"]:
                c["mean"]=64
                c["variance"]=(2 if step%2 else 1)+((f["sequence"]%3)-1)*0.0001
        self.assertFalse(a.analyze(s)["fields"]["digital_gain"]["all_four_phases_repeatable"])
        r=a.analyze(s,"variance")
        self.assertTrue(all(f["all_four_phases_repeatable"] for f in r["fields"].values()))
        self.assertFalse(r["gain_law_optically_verified"])
        self.assertFalse(r["sensor_application_delay_qualified"])
    def test_variance_no_response(self):
        self.assertFalse(a.analyze(sample(),"variance")["fields"]["analogue_gain"]["all_four_phases_repeatable"])
    def test_variance_drift(self):
        s=sample()
        for f in s:
            for c in f["channels"]:c["variance"]=1+f["sequence"]*0.01
        self.assertFalse(a.analyze(s,"variance")["fields"]["digital_gain"]["all_four_phases_repeatable"])
    def test_no_response(self):
        s=sample()
        for f in s:
            for c in f["channels"]:c["mean"]=64
        self.assertFalse(a.analyze(s)["fields"]["digital_gain"]["all_four_phases_repeatable"])
    def test_drift_is_not_gain(self):
        s=sample()
        for f in s:
            for c in f["channels"]:c["mean"]+=f["sequence"]*0.01
        self.assertFalse(a.analyze(s)["fields"]["analogue_gain"]["all_four_phases_repeatable"])
    def test_phase_specific(self):
        s=sample()
        for f in s:
            f["channels"][2]["mean"]=64
        r=a.analyze(s)["fields"]["digital_gain"]
        self.assertEqual(r["phase_response_repeatable"],[True,True,False,True])
    def test_clipping(self):
        s=sample()
        for f in s:
            for c in f["channels"]:c["storage_saturation_fraction"]=0.01
        self.assertFalse(a.analyze(s)["fields"]["exposure"]["all_four_phases_repeatable"])
    def test_missing_nonfinite_phase(self):
        for variant in range(3):
            s=sample()
            if variant==0:s.pop()
            if variant==1:s[0]["channels"][0]["mean"]=float("nan")
            if variant==2:s[0]["channels"][1]["phase"]=0
            with self.assertRaises(ValueError):a.analyze(s)
if __name__=="__main__":unittest.main()
