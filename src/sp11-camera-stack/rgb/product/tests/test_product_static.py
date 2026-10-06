#!/usr/bin/env python3
import subprocess,unittest
from pathlib import Path
P=Path(__file__).resolve().parents[1]
class StaticTests(unittest.TestCase):
    def test_shell_syntax(self):
        for name in ('install-unactivated.sh','uninstall-unactivated.sh','start-session.sh','recover-golden.sh'):
            subprocess.run(['bash','-n',str(P/name)],check=True)
    def test_units_are_opt_in_and_no_restart(self):
        main=(P/'sp11-camera-rgb.service').read_text(); pub=(P/'sp11-camera-rgb-publisher@.service').read_text()
        self.assertIn('ConditionKernelCommandLine=sp11_camera_rgb_product=1',main)
        self.assertIn('OnFailure=sp11-camera-rgb-recover.service',main)
        self.assertIn('Restart=no',main); self.assertIn('RuntimeMaxSec=4h',main)
        self.assertIn('SuccessExitStatus=143',pub); self.assertIn('Restart=no',pub)
    def test_installer_never_enables_or_starts(self):
        text=(P/'install-unactivated.sh').read_text()
        self.assertIn('systemctl disable sp11-camera-rgb.service',text)
        self.assertNotIn('systemctl enable sp11-camera-rgb.service',text)
        self.assertNotIn('systemctl start sp11-camera-rgb.service',text)
        self.assertIn('rm -f "$STATE/ENABLE"',text)
if __name__=='__main__': unittest.main()
