#!/usr/bin/env python3
"""Strictly camera-free isolated selector instrumentation test."""
import importlib.util
import sys
from pathlib import Path
import stat
import tempfile
import unittest

repo=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(repo/"src/sp11-camera-stack/rgb/service"))
sys.path.insert(0,str(repo/"src/sp11-camera-stack/routing"))
p=Path(__file__).with_name("selector_traced.py")
spec=importlib.util.spec_from_file_location("e004my_traced_selector",p)
selector=importlib.util.module_from_spec(spec)
spec.loader.exec_module(selector)
class SelectorTraceContract(unittest.TestCase):
 def test_no_images_bounded_trace_and_repeat(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/"output").mkdir(mode=0o700)
   selector._trace(root,"selector_command=front phase=before_dispatch")
   selector._trace(root,"selector_command=front phase=failed error=mock")
   t=root/"output/SELECTOR-TRACE.txt"
   self.assertTrue(t.is_file())
   self.assertEqual(stat.S_IMODE(t.stat().st_mode),0o600)
   self.assertEqual(t.read_text().splitlines(),[
      "selector_command=front phase=before_dispatch",
      "selector_command=front phase=failed error=mock"])
   self.assertFalse(any(v in t.read_text().lower() for v in ("pixel", "png", "frame")))
 def test_refuse_symlink_trace_output(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d);(root/"output").mkdir(mode=0o700)
   target=root/"target";target.write_text("protected")
   (root/"output/SELECTOR-TRACE.txt").symlink_to(target)
   with self.assertRaises(OSError):selector._trace(root,"selector_command=front")
   self.assertEqual(target.read_text(),"protected")

if __name__=="__main__":unittest.main()
