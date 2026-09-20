#!/usr/bin/env python3
"""E004jh: source-locked real rear->standard virtual video one-shot preflight.

These static/offline tests NEVER claim a real camera or V4L2 virtual device
pass. Only the isolated on-machine run can establish that.
"""
from pathlib import Path
import hashlib,subprocess,unittest

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
STAGE=Path("/tmp/sp11-e004jh-rear-virtual-source-20260920")
RUN=(HERE/"run-once.sh").read_text()
ARM=(HERE/"arm-once.sh").read_text()
INSTALL=(HERE/"install-unarmed.sh").read_text()
UNIT=(HERE/"sp11-camera-e004jh-one-shot.service").read_text()
ENTRY=(HERE/"99zzzzzz_sp11_camera_e004jh").read_text()
EXPECTED={
 "full":"9913494cc2eb4db08ba0f0d09dd4a0cad9415982a1a502f903a0217b0be4e455",
 "hardware":"ad96f706b5e0c5440707c0b9dc5d40a1376391b792f03d3d20bba5d23244f53c",
 "front":"4297bb57ae19fd972955cd679ebc0bb337b089299cfc88f8fe77c555ad8c799d",
 "loop":"2b455ad4e8785818b941f71372d4f77545bf0d265ff6f0eb5959199c93949dc1",
 "bridge":"a5b949303fbb40adbdcc62fe494823fec1524feca4d3cd7d5aa273eebdb73c15",
 "consumer":"9793eeee236dcad46cb152dbedd37f53491aa1b3798fbcc3a6396787d6ff1613",
 "r4":"1a1fa39cbc7051d4ae9db8e2970fa5f405ec7e1b4f2867ff030fb1293fda57fa",
}
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

