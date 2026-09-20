#!/usr/bin/env python3
"""E004jq source-only guardrails before staging one unique rear-only boot."""
from pathlib import Path
import re
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]


class BootSafety(unittest.TestCase):
    def read(self, file):
        return (HERE/file).read_text()

    def test_bash_and_boot_entry_syntax(self):
        for f in ("run-once.sh", "install-unarmed.sh", "arm-once.sh",
                  "retire-after-golden.sh"):
            p=HERE/f
            proc=subprocess.run(["bash","-n",str(p)],capture_output=True,
                                text=True,timeout=10)
            self.assertEqual(proc.returncode,0,proc.stderr)
        p=subprocess.run(["grub-script-check"],input="\n".join(
            self.read("99zzzzzz_sp11_camera_e004jq").splitlines()[2:])+"\n",
            text=True,capture_output=True,timeout=10)
        self.assertEqual(p.returncode,0,p.stderr)

    def test_source_identity_one_shot_and_golden_default(self):
        install=self.read("install-unarmed.sh")
        arm=self.read("arm-once.sh")
        runner=self.read("run-once.sh")
        service=self.read("sp11-camera-e004jq-one-shot.service")
        entry=self.read("99zzzzzz_sp11_camera_e004jq")
        identity="sp11-camera-e004jq-rear4k-one-shot"
        self.assertIn(identity,install)
        self.assertIn(identity,arm)
        self.assertIn(identity,entry)
        self.assertIn("sp11_camera_e004jq_rear4k=1",entry)
        self.assertIn("sp11_camera_e004jq_rear4k=1",runner)
        self.assertIn("ConditionKernelCommandLine=sp11_camera_e004jq_rear4k=1",service)
        self.assertIn("ATTEMPT-CONSUMED",runner)
        self.assertIn("ATTEMPT-ARMED",arm)
        self.assertIn("grub-reboot",arm)
        self.assertIn("saved_entry=sp11-audio-fullio-v19c",runner)
        self.assertIn("ExecStopPost=/usr/bin/systemctl --no-block reboot",service)
        self.assertIn("TimeoutStartSec=420",service)
        self.assertNotIn("grub-set-default",arm)
        self.assertIn("CAMERA-STACK-MANIFEST.sha256",install)

    def test_exact_live_rear_output_and_independent_reader(self):
        runner=self.read("run-once.sh")
        for text in ('--stream-count=27 --stream-to=-',
                     '"$3" --frames 27',
                     "rawvideoparse format=nv12 width=3840 height=2160",
                     'v4l2sink device="$5" sync=true',
                     '--stream-count=8 --stream-to=-',
                     '"$BRIDGE_APP"',
                     'source=OV13858_pgAA_bayer10 real_frames=27',
                     'bytesused:\\s*12441600'):
            self.assertIn(text,runner)
        self.assertIn("REAR_PATTERN_ACTIVE=0",runner)
        self.assertIn("test_pattern=0",runner)
        self.assertIn("E004JQ_REAL_OPTICAL_V4L2_TO_STANDARD_VIDEO90_TO_APP=PASS",runner)
        self.assertNotIn("--require-distinct",runner)  # static optical scene could repeat

    def test_front_ir_illumination_never_streamed(self):
        runner=self.read("run-once.sh")
        self.assertIn("REARVIDEO",runner)
        self.assertNotIn("FRONTVIDEO",runner)
        self.assertNotIn('--stream-count=27 --stream-to="$O/front',runner)
        self.assertNotIn("ILLUMINATION_ON=1",runner)
        self.assertIn("wait_suspend",runner)
        self.assertIn("NEUTRAL-MEDIA.txt",runner)
        self.assertIn("rmmod v4l2loopback",runner)
        self.assertIn('for dev in "$IR" "$REAR" "$FRONT"',runner)

    def test_readme_explicitly_unproven_before_runtime(self):
        readme=self.read("README.md")
        self.assertIn("Preflight/staging phase only",readme)
        self.assertIn("Do not describe an unarmed candidate",readme)


if __name__=="__main__":
    unittest.main()
