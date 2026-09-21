#!/usr/bin/env python3
"""E004kd: no-reuse/graph-before-optical/Golden-return source regression."""
from pathlib import Path
import subprocess
import unittest

HERE=Path(__file__).resolve().parent

class GraphGated4K(unittest.TestCase):
    def txt(self,name): return (HERE/name).read_text()
    def test_boot_scripts_valid(self):
        for name in ("run-once.sh","install-unarmed.sh","arm-once.sh","retire-after-golden.sh"):
            p=subprocess.run(["bash","-n",str(HERE/name)],capture_output=True,text=True,timeout=10)
            self.assertEqual(p.returncode,0,p.stderr)
        grub=subprocess.run(["grub-script-check"],
            input="\n".join(self.txt("99zzzzzz_sp11_camera_e004kd").splitlines()[2:])+"\n",
            capture_output=True,text=True,timeout=10)
        self.assertEqual(grub.returncode,0,grub.stderr)
    def test_unique_identity_and_source_pinning(self):
        install=self.txt("install-unarmed.sh")
        arm=self.txt("arm-once.sh")
        runner=self.txt("run-once.sh")
        grub=self.txt("99zzzzzz_sp11_camera_e004kd")
        service=self.txt("sp11-camera-e004kd-one-shot.service")
        identity="sp11-camera-e004kd-rear4k-extended-unique-app-one-shot"
        for text in (install,arm,grub): self.assertIn(identity,text)
        for text in (runner,grub,service): self.assertIn("sp11_camera_e004kd_rear4k_extended=1",text)
        for text in (install,arm,runner):
            self.assertNotIn("e004ka-rear4k-byte-boundary-one-shot",text)
        self.assertIn("CAMERA-STACK-MANIFEST.sha256",install)
        self.assertIn("35f658158f5d6d74ba5ea3a25c2d3d6b291fa0ba49dcd8b9c27005f124acc406",runner)
        self.assertIn("1f8378df078a118860e2bc35825fd127678ae164063e19e7d1cea2012d61259a",runner)
        self.assertIn("grub-reboot",arm)
        self.assertNotIn("grub-set-default",arm)
        self.assertIn("ATTEMPT-CONSUMED",runner)
        self.assertIn("--frames 240",runner)
        self.assertIn("--frames 120",runner)
        self.assertIn("ExecStopPost=/usr/bin/systemctl --no-block reboot",service)
    def test_exact_boot_paths_match(self):
        install=self.txt("install-unarmed.sh")
        entry=self.txt("99zzzzzz_sp11_camera_e004kd")
        self.assertIn("initrd.img-7.1.5-sp11-camera-e004kd-extended",entry)
        self.assertIn("initrd.img-7.1.5-sp11-camera-e004kd-extended",install)
        self.assertIn("sp11_entry=7.1.5-sp11-camera-e004kd-extended",entry)
    def test_graph_complete_before_any_rear_stream(self):
        runner=self.txt("run-once.sh")
        diagnostic=runner.index('camera-media-graph-diagnostic.py" --live --out-dir')
        graph=runner.index('[[ "$graph_rc" -eq 0')
        readback=runner.index('ACCEPTED-MEDIA-GRAPH.txt" > "$O/UNIFIED.tmp"')
        pattern=runner.index('--set-ctrl=test_pattern=1')
        optical=runner.index('--stream-count=240 --stream-to=-')
        self.assertTrue(diagnostic < graph < readback < pattern < optical)
        for part in ("MEDIA-DISCOVERY-ERROR.txt","MEDIA-DISCOVERY-RC.txt",
                     "UNIFIED-ERROR.txt","ACCEPTED-MEDIA-GRAPH.txt",
                     "4435c52d364e4030285c3e74372446eb452fa5722c355301201812a6d2341348"):
            self.assertIn(part,runner)
        self.assertIn('install -m 0600 "$DIAG_SOURCE" "$D/camera-media-graph-diagnostic.py"',self.txt("install-unarmed.sh"))
    def test_route_checker_python_invocation_before_capture(self):
        runner=self.txt("run-once.sh")
        route=HERE/"route-state.py"
        self.assertTrue(route.exists())
        self.assertEqual(route.stat().st_mode & 0o111,0,
                         "route helper is intentionally not executable")
        self.assertEqual(runner.count('/usr/bin/python3 "$H/route-state.py"'),4)
        self.assertNotIn('initial=$("$H/route-state.py"',runner)
        sample=HERE.parent/"e004ec-side-light-post-g3-shadow-observation"/"evidence"/"LOAD-MEDIA.txt"
        p=subprocess.run(["/usr/bin/python3",str(route),str(sample)],
                         capture_output=True,text=True,timeout=8)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("IF_ROUTE_STATE=",p.stdout)

    def test_single_intentional_gstreamer_sink_clock_change(self):
        runner=self.txt("run-once.sh")
        self.assertIn('v4l2sink device="$5" sync=true qos=true max-lateness=-1',runner)
        self.assertNotIn('v4l2sink device="$5" sync=true >',runner)
        self.assertIn('max-lateness=-1',runner)
        self.assertNotIn('v4l2sink device="$5" sync=false',runner)

    def test_no_front_stream_ir_and_retirement(self):
        runner=self.txt("run-once.sh")
        for forbidden in ("FRONTVIDEO --stream","ILLUMINATION_ON=1","front-imx681-capture --execute"):
            self.assertNotIn(forbidden,runner)
        retire=self.txt("retire-after-golden.sh")
        self.assertIn("--require-golden --require-no-camera-process",retire)
        self.assertIn("ATTEMPT-CONSUMED",retire)
        self.assertIn("sp11-camera-e004kd-rear4k-extended-unique-app-one-shot",retire)
        self.assertNotIn("sp11-camera-e004jq-rear4k-one-shot",retire)

if __name__=="__main__": unittest.main()
