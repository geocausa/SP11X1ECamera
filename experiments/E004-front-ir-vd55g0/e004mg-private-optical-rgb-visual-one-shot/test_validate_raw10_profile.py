#!/usr/bin/env python3
"""Pure synthetic, no-camera input tests of new full10 scalar acceptance."""
import tempfile
from pathlib import Path
import unittest
from validate_raw10_profile import BLOCKS,CHANNELS,FRAMES,validate

def text(camera,blocks,frame):
    tokens=[f"SP11_RGB_RAW10_PROFILE camera={camera}",f"frame={frame}",f"blocks={blocks}"]
    for k,c in enumerate(CHANNELS):
        v=17+4*k
        tokens.extend(f"{c}_{metric}={v}" for metric in ("p01","p50","p95","p99","min","max"))
        tokens.extend(f"{c}_lsb{bit}={blocks if bit==v%4 else 0}" for bit in range(4))
    return " ".join(tokens)

class Validator(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="sp11-e004mg-profile-offline-")
        self.d=Path(self.tmp.name)
        for c,blocks in BLOCKS.items():
            (self.d/(c+"-SERVICE-STDERR.txt")).write_text(
                "\n".join(text(c,blocks,f) for f in FRAMES)+"\n")
    def tearDown(self):self.tmp.cleanup()
    def test_strict_exact_native_profile(self):
        result=validate(self.d)
        self.assertEqual(result["status"],
            "PASS_SIX_SPARSE_SAME_SOURCE_FULL10_RAW_BAYER_CHANNEL_PROFILES_FRONT_REAR")
        self.assertFalse(result["recognizable_scene_or_colour_accuracy_proven"])
    def test_missing_source_frame_refused(self):
        p=self.d/"rear-SERVICE-STDERR.txt"
        p.write_text("\n".join(p.read_text().splitlines()[:-1])+"\n")
        with self.assertRaises(ValueError):validate(self.d)
    def test_wrong_bayer_blocks_refused(self):
        p=self.d/"front-SERVICE-STDERR.txt"
        p.write_text(p.read_text().replace("blocks=8160","blocks=8159",1))
        with self.assertRaises(ValueError):validate(self.d)
    def test_invalid_low_bits_refused(self):
        p=self.d/"rear-SERVICE-STDERR.txt"
        p.write_text(p.read_text().replace("R_lsb0=0","R_lsb0=3",1))
        with self.assertRaises(ValueError):validate(self.d)
    def test_reordered_quantiles_refused(self):
        p=self.d/"front-SERVICE-STDERR.txt"
        p.write_text(p.read_text().replace("R_p01=17","R_p01=190",1))
        with self.assertRaises(ValueError):validate(self.d)

if __name__=="__main__":unittest.main()
