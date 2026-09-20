#!/usr/bin/env python3
"""E004jw: regression for real-source/virtual/app text-only cadence reporting."""
from pathlib import Path
import subprocess
import tempfile
import unittest

HERE=Path(__file__).resolve().parent
RUNNER=HERE/"run-once.sh"
PREFIX='python3 - "$O/REAL-REAR-CAPTURE180.txt"'
SUFFIX="\n[[ ! -e \"$O/rear-normal90.raw\""


def validator_code():
    src=RUNNER.read_text()
    a=src.index(PREFIX)
    b=src.index(SUFFIX,a)
    result=src[a:b]
    return result.split("<<'PY'\n",1)[1].rsplit("\nPY",1)[0]+"\n"


def synthetic_logs(root, source_skip=False, virtual_skip=True, bad_app=False):
    source=[]
    for index in range(180):
        seq=index+(1 if source_skip and index>30 else 0)
        source.append(f"cap dqbuf: {index%4} seq: {seq:6d} bytesused: 14321824 "
                      f"ts: {13.0+index/29.95:.6f} field: None (ts-monotonic, ts-src-eof)\n")
    virtual=[]
    for index in range(90):
        seq=index+6+(2 if virtual_skip and index>0 else 0)
        virtual.append(f"cap dqbuf: {index%2} seq: {seq:6d} bytesused: 12441600 "
                       "field: None (ts-copy, ts-src-eof)\n")
    app=("E004JV_NV12_APPSRC_CONSUMER=PASS FRAMES=90 "
         "SIZE=12441600 VIDEO=NV12_3840x2160_30 APP_CONSUMER=GSTREAMER_APPSINK_I420 "
         "PIPELINE_MS=3090 SINK_OBSERVED_FPS=29.9000 "
         "SINK_P95_INTERARRIVAL_MS=34.300 "
         "SINK_MAX_INTERARRIVAL_MS=38.200 INTERARRIVAL_SAMPLES=89 "
         "SAMPLED_FRAME_PAYLOAD_VARIATION=YES SYNTHETIC_PTS_ONLY=YES "
         "LIVE_CAMERA_PROVEN=NO VIRTUAL_WEBCAM_CREATED=NO\n")
    if bad_app:
        app=app.replace("INTERARRIVAL_SAMPLES=89","INTERARRIVAL_SAMPLES=88")
    for name,data in (("cap", "".join(source)),("virt", "".join(virtual)),("app",app)):
        (root/name).write_text(data)
    return [str(root/x) for x in ("cap","virt","app")]


class CadenceText(unittest.TestCase):
    def run_parser(self,source_skip=False,virtual_skip=True,bad_app=False):
        with tempfile.TemporaryDirectory(prefix="sp11-e004jw-cadence-") as td:
            paths=synthetic_logs(Path(td),source_skip,virtual_skip,bad_app)
            return subprocess.run(["python3","-",*paths],input=validator_code(),
                capture_output=True,text=True,timeout=8)

    def test_full_virtual_gap_report_without_false_lossless_claim(self):
        p=self.run_parser()
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("source_frames=180",p.stdout)
        self.assertIn("source_missing_sequence_count=0",p.stdout)
        self.assertIn("virtual_frames=90",p.stdout)
        self.assertIn("virtual_missing_sequence_count=2",p.stdout)
        self.assertIn("app_real_sink_observed_fps=29.9000",p.stdout)
        self.assertIn("app_p95_interarrival_ms=34.300",p.stdout)
        self.assertIn("app_sampled_payload_variation=YES",p.stdout)
        self.assertIn("4K30_LONGRUN_PARITY_PROVEN=NO",p.stdout)

    def test_source_drop_is_reported_not_hidden(self):
        p=self.run_parser(source_skip=True,virtual_skip=False)
        self.assertEqual(p.returncode,0,p.stderr)
        self.assertIn("source_missing_sequence_count=1",p.stdout)
        self.assertIn("virtual_missing_sequence_count=0",p.stdout)

    def test_false_app_count_fails(self):
        p=self.run_parser(bad_app=True)
        self.assertNotEqual(p.returncode,0)
        self.assertIn("application_wall_cadence_not_recorded",p.stderr)

    def test_new_identity_routes_and_app_before_video(self):
        src=RUNNER.read_text()
        graph=src.index('camera-media-graph-diagnostic.py" --live --out-dir')
        pattern=src.index("--set-ctrl=test_pattern=1")
        optical=src.index("--stream-count=180 --stream-to=-")
        self.assertTrue(graph<pattern<optical)
        self.assertEqual(src.count('/usr/bin/python3 "$H/route-state.py"'),4)
        for token in ("--stream-count=90 --stream-to=-","--frames 90",
                      "SINK_OBSERVED_FPS","virtual_missing_sequence_count"):
            self.assertIn(token,src)
        self.assertNotIn("sp11-camera-e004ju-python-route-rear4k-one-shot",src)

if __name__=="__main__": unittest.main()
