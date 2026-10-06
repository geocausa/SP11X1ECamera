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
        self.assertIn('sudo -n "$HERE/verify-unactivated.py"',text)
        self.assertIn('private_optical_preview.py',text)
        self.assertIn('"$STATE/private-optical"',text)
        self.assertIn('camera-session-contract.py',text)
        self.assertIn('rm -rf "$STATE/output" "$STATE/private-optical"',text)
        self.assertIn('rm -f "$STATE/session.lock" "$STATE/ENABLE"',text)
    def test_visual_gate_helper_is_product_scoped(self):
        text=(P/'private_optical_preview.py').read_text()
        self.assertIn('sp11_camera_rgb_product=1',text)
        self.assertIn('/var/lib/sp11-camera-rgb',text)
        self.assertIn('/dev/video91',text); self.assertIn('/dev/video90',text)
        self.assertIn('1920,1080',text); self.assertIn('3840,2160',text)
        self.assertNotIn('requests.',text); self.assertNotIn('urllib',text)
if __name__=='__main__': unittest.main()
