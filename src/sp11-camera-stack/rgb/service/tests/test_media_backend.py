# SPDX-License-Identifier: MIT
"""Camera-free exact-argv kernel-backend mock tests. No OS device access."""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
import media_backend
policy = media_backend.route_policy
MEDIA_FIXTURE = ROOT.parents[1] / "routing/tests/neutral-media.txt"
TEXT = MEDIA_FIXTURE.read_text()


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
            edge = ((source, pad, policy.canonical(target), int(tp))
                    if arrow == "->"
                    else (policy.canonical(target), int(tp), source, pad))
            if edge in state:
                line = line[:-2] + "[ENABLED]"
        lines.append(line)
    return "\n".join(lines) + "\n"


class FakeOS:
    def __init__(self):
        self.state = set()
        self.commands = []
        self.authority = True
        self.lock = True
        self.no_users = True
        self.fail_read = False
        self.fail_after_write = False

    def run(self, args, *, timeout):
        self.commands.append((args, timeout))
        assert timeout == 7.0
        assert args[:3] == ("media-ctl", "-d", "/dev/media0")
        if args[3] == "-p":
            if self.fail_read:
                raise TimeoutError("injected graph read timeout")
            return render(self.state)
        assert args[3] == "-l" and len(args) == 5
        m = re.fullmatch(r'"([^"]+)":(\d+) -> "([^"]+)":(\d+) \[([01])\]', args[4])
        assert m is not None
        edge = (m[1], int(m[2]), m[3], int(m[4]))
        assert edge in (*policy.FRONT, *policy.REAR)
        if m[5] == "1":
            self.state.add(edge)
        else:
            self.state.remove(edge)
        if self.fail_after_write:
            raise TimeoutError("injected uncertain link write")
        return ""

    def backend(self):
        return media_backend.PhysicalMediaBackend(
            "/dev/media0", authorized=lambda: self.authority,
            exclusive=lambda: self.lock, no_camera_users=lambda: self.no_users,
            run=self.run)


class PhysicalAdapterTests(unittest.TestCase):
    def test_all_seven_ordered_write_arguments_and_verified_neutral(self):
        os = FakeOS()
        controller = policy.Controller(os.backend())
        self.assertEqual(len(controller.transition("front")), 2)
        self.assertEqual(len(controller.transition("rear")), 4)
        self.assertEqual(len(controller.transition("neutral")), 2)
        self.assertEqual(os.state, set())
        writes = [x[0][4] for x in os.commands if x[0][3] == "-l"]
        self.assertEqual(writes, [
            '"msm_csiphy2":1 -> "msm_csid1":0 [1]',
            '"msm_csid1":1 -> "msm_vfe1_rdi0":0 [1]',
            '"msm_csid1":1 -> "msm_vfe1_rdi0":0 [0]',
            '"msm_csiphy2":1 -> "msm_csid1":0 [0]',
            '"msm_csiphy1":1 -> "msm_csid0":0 [1]',
            '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [1]',
            '"msm_csid0":1 -> "msm_vfe0_rdi0":0 [0]',
            '"msm_csiphy1":1 -> "msm_csid0":0 [0]'])
        self.assertFalse(controller.poisoned)

    def test_bad_media_address_rejected_before_command(self):
        for value in ("/dev/media0;systemctl suspend", "/dev/video0",
                      "../../dev/media0", "/dev/media01", ""):
            with self.subTest(value=value), self.assertRaises(ValueError):
                media_backend.PhysicalMediaBackend(
                    value, authorized=lambda: True, exclusive=lambda: True,
                    no_camera_users=lambda: True)

    def test_missing_authorization_lock_or_fd_release_never_writes(self):
        for field in ("authority", "lock", "no_users"):
            with self.subTest(field=field):
                os = FakeOS()
                setattr(os, field, False)
                controller = policy.Controller(os.backend())
                with self.assertRaises(policy.Rejected):
                    controller.transition("front")
                self.assertFalse(any(x[0][3] == "-l" for x in os.commands))
                self.assertTrue(controller.poisoned)

    def test_lost_exclusive_lease_prevents_next_link(self):
        os = FakeOS()
        real_run = os.run
        def revoke_after_first_write(argv, *, timeout):
            value = real_run(argv, timeout=timeout)
            if argv[3] == "-l":
                os.lock = False
            return value
        backend = os.backend()
        backend.run = revoke_after_first_write
        ctl = policy.Controller(backend)
        with self.assertRaises(policy.Rejected):
            ctl.transition("front")
        self.assertEqual(len([x for x in os.commands if x[0][3] == "-l"]), 1)
        self.assertTrue(ctl.poisoned)

    def test_uncertain_write_never_retried(self):
        os = FakeOS()
        os.fail_after_write = True
        ctl = policy.Controller(os.backend())
        with self.assertRaises(TimeoutError):
            ctl.transition("front")
        self.assertTrue(ctl.poisoned)
        old_count = len(os.commands)
        with self.assertRaises(policy.Rejected):
            ctl.transition("neutral")
        self.assertEqual(len(os.commands), old_count)

    def test_graph_read_timeout_denies_and_poison(self):
        os = FakeOS()
        os.fail_read = True
        ctl = policy.Controller(os.backend())
        with self.assertRaises(TimeoutError):
            ctl.transition("front")
        self.assertTrue(ctl.poisoned)
        self.assertFalse(any(x[0][3] == "-l" for x in os.commands))

    def test_cannot_write_ir_or_isp_path_directly(self):
        os = FakeOS()
        b = os.backend()
        for edge in (("msm_csiphy0", 1, "msm_csid0", 0),
                     ("msm_csid1", 4, "msm_vfe1_pix", 0)):
            with self.subTest(edge=edge), self.assertRaises(policy.Rejected):
                b.set_link(edge, True)
        self.assertEqual(os.commands, [])

    def test_invalid_target_denied_before_read(self):
        os = FakeOS()
        with self.assertRaises(policy.Rejected):
            media_backend.validated_transition(os.backend(), "ir")
        self.assertEqual(os.commands, [])


if __name__ == "__main__":
    unittest.main()
