#!/usr/bin/python3
"""E004ki camera-free exact route-switching state and negative regression."""
from pathlib import Path
import runpy
import re
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
ARCHIVE=(ROOT/"experiments/E004-front-ir-vd55g0/"
         "e004ec-side-light-post-g3-shadow-observation/evidence/LOAD-MEDIA.txt")
MOD=runpy.run_path(str(HERE/"camera-session-contract.py"))

def toggled(text,source,target,pad,enabled):
    block=re.search(rf"^- entity \d+: {re.escape(source)} \("
                    rf".*?(?=^- entity |\Z)",text,re.M|re.S)
    assert block is not None,source
    status="ENABLED" if enabled else ""
    original=block.group(0)
    original_link=re.search(
       rf'(^\s*-> "{re.escape(target)}":{pad} )\[([^\]]*)\]\s*$',
       original,re.M)
    assert original_link is not None,(source,target,pad)
    before=original_link.group(0)
    after=original_link.group(1)+f"[{status}]"
    changed=text[:block.start()]+original.replace(before,after,1)+text[block.end():]
    # A real media graph reports each edge at both source and sink.
    source_pad=1 if source.startswith("msm_csiphy") or "rdi" in target else 4
    reverse=re.search(rf"^- entity \d+: {re.escape(target)} \("
                      rf".*?(?=^- entity |\Z)",changed,re.M|re.S)
    assert reverse is not None
    old=reverse.group(0)
    new=re.sub(rf'(<- "{re.escape(source)}":{source_pad} )\[[^\]]*\]',
               lambda m:m[1]+f"[{status}]",old,count=1)
    assert new!=old or before==after
    return changed[:reverse.start()]+new+changed[reverse.end():]

def from_neutral(front=False,rear=False,pix=False,cross=False):
    text=ARCHIVE.read_text()
    if front or pix or cross:
        text=toggled(text,"msm_csiphy2","msm_csid1",0,True)
        if front:text=toggled(text,"msm_csid1","msm_vfe1_rdi0",0,True)
        if pix:text=toggled(text,"msm_csid1","msm_vfe1_pix",0,True)
        if cross:text=toggled(text,"msm_csid1","msm_vfe0_rdi0",0,True)
    if rear:
        text=toggled(text,"msm_csiphy1","msm_csid0",0,True)
        text=toggled(text,"msm_csid0","msm_vfe0_rdi0",0,True)
    return text