class RealRearVirtualCandidate(unittest.TestCase):
 def test_binaries_accepted_51_file_package_and_source_lock(self):
  self.assertEqual(sha(STAGE/"stage/CAMERA-STACK-MANIFEST.sha256"),EXPECTED["full"])
  self.assertEqual(sha(STAGE/"hardware/HARDWARE-MANIFEST.sha256"),EXPECTED["hardware"])
  self.assertEqual(sha(STAGE/"candidate/camss/qcom-camss.ko"),EXPECTED["front"])
  self.assertEqual(sha(STAGE/"bridge/rear-bayer-stdin-to-nv12"),EXPECTED["bridge"])
  self.assertEqual(sha(REPO/"experiments/E004-front-ir-vd55g0/e004je-rear-live-appsrc-bridge/nv12-appsrc-consumer.py"),EXPECTED["consumer"])
  self.assertEqual(sha(STAGE/"stage/usr/lib/sp11-front-imx681/userspace/iq/authority/r4-bootstrap.bin"),EXPECTED["r4"])
  self.assertEqual(sha("/tmp/sp11-e004jg-loopback-source-20260920/source/v4l2loopback/v4l2loopback.ko"),EXPECTED["loop"])
  for h in ("full","front","bridge","loop","consumer"):
   self.assertIn(EXPECTED[h],INSTALL if h=="full" else RUN if h=="front" else INSTALL+RUN)

 def test_unique_conditional_golden_return_and_rearm_refusal(self):
  self.assertIn("sp11_camera_e004jh_two_rgb_dma_guard=1",UNIT)
  self.assertIn("ConditionKernelCommandLine=sp11_camera_e004jh_two_rgb_dma_guard=1",UNIT)
  self.assertIn("ExecStopPost=/usr/bin/systemctl --no-block reboot",UNIT)
  self.assertIn("TimeoutStartSec=360",UNIT)
  self.assertIn("sp11-audio-fullio-v19c",ARM)
  self.assertIn("E004JH_IDENTITY_CONSUMED_DO_NOT_REARM",ARM)
  self.assertIn("ATTEMPT-CONSUMED",RUN)
  self.assertIn("ONE_SHOT_NO_RETRY",RUN)
  self.assertIn("sp11-camera-e004jh-two-rgb-dma-guard-one-shot",ENTRY)
  self.assertNotIn("e004jf",ENTRY)
  self.assertNotIn("e004jg-virtual-rear-one-shot",ENTRY)

 def test_source_locked_loopback_and_gst_publisher_precede_camera_start(self):
  self.assertIn("LOOP_SOURCE_DEB=",INSTALL)
  self.assertIn("007a2aa9a723976318407c871b2f1ecdbcd3dc065bf482b0b86f03b026ef40e0",INSTALL)
  self.assertIn('sudo -n install -m 0644 "$LOOP_SOURCE" "$D/v4l2loopback.ko"',INSTALL)
  self.assertIn("REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt",INSTALL)
  self.assertIn("REAL-REAR-VIRTUAL-PUBLISHER-DRYRUN.txt",ARM)
  self.assertLess(RUN.index('LOOP_MOD=$D/v4l2loopback.ko'),RUN.index("modprobe i2c_qcom_cci"))
  self.assertLess(RUN.index('sha256sum "$LOOP_MOD"'),RUN.index("modprobe i2c_qcom_cci"))
  self.assertIn("fallback_exit <= grub2_start",RUN)
  self.assertIn("grep -qx 'next_entry='",RUN)

 def test_actual_rear_bayer_to_nv12_virtual_v4l2_to_independent_reader(self):
  self.assertIn('v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=27 --stream-to=-',RUN)
  self.assertIn('"$3" --frames 27',RUN)
  self.assertIn("fdsrc fd=0 blocksize=3110400",RUN)
  self.assertIn("v4l2sink device=\"$5\" sync=true",RUN)
  self.assertIn('insmod "$LOOP_MOD" devices=1 video_nr=90',RUN)
  self.assertIn('v4l2-ctl --list-devices',RUN)
  self.assertIn('v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=8 --stream-to=-',RUN)
  self.assertIn('E004JE_NV12_APPSRC_CONSUMER=PASS FRAMES=8',RUN)
  self.assertIn('E004JH_REAL_OPTICAL_V4L2_TO_STANDARD_VIDEO90_TO_APP=PASS',RUN)
  self.assertIn('rmmod v4l2loopback',RUN)
  self.assertIn('bash -o pipefail -c',RUN)
  self.assertNotIn('stream-to="$O/rear-normal8.raw"',RUN)

 def test_front_gated_qc10c_and_ir_never_started(self):
  self.assertIn("--post-g3-write-policy shadow",RUN)
  self.assertIn("list(range(27))",RUN)
  self.assertIn("7778304",RUN)
  self.assertIn('PASS_REAL_REAR27_TO_STANDARD_VIRTUAL_NV12_WEB_CAM8_FRONT27_QC10C_DMA_GUARD',RUN)
  self.assertIn('[[ ! -e "$LOOP_DEV" && ! -d /sys/module/v4l2loopback ]]',RUN)
  self.assertIn("wait_suspend",RUN)
  self.assertIn("BETWEEN-NEUTRAL.txt",RUN)
  self.assertNotIn('v4l2-ctl -d "$IR"',RUN)
  self.assertNotIn("ILLUMINATION_ON=1",RUN)

 def test_syntax_and_inspection_only(self):
  for sh in HERE.glob("*.sh"):
   p=subprocess.run(["bash","-n",str(sh)],capture_output=True,text=True,timeout=12)
   self.assertEqual(p.returncode,0,sh.name+p.stderr)
  p=subprocess.run(["grub-script-check"],input="\n".join(ENTRY.splitlines()[2:]),
                   capture_output=True,text=True,timeout=12)
  self.assertEqual(p.returncode,0,p.stderr)
  p=subprocess.run(["systemd-analyze","verify",str(HERE/"sp11-camera-e004jh-one-shot.service")],
                   capture_output=True,text=True,timeout=12)
  self.assertNotIn("Failed to parse",p.stderr)

if __name__=="__main__": unittest.main(verbosity=2)
