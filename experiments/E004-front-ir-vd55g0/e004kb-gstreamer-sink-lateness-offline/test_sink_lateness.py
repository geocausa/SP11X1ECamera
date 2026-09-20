#!/usr/bin/python3
"""E004kb: installed GStreamer source/sink property and paced-source regression."""
from pathlib import Path
import subprocess
import unittest

HERE=Path(__file__).resolve().parent
SCRIPT=HERE/"gst_sink_lateness_probe.py"


class GstLateFrames(unittest.TestCase):
    def test_installed_real_v4l2sink_defaults(self):
        from gst_sink_lateness_probe import inspect_default_v4l2sink
        props=inspect_default_v4l2sink()
        self.assertEqual(props["v4l2sink_max_lateness_default_ns"],5000000)
        self.assertTrue(props["v4l2sink_sync_default"])
        self.assertTrue(props["v4l2sink_qos_default"])

    def test_rawvideoparse_30fps_generates_non_wall_clock_pts(self):
        from gst_sink_lateness_probe import probe_rawvideoparse_pts, FRAME_NS
        self.assertEqual(probe_rawvideoparse_pts(),[0,FRAME_NS,2*FRAME_NS])

    def test_22fps_real_fdsrc_to_30fps_caps_default_late_drops(self):
        from gst_sink_lateness_probe import simulate_paced_fdsrc
        n=35
        model=simulate_paced_fdsrc("v4l2sink_default_clock_model",n,22)
        unlimited=simulate_paced_fdsrc("no_lateness_drop",n,22)
        unsynced=simulate_paced_fdsrc("unsynced",n,22)
        self.assertEqual(model["synthetic_paced_fdsrc_frames_written"],n)
        self.assertEqual(model["synthetic_fdsrc_bytes_written"],n*320*180*3//2)
        self.assertGreater(model["fakesink_late_dropped_frames"],0)
        self.assertLess(model["fakesink_rendered_frames"],n)
        self.assertEqual(unlimited["fakesink_rendered_frames"],n)
        self.assertEqual(unsynced["fakesink_rendered_frames"],n)
        for item in (model,unlimited,unsynced):
            self.assertFalse(item["real_camera_or_4k_device_activated"])

    def test_source_only_no_camera_activation_or_pixel_file(self):
        s=SCRIPT.read_text()
        for banned in ("/dev/video","--set-ctrl","media-ctl",
                       "insmod","modprobe","grub-reboot","BootNext",
                       "ILLUMINATION_ON","fopen(","O_CREAT"):
            self.assertNotIn(banned,s)
        self.assertIn("Gst.ElementFactory.make(\"v4l2sink\")",s)
        self.assertIn("fakesink name=sink signal-handoffs=true",s)


if __name__=="__main__":
    unittest.main()
