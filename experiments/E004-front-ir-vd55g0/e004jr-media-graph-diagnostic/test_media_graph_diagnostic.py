#!/usr/bin/env python3
"""E004jr: archived accepted/missing graph and nonactivation regressions."""
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
SOURCE=HERE/"camera-media-graph-diagnostic.py"
OK=ROOT/"experiments/E004-front-ir-vd55g0/e004ec-side-light-post-g3-shadow-observation/evidence/LOAD-MEDIA.txt"
MISSING=ROOT/"experiments/E004-front-ir-vd55g0/e004ft-live-pattern-hlos/evidence/MEDIA-BEFORE.txt"
spec=importlib.util.spec_from_file_location("e004jr_media",SOURCE)
module=importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class MediaGraph(unittest.TestCase):
    def test_accepted_archived_graph(self):
        p=module.topology_report(OK.read_text(errors="replace"))
        self.assertTrue(p["required_complete"],p)
        self.assertGreaterEqual(p["video_node_count"],2)
        self.assertEqual(p["required_missing"],[])

    def test_archived_missing_camera_sensors(self):
        p=module.topology_report(MISSING.read_text(errors="replace"))
        self.assertFalse(p["required_complete"])
        self.assertIn("ov13858 ",p["required_missing"])
        self.assertIn("imx681 ",p["required_missing"])

    def test_exact_required_entity_mutation(self):
        raw=OK.read_text(errors="replace")
        bad=raw.replace("msm_vfe1_video3","msm_vfe1_videoX")
        p=module.topology_report(bad)
        self.assertFalse(p["required_complete"])
        self.assertIn("msm_vfe1_video3",p["required_missing"])

    def test_bounded_media_names(self):
        self.assertTrue(module.safe_media_name(Path("/dev/media0")))
        self.assertTrue(module.safe_media_name(Path("/dev/media12")))
        for name in ("media", "media0/x", "media-1", "video0", "media0.old"):
            self.assertFalse(module.safe_media_name(Path(name)))

    def test_private_directory_gate_refuses_user_owned(self):
        with tempfile.TemporaryDirectory(prefix="sp11-e004jr-test-") as td:
            with self.assertRaises(PermissionError):
                module.private_dir(Path(td))

    def test_exclusive_output_writes_no_overwrite(self):
        with tempfile.TemporaryDirectory(prefix="sp11-e004jr-write-") as td:
            root=Path(td)
            module.checked_write(root,"DISCOVERY.json","first")
            with self.assertRaises(FileExistsError):
                module.checked_write(root,"DISCOVERY.json","second")
            self.assertEqual((root/"DISCOVERY.json").read_text(),"first")

    def test_offline_cli_exit_verdict(self):
        for fixture,expected in ((OK,0),(MISSING,2)):
            p=subprocess.run(["python3",str(SOURCE),"--from-file",str(fixture)],
                             capture_output=True,text=True,timeout=8)
            self.assertEqual(p.returncode,expected,p.stderr)
            self.assertIn("archived_text_only",p.stdout)

    def test_live_requires_explicit_private_destination(self):
        p=subprocess.run(["python3",str(SOURCE),"--live"],capture_output=True,
                         text=True,timeout=8)
        self.assertEqual(p.returncode,2)
        self.assertIn("--live requires",p.stderr)

    def test_no_stream_or_boot_code(self):
        src=SOURCE.read_text()
        for banned in ("/dev/video90","v4l2-ctl","--stream","modprobe",
                       "insmod","grub-reboot","systemctl reboot","BootNext",
                       "ILLUMINATION_ON"):
            self.assertNotIn(banned,src)
        self.assertIn('["media-ctl","-d",str(m),"-p"]',src)
        self.assertIn("MAX_TOPOLOGY_BYTES = 128 * 1024",src)
        self.assertIn("MAX_SECONDS = 8.0",src)


if __name__=="__main__":
    unittest.main()
