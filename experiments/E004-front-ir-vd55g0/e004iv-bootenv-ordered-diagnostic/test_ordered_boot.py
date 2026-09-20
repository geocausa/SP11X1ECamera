#!/usr/bin/env python3
"""E004iv static safety contract; NO service install, camera or boot."""
from pathlib import Path
import subprocess
import unittest
HERE=Path(__file__).resolve().parent
ENTRY=HERE/"99zzzzzz_sp11_camera_e004iv"
UNIT=HERE/"sp11-camera-e004iv-bootenv-diagnostic.service"
RUN=HERE/"run-diagnostic-once.sh"
INSTALL=HERE/"install-unarmed.sh"
ARM=HERE/"arm-once.sh"

class DiagnosticTests(unittest.TestCase):
    def test_grub_entry_uses_exact_original_golden_boot_files(self):
        s=ENTRY.read_text()
        paths=("x1e80100-microsoft-denali-sp11-fullio-v19c.dtb",
               "vmlinuz-7.1.5-sp11-render-parity-v4+",
               "initrd.img-7.1.5-sp11-fullio-v19c")
        for name in paths:
            self.assertIn("/boot/sp11-7.1.5-audio-fullio-v19c/"+name,s)
        self.assertIn("sp11_camera_e004iv_bootenv_diagnostic=1",s)
        self.assertIn("modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0",s)
        self.assertNotIn("e004iq",s)
        self.assertNotIn("grub-reboot",s)
    def test_grub_entry_parse_check(self):
        p=subprocess.run(["grub-script-check"],input="\n".join(ENTRY.read_text().splitlines()[2:]),
                         capture_output=True,text=True,timeout=15)
        self.assertEqual(p.returncode,0,p.stderr)
    def test_diagnostic_ordered_after_both_writers(self):
        s=UNIT.read_text()
        self.assertIn("After=local-fs.target grub2-common.service grub-initrd-fallback.service",s)
        self.assertIn("Wants=grub2-common.service grub-initrd-fallback.service",s)
        self.assertIn("ConditionKernelCommandLine=sp11_camera_e004iv_bootenv_diagnostic=1",s)
        self.assertIn("ExecStopPost=/usr/bin/systemctl --no-block reboot",s)
        self.assertIn("TimeoutStartSec=90",s)
        self.assertNotIn("Restart=always",s)
    def test_script_fail_closed_and_keeps_private_invalid_bytes(self):
        s=RUN.read_text()
        self.assertIn('cp -- /boot/grub/grubenv "$OUT/grubenv-observed.bin"',s)
        self.assertLess(s.index("cp -- /boot/grub/grubenv"),
                        s.index("grub-editenv /boot/grub/grubenv list"))
        self.assertIn('grep -qx \'saved_entry=sp11-audio-fullio-v19c\'',s)
        self.assertIn('grep -qx \'next_entry=\'',s)
        self.assertIn("NO_SAME_BOOT_RETRY",s)
        self.assertIn("ATTEMPT-CONSUMED",s)
    def test_scripts_never_access_camera(self):
        for f in (ENTRY,UNIT,RUN,INSTALL,ARM):
            s=f.read_text()
            for bad in ("insmod qcom_camss", "insmod imx681",
                        "insmod ov13858", "insmod sp11-vd55g0",
                        "modprobe imx681", "modprobe qcom_camss",
                        "VIDIOC_STREAMON","/dev/i2c-", "illumination_enable"):
                self.assertNotIn(bad,s,f.name)
        self.assertNotIn("modprobe ",RUN.read_text())
    def test_unique_arm_and_persistent_golden(self):
        s=ARM.read_text()
        self.assertIn('grub-reboot "$ID"',s)
        self.assertIn("sp11-audio-fullio-v19c",s)
        self.assertIn("ATTEMPT-ARMED",s)
        self.assertIn("ATTEMPT-CONSUMED",s)
    def test_no_duplicate_rearm_after_evidence(self):
        s=ARM.read_text()
        self.assertIn('[[ ! -f "$T/evidence/OBSERVED.json" ]]',s)
        self.assertIn("ATTEMPT-CONSUMED",s)
    def test_unarmed_install_does_not_trigger_boot(self):
        s=INSTALL.read_text()
        self.assertNotIn('grub-reboot "$ID"',s)
        self.assertNotIn('systemctl reboot',s)
        self.assertIn('[[ ! -e "$T/evidence/OBSERVED.json" ]]',s)
    def test_diagnostic_runner_source_is_valid_shell(self):
        for f in (RUN,INSTALL,ARM):
            p=subprocess.run(["bash","-n",str(f)],capture_output=True,text=True,timeout=12)
            self.assertEqual(p.returncode,0,p.stderr)
if __name__=="__main__": unittest.main(verbosity=2)
