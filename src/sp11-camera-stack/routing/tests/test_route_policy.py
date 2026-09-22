# SPDX-License-Identifier: MIT
import copy
import re
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import route_policy as policy

TEXT = Path(__file__).with_name("neutral-media.txt").read_text()
EDGES = []
source = None
pad = None
for line in TEXT.splitlines():
    m = re.match(r"- entity \d+: (.*?) \(", line)
    if m:
        source = policy.canonical(m[1])
    m = re.match(r"\s*pad(\d+):", line)
    if m:
        pad = int(m[1])
    m = re.fullmatch(r'\s*-> "([^"]+)":(\d+) \[([^\]]*)\]', line)
    if m:
        EDGES.append((source, pad, policy.canonical(m[1]), int(m[2])))

def render(state):
    source = None
    pad = None
    lines = []
    for line in TEXT.splitlines():
        m = re.match(r"- entity \d+: (.*?) \(", line)
        if m:
            source = policy.canonical(m[1])
        m = re.match(r"\s*pad(\d+):", line)
        if m:
            pad = int(m[1])
        m = re.fullmatch(r'\s*(->|<-) "([^"]+)":(\d+) \[\]', line)
        if m:
            arrow, target, tp = m.groups()
            key = ((source, pad, policy.canonical(target), int(tp)) if arrow == "->"
                   else (policy.canonical(target), int(tp), source, pad))
            if key in state:
                line = line[:-2] + "[ENABLED]"
        lines.append(line)
    return "\n".join(lines) + "\n"

class MemoryBackend:
    def __init__(self, camera="neutral"):
        self.state = set(policy.ROUTES[camera])
        self.writes = []
        self.reads = 0
        self.stopped = True
        self.locked = True
        self.fail_at = None
        self.uncertain = False
        self.no_effect = False
        self.drift_read = None

    def all_cameras_stopped(self):
        return self.stopped

    def exclusive_session_held(self):
        return self.locked

    def read_graph(self):
        self.reads += 1
        if self.reads == self.drift_read:
            self.state.add(("msm_csiphy0", 1, "msm_csid0", 0))
        return render(self.state)

    def set_link(self, edge, enable):
        self.writes.append((edge, enable))
        fail = len(self.writes) == self.fail_at
        if fail and not self.uncertain:
            raise OSError("injected link failure")
        if not self.no_effect:
            self.state.add(edge) if enable else self.state.remove(edge)
        if fail:
            raise OSError("write may have succeeded")

