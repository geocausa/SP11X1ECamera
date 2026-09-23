#!/usr/bin/python3
"""Synthetic-only non-optical correlation and alignment regression."""
import unittest
import numpy as np
from repeatability import corr,image_components,shifted_aggregate

class ScalarRepeatability(unittest.TestCase):
    def test_exact_repeatable_fine_pattern(self):
        rs=np.random.default_rng(122)
        arr=rs.normal(100,3,(100,128)).astype(np.float32)
        lo,hi=image_components(arr)
        self.assertLess(abs(corr(hi,hi)-1.),1e-6)
        self.assertLess(abs(corr(lo,lo)-1.),1e-6)
        self.assertEqual(shifted_aggregate(hi,hi)["best_shift_sample_y_x"],[0,0])
    def test_independent_noise_does_not_falsely_claim_repeatability(self):
        x=np.random.default_rng(123).normal(0,1,(128,128)).astype(np.float32)
        y=np.random.default_rng(456).normal(0,1,(128,128)).astype(np.float32)
        self.assertLess(abs(corr(x,y)),.08)
    def test_known_shift_reports_correct_direction(self):
        x=np.random.default_rng(0).normal(0,1,(96,120)).astype(np.float32)
        y=np.roll(x,shift=(1,-2),axis=(0,1))
        d=shifted_aggregate(x,y)
        self.assertEqual(d["best_shift_sample_y_x"],[1,-2])
        self.assertGreater(d["best_correlation_within_plusminus_eight_original_pixels"],.999)
    def test_flat_arrays_no_invented_correlation(self):
        arr=np.ones((64,64),dtype=np.float32)
        self.assertIsNone(corr(arr,arr))
        self.assertIsNone(shifted_aggregate(arr,arr)["same_position_correlation"])
    def test_invalid_dimensions_fail(self):
        with self.assertRaises(ValueError):corr(np.zeros((3,4)),np.zeros((3,5)))
        with self.assertRaises(ValueError):image_components(np.zeros((4,4)))
        with self.assertRaises(ValueError):shifted_aggregate(np.zeros((4,32)),np.zeros((4,32)))

if __name__=="__main__":unittest.main()
