#!/usr/bin/python3
"""Camera-free preview format, privacy and no-clobber tests."""
import importlib.util
from pathlib import Path
import stat
import tempfile
import unittest
p=Path(__file__).with_name("private_optical_preview.py")
spec=importlib.util.spec_from_file_location("local_rgb_preview",p)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
class PreviewTests(unittest.TestCase):
    def test_private_png_no_clobber(self):
        with tempfile.TemporaryDirectory() as d:
            photo=Path(d)/"synthetic.png"
            result=module.save_rgb_png(bytes([75,105,135])*(1920*1080),1920,1080,photo)
            self.assertEqual(result["mode_octal"],"0600")
            self.assertEqual(stat.S_IMODE(photo.stat().st_mode),0o600)
            self.assertEqual(photo.read_bytes()[:8],b"\x89PNG\r\n\x1a\n")
            with self.assertRaises(FileExistsError):
                module.save_rgb_png(bytes([50,60,70])*(1920*1080),1920,1080,photo)
    def test_unexpected_dimensions_refused(self):
        with tempfile.TemporaryDirectory() as d:
            bad=Path(d)/"bad.png"
            with self.assertRaises(ValueError):
                module.save_rgb_png(b"\0"*100,1920,1080,bad)
            self.assertFalse(bad.exists())
    def test_default_rejects_live_outside_candidate(self):
        with self.assertRaises(RuntimeError):
            module.run("front")
        with self.assertRaises(RuntimeError):
            module.run("ir")
        with self.assertRaises(RuntimeError):
            module.run("front", "unknown-stage")
if __name__=="__main__":unittest.main()
