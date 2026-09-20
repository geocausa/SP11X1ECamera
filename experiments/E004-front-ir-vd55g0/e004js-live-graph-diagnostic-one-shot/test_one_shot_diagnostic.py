#!/usr/bin/env python3
"""E004js source-only unique one-shot safety and bound diagnostics."""
from pathlib import Path
import subprocess
import unittest
HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
DIAG=ROOT/"experiments/E004-front-ir-vd55g0/e004jr-media-graph-diagnostic/camera-media-graph-diagnostic.py"

class E004jsSafety(unittest.TestCase):
    def read(self,name): return (HERE/name).read_text()
    def test_bash_and_grub_syntax(self):
        for f in ("run-once.sh","install-unarmed.sh","arm-once.sh","retire-after-golden.sh"):
            p=subprocess.run(["bash","-n",str(HERE/f)],capture_output=True,text=True,timeout=5)
            self.assertEqual(p.returncode,0,p.stderr)
        p=subprocess.run(["grub-script-check"],
                         input="\n".join(self.read("99zzzzzz_sp11_camera_e004js").splitlines()[2:])+"\n",
                         capture_output=True,text=True,timeout=5)
        self.assertEqual(p.returncode,0,p.stderr)
    def test_distinct_identity_and_unconditional_golden_return(self):
        arm=self.read("arm-once.sh")
        runner=self.read("run-once.sh")
        service=self.read("sp11-camera-e004js-one-shot.service")
        entry=self.read("99zzzzzz_sp11_camera_e004js")
        identity="sp11-camera-e004js-graph-one-shot"
        self.assertIn(identity,entry)
        self.assertIn(identity,arm)
        self.assertIn("sp11_camera_e004js_diag=1",entry)
        self.assertIn("sp11_camera_e004js_diag=1",runner)
        self.assertIn("ConditionKernelCommandLine=sp11_camera_e004js_diag=1",service)
        self.assertIn("ExecStopPost=/usr/bin/systemctl --no-block reboot",service)
        self.assertIn("ATTEMPT-CONSUMED",runner)
        self.assertIn("ATTEMPT-ARMED",arm)
        self.assertIn("grub-reboot",arm)
        self.assertNotIn("grub-set-default",arm)
        self.assertIn("saved_entry=sp11-audio-fullio-v19c",runner)
    def test_diagnostic_only_never_stream(self):
        runner=self.read("run-once.sh")
        for forbidden in ("--stream", "test_pattern=1", "v4l2sink", "gst-launch",
                          "v4l2loopback.ko", "media-ctl -l", "media-ctl -V",
                          "ILLUMINATION_ON=1", "front-imx681-capture"):
            self.assertNotIn(forbidden,runner)
        self.assertIn("camera-media-graph-diagnostic.py",runner)
        self.assertIn("BIND-STATUS.txt",runner)
        self.assertIn("DIAGNOSTIC-ERROR.txt",runner)
        self.assertIn("DIAGNOSTIC-RC.txt",runner)
        self.assertIn("MEDIA-NODES.txt",runner)
        self.assertIn("optical_frames=0",runner)
        self.assertIn("virtual_webcam_frames=0",runner)
    def test_exact_package_module_hashes_and_private_graph(self):
        runner=self.read("run-once.sh")
        install=self.read("install-unarmed.sh")
        for text in ("9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455",
                     "862732b7c9e4712360840a033a016239beac7e81a7d620aff61db51efb8ecdc7"):
            self.assertIn(text,runner)
            self.assertIn(text,install)
        self.assertIn("--live --out-dir",runner)
        self.assertIn("mkdir -m 0700",runner)
        self.assertIn("sha256sum -c CAMERA-STACK-MANIFEST.sha256",runner)
        self.assertTrue(DIAG.exists())
    def test_retire_requires_golden(self):
        retirement=self.read("retire-after-golden.sh")
        self.assertIn("--require-golden --require-no-camera-process",retirement)
        self.assertIn("ATTEMPT-CONSUMED",retirement)
        self.assertIn("ATTEMPT-RESULT.txt",retirement)
        self.assertIn("update-grub",retirement)
        self.assertIn("sp11-camera-e004js-graph-one-shot",retirement)
        self.assertNotIn("sp11-camera-e004jq-rear4k-one-shot",retirement)

if __name__=="__main__":
    unittest.main()
