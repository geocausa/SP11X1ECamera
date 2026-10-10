#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import runpy,unittest
from pathlib import Path
check=runpy.run_path(str(Path(__file__).with_name("gamma-response.py")))["cci_sequence_matches"]
def rows(begin):return [(n,) for n in range(begin,begin+6)]
class Counter(unittest.TestCase):
 def test_initial(self):self.assertTrue(check(rows(0),rows(0),0))
 def test_second(self):self.assertTrue(check(rows(6),rows(6),1))
 def test_third(self):self.assertTrue(check(rows(12),rows(12),2))
 def test_unexpected_reset(self):self.assertFalse(check(rows(0),rows(0),1))
 def test_gap(self):self.assertFalse(check(rows(6)[:-1]+[(12,)],rows(6),1))
 def test_readback_wrong_identity(self):self.assertFalse(check(rows(6),rows(7),1))
unittest.main()
