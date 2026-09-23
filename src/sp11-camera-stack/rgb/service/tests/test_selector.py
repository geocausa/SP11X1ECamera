#!/usr/bin/env python3
"""Offline root selector acceptance using the existing exact 119-edge fake OS."""
import sys
import unittest
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
from test_rgb_device_backend import DISCOVERY, OwnerFake
from rgb_device_backend import RGBDeviceBackend
from session import RGBSession, SessionRejected
from selector import RGBSelector
import rgbctl


class RGBSelectorTests(unittest.TestCase):
    def setUp(self):
        self.os=OwnerFake()
        self.s=RGBSelector(RGBSession(RGBDeviceBackend(DISCOVERY,self.os)))

    def test_manual_front_rear_off_quit_exact_controller_and_unit(self):
        self.assertEqual(self.s.dispatch("status"),{"status":"OK","selected":"off"})
        self.assertEqual(self.s.dispatch("front"),{"status":"OK","selected":"front"})
        self.assertEqual(self.s.dispatch("front"),{"status":"OK","selected":"front","already_active":True})
        self.assertEqual(self.s.dispatch("status"),{"status":"OK","selected":"front"})
        self.assertEqual(self.s.dispatch("rear"),{"status":"OK","selected":"rear"})
        self.assertEqual(self.os.invocations,{"front":1,"rear":1})
        self.assertEqual(self.s.session.completed_stops,1)
        self.assertEqual(self.s.dispatch("off"),{"status":"OK","selected":"off"})
        self.assertEqual(self.s.dispatch("quit"),
                         {"status":"OK","selected":"off","finished":True})
        self.assertTrue(self.s.finished)
        self.assertEqual(self.os.phase,set())
        self.assertEqual(self.s.session.completed_stops,2)
        self.assertIsNone(self.os.active)

    def test_rejected_commands_do_not_mutate(self):
        for command in ("ir","sleep","standby","run shell","front; reboot",None,""):
            self.assertEqual(self.s.dispatch(command)["status"],"REJECTED")
        self.assertEqual(self.os.commands,[])
        self.assertEqual(self.s.dispatch("quit")["status"],"OK")
        with self.assertRaisesRegex(SessionRejected,"TERMINAL"):
            self.s.dispatch("front")

    def test_wrong_live_graph_status_rejected(self):
        self.s.dispatch("front")
        self.os.phase=set()
        with self.assertRaisesRegex(SessionRejected,"GRAPH_DRIFT"):
            self.s.dispatch("status")
        self.assertEqual(self.os.active,"front")

    def test_missing_publisher_status_rejected(self):
        self.s.dispatch("rear")
        self.os.active=None
        with self.assertRaisesRegex(SessionRejected,"PUBLISHER"):
            self.s.dispatch("status")
        self.assertEqual(self.s.session.active,"rear")

    def test_reader_open_blocks_switch_and_poisoned(self):
        self.s.dispatch("front")
        self.os.reader_open=True
        with self.assertRaisesRegex(SessionRejected,"FDS_STILL_OPEN"):
            self.s.dispatch("rear")
        self.assertTrue(self.s.session.poisoned)
        self.assertEqual(self.os.phase,set(self.s.session.backend.graph.read_graph() and
                                           __import__("media_backend").route_policy.FRONT))

    def test_failed_streamoff_blocks_switch_and_poisoned(self):
        self.s.dispatch("rear")
        self.os.stops_ok=False
        with self.assertRaisesRegex(SessionRejected,"STREAMOFF"):
            self.s.dispatch("front")
        self.assertTrue(self.s.session.poisoned)
        self.assertEqual(self.os.phase,set(__import__("media_backend").route_policy.REAR))

    def test_cli_reject_invalid_action_before_socket_or_privilege(self):
        for action in ("ir","suspend","on","front; reboot"):
            with self.assertRaises(ValueError):
                rgbctl.command("e004ma",action)
        with self.assertRaises(ValueError):
            rgbctl.command("e004ma;reboot","front")
        with patch.object(rgbctl.os,"geteuid",return_value=1000):
            with self.assertRaises(PermissionError):
                rgbctl.command("e004ma","front")


if __name__=="__main__":
    unittest.main()