class RouteTests(unittest.TestCase):
    def test_all_nine_transitions(self):
        for initial in policy.ROUTES:
            for target in policy.ROUTES:
                with self.subTest(initial=initial, target=target):
                    b = MemoryBackend(initial)
                    c = policy.Controller(b)
                    steps = c.transition(target)
                    self.assertEqual(b.state, set(policy.ROUTES[target]))
                    self.assertFalse(c.poisoned)
                    self.assertEqual(len(steps), 0 if initial == target else
                                     len(policy.ROUTES[initial]) + len(policy.ROUTES[target]))
                    if initial != target and initial != "neutral" and target != "neutral":
                        self.assertEqual(steps[1].after, frozenset())
                        self.assertFalse(steps[0].enable)
                        self.assertEqual(steps[0].edge, policy.ROUTES[initial][1])
                        self.assertTrue(steps[2].enable)

    def test_all_240_shortest_paths(self):
        for sensor in ("imx681", "ov13858", "sp11-vd55g0"):
            paths = [[edge] for edge in EDGES if edge[0] == sensor]
            for _ in range(3):
                paths = [path + [edge] for path in paths for edge in EDGES
                         if edge[0] == path[-1][2]]
            self.assertEqual(len(paths), 80)
            admitted = 0
            for path in paths:
                try:
                    policy.admit_path(sensor, tuple(path))
                    admitted += 1
                except policy.Rejected:
                    pass
            self.assertEqual(admitted, 0 if sensor == "sp11-vd55g0" else 1)

    def test_unrecognized_camera_path_pad_and_name(self):
        with self.assertRaises(policy.Rejected):
            policy.plan(TEXT, "ir")
        with self.assertRaises(policy.Rejected):
            policy.camera_for_sensor("imx681 1-0011")
        path = (("imx681 77-0010", 0, "msm_csiphy2", 0),
                *policy.FRONT, ("msm_vfe1_rdi0", 1, "msm_vfe1_video0", 0))
        self.assertEqual(policy.admit_path("imx681 77-0010", path), "front")
        bad = list(path)
        bad[1] = ("msm_csiphy2", 0, "msm_csid1", 0)
        with self.assertRaises(policy.Rejected):
            policy.admit_path("imx681", tuple(bad))

    def test_partial_or_mixed_initial_graph_rejected(self):
        for state in ({policy.FRONT[0]}, {policy.FRONT[1]},
                      set(policy.FRONT + policy.REAR),
                      {("msm_csiphy0", 1, "msm_csid0", 0)}):
            b = MemoryBackend()
            b.state = state
            c = policy.Controller(b)
            with self.assertRaises(policy.Rejected):
                c.transition("front")
            self.assertTrue(c.poisoned)
            self.assertEqual(b.writes, [])

    def test_complete_graph_and_direction_integrity(self):
        front = render(set(policy.FRONT))
        cases = [
            TEXT.replace('- entity 7:', '- entity 4:', 1),
            TEXT.replace('msm_csiphy4', 'msm_csiphy3'),
            TEXT.replace('[ENABLED,IMMUTABLE]', '[]', 1),
            TEXT.replace('":0 []', '":0 [UNKNOWN]', 1),
            TEXT.replace('-> "msm_csid4":0 []', '-> "msm_csid4":1 []', 1),
            TEXT.replace('(2 pads, 6 links, 0 routes)', '(2 pads, 6 links, 1 routes)', 1),
            front.replace('-> "msm_csid1":0 [ENABLED]', '-> "msm_csid1":0 []', 1),
            TEXT.replace('\t\t-> "msm_csid4":0 []\n', '', 1),
        ]
        for text in cases:
            with self.subTest(text=text[:70]):
                with self.assertRaises(policy.Rejected):
                    policy.snapshot(text)

    def test_lock_or_stream_prevents_any_write(self):
        for attr in ("stopped", "locked"):
            b = MemoryBackend()
            setattr(b, attr, False)
            c = policy.Controller(b)
            with self.assertRaises(policy.Rejected):
                c.transition("front")
            self.assertEqual(b.writes, [])
            self.assertTrue(c.poisoned)

    def test_every_write_failure_is_terminal(self):
        for index in range(1, 5):
            for uncertain in (False, True):
                b = MemoryBackend("front")
                b.fail_at = index
                b.uncertain = uncertain
                c = policy.Controller(b)
                with self.assertRaises(OSError):
                    c.transition("rear")
                self.assertEqual(len(b.writes), index)
                with self.assertRaises(policy.Rejected):
                    c.transition("neutral")
                self.assertEqual(len(b.writes), index)

    def test_graph_drift_before_each_write_is_terminal(self):
        # Read1 plans, then read2/4/6/8 precedes each of four writes.
        for read in (2, 4, 6, 8):
            b = MemoryBackend("front")
            b.drift_read = read
            c = policy.Controller(b)
            with self.assertRaises(policy.Rejected):
                c.transition("rear")
            self.assertEqual(len(b.writes), (read - 2) // 2)
            self.assertTrue(c.poisoned)

    def test_successful_ioctl_without_effect_is_rejected(self):
        b = MemoryBackend()
        b.no_effect = True
        c = policy.Controller(b)
        with self.assertRaisesRegex(policy.Rejected, "GRAPH_WRITE_NOT_CONFIRMED"):
            c.transition("front")
        self.assertEqual(len(b.writes), 1)

    def test_interrupt_poisoning_and_lost_lease(self):
        b = MemoryBackend()
        def interrupt(edge, enable):
            b.writes.append((edge, enable))
            raise KeyboardInterrupt()
        b.set_link = interrupt
        c = policy.Controller(b)
        with self.assertRaises(KeyboardInterrupt):
            c.transition("front")
        self.assertTrue(c.poisoned)
        with self.assertRaises(policy.Rejected):
            c.transition("neutral")
        self.assertEqual(len(b.writes), 1)
        b = MemoryBackend()
        original = b.set_link
        def lose_lock(edge, enable):
            original(edge, enable)
            b.locked = False
        b.set_link = lose_lock
        c = policy.Controller(b)
        with self.assertRaises(policy.Rejected):
            c.transition("front")
        self.assertEqual(len(b.writes), 1)

    def test_final_read_and_noop_are_checked(self):
        for initial, target, drift in (("neutral", "neutral", 2), ("neutral", "front", 6)):
            b = MemoryBackend(initial)
            b.drift_read = drift
            c = policy.Controller(b)
            with self.assertRaisesRegex(policy.Rejected, "FINAL_GRAPH_MISMATCH"):
                c.transition(target)

if __name__ == "__main__":
    unittest.main()
