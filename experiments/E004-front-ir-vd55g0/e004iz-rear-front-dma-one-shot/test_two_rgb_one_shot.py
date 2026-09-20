#!/usr/bin/env python3
"""E004iz: no hardware access; strict two-RGB-camera single-use proof checks."""
from pathlib import Path
import hashlib,json,re,subprocess,unittest

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
ARCHIVE=HERE.parent/"e004dz-canonical-package-rgb-handoff/runtime-output/REAR-NORMAL8.txt"
SOURCE=Path("/tmp/sp11-e004iz-two-rgb-candidate-20260920")
RUN=(HERE/"run-once.sh").read_text()
SERVICE=(HERE/"sp11-camera-e004iz-one-shot.service").read_text()
ENTRY=(HERE/"99zzzzzz_sp11_camera_e004iz").read_text()
ARM=(HERE/"arm-once.sh").read_text()
INSTALL=(HERE/"install-unarmed.sh").read_text()
GOLDEN="sp11-audio-fullio-v19c"
CANONICAL_MANIFEST="11a649fafbfbfc3467f86f2f17d8ff4d4a86e2f5f4fc36c7f1d1c7839160c646"
CAND_SHA="4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d"

class TwoRGBOneShotTests(unittest.TestCase):
    def test_golden_boot_and_grub_writers_unmodified_then_camera(self):
        self.assertIn("Wants=systemd-udev-settle.service grub2-common.service grub-initrd-fallback.service",SERVICE)
        self.assertIn("After=local-fs.target systemd-udev-settle.service grub2-common.service grub-initrd-fallback.service",SERVICE)
        self.assertIn("ExecStopPost=/usr/bin/systemctl --no-block reboot",SERVICE)
        self.assertIn("ConditionKernelCommandLine=sp11_camera_e004iz_two_rgb_dma_guard=1",SERVICE)
        self.assertIn("$(systemctl show grub2-common.service -p Result --value)",RUN)
        self.assertIn("$(systemctl show grub-initrd-fallback.service -p Result --value)",RUN)
        self.assertIn("grep -qx 'next_entry='",RUN)
        self.assertIn("grep -qx 'saved_entry="+GOLDEN+"'",RUN)
        self.assertLess(RUN.index("grub2-common.service -p Result"),
                        RUN.index("modprobe i2c_qcom_cci"))
        self.assertLess(RUN.index("grep -qx 'next_entry='"),
                        RUN.index("modprobe i2c_qcom_cci"))

    def test_unique_one_shot_identity_uses_nondefault_three_sensor_dtb(self):
        self.assertIn("/boot/sp11-7.1.5-camera-e004iz-two-rgb-dma-guard/",ENTRY)
        self.assertIn("sp11-camera-e004iz-two-rgb-dma-guard-one-shot",ENTRY)
        self.assertIn("sp11_camera_e004iz_two_rgb_dma_guard=1",ENTRY)
        self.assertIn("modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0",ENTRY)
        self.assertIn("sp11-audio-fullio-v19c",ARM)
        self.assertIn('grub-reboot "$ID"',ARM)
        self.assertNotIn("e004iq",ENTRY)
        self.assertNotIn("e004iv",ENTRY)
        self.assertNotIn("e004iw",ENTRY)

    def test_exact_accepted_package_and_new_qc10c_guard(self):
        self.assertTrue(SOURCE.is_dir())
        manifest=SOURCE/"stage/CAMERA-STACK-MANIFEST.sha256"
        candidate=SOURCE/"candidate/camss/qcom-camss.ko"
        self.assertEqual(hashlib.sha256(manifest.read_bytes()).hexdigest(),CANONICAL_MANIFEST)
        self.assertEqual(hashlib.sha256(candidate.read_bytes()).hexdigest(),CAND_SHA)
        self.assertIn(CANONICAL_MANIFEST,RUN)
        self.assertIn(CAND_SHA,RUN)
        self.assertIn(CANONICAL_MANIFEST,INSTALL)
        self.assertIn(CAND_SHA,INSTALL)

    def test_owner_scoped_git_and_no_live_same_boot_retry(self):
        self.assertEqual(RUN.count('runuser -u geoca -- git -C "$R" rev-parse'),3)
        self.assertNotIn('git config --global',RUN)
        self.assertIn("ATTEMPT-CONSUMED",RUN)
        self.assertIn("ATTEMPT-ARMED",ARM)
        self.assertIn("ONE_SHOT_NO_RETRY",RUN)
        self.assertIn("ATTEMPT-CONSUMED",ARM)
        self.assertIn("TimeoutStartSec=360",SERVICE)

    def test_rear_capture_precedes_front_and_has_neutral_handoff(self):
        self.assertIn("E004IZ_REAR_NORMAL_BAYER8=PASS",RUN)
        self.assertIn("pixelformat=pgAA",RUN)
        self.assertIn("--stream-count=1",RUN)
        self.assertIn("--stream-count=8",RUN)
        self.assertIn("rear-normal8.raw",RUN)
        self.assertIn("rear-colorbar.raw",RUN)
        self.assertIn("14321824",RUN)
        self.assertIn("6987a73633dd085044b6893909cee663998b2c8cd8b5b2030ad95e01b8f09346",RUN)
        self.assertIn('"$H/route-state.py" "$O/BETWEEN-NEUTRAL.txt" --expect neutral',RUN)
        self.assertLess(RUN.index("E004IZ_REAR_NORMAL_BAYER8=PASS"),
                        RUN.index("front-imx681-launcher.py"))
        self.assertIn('v4l2-ctl -d "$REARSENSORDEV" --set-ctrl=test_pattern=0',RUN)
        self.assertIn("REAR-UNDO-1.txt",RUN)
        self.assertIn("REAR-UNDO-2.txt",RUN)

    def test_front_existing_27_frame_shadow_gate_and_no_ir_stream(self):
        self.assertIn("--post-g3-write-policy shadow",RUN)
        self.assertIn("list(range(27))",RUN)
        self.assertIn("7778304",RUN)
        self.assertIn("PASS_REAR8_FRONT27_QC10C_DMA_GUARD",RUN)
        self.assertNotIn("--enable-ir",RUN)
        self.assertNotIn("illumination=1",RUN)
        self.assertNotIn("VIDIOC_STREAMON_IR",RUN)
        self.assertNotIn('v4l2-ctl -d "$IR"',RUN)
        self.assertNotIn("grub-reboot",RUN)

    def test_rear_archived_verbose_matches_candidate_sequence_parser(self):
        text=ARCHIVE.read_text()
        seq=[int(x) for x in re.findall(r'seq:\s*(\d+)\s+bytesused:\s*14321824',text)]
        timestamps=[float(x) for x in re.findall(r'ts:\s*([0-9]+\.[0-9]+)',text)]
        self.assertEqual(seq,list(range(8)))
        self.assertEqual(len(timestamps),8)
        fps=7/(timestamps[-1]-timestamps[0])
        self.assertTrue(28.5<=fps<=31.5)

    def test_real_boot_writer_exit_timestamps_are_gated_before_camera(self):
        self.assertIn("ExecMainStartTimestampMonotonic",RUN)
        self.assertIn("ExecMainExitTimestampMonotonic",RUN)
        self.assertIn("ExecMainStatus",RUN)
        self.assertIn("fallback_exit <= grub2_start",RUN)
        self.assertLess(RUN.index("fallback_exit <= grub2_start"),
                        RUN.index("modprobe i2c_qcom_cci"))

    def test_rear_pattern_cleanup_only_when_actually_active(self):
        self.assertIn("REAR_PATTERN_ACTIVE=0",RUN)
        self.assertIn("REAR_PATTERN_ACTIVE:-0",RUN)
        self.assertLess(RUN.index("REAR_PATTERN_ACTIVE=1"),
                        RUN.index('v4l2-ctl -d "$REARSENSORDEV" --set-ctrl=test_pattern=0\nREAR_PATTERN_ACTIVE=0'))
        self.assertIn("ILLUMINATION_ON",RUN)
        self.assertIn("E004J_CSIPHY0_DPHY_WINDOWS_PARITY",RUN)

    def test_source_scripts_and_grub_parse(self):
        for path in HERE.glob("*.sh"):
            p=subprocess.run(["bash","-n",str(path)],capture_output=True,text=True,timeout=12)
            self.assertEqual(p.returncode,0,path.name+" "+p.stderr)
        p=subprocess.run(["grub-script-check"],input="\n".join(ENTRY.splitlines()[2:]),
                         capture_output=True,text=True,timeout=12)
        self.assertEqual(p.returncode,0,p.stderr)

if __name__=="__main__":unittest.main(verbosity=2)
