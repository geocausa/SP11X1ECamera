#!/usr/bin/env python3
"""E004kd text-only provenance, partial-frame and runtime safety regressions."""
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
VALIDATOR = HERE / "validate-partial.py"
RUNNER = HERE / "run-once.sh"


def logs(root: Path, read_count: int=58, app_count: int=58,
         result: str="PARTIAL", publisher_frames: int=240,
         invalid_timeline: bool=False, meter_frames: int | None=None,
         meter_tail: int=0, meter_result: str | None=None):
    seq=[f"cap dqbuf: {i%4} seq: {i:6d} bytesused: 14321824 "
         f"ts: {10+i/22.62:.6f} field: None (ts-monotonic)\n"
         for i in range(publisher_frames)]
    virtual=[f"cap dqbuf: {i%4} seq: {i+6:6d} bytesused: 12441600 "
             "field: None (ts-copy)\n" for i in range(read_count)]
    shortfall = "NONE" if result == "PASS" else "INPUT_IDLE_TIMEOUT_OFFSET_0"
    application=(f"E004JX_NV12_APPSRC_CONSUMER={result} FRAMES={app_count} "
                 f"REQUESTED_FRAMES=120 INPUT_SHORTFALL_REASON={shortfall} "
                 "SIZE=12441600 VIDEO=NV12_3840x2160_30 "
                 "APP_CONSUMER=GSTREAMER_APPSINK_I420 PIPELINE_MS=3300 "
                 "SINK_OBSERVED_FPS=19.2727 SINK_P95_INTERARRIVAL_MS=64.800 "
                 "SINK_MAX_INTERARRIVAL_MS=91.300 "
                 f"INTERARRIVAL_SAMPLES={app_count-1} "
                 "SAMPLED_FRAME_PAYLOAD_VARIATION=YES SYNTHETIC_PTS_ONLY=YES "
                 "DISTINCT_PAYLOADS_VERIFIED=YES "
                 "LIVE_CAMERA_PROVEN=NO VIRTUAL_WEBCAM_CREATED=NO\n")
    events=("PUBLISHER_START_NS=1000000000\n"
            "VIRTUAL_FORMAT_READY_NS=1200000000\n"
            f"READER_START_NS={1100000000 if invalid_timeline else 1300000000}\n"
            "READER_END_NS=5000000000\n"
            "PUBLISHER_END_NS=4300000000\n")
    n=app_count if meter_frames is None else meter_frames
    mstatus=("PASS" if n==120 and result=="PASS" else "PARTIAL") if meter_result is None else meter_result
    total=n*12441600+meter_tail
    meter=(f"E004JZ_4K_PIPE={mstatus} REQUESTED_FRAMES=120 "
           f"FULL_FRAMES={n} BYTES_IN={total} BYTES_OUT={total} "
           f"INCOMPLETE_TAIL_BYTES={meter_tail} "
           f"TERMINATION={'EOF' if mstatus=='PASS' else 'INPUT_IDLE'} "
           "CAMERA_PROVEN_BY_THIS_TOOL=NO PIXELS_SAVED=NO\\n")
    for name, content in (("source", "".join(seq)),("virtual", "".join(virtual)),
                          ("app", application),("events",events),("meter",meter)):
        (root/name).write_text(content)
    return [str(root/name) for name in ("source","virtual","app","events","meter")]


