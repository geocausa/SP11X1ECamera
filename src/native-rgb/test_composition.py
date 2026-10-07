#!/usr/bin/env python3
"""Check native source admission and repeatable composition without device access."""
import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("native_build", HERE / "build.py")
build = importlib.util.module_from_spec(spec)
spec.loader.exec_module(build)

class CompositionTests(unittest.TestCase):
    def test_changed_input_rejected(self):
        with self.assertRaisesRegex(ValueError, "digest changed"):
            build.checked_source("src/front-imx681/kernel/camss/camss.c", "0" * 64)

    def test_external_input_rejected(self):
        with self.assertRaisesRegex(ValueError, "outside checkout"):
            build.checked_source("../not-a-project-source.c", "0" * 64)

    def test_repeatable_composition_and_retained_guards(self):
        with tempfile.TemporaryDirectory(prefix="native-rgb-compose-") as directory:
            a, b = Path(directory) / "a", Path(directory) / "b"
            with contextlib.redirect_stdout(io.StringIO()):
                left, right = build.assemble(a), build.assemble(b)
            self.assertEqual(left["staged_sources"], right["staged_sources"])
            self.assertEqual(left["rear_fragments"], 52)
            self.assertFalse(left["runtime_access"])
            self.assertTrue(left["overlay_audit"]["v4l2_nv12_streaming_still_forbidden"])
            core = (a / "camss/camss.c").read_text()
            self.assertIn("for_each_sgtable_dma_sg(sgt, sg, i)", core)
            self.assertIn("sg_dma_address(sg) != cursor", core)
            self.assertIn("e005y_vfe1_owner_init", core)
            runner = (a / "camss/camss-vfe-e008k-rear-runner.inc").read_text()
            self.assertIn("e011i_rear_reclaim_after_stop", runner)
            vfe = (a / "camss/camss-vfe-680.c").read_text()
            self.assertIn('#include "camss-e011z-rear-startup-adaptive-bind.inc"', vfe)
            bf = (a / "camss/camss-vfe-e008t-rear-bf-semantic.inc").read_text()
            self.assertNotIn("struct e008o_rear_bootstrap", bf)
            self.assertNotIn("struct e008o_rear_packet_state", bf)
            self.assertIn("if (!s || s->sealed)", bf)
            self.assertIn("p->regs.scalar.request_id != p->request_id", bf)
            gate = (a / "camss/camss-vfe-e008o-rear-semantic-state.inc").read_text()
            self.assertIn("return -EOPNOTSUPP;", gate)
            self.assertFalse(list(a.rglob("*.ko")))
            before = (a / "source-manifest.json").read_bytes()
            with self.assertRaises(FileExistsError):
                build.assemble(a)
            self.assertEqual(before, (a / "source-manifest.json").read_bytes())

if __name__ == "__main__":
    unittest.main(verbosity=2)
