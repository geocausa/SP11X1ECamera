#!/usr/bin/env python3
"""Camera-free contract: test state machine with an injected fake backend."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from session import RGBSession, SessionRejected


class FakeBackend:
    def __init__(self):
        self.phase = "neutral"
        self.authority = True
        self.lock = True
        self.no_users = True
        self.ir_safe = True
        self.publisher = None
        self.started = []
        self.stopped = []
        self.configured = []
        self.transitions = []
        self.fail_at = None
        self.stop_valid = True

    def fail(self, stage):
        if self.fail_at == stage:
            raise RuntimeError("INJECT_" + stage)

    def authorized(self):
        self.fail("authorized")
        return self.authority

    def holds_exclusive_lease(self):
        self.fail("lease")
        return self.lock

    def ir_off(self):
        self.fail("ir")
        return self.ir_safe

    def camera_users_closed(self):
        self.fail("closed")
        return self.no_users

    def route_phase(self):
        self.fail("graph")
        return self.phase

    def activate_route(self, camera):
        self.fail("activate_before")
        assert self.phase == "neutral" and self.publisher is None
        self.transitions.append(("neutral", camera))
        self.phase = camera
        self.fail("activate_after")

    def configure(self, camera):
        self.fail("configure")
        assert self.phase == camera
        self.configured.append(camera)

    def start_publisher(self, camera):
        self.fail("start_before")
        assert self.publisher is None and self.phase == camera
        self.publisher = camera
        self.started.append(camera)
        self.no_users = False
        self.fail("start_after")

    def publisher_running(self, camera):
        self.fail("running")
        return self.publisher == camera

    def stop_publisher(self, camera):
        self.fail("stop_before")
        assert self.publisher == camera
        if self.stop_valid:
            self.publisher = None
            self.stopped.append(camera)
            self.no_users = True
        self.fail("stop_after")
        return self.stop_valid

    def neutralize_route(self, camera):
        self.fail("neutral_before")
        assert self.phase == camera and self.publisher is None
        self.transitions.append((camera, "neutral"))
        self.phase = "neutral"
        self.fail("neutral_after")


class ControllerTests(unittest.TestCase):
    def setUp(self):
        self.b = FakeBackend()
        self.s = RGBSession(self.b)

    def test_four_process_selection_neutral_every_close(self):
        for camera in ("front", "rear", "front", "rear"):
            self.s.open(camera)
            self.assertEqual(self.s.active, camera)
            self.s.stop()
            self.assertIsNone(self.s.active)
            self.assertEqual(self.b.phase, "neutral")
        self.assertEqual(self.s.completed_stops, 4)
        self.assertEqual(self.b.started, ["front", "rear", "front", "rear"])
        self.assertEqual(self.b.stopped, self.b.started)
        self.assertEqual(len(self.b.transitions), 8)

    def test_switch_drains_before_activation(self):
        self.s.open("front")
        self.s.switch("rear")
        self.assertEqual(self.b.transitions, [
            ("neutral", "front"), ("front", "neutral"),
            ("neutral", "rear")])
        self.assertEqual(self.s.completed_stops, 1)
        self.assertEqual(self.s.active, "rear")
        self.s.close()
        self.assertIsNone(self.s.active)

    def test_input_validation_never_mutates_route(self):
        for name in ("ir", "none", "", "../front", None):
            with self.subTest(camera=name), self.assertRaises(SessionRejected):
                self.s.open(name)
            self.assertFalse(self.s.poisoned)
            self.assertEqual(self.b.transitions, [])
        with self.assertRaisesRegex(SessionRejected, "NO_ACTIVE_CAMERA"):
            self.s.stop()

    def test_duplicate_open_and_switch_do_not_touch_camera(self):
        self.s.open("front")
        for callback in (lambda: self.s.open("rear"),
                         lambda: self.s.switch("front")):
            with self.assertRaises(SessionRejected):
                callback()
            self.assertEqual(self.b.transitions, [("neutral", "front")])
        self.s.close()

    def test_no_external_app_fd_allows_unsafe_route_change(self):
        self.b.no_users = False
        with self.assertRaisesRegex(SessionRejected, "FDS_OR_READERS"):
            self.s.open("front")
        self.assertTrue(self.s.poisoned)
        self.assertEqual(self.b.transitions, [])

    def test_authority_lock_and_ir_are_fail_closed(self):
        for attr in ("authority", "lock", "ir_safe"):
            with self.subTest(attr=attr):
                b = FakeBackend()
                setattr(b, attr, False)
                s = RGBSession(b)
                with self.assertRaises(SessionRejected):
                    s.open("front")
                self.assertTrue(s.poisoned)
                self.assertEqual(b.transitions, [])
                with self.assertRaisesRegex(SessionRejected, "POISONED"):
                    s.open("rear")

    def test_non_neutral_graph_denies_initial_open(self):
        self.b.phase = "rear"
        with self.assertRaisesRegex(SessionRejected, "NOT_NEUTRAL"):
            self.s.open("front")
        self.assertEqual(self.b.transitions, [])
        self.assertTrue(self.s.poisoned)

    def test_no_neutralization_before_verified_streamoff(self):
        self.s.open("front")
        self.b.stop_valid = False
        with self.assertRaisesRegex(SessionRejected, "STREAMOFF"):
            self.s.stop()
        self.assertEqual(self.b.phase, "front")
        self.assertEqual(self.b.transitions, [("neutral", "front")])
        self.assertTrue(self.s.poisoned)
        with self.assertRaisesRegex(SessionRejected, "POISONED"):
            self.s.switch("rear")

    def test_no_neutralization_with_remaining_reader(self):
        self.s.open("rear")
        self.b.no_users = False
        real_stop = self.b.stop_publisher
        def leaked_client(camera):
            result = real_stop(camera)
            self.b.no_users = False
            return result
        self.b.stop_publisher = leaked_client
        with self.assertRaisesRegex(SessionRejected, "FDS_STILL_OPEN"):
            self.s.stop()
        self.assertEqual(self.b.phase, "rear")
        self.assertTrue(self.s.poisoned)

    def test_lease_lost_while_publisher_running(self):
        self.s.open("front")
        self.b.lock = False
        with self.assertRaisesRegex(SessionRejected, "EXCLUSIVE"):
            self.s.stop()
        self.assertEqual(self.b.phase, "front")
        self.assertTrue(self.s.poisoned)

    def test_uncertain_activate_after_link_write_poison(self):
        self.b.fail_at = "activate_after"
        with self.assertRaisesRegex(RuntimeError, "activate_after"):
            self.s.open("front")
        self.assertEqual(self.b.phase, "front")
        self.assertTrue(self.s.poisoned)
        with self.assertRaisesRegex(SessionRejected, "POISONED"):
            self.s.close()

    def test_configure_or_start_failure_never_guesses_rollback(self):
        for stage in ("configure", "start_before", "start_after"):
            with self.subTest(stage=stage):
                b = FakeBackend()
                b.fail_at = stage
                s = RGBSession(b)
                with self.assertRaises(RuntimeError):
                    s.open("rear")
                self.assertTrue(s.poisoned)
                self.assertEqual(b.phase, "rear")
                self.assertEqual(b.transitions, [("neutral", "rear")])

    def test_stop_after_reap_error_never_guesses_neutral(self):
        self.s.open("front")
        self.b.fail_at = "stop_after"
        with self.assertRaises(RuntimeError):
            self.s.stop()
        self.assertTrue(self.s.poisoned)
        self.assertEqual(self.b.phase, "front")

    def test_uncertain_neutral_after_link_write_poison(self):
        self.s.open("front")
        self.b.fail_at = "neutral_after"
        with self.assertRaises(RuntimeError):
            self.s.stop()
        self.assertTrue(self.s.poisoned)
        self.assertEqual(self.s.active, "front")
        with self.assertRaisesRegex(SessionRejected, "POISONED"):
            self.s.open("rear")

    def test_read_only_close_on_neutral(self):
        self.s.close()
        self.assertEqual(self.b.transitions, [])
        self.assertEqual(self.s.completed_stops, 0)


if __name__ == "__main__":
    unittest.main()
