#!/usr/bin/env python3
"""E004kh front-only RAW10 RDI one-shot: strict offline physical/boot safety."""
from pathlib import Path
import runpy
import re
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCHIVE=ROOT/"experiments/E004-front-ir-vd55g0/e004ec-side-light-post-g3-shadow-observation/evidence/LOAD-MEDIA.txt"
ROUTE=runpy.run_path(str(HERE/"route-state.py"))


def enable(text,src,dest,pad=0):
    rx=(rf"(^- entity \d+: {re.escape(src)} \(.*?\n)"
        rf"(.*?)(?=^- entity |\Z)")
    block=re.search(rx,text,re.M|re.S)
    assert block,src
    before=block.group(0)
    target=rf'(-> "{re.escape(dest)}":{pad}) \[\]'
    changed,count=re.subn(target,r"\1 [ENABLED]",before,count=1)
    assert count==1,(src,dest,pad)
    return text[:block.start()]+changed+text[block.end():]


class FrontSafe(unittest.TestCase):
    def test_readonly_route_neutral_rear_front_rdi_front_pix_and_mixed(self):
        s=ARCHIVE.read_text()
        name,_=ROUTE["classify"](s)
        self.assertEqual(name,"neutral")
        rear=enable(enable(s,"msm_csiphy1","msm_csid0"),"msm_csid0","msm_vfe0_rdi0")
        self.assertEqual(ROUTE["classify"](rear)[0],"rear-only")
        phy=enable(s,"msm_csiphy2","msm_csid1")
        self.assertEqual(ROUTE["classify"](phy)[0],"invalid-partial")
        front=enable(phy,"msm_csid1","msm_vfe1_rdi0")
        self.assertEqual(ROUTE["classify"](front)[0],"front-rdi-only")
        cross=enable(phy,"msm_csid1","msm_vfe0_rdi0")
        self.assertEqual(ROUTE["classify"](cross)[0],"invalid-cross-route")
        front_pix=enable(phy,"msm_csid1","msm_vfe1_pix")
        self.assertEqual(ROUTE["classify"](front_pix)[0],"front-pix-only")
        self.assertEqual(ROUTE["classify"](enable(front,"msm_csid1","msm_vfe1_pix"))[0],"invalid-partial")
        self.assertEqual(ROUTE["classify"](enable(front,"msm_csiphy1","msm_csid0"))[0],"invalid-mixed")

    def test_front_staged_only_after_first_live_44_entity_graph(self):
        s=(HERE/"run-once.sh").read_text()
        graph=s.index('camera-media-graph-diagnostic.py" --live --out-dir')
        front_phy=s.index('media-ctl -d "$MEDIA" -l \'"msm_csiphy2":1 -> "msm_csid1":0 [1]\'')
        front_rdi=s.index('media-ctl -d "$MEDIA" -l \'"msm_csid1":1 -> "msm_vfe1_rdi0":0 [1]\'')
        stream=s.index('--stream-count=72 --stream-to=-')
        self.assertLess(graph,front_phy)
        self.assertLess(front_phy,front_rdi)
        self.assertLess(front_rdi,stream)
        self.assertIn('FRONT-RDI-ON-MEDIA.txt" --expect front-rdi-only',s)
        self.assertIn('FRONT-PRE-NEUTRAL.txt" --expect neutral',s)
        self.assertIn('FRONT-RDI-CONFIG.txt',s)
        self.assertIn('pixelformat=pRAA',s)
        self.assertIn("['front_rdi_video_device']",s)
        self.assertIn('msm_vfe1_rdi0:0 msm_vfe1_rdi0:1',s)
        self.assertNotIn('"msm_csid1":1 -> "msm_vfe0_rdi0":0 [1]',s)
        self.assertIn('fmt:SRGGB10_1X10/3840x2160',s)
        self.assertIn('--frames 24 --require-distinct',s)
        self.assertNotIn('media-ctl -d "$MEDIA" -l \'"msm_csid1":4 -> "msm_vfe1_pix":0 [1]\'',s)
        self.assertNotIn("set-ctrl=test_pattern",s)
        self.assertNotIn("--execute",s)
        self.assertIn("insmod \"$LOOP_MOD\" devices=1 video_nr=91",s)

    def test_complete_root_pins_golden_and_one_shot_retire(self):
        inst=(HERE/"install-unarmed.sh").read_text()
        arm=(HERE/"arm-once.sh").read_text()
        run=(HERE/"run-once.sh").read_text()
        retire=(HERE/"retire-after-golden.sh").read_text()
        service=(HERE/"sp11-camera-e004kh-one-shot.service").read_text()
        for s in (inst,arm,run,retire):
            self.assertIn("e004kh",s)
        self.assertIn("CAMERA-STACK-MANIFEST.sha256",inst)
        self.assertIn("verify-package.py",inst)
        self.assertIn("FRONT_SOURCE_SHA",inst)
        self.assertIn("FRONT_APP_SHA",inst)
        self.assertIn("FRONT_ROUTE_SHA",inst)
        self.assertIn("FRONT_VALIDATOR_SHA",inst)
        self.assertIn("FRONT-OFFLINE-PIPE-DRYRUN.txt",arm)
        self.assertIn("FRONT-OFFLINE-PIPE-DRYRUN.txt",run)
        self.assertIn("grub-reboot \"$ID\"",arm)
        self.assertIn("saved_entry=sp11-audio-fullio-v19c",run)
        self.assertIn("grub-initrd-fallback.service",run)
        self.assertIn("grub2-common.service",run)
        self.assertIn("ExecStopPost=/usr/bin/systemctl --no-block reboot",service)
        self.assertIn("ATTEMPT-CONSUMED",run)
        self.assertIn("ATTEMPT-CONSUMED",retire)
        self.assertIn("rm -rf -- \"$D\"",retire)
        self.assertIn("camera-overlap-guard.sh",arm)
        self.assertIn("camera-overlap-guard.sh",retire)
        self.assertIn("FRONT-RDI-UNDO.txt",run)
        self.assertIn("FRONT-PHY-UNDO.txt",run)
        self.assertIn("FRONT-PIX-UNDO.txt",run)
        self.assertIn("REAR-RDI-UNDO.txt",run)
        self.assertIn("REAR-PHY-UNDO.txt",run)
        self.assertIn("FRONT-1080P-V4L2-TEXT-VALIDATION.txt",run)
        discovery=(HERE/"discover-unified.py").read_text()
        self.assertIn("'msm_vfe1_video0'",discovery)
        self.assertIn("'front_rdi_video_device'",discovery)

    def test_no_legacy_or_rear_pipeline_experiment(self):
        run=(HERE/"run-once.sh").read_text()
        for banned in ("rear-colorbar.raw","REAR-VIRTUAL-","REAR-4K-","FRAMES=240",
                       "FRAMES=120","stream-count=240","stream-count=120",
                       "SP11-Rear-Preview","IR_ILLUMINATION_ENABLE",
                       "FRONT-LAUNCH-DRYRUN.json"):
            self.assertNotIn(banned,run)
        install=(HERE/"install-unarmed.sh").read_text()
        self.assertNotIn("rear-bayer-4k-240",install)
        self.assertNotIn("nv12-4k-pipe-audit",install)
        self.assertIn("LOOP_SHA",install)
        self.assertIn("video_nr=91",run)
        self.assertIn("max-lateness=-1",run)
        self.assertIn("--stream-count=72",run)
        self.assertIn("--stream-count=24",run)
        self.assertIn('FRONT_NV12_AUDIT_SHA',install)
        self.assertIn('LOOP_SHA',install)
        self.assertNotIn("FRONT-LAUNCH-DRYRUN.json",(HERE/"arm-once.sh").read_text())

    def test_guide_fails_closed_on_wrong_front_qc10c_pixel_input(self):
        test_root=ROOT/"experiments/E004-front-ir-vd55g0/e004ke-front-rdi-rggb-raw-bypass"
        s=(test_root/"front-rggb10p-to-nv12-1080.c").read_text()
        self.assertIn("SRC_BYTES=SRC_STRIDE*SRC_H",s)
        self.assertIn("QC10C_DECODED=NO",s)
        self.assertIn("REAL_SENSOR_PROVEN_BY_CALLER=NO",s)


if __name__=="__main__":
    unittest.main()
