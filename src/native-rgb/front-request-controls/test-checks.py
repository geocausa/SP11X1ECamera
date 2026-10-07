# SPDX-License-Identifier: GPL-2.0-only
import runpy,unittest
from pathlib import Path
checks=runpy.run_path(str(Path(__file__).with_name("checks.py")))
class TraceChecks(unittest.TestCase):
 def log(self,first):
  return "\n".join(f"NATIVE_FRONT_OWNER_MATCH group={g} sequence={s}" for s in range(first,first+4) for g in range(5))
 def test_zero_origin(self):self.assertEqual(checks["owner_groups"](self.log(0))["checks"],20)
 def test_one_origin(self):self.assertEqual(checks["owner_groups"](self.log(1))["first"],1)
 def test_missing_group(self):
  with self.assertRaises(ValueError):checks["owner_groups"](self.log(1).replace("group=4","group=7"))
 def test_discontinuity(self):
  with self.assertRaises(ValueError):checks["owner_groups"](self.log(1).replace("sequence=3","sequence=9"))
 def test_default_iommu_not_fault(self):self.assertEqual(checks["critical_signatures"]("iommu: Default domain type: Translated"),[])
 def test_real_faults(self):
  for v in ["IOMMU translation fault at address", "arm-smmu 123: unexpected fault", "BUG: null", "NATIVE_FRONT_OWNER_REJECT"]:
   self.assertEqual(len(checks["critical_signatures"](v)),1)
if __name__=="__main__":unittest.main()