class PartialReal4kAudit(unittest.TestCase):
    def validate(self, **kwargs):
        root=tempfile.TemporaryDirectory(prefix="sp11-e004kd-text-audit-")
        self.addCleanup(root.cleanup)
        options={key:value for key,value in kwargs.items() if key in (
            "read_count","app_count","result","publisher_frames","invalid_timeline",
            "meter_frames","meter_tail","meter_result")}
        args=logs(Path(root.name),**options)
        return subprocess.run(["python3",str(VALIDATOR),*args[:4],
                               "--meter",args[4],"--publisher-rc",
                               str(kwargs.get("publisher_rc",0)),"--reader-rc",
                               str(kwargs.get("reader_rc",1))],
                              capture_output=True,text=True,timeout=5)

    def test_realistic_partial_keeps_both_cadences_and_fails_closed(self):
        p=self.validate()
        self.assertEqual(p.returncode,1,p.stderr)
        for part in ("E004KD_TEXT_ONLY_TELEMETRY=PARTIAL_FAIL_CLOSED",
                     "sensor_frames=240","sensor_missing_seq=0",
                     "virtual_full_frames=58","virtual_missing_seq=0",
                     "app_verdict=PARTIAL","app_frames=58",
                     "app_observed_fps=19.2727","format_ready_to_reader_ms=100.0",
                     "CAMERA_FPS_INDEPENDENT_OF_SYNTHETIC_PTS=YES"):
            self.assertIn(part,p.stdout)

    def test_complete_120_and_producer_240_allowed_only_if_all_exit_cleanly(self):
        p=self.validate(read_count=120,app_count=120,result="PASS",reader_rc=0)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("E004KD_TEXT_ONLY_TELEMETRY=COMPLETE_PASS",p.stdout)
        self.assertIn("app_frames=120",p.stdout)

    def test_false_complete_or_missing_frames_never_returns_success(self):
        p=self.validate(read_count=58,app_count=58,result="PASS",reader_rc=0)
        self.assertEqual(p.returncode,2)
        self.assertIn("FALSE_APPLICATION_SUCCESS",p.stderr)
        p=self.validate(read_count=58,app_count=59)
        self.assertEqual(p.returncode,2)
        self.assertIn("INCONSISTENT_APP_SINK_FRAME_COUNT",p.stderr)
        p=self.validate(publisher_frames=239,reader_rc=0)
        self.assertEqual(p.returncode,2)
        self.assertIn("PUBLISHER_SUCCESS_WITH_INCOMPLETE_SOURCE",p.stderr)

    def test_meter_partial_and_byte_delta_preserved(self):
        p=self.validate(read_count=69,app_count=68,meter_frames=68,
                        meter_tail=12439552,reader_rc=124)
        self.assertEqual(p.returncode,1,p.stderr)
        self.assertIn("meter_full_4k_frames=68",p.stdout)
        self.assertIn("meter_incomplete_tail_bytes=12439552",p.stdout)
        self.assertIn("meter_output_minus_app_complete_bytes=12439552",p.stdout)

    def test_meter_full_frames_less_than_app_claim_is_invalid(self):
        p=self.validate(read_count=69,app_count=68,meter_frames=67)
        self.assertEqual(p.returncode,2)
        self.assertIn("APP_COUNT_EXCEEDS_FULL_BYTE_METER_FRAMES",p.stderr)

    def test_meter_cannot_claim_pass_with_incomplete_tail(self):
        p=self.validate(read_count=120,app_count=120,result="PASS",reader_rc=0,
                        meter_frames=119,meter_tail=12439552,meter_result="PASS")
        self.assertEqual(p.returncode,2)
        self.assertIn("FALSE_BYTE_METER_SUCCESS",p.stderr)

    def test_fake_unique_flag_missing_on_complete_app_rejected(self):
        root=tempfile.TemporaryDirectory(prefix="sp11-e004kd-unique-negative-")
        self.addCleanup(root.cleanup)
        args=logs(Path(root.name),read_count=120,app_count=120,result="PASS")
        app=Path(args[2]);app.write_text(app.read_text().replace(
            "DISTINCT_PAYLOADS_VERIFIED=YES","DISTINCT_PAYLOADS_VERIFIED=NO"))
        p=subprocess.run(["python3",str(VALIDATOR),*args[:4],
                          "--meter",args[4],"--publisher-rc","0",
                          "--reader-rc","0"],capture_output=True,text=True,timeout=5)
        self.assertEqual(p.returncode,2)
        self.assertIn("COMPLETE_APP_DID_NOT_VERIFY_ALL_FRAME_PAYLOADS_DISTINCT",p.stderr)

    def test_bad_timeline_is_rejected_before_any_rate_inference(self):
        p=self.validate(invalid_timeline=True)
        self.assertEqual(p.returncode,2)
        self.assertIn("INVALID_SUBSCRIBER_TIMELINE",p.stderr)

    def test_runner_pins_app_and_validator_before_activating_camera(self):
        src=RUNNER.read_text()
        self.assertIn("sp11_camera_e004kd_rear4k_extended=1",src)
        a=src.index("validate-partial.py")
        camera=src.index("modprobe i2c_qcom_cci")
        self.assertLess(a,camera)
        graph=src.index('camera-media-graph-diagnostic.py" --live --out-dir')
        optical=src.index("--stream-count=240 --stream-to=-")
        self.assertLess(graph,optical)
        self.assertIn("REAR-4K-PROCESS-EVENTS.txt",src)
        self.assertIn("REAR-4K-PUBLISHER-DONE.txt",src)
        self.assertIn("publisher_inner_rc=$?",src)
        self.assertIn("--idle-seconds 6",src)
        self.assertIn("E004KD_BOUNDED_REAL_4K_APP_INCOMPLETE_OR_UNVERIFIED_FAIL_CLOSED",src)
        for forbidden in ("grub-set-default","ILLUMINATION_ON=1","front-imx681-capture --execute"):
            self.assertNotIn(forbidden,src)
        install=(HERE/"install-unarmed.sh").read_text()
        self.assertIn("fd23a7eec5fbdb5dd8576b3682652633e2dab60ffe0df9a6e6416bff430f40ea",install)
        self.assertIn("e004jx-rear-4k-partial-telemetry",install)
        self.assertIn("E004JZ_4K_PIPE",src)
        self.assertIn("--meter",src)


if __name__=="__main__":
    unittest.main()
