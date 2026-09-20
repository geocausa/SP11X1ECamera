#!/usr/bin/env python3
"""E004jy text-only provenance, partial-frame and runtime safety regressions."""
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
VALIDATOR = HERE / "validate-partial.py"
RUNNER = HERE / "run-once.sh"


def logs(root: Path, read_count: int=58, app_count: int=58,
         result: str="PARTIAL", publisher_frames: int=180,
         invalid_timeline: bool=False):
    seq=[f"cap dqbuf: {i%4} seq: {i:6d} bytesused: 14321824 "
         f"ts: {10+i/22.62:.6f} field: None (ts-monotonic)\n"
         for i in range(publisher_frames)]
    virtual=[f"cap dqbuf: {i%4} seq: {i+6:6d} bytesused: 12441600 "
             "field: None (ts-copy)\n" for i in range(read_count)]
    shortfall = "NONE" if result == "PASS" else "INPUT_IDLE_TIMEOUT_OFFSET_0"
    application=(f"E004JX_NV12_APPSRC_CONSUMER={result} FRAMES={app_count} "
                 f"REQUESTED_FRAMES=90 INPUT_SHORTFALL_REASON={shortfall} "
                 "SIZE=12441600 VIDEO=NV12_3840x2160_30 "
                 "APP_CONSUMER=GSTREAMER_APPSINK_I420 PIPELINE_MS=3300 "
                 "SINK_OBSERVED_FPS=19.2727 SINK_P95_INTERARRIVAL_MS=64.800 "
                 "SINK_MAX_INTERARRIVAL_MS=91.300 "
                 f"INTERARRIVAL_SAMPLES={app_count-1} "
                 "SAMPLED_FRAME_PAYLOAD_VARIATION=YES SYNTHETIC_PTS_ONLY=YES "
                 "LIVE_CAMERA_PROVEN=NO VIRTUAL_WEBCAM_CREATED=NO\n")
    events=("PUBLISHER_START_NS=1000000000\n"
            "VIRTUAL_FORMAT_READY_NS=1200000000\n"
            f"READER_START_NS={1100000000 if invalid_timeline else 1300000000}\n"
            "READER_END_NS=5000000000\n"
            "PUBLISHER_END_NS=4300000000\n")
    for name, content in (("source", "".join(seq)),("virtual", "".join(virtual)),
                          ("app", application),("events",events)):
        (root/name).write_text(content)
    return [str(root/name) for name in ("source","virtual","app","events")]


class PartialReal4kAudit(unittest.TestCase):
    def validate(self, **kwargs):
        root=tempfile.TemporaryDirectory(prefix="sp11-e004jy-text-audit-")
        self.addCleanup(root.cleanup)
        options={key:value for key,value in kwargs.items() if key in (
            "read_count","app_count","result","publisher_frames","invalid_timeline")}
        args=logs(Path(root.name),**options)
        return subprocess.run(["python3",str(VALIDATOR),*args,"--publisher-rc",
                               str(kwargs.get("publisher_rc",0)),"--reader-rc",
                               str(kwargs.get("reader_rc",1))],
                              capture_output=True,text=True,timeout=5)

    def test_realistic_partial_keeps_both_cadences_and_fails_closed(self):
        p=self.validate()
        self.assertEqual(p.returncode,1,p.stderr)
        for part in ("E004JY_TEXT_ONLY_TELEMETRY=PARTIAL_FAIL_CLOSED",
                     "sensor_frames=180","sensor_missing_seq=0",
                     "virtual_full_frames=58","virtual_missing_seq=0",
                     "app_verdict=PARTIAL","app_frames=58",
                     "app_observed_fps=19.2727","format_ready_to_reader_ms=100.0",
                     "CAMERA_FPS_INDEPENDENT_OF_SYNTHETIC_PTS=YES"):
            self.assertIn(part,p.stdout)

    def test_complete_90_and_producer_180_allowed_only_if_all_exit_cleanly(self):
        p=self.validate(read_count=90,app_count=90,result="PASS",reader_rc=0)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("E004JY_TEXT_ONLY_TELEMETRY=COMPLETE_PASS",p.stdout)
        self.assertIn("app_frames=90",p.stdout)

    def test_false_complete_or_missing_frames_never_returns_success(self):
        p=self.validate(read_count=58,app_count=58,result="PASS",reader_rc=0)
        self.assertEqual(p.returncode,2)
        self.assertIn("FALSE_APPLICATION_SUCCESS",p.stderr)
        p=self.validate(read_count=58,app_count=59)
        self.assertEqual(p.returncode,2)
        self.assertIn("INCONSISTENT_APP_SINK_FRAME_COUNT",p.stderr)
        p=self.validate(publisher_frames=179,reader_rc=0)
        self.assertEqual(p.returncode,2)
        self.assertIn("PUBLISHER_SUCCESS_WITH_INCOMPLETE_SOURCE",p.stderr)

    def test_bad_timeline_is_rejected_before_any_rate_inference(self):
        p=self.validate(invalid_timeline=True)
        self.assertEqual(p.returncode,2)
        self.assertIn("INVALID_SUBSCRIBER_TIMELINE",p.stderr)

    def test_runner_pins_app_and_validator_before_activating_camera(self):
        src=RUNNER.read_text()
        self.assertIn("sp11_camera_e004jy_rear4k_partial=1",src)
        a=src.index("validate-partial.py")
        camera=src.index("modprobe i2c_qcom_cci")
        self.assertLess(a,camera)
        graph=src.index('camera-media-graph-diagnostic.py" --live --out-dir')
        optical=src.index("--stream-count=180 --stream-to=-")
        self.assertLess(graph,optical)
        self.assertIn("REAR-4K-PROCESS-EVENTS.txt",src)
        self.assertIn("REAR-4K-PUBLISHER-DONE.txt",src)
        self.assertIn("publisher_inner_rc=$?",src)
        self.assertIn("--idle-seconds 6",src)
        self.assertIn("E004JY_BOUNDED_REAL_4K_APP_INCOMPLETE_OR_UNVERIFIED_FAIL_CLOSED",src)
        for forbidden in ("grub-set-default","ILLUMINATION_ON=1","front-imx681-capture --execute"):
            self.assertNotIn(forbidden,src)
        install=(HERE/"install-unarmed.sh").read_text()
        self.assertIn("10a1916de8e49c17e20b3493f49618108298a2835a4dbac255a02120eb519e69",install)
        self.assertIn("e004jx-rear-4k-partial-telemetry",install)


if __name__=="__main__":
    unittest.main()
