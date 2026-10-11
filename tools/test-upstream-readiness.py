#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location("gate", Path(__file__).with_name("check-upstream-readiness.py"))
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class GateTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.addCleanup(self.temp.cleanup)
        (self.root / "source.c").write_text("/* owned synthetic test source */\n")
        pin = hashlib.sha256((self.root / "source.c").read_bytes()).hexdigest()
        items = []
        for name in sorted(gate.REQUIRED):
            f = name + ".json"
            (self.root / f).write_text(json.dumps({"component": name, "result": "PASS",
                "hardware_qualified": True, "validation_scope": "synthetic gate fixture only",
                "source_sha256": {"source.c": pin}}))
            items.append({"id": name, "status": "ready", "provenance": "project-mathematics",
                "provenance_reviewed": True, "license_reviewed": True,
                "private_runtime_dependencies": [], "sources": ["source.c"], "evidence": f,
                "hardware_required": True})
        self.doc = {"version": 1, "components": items}

    def test_valid_synthetic_gate(self):
        self.assertEqual(gate.audit(self.doc, self.root), [])

    def test_empty_manifest_cannot_pass(self):
        self.assertTrue(gate.audit({"version": 1, "components": []}, self.root))

    def test_malformed_identifier_and_version(self):
        self.doc["components"][0]["id"] = []
        self.assertTrue(gate.audit(self.doc, self.root))
        self.doc["version"] = True
        self.assertTrue(gate.audit(self.doc, self.root))

    def test_missing_component(self):
        self.doc["components"].pop()
        self.assertTrue(gate.audit(self.doc, self.root))

    def test_duplicate_component(self):
        self.doc["components"].append(copy.deepcopy(self.doc["components"][0]))
        self.assertTrue(gate.audit(self.doc, self.root))

    def test_private_runtime_dependency(self):
        self.doc["components"][0]["private_runtime_dependencies"] = ["private-input"]
        self.assertTrue(gate.audit(self.doc, self.root))

    def test_unreviewed_trace_or_license(self):
        for field in ["provenance_reviewed", "license_reviewed"]:
            d = copy.deepcopy(self.doc)
            d["components"][0][field] = False
            self.assertTrue(gate.audit(d, self.root))

    def test_unknown_provenance(self):
        self.doc["components"][0]["provenance"] = "private"
        self.assertTrue(gate.audit(self.doc, self.root))

    def test_paths_and_symlinks_rejected(self):
        (self.root / "alias").symlink_to(self.root / "source.c")
        for path in ["../source.c", "/etc/passwd", "alias"]:
            with self.assertRaises(ValueError):
                gate.local_file(self.root, path)

    def test_changed_source_invalidates_evidence(self):
        (self.root / "source.c").write_text("changed after test")
        self.assertTrue(gate.audit(self.doc, self.root))

    def test_no_hardware_evidence(self):
        item = self.doc["components"][0]
        f = self.root / item["evidence"]
        data = json.loads(f.read_text())
        data["hardware_qualified"] = False
        f.write_text(json.dumps(data))
        self.assertTrue(gate.audit(self.doc, self.root))

    def test_hardware_opt_out_cannot_bypass_camera_qualification(self):
        item = next(i for i in self.doc["components"] if i["id"] == "front-startup")
        item["hardware_required"] = False
        f = self.root / item["evidence"]
        data = json.loads(f.read_text())
        data["hardware_qualified"] = False
        f.write_text(json.dumps(data))
        problems = gate.audit(self.doc, self.root)
        self.assertTrue(any("cannot be disabled" in p for p in problems))
        self.assertTrue(any("hardware qualification missing" in p for p in problems))

    def test_submission_documentation_can_have_source_only_evidence(self):
        item = next(i for i in self.doc["components"] if i["id"] == "submission-export")
        item["hardware_required"] = False
        f = self.root / item["evidence"]
        data = json.loads(f.read_text())
        data["hardware_qualified"] = False
        f.write_text(json.dumps(data))
        self.assertEqual(gate.audit(self.doc, self.root), [])

    def test_missing_evidence(self):
        self.doc["components"][0]["evidence"] = "missing.json"
        self.assertTrue(gate.audit(self.doc, self.root))

    def test_wrong_component_evidence(self):
        self.doc["components"][0]["evidence"] = self.doc["components"][1]["evidence"]
        self.assertTrue(gate.audit(self.doc, self.root))


if __name__ == "__main__":
    unittest.main(verbosity=2)
