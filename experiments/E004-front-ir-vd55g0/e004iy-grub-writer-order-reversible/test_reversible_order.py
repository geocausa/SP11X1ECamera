#!/usr/bin/env python3
"""E004iy: fail-closed ordering and rollback static tests on Golden.

No installed unit, GRUB block or boot is modified by these tests.
"""
from pathlib import Path
import json
import os
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
DROP=HERE/"90-sp11-serialize-grubenv-writers.conf"
INSTALL=HERE/"install-unarmed.sh"
ROLLBACK=HERE/"rollback.sh"
REAL="/etc/systemd/system/grub2-common.service.d/90-sp11-serialize-grubenv-writers.conf"
STOCK=Path("/usr/lib/systemd/system")
class GRUBServiceOrder(unittest.TestCase):
    def test_only_dependency_directives_staged(self):
        data=DROP.read_text()
        lines=[s for s in data.splitlines() if s and not s.startswith("#")]
        self.assertEqual(lines,["[Unit]",
            "Wants=grub-initrd-fallback.service",
            "After=grub-initrd-fallback.service"])

    def test_disposable_complete_unit_graph_verify(self):
        with tempfile.TemporaryDirectory(prefix="sp11-e004iy-unit-",dir="/tmp") as td:
            base=Path(td)
            for name in ("grub2-common.service","grub-initrd-fallback.service"):
                (base/name).write_bytes((STOCK/name).read_bytes())
            d=base/"grub2-common.service.d"
            d.mkdir()
            (d/"90-sp11-serialize-grubenv-writers.conf").write_bytes(DROP.read_bytes())
            env=os.environ.copy()
            env["SYSTEMD_UNIT_PATH"]=str(base)+":/usr/lib/systemd/system:/etc/systemd/system"
            result=subprocess.run(["systemd-analyze","verify",
                    str(base/"grub2-common.service"),
                    str(base/"grub-initrd-fallback.service")],
                    capture_output=True,text=True,env=env,timeout=28)
            self.assertEqual(result.returncode,0,result.stderr[-650:])

    def test_original_unit_commands_preserved(self):
        original=(STOCK/"grub2-common.service").read_text()
        self.assertIn("grub-editenv /boot/grub/grubenv unset recordfail",original)
        self.assertIn("Requires=boot-complete.target",original)
        self.assertNotIn("ExecStart=",DROP.read_text())
        self.assertNotIn("ExecStartPre=",DROP.read_text())
        self.assertNotIn("ExecStartPost=",DROP.read_text())
        self.assertNotIn("WantedBy=",DROP.read_text())

    def test_install_does_not_reboot_or_arm_camera(self):
        source=INSTALL.read_text()
        for forbidden in ("grub-reboot","systemctl reboot","modprobe ",
                          "insmod ","VIDIOC_STREAMON","/dev/i2c-"):
            self.assertNotIn(forbidden,source)
        self.assertIn("--require-clean-tracked --require-golden --require-no-camera-process",source)
        self.assertIn('sed -n \'s/^next_entry=//p\'',source)
        self.assertIn('sudo -n cmp --silent /boot/grub/grubenv "$ROOT/grubenv-before.bin"',source)

    def test_only_exact_removable_dropin_and_private_snapshot(self):
        source=INSTALL.read_text()
        self.assertIn('SERVICE=/etc/systemd/system/grub2-common.service.d',source)
        self.assertIn('DROP=$SERVICE/90-sp11-serialize-grubenv-writers.conf',source)
        self.assertIn('ROOT=/var/lib/sp11-camera-e004iy',source)
        self.assertIn('sudo -n test ! -e "$DROP"',source)
        self.assertIn('sudo -n test ! -e "$SERVICE"',source)
        self.assertIn('sudo -n cp -- /boot/grub/grubenv "$ROOT/grubenv-before.bin"',source)
        self.assertIn('sudo -n install -m 0644 "$T/90-sp11-serialize-grubenv-writers.conf" "$DROP"',source)

    def test_rollback_checks_exact_owned_file_and_golden_before_removal(self):
        rollback=ROLLBACK.read_text()
        self.assertIn('sudo -n cmp --silent "$T/90-sp11-serialize-grubenv-writers.conf" "$DROP"',rollback)
        self.assertIn('sudo -n rm -f -- "$DROP"',rollback)
        self.assertIn('sudo -n rmdir -- "$SERVICE"',rollback)
        self.assertIn('sudo -n systemctl daemon-reload',rollback)
        self.assertIn('sudo -n test -f "$ROOT/grubenv-before.bin"',rollback)
        self.assertNotIn('grub-reboot',rollback)
        self.assertNotIn('systemctl reboot',rollback)

    def test_shell_syntax(self):
        for path in (INSTALL,ROLLBACK):
            result=subprocess.run(["bash","-n",str(path)],capture_output=True,text=True,timeout=10)
            self.assertEqual(result.returncode,0,result.stderr)

    def test_not_installed_at_time_of_offline_test(self):
        self.assertFalse(Path(REAL).exists())
        self.assertFalse(Path("/var/lib/sp11-camera-e004iy").exists())

if __name__=="__main__":unittest.main(verbosity=2)