class NativeCameraSwitch(unittest.TestCase):
    def test_full_front_neutral_rear_neutral_cycle(self):
        n=ARCHIVE.read_text()
        f=from_neutral(front=True)
        r=from_neutral(rear=True)
        states=[n,f,n,r,n]
        proof=MOD["full_cycle"](states,[(True,True)]*4)
        self.assertEqual(proof["verified_media_graph_phases"],
            ["neutral","front-rdi-only","neutral","rear-only","neutral"])
        self.assertEqual(proof["transition_count"],4)
        self.assertFalse(proof["real_front_rear_switching_proven"])
        self.assertFalse(proof["boot_service_driver_or_sensor_activated"])
        self.assertEqual(proof["front_device_contract"]["node"],"/dev/video91")
        self.assertEqual(proof["rear_device_contract"]["node"],"/dev/video90")
        self.assertEqual(proof["front_device_contract"]["output_bytes_per_frame"],3110400)
        self.assertEqual(proof["rear_device_contract"]["output_bytes_per_frame"],12441600)

    def test_reject_direct_switch_without_neutral_or_process_exit(self):
        check=MOD["authorize"]
        for before,after in (("front-rdi-only","rear-only"),
                              ("rear-only","front-rdi-only"),
                              ("neutral","neutral")):
            with self.assertRaises(ValueError):
                check(before,after,True,True)
        for prior,new in (("neutral","front-rdi-only"),
                          ("front-rdi-only","neutral"),
                          ("neutral","rear-only"),
                          ("rear-only","neutral")):
            for exit_proofs in ((False,True),(True,False),(False,False)):
                with self.assertRaises(ValueError):
                    check(prior,new,*exit_proofs)

    def test_reject_front_pix_front_cross_instance_and_mixed_routes(self):
        for graph in (from_neutral(pix=True),
                      from_neutral(cross=True),
                      from_neutral(front=True,rear=True),
                      from_neutral(front=True,pix=True)):
            with self.assertRaises(ValueError):
                MOD["classify"](graph)

    def test_partial_or_truncated_media_graph_fails(self):
        graph=ARCHIVE.read_text()
        self.assertEqual(MOD["classify"](graph)[0],"neutral")
        with self.assertRaises(ValueError):
            MOD["classify"](graph.replace("- entity ","- entity OMIT ",1))
        partial=toggled(graph,"msm_csiphy2","msm_csid1",0,True)
        with self.assertRaises(ValueError):
            MOD["classify"](partial)
        partial=toggled(graph,"msm_csid0","msm_vfe0_rdi0",0,True)
        with self.assertRaises(ValueError):
            MOD["classify"](partial)
        with self.assertRaises(ValueError):
            MOD["classify"](graph.replace('"msm_vfe1_rdi0":0','"DOES_NOT_EXIST":0'))

    def test_wrong_sequence_and_fake_intermediate_neutral_fail(self):
        n=ARCHIVE.read_text()
        f=from_neutral(front=True);r=from_neutral(rear=True)
        for steps in ([n,f,r,n,n],[n,f,f,r,n],[n,r,n,f,n],[n,f,n,r,f]):
            with self.assertRaises(ValueError):
                MOD["full_cycle"](steps,[(True,True)]*4)
        with self.assertRaises(ValueError):
            MOD["full_cycle"]([n,f,n,r,n],
                [(True,True),(False,True),(True,True),(True,True)])

    def test_unchecked_ir_and_other_csid_routes_rejected(self):
        n=ARCHIVE.read_text()
        for source,target in (("msm_csiphy0","msm_csid0"),
                              ("msm_csiphy4","msm_csid3"),
                              ("msm_csiphy2","msm_csid2")):
            bad=toggled(n,source,target,0,True)
            with self.assertRaises(ValueError): MOD["classify"](bad)

    def test_asymmetric_duplicate_and_truncated_edges_rejected(self):
        n=ARCHIVE.read_text()
        bad=n.replace('-> "msm_csid2":0 []','-> "msm_csid2":0 [ENABLED]',1)
        with self.assertRaises(ValueError): MOD["classify"](bad)
        for old,new in (('-> "msm_csid2":0 []',''),
                        ('-> "msm_csid2":0 []','-> "msm_csid2":0 [UNKNOWN]'),
                        ('[ENABLED,IMMUTABLE]','[IMMUTABLE]'),
                        ('- entity 4: msm_csiphy1','- entity 1: msm_csiphy1'),
                        ('/dev/v4l-subdev1','/dev/v4l-subdev0')):
            with self.assertRaises(ValueError): MOD["classify"](n.replace(old,new,1))

    def test_i2c_adapter_numbers_remain_dynamic(self):
        n=ARCHIVE.read_text().replace('imx681 1-0010','imx681 42-0010')
        self.assertEqual(MOD["classify"](n)[0],"neutral")

    def test_cli_only_reads_fixture_and_does_not_open_cameras(self):
        program=(HERE/"camera-session-contract.py").read_text()
        for forbidden in ("subprocess","os.system","modprobe","insmod","media-ctl",
                          "grub-reboot","open('/dev/","/dev/media",
                          "V4L2_CID_TEST_PATTERN","ILLUMINATION_ON",
                          "O_CREAT","fopen("):
            self.assertNotIn(forbidden,program)
        self.assertIn('"real_front_rear_switching_proven":False',program)
        self.assertIn('"golden_persistent_camera_installation_proven":False',program)
        with tempfile.TemporaryDirectory(prefix="sp11-e004ki-snapshots-") as tmp:
            graphs=[ARCHIVE.read_text(),from_neutral(front=True),ARCHIVE.read_text(),
                    from_neutral(rear=True),ARCHIVE.read_text()]
            files=[]
            for i,data in enumerate(graphs):
                path=Path(tmp)/f"snapshot_{i}.txt"
                path.write_text(data);files.extend(("--snapshot",str(path)))
            run=subprocess.run(["python3",str(HERE/"camera-session-contract.py"),
                 *files,"--all-processes-stopped"],
                capture_output=True,text=True,timeout=10)
            self.assertEqual(run.returncode,0,run.stderr)
            self.assertIn('"transition_count": 4',run.stdout)
            bad=subprocess.run(["python3",str(HERE/"camera-session-contract.py"),
                 *files],capture_output=True,text=True,timeout=10)
            self.assertNotEqual(bad.returncode,0)

if __name__=="__main__":
    unittest.main()
