#!/usr/bin/env python3
"""Read-only Golden audit plus disposable local grubenv negative tests.

Fixture commands only mutate unique files in TemporaryDirectory; never
/boot, /etc, NVRAM, camera/PMIC or actual systemd configuration.
"""
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
AUDIT=runpy.run_path(str(HERE/"boot_env_preflight.py"))["audit"]
EXPECT="sp11-audio-fullio-v19c"

class BootEnvTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory(prefix="sp11-e004ir-offline-")
        self.addCleanup(self.temp.cleanup)
        self.d=Path(self.temp.name)
        self.env=self.d/"grubenv"
        subprocess.run(["grub-editenv",str(self.env),"create"],check=True)
        self.set_vars("saved_entry="+EXPECT,"next_entry=")
        self.line=self.d/"cmdline"
        self.line.write_text(
          "BOOT_IMAGE=/boot/vmlinuz ro "
          "sp11_entry=7.1.5-sp11-camera-e004ir-diagnostic "
          "sp11_camera_e004ir_diagnostic=1\n")

    def set_vars(self,*entries):
        subprocess.run(["grub-editenv",str(self.env),"set",*entries],
                       capture_output=True,text=True,check=True)

    def test_accept_exact_candidate_without_modifying_environment(self):
        before=self.env.read_bytes()
        r=AUDIT(self.env,self.line,require_candidate=True)
        self.assertEqual(r["saved_entry"],EXPECT)
        self.assertFalse(r["camera_access_authorized"])
        self.assertEqual(before,self.env.read_bytes())

    def test_accept_golden_readonly_environment(self):
        before=Path("/boot/grub/grubenv").read_bytes()
        r=AUDIT(Path("/boot/grub/grubenv"),Path("/proc/cmdline"))
        self.assertEqual(r["saved_entry"],EXPECT)
        self.assertEqual(before,Path("/boot/grub/grubenv").read_bytes())

    def test_reject_corrupt_grubenv_header(self):
        raw=bytearray(self.env.read_bytes())
        raw[0]=ord("X")
        self.env.write_bytes(raw)
        with self.assertRaisesRegex(ValueError,"GRUB_ENV_UNREADABLE_OR_INVALID"):
            AUDIT(self.env,self.line,require_candidate=True)

    def test_reject_short_environment(self):
        self.env.write_bytes(self.env.read_bytes()[:100])
        with self.assertRaises(ValueError):
            AUDIT(self.env,self.line,require_candidate=True)

    def test_reject_wrong_saved_entry(self):
        self.set_vars("saved_entry=some-other-boot")
        with self.assertRaisesRegex(ValueError,"PERSISTENT_GOLDEN_ENTRY"):
            AUDIT(self.env,self.line,require_candidate=True)

    def test_reject_armed_next_entry(self):
        self.set_vars("next_entry=another-one-shot")
        with self.assertRaisesRegex(ValueError,"GRUB_ONE_SHOT_NOT_CONSUMED"):
            AUDIT(self.env,self.line,require_candidate=True)

    def test_reject_missing_next_entry(self):
        subprocess.run(["grub-editenv",str(self.env),"unset","next_entry"],check=True)
        with self.assertRaisesRegex(ValueError,"GRUB_ONE_SHOT_NOT_CONSUMED"):
            AUDIT(self.env,self.line,require_candidate=True)

    def test_reject_missing_candidate_boot_marker(self):
        self.line.write_text("BOOT_IMAGE=/boot/vmlinuz ro\n")
        with self.assertRaisesRegex(ValueError,"CANDIDATE_CMDLINE_MARKER"):
            AUDIT(self.env,self.line,require_candidate=True)

    def test_reject_wrong_candidate_boot_identifier(self):
        self.line.write_text("sp11_entry=7.1.5-sp11-camera-something-else "
                             "sp11_camera_e004ir_diagnostic=1\n")
        with self.assertRaisesRegex(ValueError,"CANDIDATE_BOOT_ID_MISMATCH"):
            AUDIT(self.env,self.line,require_candidate=True)

    def test_reject_duplicate_candidate_marker(self):
        text=self.line.read_text()
        self.line.write_text(text+" sp11_camera_e004ir_diagnostic=1")
        with self.assertRaisesRegex(ValueError,"DUPLICATED_CMDLINE_WORDS"):
            AUDIT(self.env,self.line,require_candidate=True)

    def test_unit_explicitly_orders_grubenv_mutators(self):
        content=(HERE/"sp11-camera-e004ir-grubenv-diagnostic.service").read_text()
        self.assertIn("ConditionKernelCommandLine=sp11_camera_e004ir_diagnostic=1",content)
        self.assertIn("Wants=grub2-common.service grub-initrd-fallback.service",content)
        self.assertIn("After=local-fs.target grub2-common.service grub-initrd-fallback.service",content)
        for forbidden in ("ExecStopPost=","ExecStartPost=","[Install]",
                          "insmod ","grub-reboot","systemctl reboot"):
            self.assertNotIn(forbidden,content)

if __name__=="__main__":
    unittest.main(verbosity=2)
