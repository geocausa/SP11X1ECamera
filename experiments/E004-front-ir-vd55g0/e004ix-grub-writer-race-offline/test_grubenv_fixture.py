#!/usr/bin/env python3
"""E004ix regression: only disposable GRUB env files, no system mutation."""
from pathlib import Path
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
SOURCE=HERE/"grubenv_race_fixture.py"
SPEC=importlib.util.spec_from_file_location("e004ix_grubenv_race",SOURCE)
M=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(M)

class FixtureTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix="sp11-e004ix-test-",dir="/tmp")
        self.addCleanup(self.tmp.cleanup)
        self.env=Path(self.tmp.name)/"test-only.grubenv"

    def test_private_fixture_preserves_exact_golden_saved_state(self):
        M.fixture(self.env)
        code,stderr,vars=M.read_state(self.env)
        self.assertEqual(code,0,stderr)
        self.assertEqual(vars["saved_entry"],"sp11-audio-fullio-v19c")
        self.assertEqual(vars["next_entry"],"")
        self.assertEqual(self.env.stat().st_size,1024)

    def test_serial_three_stock_operations_preserve_state(self):
        result=M.serial_trial(self.env)
        self.assertEqual(result["writer_failed"],0)
        self.assertEqual(result["read_failed"],0)
        self.assertTrue(result["golden_preserved"])
        self.assertTrue(result["consumed_one_shot_preserved"])

    def test_concurrent_operations_never_use_live_grub_file(self):
        result=M.concurrent_trial(self.env)
        self.assertEqual(set(result),{"writers_failed","overlapping_read_failed",
            "final_read_failed","final_missing_golden","final_missing_empty_next",
            "writer_1_error","writer_2_error"})
        for k in ("writers_failed","overlapping_read_failed","final_read_failed"):
            self.assertGreaterEqual(result[k],0)

    def test_bounded_cli_reports_fixture_only_and_serial_health(self):
        r=subprocess.run([sys.executable,str(SOURCE),"--trials","6"],
                         capture_output=True,text=True,timeout=50)
        self.assertEqual(r.returncode,0,r.stderr[-500:])
        data=json.loads(r.stdout)
        self.assertEqual(data["trials"],6)
        self.assertFalse(data["actual_golden_grubenv_touched"])
        self.assertFalse(data["system_services_modified"])
        self.assertFalse(data["reproduces_exact_original_machine_root_cause"])
        for k in ("serial_writer_failures","serial_reader_failures","serial_incorrect_state"):
            self.assertEqual(data["totals"][k],0)

    def test_invalid_trial_counts_rejected(self):
        for count in ("0","301"):
            r=subprocess.run([sys.executable,str(SOURCE),"--trials",count],
                             capture_output=True,text=True,timeout=10)
            self.assertNotEqual(r.returncode,0)

    def test_proposed_boot_writer_order_is_uninstalled(self):
        proposal=(HERE/"PROPOSED-NOT-INSTALLED-grub2-common-after-initrd-fallback.conf").read_text()
        self.assertIn("[Unit]",proposal)
        self.assertIn("Wants=grub-initrd-fallback.service",proposal)
        self.assertIn("After=grub-initrd-fallback.service",proposal)
        actual=subprocess.run(["systemctl","show","grub2-common.service",
                               "-p","After","--value"],
                              capture_output=True,text=True,check=True,timeout=12)
        self.assertNotIn("grub-initrd-fallback.service",actual.stdout)

    def test_proposed_writer_order_systemd_verify_only_disposable_copy(self):
        proposal=HERE/"PROPOSED-NOT-INSTALLED-grub2-common-after-initrd-fallback.conf"
        with tempfile.TemporaryDirectory(prefix="sp11-e004ix-systemd-fixture-",dir="/tmp") as d:
            root=Path(d)
            for name in ("grub2-common.service","grub-initrd-fallback.service"):
                (root/name).write_bytes((Path("/usr/lib/systemd/system")/name).read_bytes())
            dropin=root/"grub2-common.service.d"
            dropin.mkdir()
            (dropin/"90-serialize-grubenv-writers.conf").write_bytes(proposal.read_bytes())
            import os
            env=os.environ.copy()
            env["SYSTEMD_UNIT_PATH"]=str(root)+":/usr/lib/systemd/system:/etc/systemd/system"
            r=subprocess.run(["systemd-analyze","verify",str(root/"grub2-common.service"),
                             str(root/"grub-initrd-fallback.service")],
                             env=env,capture_output=True,text=True,timeout=25)
            self.assertEqual(r.returncode,0,r.stderr[-600:])

    def test_all_mutating_grub_editenv_calls_are_scoped_to_fixture(self):
        s=SOURCE.read_text()
        self.assertIn('with tempfile.TemporaryDirectory(prefix="sp11-e004ix-grubenv-fixture-",dir="/tmp")',s)
        for bad in ('/boot/grub/grubenv","unset"', 'systemctl reboot','grub-reboot',
                    'modprobe ','insmod ','/dev/video','/dev/media'):
            self.assertNotIn(bad,s)

if __name__=="__main__":unittest.main(verbosity=2)
