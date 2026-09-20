#!/usr/bin/env python3
"""E004jf: hardware-free tests for ONE unique Golden-return live rear appsrc run."""
from pathlib import Path
import hashlib
import json
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
SOURCE=Path("/tmp/sp11-e004jf-rear-appsrc-source-20260920")
RUN=(HERE/"run-once.sh").read_text()
INSTALL=(HERE/"install-unarmed.sh").read_text()
ARM=(HERE/"arm-once.sh").read_text()
UNIT=(HERE/"sp11-camera-e004jf-one-shot.service").read_text()
ENTRY=(HERE/"99zzzzzz_sp11_camera_e004jf").read_text()
CANONICAL="3f3bf8d3ea40a5045896f8ab3053bad14f09cc8fe3c328738905b33a5cf33c71"
DRIVER="4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d"
BRIDGE_BIN="a5b949303fbb40adbdcc62fe494823fec1524feca4d3cd7d5aa273eebdb73c15"
BRIDGE_PY="9793eeee236dcad46cb152dbedd37f53491aa1b3798fbcc3a6396787d6ff1613"
R4="1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa"

def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

class LiveRearAppsrcOneShot(unittest.TestCase):
    def test_canonical_r4_complete_package_and_driver_binaries(self):
        stage=SOURCE/"stage"
        self.assertEqual(sha(stage/"CAMERA-STACK-MANIFEST.sha256"),CANONICAL)
        self.assertEqual(sha(stage/"usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin"),R4)
        self.assertEqual(sha(SOURCE/"candidate/camss/qcom-camss.ko"),DRIVER)
        self.assertEqual(sha(SOURCE/"bridge/rear-bayer-stdin-to-nv12"),BRIDGE_BIN)
        self.assertEqual(sha(REPO/"experiments/E004-front-ir-vd55g0/e004je-rear-live-appsrc-bridge/nv12-appsrc-consumer.py"),BRIDGE_PY)
        self.assertIn("--require-r4",INSTALL)
        self.assertIn(CANONICAL,INSTALL)
        self.assertIn(CANONICAL,RUN)
        self.assertIn(DRIVER,RUN)

    def test_live_unmodified_golden_with_unique_one_shot(self):
        self.assertIn("sp11_camera_e004jf_two_rgb_dma_guard=1",UNIT)
        self.assertIn("sp11-camera-e004jf-two-rgb-dma-guard-one-shot",ENTRY)
        self.assertIn("/boot/sp11-7.1.5-camera-e004jf-two-rgb-dma-guard/",ENTRY)
        self.assertIn("sp11-audio-fullio-v19c",ARM)
        self.assertIn("ExecStopPost=/usr/bin/systemctl --no-block reboot",UNIT)
        self.assertIn("TimeoutStartSec=360",UNIT)
        self.assertIn("E004JF_IDENTITY_CONSUMED_DO_NOT_REARM",ARM)
        self.assertIn("ATTEMPT-CONSUMED",RUN)
        self.assertIn("ONE_SHOT_NO_RETRY",RUN)
        self.assertNotIn("e004jc",ENTRY)

    def test_real_grub_writers_and_driver_gate_before_camera(self):
        self.assertIn("Wants=systemd-udev-settle.service grub2-common.service grub-initrd-fallback.service",UNIT)
        self.assertIn("fallback_exit <= grub2_start",RUN)
        self.assertIn("grep -qx 'next_entry='",RUN)
        self.assertIn("grep -qx 'saved_entry=sp11-audio-fullio-v19c'",RUN)
        self.assertIn("sp11-serialize-grubenv-writers.conf",RUN)
        self.assertLess(RUN.index("fallback_exit <= grub2_start"),RUN.index("modprobe i2c_qcom_cci"))

    def test_source_locked_root_copied_rear_stream_bridge_before_camera(self):
        for digest in (BRIDGE_BIN,BRIDGE_PY):
            self.assertIn(digest,INSTALL)
            self.assertIn(digest,ARM)
            self.assertIn(digest,RUN)
        self.assertIn('install -m 0700 "$SOURCE/bridge/rear-bayer-stdin-to-nv12"',INSTALL)
        self.assertIn('install -m 0600 "$BRIDGE_SOURCE/nv12-appsrc-consumer.py"',INSTALL)
        self.assertIn('E004JE_NV12_APPSRC_CONSUMER=PASS FRAMES=1',INSTALL)
        self.assertIn('E004JE_BAYER10_STREAM_NV12=PASS FRAMES=1',INSTALL)
        self.assertIn("REAR-APP-DRYRUN.txt",ARM)
        self.assertLess(RUN.index('BRIDGE_BIN=$D/bridge/rear-bayer-stdin-to-nv12'),
                        RUN.index("modprobe i2c_qcom_cci"))

    def test_real_v4l2_stdout_bayer_to_gst_appsrc_pipeline(self):
        self.assertIn('v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=8 --stream-to=-',RUN)
        self.assertIn('bash -o pipefail -c',RUN)
        self.assertIn('"$3" --frames 8',RUN)
        self.assertIn('/usr/bin/python3 "$5" --frames 8',RUN)
        self.assertIn("timeout --signal=TERM --kill-after=3s 40s",RUN)
        self.assertIn("E004JE_BAYER10_STREAM_NV12=PASS FRAMES=8",RUN)
        self.assertIn("E004JE_NV12_APPSRC_CONSUMER=PASS FRAMES=8",RUN)
        self.assertIn("E004JF_REAL_REAR_TO_GSTREAMER_APPSRC=PASS",RUN)
        self.assertIn('[[ ! -e "$O/rear-normal8.raw" && ! -e "$O/rear-normal8.nv12" ]]',RUN)
        self.assertNotIn('stream-to="$O/rear-normal8.raw"',RUN)

    def test_route_transitions_and_suspension(self):
        checkpoints=("INITIAL-NORMALIZED-MEDIA.txt","REAR-ON-MEDIA.txt",
                     "BETWEEN-NEUTRAL.txt","FRONT-MEDIA.txt","NEUTRAL-MEDIA.txt")
        indexes=[RUN.index(c) for c in checkpoints]
        self.assertEqual(indexes,sorted(indexes))
        self.assertIn("REAR_PATTERN_ACTIVE=0",RUN)
        self.assertIn("wait_suspend",RUN)
        self.assertIn("REAR-UNDO-1.txt",RUN)
        self.assertIn("UNDO-1.txt",RUN)

    def test_prior_front_qc10c_live_guard_still_used_only_as_compressed(self):
        self.assertIn("--post-g3-write-policy shadow",RUN)
        self.assertIn("list(range(27))",RUN)
        self.assertIn("7778304",RUN)
        self.assertIn("POLICY=shadow",RUN)
        self.assertIn("PASS_REAL_REAR8_GSTREAMER_APPSRC_FRONT27_QC10C_DMA_GUARD",RUN)
        self.assertNotIn("front_nv12",RUN)
        self.assertNotIn("VIDIOC_STREAMON_IR",RUN)
        self.assertNotIn('v4l2-ctl -d "$IR"',RUN)
        self.assertNotIn("ILLUMINATION_ON=1",RUN)

    def test_shell_grub_and_unit_syntax(self):
        for path in HERE.glob("*.sh"):
            p=subprocess.run(["bash","-n",str(path)],capture_output=True,text=True,timeout=12)
            self.assertEqual(p.returncode,0,path.name+" "+p.stderr)
        p=subprocess.run(["grub-script-check"],input="\n".join(ENTRY.splitlines()[2:]),
                         capture_output=True,text=True,timeout=12)
        self.assertEqual(p.returncode,0,p.stderr)
        p=subprocess.run(["systemd-analyze","verify",str(HERE/"sp11-camera-e004jf-one-shot.service")],
                         capture_output=True,text=True,timeout=12)
        self.assertIn(p.returncode,(0,1))
        self.assertNotIn("Failed to parse",p.stderr)

if __name__=="__main__":unittest.main(verbosity=2)
