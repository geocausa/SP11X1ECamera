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

    def test_isolated_nv12_trial_composition(self):
        with tempfile.TemporaryDirectory(prefix="native-nv12-trial-") as directory:
            out = Path(directory) / "candidate"
            with contextlib.redirect_stdout(io.StringIO()):
                result = build.assemble(out, nv12_trial=True)
            self.assertTrue(result["nv12_trial_staged"])
            self.assertTrue(result["nv12_trial_default_denied"])
            self.assertFalse(result["runtime_access"])
            self.assertFalse(result["nv12_runtime_proven"])
            core = (out / "camss/camss.c").read_text()
            self.assertIn("atomic_cmpxchg(&attempted, 0, 1)", core)
            self.assertIn("native_nv12_commands_validate", core)
            self.assertIn("native_nv12_commands_transform", core)
            self.assertIn("result.live_completed != 4", core)
            vfe = (out / "camss/camss-vfe-680.c").read_text()
            self.assertIn("vfe680_x1e_linear_cold_state(vfe)", vfe)
            self.assertIn("explicit bw_limiter disable", vfe)
            self.assertIn("!addr->linear_nv12 && client == 0", vfe)
            self.assertIn("own->linear_nv12 ? 5529600", vfe)
            self.assertTrue((out / "camss/native-front-nv12-commands.h").exists())
            self.assertFalse(list(out.rglob("*.ko")))

    def test_owner_trial_isolation(self):
        with tempfile.TemporaryDirectory(prefix="native-owner-trial-") as directory:
            out = Path(directory) / "candidate"
            with self.assertRaisesRegex(ValueError, "requires isolated NV12"):
                build.assemble(out, front_owner_trial=True)
            self.assertFalse(out.exists())
            with contextlib.redirect_stdout(io.StringIO()):
                result = build.assemble(out, nv12_trial=True, front_owner_trial=True)
            self.assertTrue(result["front_owner_trial_staged"])
            self.assertFalse(result["runtime_access"])
            self.assertTrue((out / "camss/native-front-owner.h").exists())
            csid = (out / "camss/camss-csid-680.c").read_text()
            self.assertLess(csid.index("csid680_native_front_owner_latch(csid, buf_done_val);"),
                            csid.index("WRITE_ONCE(csid->x1e_buf_done_last, buf_done_val);"))
            vfe = (out / "camss/camss-vfe-680.c").read_text()
            order = __import__("re").search(
                r"vfe680_x1e_windows_bus_client_order\[\] = \{([^}]+)\}", vfe).group(1)
            admitted = [int(x.strip()) for x in order.split(",") if x.strip()]
            mapping = __import__("re").search(
                r"bus_index\[NATIVE_OWNER_WMS\] = \{([^}]+)\}", vfe).group(1)
            logical = [admitted[int(x.strip())] for x in mapping.split(",") if x.strip()]
            self.assertEqual(logical, [0, 1, 2, 3, 11, 12, 13, 14, 18])
            self.assertFalse(list(out.rglob("*.ko")))

    def test_queue_requires_owner_and_nv12(self):
        with tempfile.TemporaryDirectory(prefix="native-queue-trial-") as directory:
            out = Path(directory) / "candidate"
            with self.assertRaisesRegex(ValueError, "requires"):
                build.assemble(out, nv12_trial=True, front_queue_trial=True)
            self.assertFalse(out.exists())
            with contextlib.redirect_stdout(io.StringIO()):
                result = build.assemble(out, nv12_trial=True, front_owner_trial=True,
                                        front_queue_trial=True)
            self.assertTrue(result["front_queue_trial_staged"])
            self.assertFalse(result["runtime_access"])
            core = (out / "camss/camss.c").read_text()
            loop = (out / "camss/native-front-queue.inc").read_text()
            self.assertIn("result->native_queue_started = true", core)
            self.assertIn("NATIVE_FRONT_QUEUE_STOPPED", core)
            self.assertIn("for (frame = 5; ; frame++)", loop)
            self.assertIn("result->native_inflight[slot]", loop)
            self.assertIn("frame > U32_MAX - video_base", loop)
            self.assertFalse(list(out.rglob("*.ko")))

    def test_metadata_requires_queue_and_stays_isolated(self):
        with tempfile.TemporaryDirectory(prefix="native-meta-trial-") as directory:
            out = Path(directory) / "candidate"
            with self.assertRaisesRegex(ValueError, "requires serialized"):
                build.assemble(out, nv12_trial=True, front_owner_trial=True,
                               front_meta_trial=True)
            self.assertFalse(out.exists())
            with contextlib.redirect_stdout(io.StringIO()):
                result = build.assemble(out, nv12_trial=True, front_owner_trial=True,
                                        front_queue_trial=True, front_meta_trial=True)
            self.assertTrue(result["front_meta_trial_staged"])
            self.assertFalse(result["runtime_access"])
            self.assertTrue((out / "camss/native-front-stats.h").exists())
            self.assertFalse(list(out.rglob("*.ko")))

    def test_typed_parameters_require_metadata(self):
        with tempfile.TemporaryDirectory(prefix="native-params-trial-") as directory:
            out = Path(directory) / "candidate"
            with self.assertRaisesRegex(ValueError, "require frame metadata"):
                build.assemble(out, nv12_trial=True, front_owner_trial=True,
                               front_queue_trial=True, front_params_trial=True)
            self.assertFalse(out.exists())
            with contextlib.redirect_stdout(io.StringIO()):
                result = build.assemble(out, nv12_trial=True, front_owner_trial=True,
                                        front_queue_trial=True, front_meta_trial=True,
                                        front_params_trial=True)
            self.assertTrue(result["front_params_trial_staged"])
            self.assertFalse(result["runtime_access"])
            self.assertTrue((out / "camss/native-front-params.h").exists())
            self.assertFalse(list(out.rglob("*.ko")))

    def test_repeatable_composition_and_retained_guards(self):
        with tempfile.TemporaryDirectory(prefix="native-rgb-compose-") as directory:
            a, b = Path(directory) / "a", Path(directory) / "b"
            with contextlib.redirect_stdout(io.StringIO()):
                left, right = build.assemble(a), build.assemble(b)
            self.assertEqual(left["staged_sources"], right["staged_sources"])
            self.assertEqual(left["rear_fragments"], 52)
            self.assertFalse(left["runtime_access"])
            self.assertFalse(left["nv12_trial_staged"])
            self.assertFalse((a / "camss/native-front-nv12-commands.h").exists())
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
