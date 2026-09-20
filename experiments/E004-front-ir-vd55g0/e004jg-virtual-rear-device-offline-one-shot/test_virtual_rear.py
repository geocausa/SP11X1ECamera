#!/usr/bin/env python3
"""E004jg offline contract: isolated virtual rear webcam on Golden ABI.

Only static and SHA gates; the real V4L2 endpoint requires an actual isolated
physical boot and its result must NOT be inferred from these tests.
"""
from pathlib import Path
import hashlib
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
BUILD=Path("/tmp/sp11-e004jg-loopback-source-20260920")
ENTRY=(HERE/"99zzzzzz_sp11_e004jg_virtual_rear").read_text()
RUN=(HERE/"run-once.sh").read_text()
INSTALL=(HERE/"install-unarmed.sh").read_text()
ARM=(HERE/"arm-once.sh").read_text()
RETIRE=(HERE/"retire-after-golden.sh").read_text()
UNIT=(HERE/"sp11-e004jg-virtual-rear.service").read_text()
MOD_SHA="2b455ad4e8785818b941f71372d4f77545bf0d265ff6f0eb5959199c93949dc1"
DEB_SHA="007a2aa9a723976318407c871b2f1ecdbcd3dc065bf482b0b86f03b026ef40e0"
APP_SHA="9793eeee236dcad46cb152dbedd37f53491aa1b3798fbcc3a6396787d6ff1613"

class IsolatedVirtualRear(unittest.TestCase):
    def test_source_package_and_golden_v4_module_abi(self):
        mod=BUILD/"source/v4l2loopback/v4l2loopback.ko"
        deb=BUILD/"v4l2loopback-source_0.15.3-1ubuntu2_all.deb"
        self.assertEqual(hashlib.sha256(mod.read_bytes()).hexdigest(),MOD_SHA)
        self.assertEqual(hashlib.sha256(deb.read_bytes()).hexdigest(),DEB_SHA)
        self.assertEqual(
            subprocess.check_output(["modinfo","-F","vermagic",str(mod)],text=True).strip(),
            "7.1.5-sp11-render-parity-v4+ SMP preempt mod_unload modversions aarch64")
        self.assertEqual(subprocess.check_output(["modinfo","-F","license",str(mod)],text=True).strip(),"GPL")
        self.assertIn(MOD_SHA,INSTALL)
        self.assertIn(DEB_SHA,INSTALL)
        self.assertIn(MOD_SHA,RUN)
        self.assertIn(APP_SHA,RUN)

    def test_unique_isolated_no_camera_boot_uses_unchanged_golden_dtb(self):
        self.assertIn("sp11-e004jg-virtual-rear-one-shot",ENTRY)
        self.assertIn("sp11_virtual_rear_e004jg=1",ENTRY)
        self.assertIn("sp11_entry=7.1.5-sp11-e004jg-virtual-rear",ENTRY)
        self.assertIn("sp11-fullio-v19c.dtb",ENTRY)
        self.assertNotIn("sp11-unified-rgb-ir.dtb",ENTRY)
        self.assertIn("sp11-7.1.5-audio-fullio-v19c/vmlinuz",INSTALL)
        self.assertIn("sp11-7.1.5-audio-fullio-v19c/initrd",INSTALL)
        self.assertIn("sp11-7.1.5-audio-fullio-v19c/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb",INSTALL)
        self.assertIn("sp11-audio-fullio-v19c",ARM)
        self.assertNotIn("e004jf",ENTRY)
        self.assertNotIn("e004jf",UNIT)

    def test_writer_order_and_fail_closed_single_use_golden_reboot(self):
        self.assertIn("grub2-common.service grub-initrd-fallback.service",UNIT)
        self.assertIn("ExecStopPost=/usr/bin/systemctl --no-block reboot",UNIT)
        self.assertIn("ConditionKernelCommandLine=sp11_virtual_rear_e004jg=1",UNIT)
        self.assertIn("TimeoutStartSec=180",UNIT)
        self.assertIn("fallback_finish <= grub2_start",RUN)
        self.assertIn("grep -qx 'next_entry='",RUN)
        self.assertIn("grep -qx 'saved_entry=sp11-audio-fullio-v19c'",RUN)
        self.assertIn("ATTEMPT-CONSUMED",RUN)
        self.assertIn("E004JG_IDENTITY_CONSUMED_DO_NOT_REARM",ARM)
        self.assertIn("grub-reboot",ARM)
        self.assertIn("systemctl reboot --no-block",ARM)
        self.assertIn("sudo -n rm -rf -- \"$D\"",RETIRE)

    def test_synthetic_source_creates_one_v4l2_video_endpoint(self):
        self.assertIn('insmod "$MOD" devices=1 video_nr=90',RUN)
        self.assertIn("card_label=SP11-Rear-Preview",RUN)
        self.assertIn("exclusive_caps=0",RUN)
        self.assertIn('v4l2-ctl --list-devices',RUN)
        self.assertIn('videotestsrc pattern=ball is-live=true num-buffers=90',RUN)
        self.assertIn("video/x-raw,format=NV12,width=1920,height=1080,framerate=30/1",RUN)
        self.assertIn('v4l2sink device="$VIDEO"',RUN)
        self.assertIn('v4l2-ctl -d "$1" --stream-mmap=4 --stream-count=8 --stream-to=-',RUN)
        self.assertIn("bash -o pipefail",RUN)
        self.assertIn('E004JE_NV12_APPSRC_CONSUMER=PASS FRAMES=8',RUN)
        self.assertIn("rmmod v4l2loopback",RUN)
        self.assertIn("E004JG_MODULE_AND_DEVICE_REMOVED=PASS",RUN)

    def test_no_live_optical_or_ir_or_secret_sensor_configuration(self):
        self.assertNotIn("modprobe qcom_camss",RUN)
        self.assertNotIn("insmod \"$CAND\"",RUN)
        self.assertNotIn("ov13858.ko",RUN)
        self.assertNotIn("imx681.ko",RUN)
        self.assertNotIn("ILLUMINATION_ON=1",RUN)
        self.assertNotIn("SecurePD",RUN)
        self.assertNotIn("FRONT-LAUNCHER",RUN)
        self.assertNotIn('--stream-to="$O/rear-normal8.raw"',RUN)
        self.assertIn("qcom_camss imx681 ov13858 sp11_vd55g0",RUN)

    def test_shell_grub_and_systemd_syntax(self):
        for path in HERE.glob("*.sh"):
            proc=subprocess.run(["bash","-n",str(path)],capture_output=True,text=True,timeout=12)
            self.assertEqual(proc.returncode,0,path.name+":"+proc.stderr)
        proc=subprocess.run(["grub-script-check"],input="\n".join(ENTRY.splitlines()[2:]),
                            capture_output=True,text=True,timeout=12)
        self.assertEqual(proc.returncode,0,proc.stderr)
        proc=subprocess.run(["systemd-analyze","verify",str(HERE/"sp11-e004jg-virtual-rear.service")],
                            capture_output=True,text=True,timeout=12)
        self.assertNotIn("Failed to parse",proc.stderr)

if __name__=="__main__":unittest.main(verbosity=2)
