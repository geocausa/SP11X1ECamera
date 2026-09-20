#!/usr/bin/env python3
"""E004jp: unarmed one-shot, exact 4K V4L2 synthetic source/safety checks."""
from pathlib import Path
import hashlib
import re
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ID="sp11-e004jp-virtual-rear-4k-one-shot"
CMDLINE="sp11_virtual_rear_4k_e004jp=1"
KERNEL="7.1.5-sp11-render-parity-v4+"
GOLDEN="sp11-audio-fullio-v19c"
ENTRY=HERE/"99zzzzzz_sp11_e004jp_virtual_rear_4k"
FILES={p.name:p.read_text() for p in HERE.iterdir() if p.is_file()
       and p.suffix in (".sh", ".service")}
RUN=FILES["run-once.sh"]
INSTALL=FILES["install-unarmed.sh"]
ARM=FILES["arm-once.sh"]
RETIRE=FILES["retire-after-golden.sh"]
SERVICE=FILES["sp11-e004jp-virtual-rear-4k.service"]


class Synthetic4kSafety(unittest.TestCase):
    def test_unique_identity_and_no_consumed_prior_candidate(self):
        for f in [ENTRY.read_text(),RUN,INSTALL,ARM,RETIRE,SERVICE]:
            self.assertIn("e004jp",f)
            self.assertNotIn("e004jg",f)
        self.assertIn(ID,ENTRY.read_text())
        self.assertIn(ID,INSTALL)
        self.assertIn(ID,ARM)
        self.assertIn(ID,RETIRE)
        self.assertIn(CMDLINE,ENTRY.read_text())
        self.assertIn(CMDLINE,RUN)
        self.assertIn(CMDLINE,SERVICE)
        self.assertIn("sp11_entry=7.1.5-sp11-e004jp-virtual-rear-4k",RUN)

    def test_source_artifacts_and_exact_hash_gates(self):
        module_hash="305faddd6082eb1f460fe78954abe5c2ede90b4d823f7cb21f56c76d6bd22b3c"
        reader_hash="813d6ad77f5b936955df178c4b426c3c3844d6d640f4377dd7196b5f1fba96a5"
        for stage in (INSTALL,ARM,RUN):
            self.assertIn(module_hash,stage)
            self.assertIn(reader_hash,stage)
        self.assertIn("--require-clean-tracked --require-golden --require-no-camera-process",INSTALL)
        self.assertIn("EXPECTED-HEAD",INSTALL)
        self.assertIn("EXPECTED-HEAD",ARM)
        self.assertIn("EXPECTED-HEAD",RUN)
        self.assertIn("ATTEMPT-CONSUMED",ARM)
        self.assertIn("ATTEMPT-CONSUMED",RUN)

    def test_synthetic_4k_standard_capture_to_independent_app(self):
        for required in ("videotestsrc pattern=ball", "format=NV12,width=3840,height=2160",
                         "Width/Height.*3840/2160", "Pixel Format.*NV12",
                         "v4l2-ctl -d \"$1\" --stream-mmap=4 --stream-count=8",
                         "E004JN_NV12_APPSRC_CONSUMER=PASS FRAMES=8",
                         "SIZE=12441600 VIDEO=NV12_3840x2160_30",
                         "LIVE_CAMERA_PROVEN=NO VIRTUAL_WEBCAM_CREATED=NO",
                         "SP11-Rear-Preview"):
            self.assertIn(required,RUN)
        self.assertNotIn("width=1920",RUN)
        self.assertNotIn("e004je",INSTALL)

    def test_original_golden_boot_assets_unchanged_and_auto_return(self):
        for v in ("sp11-7.1.5-audio-fullio-v19c/vmlinuz-7.1.5-sp11-render-parity-v4+",
                  "sp11-7.1.5-audio-fullio-v19c/initrd.img-7.1.5-sp11-fullio-v19c",
                  "sp11-7.1.5-audio-fullio-v19c/x1e80100-microsoft-denali-sp11-fullio-v19c.dtb"):
            self.assertIn(v,INSTALL)
        self.assertIn("modprobe.blacklist=qcom_camss,imx681,ov13858,sp11_vd55g0,vd55g0",ENTRY.read_text())
        self.assertIn("grub-reboot \"$ID\"",ARM)
        self.assertIn("next_entry=",RUN)
        self.assertIn("saved_entry="+GOLDEN,RUN)
        self.assertIn("ExecStopPost=/usr/bin/systemctl --no-block reboot",SERVICE)
        self.assertIn("ConditionKernelCommandLine="+CMDLINE,SERVICE)
        self.assertIn("rmmod v4l2loopback",RUN)
        self.assertIn("! -e /dev/video90",RETIRE)
        self.assertIn("sudo -n rm -rf -- \"$D\"",RETIRE)
        self.assertNotIn("qcom_camss.ko",RUN)

    def test_all_boot_assets_names_agree(self):
        entry=ENTRY.read_text()
        for path in ("/boot/sp11-7.1.5-e004jp-virtual-rear/",
                     "initrd.img-7.1.5-sp11-e004jp-virtual-rear-4k"):
            self.assertIn(path,entry)
            self.assertIn(path.strip("/").split("/")[-1],INSTALL)
        self.assertIn("sp11-e004jp-virtual-rear-4k.service",INSTALL)
        self.assertIn("sp11-e004jp-virtual-rear-4k.service",RETIRE)
        self.assertIn("sp11-e004jp-virtual-rear-4k-run-once",SERVICE)
        self.assertIn("sp11-e004jp-virtual-rear-4k-run-once",INSTALL)

    def test_shell_grub_syntax(self):
        paths=[str(HERE/n) for n in ("install-unarmed.sh","run-once.sh","arm-once.sh",
                                     "retire-after-golden.sh")]
        subprocess.run(["bash","-n",*paths],check=True,timeout=15)
        subprocess.run(["grub-script-check"],input="\n".join(ENTRY.read_text().splitlines()[2:]),
                       text=True,check=True,timeout=15)


if __name__=="__main__":
    unittest.main()
