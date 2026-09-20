#!/usr/bin/env python3
"""E004iw: no camera. Validate exact owner-scoped repo read and one-shot gate."""
from pathlib import Path
import json
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
R=HERE.parents[2]
PREV=HERE.parent/"e004iv-bootenv-ordered-diagnostic"
ENTRY=HERE/"99zzzzzz_sp11_camera_e004iw"
SERVICE=HERE/"sp11-camera-e004iw-bootenv-diagnostic.service"
RUN=HERE/"run-diagnostic-once.sh"

class OwnerSafeBootTests(unittest.TestCase):
    def test_prior_identity_consumed(self):
        previous=json.loads((PREV/"evidence/OBSERVED.json").read_text())
        self.assertFalse(previous["retry_original_e004iv_identity"])
        self.assertFalse(previous["candidate_grubenv_read_reached"])

    def test_owner_scoped_git_read_is_identical_on_golden(self):
        normal=subprocess.run(["git","-C",str(R),"rev-parse","HEAD"],
                              capture_output=True,text=True,check=True,timeout=15)
        owner=subprocess.run(["sudo","-n","runuser","-u","geoca","--",
                              "git","-C",str(R),"rev-parse","HEAD"],
                             capture_output=True,text=True,check=True,timeout=15)
        self.assertEqual(normal.stdout,owner.stdout)
        self.assertEqual(len(normal.stdout.strip()),40)

    def test_two_expected_head_reads_use_checkout_owner(self):
        text=RUN.read_text()
        self.assertEqual(text.count('runuser -u geoca -- git -C "$R" rev-parse HEAD'),2)
        self.assertNotIn('git config --global',text)
        self.assertNotIn('safe.directory',text)
        self.assertNotIn('[[ "$(cat "$D/EXPECTED-HEAD")" == "$(git -C',text)

    def test_grub_uses_original_golden_boot_artifacts(self):
        text=ENTRY.read_text()
        for name in ("x1e80100-microsoft-denali-sp11-fullio-v19c.dtb",
                     "vmlinuz-7.1.5-sp11-render-parity-v4+",
                     "initrd.img-7.1.5-sp11-fullio-v19c"):
            self.assertIn("/boot/sp11-7.1.5-audio-fullio-v19c/"+name,text)
        self.assertIn("sp11_camera_e004iw_bootenv_diagnostic=1",text)
        self.assertIn("modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0",text)
        self.assertNotIn("e004iv",text)

    def test_diagnostic_starts_after_both_writers_and_reboots(self):
        text=SERVICE.read_text()
        self.assertIn("After=local-fs.target grub2-common.service grub-initrd-fallback.service",text)
        self.assertIn("ConditionKernelCommandLine=sp11_camera_e004iw_bootenv_diagnostic=1",text)
        self.assertIn("ExecStopPost=/usr/bin/systemctl --no-block reboot",text)
        self.assertIn("TimeoutStartSec=90",text)

    def test_runner_snapshots_before_read_and_checks_golden_entry(self):
        text=RUN.read_text()
        self.assertLess(text.index('cp -- /boot/grub/grubenv "$OUT/grubenv-observed.bin"'),
                        text.index('grub-editenv /boot/grub/grubenv list'))
        self.assertIn("saved_entry=sp11-audio-fullio-v19c",text)
        self.assertIn("grep -qx 'next_entry='",text)
        self.assertIn("ATTEMPT-CONSUMED",text)
        self.assertIn("NO_SAME_BOOT_RETRY",text)

    def test_no_camera_modules_or_capture_in_any_runner(self):
        text=RUN.read_text()
        for danger in ("modprobe qcom_camss","insmod qcom_camss",
                       "VIDIOC_STREAMON","/dev/i2c-","media-ctl -d",
                       "grub-reboot"):
            self.assertNotIn(danger,text)

    def test_unique_one_shot_arm_blocks_reuse_and_checks_golden(self):
        text=(HERE/"arm-once.sh").read_text()
        self.assertIn('grub-reboot "$ID"',text)
        self.assertIn("sp11-audio-fullio-v19c",text)
        self.assertIn("ATTEMPT-ARMED",text)
        self.assertIn("ATTEMPT-CONSUMED",text)
        self.assertIn('[[ ! -f "$T/evidence/OBSERVED.json" ]]',text)

    def test_all_lifecycle_scripts_use_actual_owner_safe_directory(self):
        correct="experiments/E004-front-ir-vd55g0/e004iw-bootenv-owner-safe-diagnostic"
        for name in ("install-unarmed.sh","arm-once.sh","retire-after-golden.sh"):
            source=(HERE/name).read_text()
            self.assertIn(correct,source,name)
            self.assertNotIn("e004iw-bootenv-ordered-diagnostic",source,name)
        for needed in ("run-diagnostic-once.sh",
                       "99zzzzzz_sp11_camera_e004iw",
                       "sp11-camera-e004iw-bootenv-diagnostic.service"):
            self.assertTrue((HERE/needed).is_file(),needed)

    def test_unarmed_install_does_not_arm(self):
        text=(HERE/"install-unarmed.sh").read_text()
        self.assertNotIn('grub-reboot "$ID"',text)
        self.assertNotIn('systemctl reboot',text)
        self.assertIn('[[ ! -e "$T/evidence/OBSERVED.json" ]]',text)

    def test_shell_and_grub_syntax(self):
        for f in ("run-diagnostic-once.sh","install-unarmed.sh","arm-once.sh",
                  "retire-after-golden.sh"):
            r=subprocess.run(["bash","-n",str(HERE/f)],capture_output=True,text=True,timeout=12)
            self.assertEqual(r.returncode,0,r.stderr)
        r=subprocess.run(["grub-script-check"],input="\n".join(ENTRY.read_text().splitlines()[2:]),
                         capture_output=True,text=True,timeout=12)
        self.assertEqual(r.returncode,0,r.stderr)

if __name__=="__main__":unittest.main(verbosity=2)
