#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Exercise the real pinned public archive and fail-closed source verification."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import tempfile
import unittest

spec = importlib.util.spec_from_file_location(
    "reference", Path(__file__).with_name("verify-upstream-ife-reference.py"))
reference = importlib.util.module_from_spec(spec)
spec.loader.exec_module(reference)


class ReferenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temporary = tempfile.TemporaryDirectory(prefix="sp11-ife-verifier-test-")
        cls.archive = Path(cls.temporary.name) / "archive"
        # Check the original before copying it; mutations affect only this copy.
        reference.verify(ARGS.archive, MANIFEST)
        shutil.copytree(ARGS.archive, cls.archive)

    @classmethod
    def tearDownClass(cls):
        cls.temporary.cleanup()

    def setUp(self):
        self.manifest = copy.deepcopy(MANIFEST)

    def test_complete_source_and_replay(self):
        self.assertEqual(reference.verify(self.archive, self.manifest), 369)
        self.assertEqual(reference.replay(self.archive, self.manifest), 325)

    def test_changed_patch_rejected(self):
        path = self.archive / "normalized/patch-74.patch"
        original = path.read_bytes()
        try:
            path.write_bytes(original + b"\n")
            with self.assertRaisesRegex(ValueError, "changed source"):
                reference.verify(self.archive, self.manifest)
        finally:
            path.write_bytes(original)

    def test_missing_patch_rejected(self):
        path = self.archive / "patch-52.patch"
        original = path.read_bytes()
        try:
            path.unlink()
            with self.assertRaisesRegex(ValueError, "missing regular file"):
                reference.verify(self.archive, self.manifest)
        finally:
            path.write_bytes(original)

    def test_symlink_rejected(self):
        path = self.archive / "patch-52.patch"
        original = path.read_bytes()
        try:
            path.unlink()
            path.symlink_to("normalized/patch-52.patch")
            with self.assertRaisesRegex(ValueError, "symlink"):
                reference.verify(self.archive, self.manifest)
        finally:
            path.unlink()
            path.write_bytes(original)

    def test_duplicate_pin_rejected(self):
        self.manifest["files"].append(self.manifest["files"][0])
        with self.assertRaisesRegex(ValueError, "duplicate"):
            reference.verify(self.archive, self.manifest)

    def test_incomplete_series_rejected(self):
        self.manifest["files"] = [x for x in self.manifest["files"]
                                  if x["path"] != "patch-52.patch"]
        with self.assertRaisesRegex(ValueError, "incomplete"):
            reference.verify(self.archive, self.manifest)

    def test_wrong_identity_rejected(self):
        self.manifest["patches"][52]["message_id"] = "different-series"
        with self.assertRaisesRegex(ValueError, "identity"):
            reference.verify(self.archive, self.manifest)

    def test_path_escape_rejected(self):
        self.manifest["files"][0]["path"] = "../outside"
        with self.assertRaisesRegex(ValueError, "archive path"):
            reference.verify(self.archive, self.manifest)

    def test_replay_blob_mismatch_rejected(self):
        path = self.archive / "normalized/patch-74.patch"
        original = path.read_bytes()
        try:
            # A changed expected Git blob must fail even when replay is called
            # directly, without the SHA-256 verification entry point.
            text = original.decode()
            import re
            text, changed = re.subn(r"(?m)^index [0-9a-f]+\.\.",
                                   "index " + "f" * 13 + "..", text, count=1)
            self.assertEqual(changed, 1)
            path.write_text(text)
            with self.assertRaisesRegex(ValueError, "Git blob mismatch"):
                reference.replay(self.archive, self.manifest)
        finally:
            path.write_bytes(original)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--manifest", type=Path, required=True)
    ARGS = parser.parse_args()
    MANIFEST = json.loads(ARGS.manifest.read_text())
    unittest.main(argv=[__file__], verbosity=2)
