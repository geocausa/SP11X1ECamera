# SPDX-License-Identifier: MIT
"""Candidate admission and stop-proof failure injection; no hardware access."""
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
HERE=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(HERE))
import candidate_owner
from session import SessionRejected


class OwnerTests(unittest.TestCase):
    def fake(self,root):
        owner=candidate_owner.CandidateOwner.__new__(candidate_owner.CandidateOwner)
        owner.id="e004lz"
        owner.root=Path(root)
        owner.boot="fresh-boot-id"
        owner.media="/dev/media0"
        owner.physical=("/dev/video12","/dev/video14")
        owner.authorized=lambda:True
        owner.lease_held=lambda:True
        return owner

    def test_reject_unprivileged_before_camera_io(self):
        with patch.object(candidate_owner.os,"geteuid",return_value=1000):
            with self.assertRaisesRegex(SessionRejected,"ROOT_PRIVATE"):
                candidate_owner.CandidateOwner("e004lz",
                    staged=Path("/var/lib/sp11-camera-e004lz"),
                    discovery={})

    def test_reject_incorrect_identity_before_camera_io(self):
        with self.assertRaisesRegex(SessionRejected,"FRESH_CANDIDATE"):
            candidate_owner.CandidateOwner("e004ly;reboot",
                staged=Path("/tmp/unarmed"),discovery={})

    def test_exact_unit_and_command_allowlist(self):
        with tempfile.TemporaryDirectory() as d:
            owner=self.fake(d)
            commands=[]
            with patch.object(candidate_owner,"bounded_command",
                              side_effect=lambda argv,timeout:commands.append((argv,timeout)) or ""):
                owner.run(("systemctl","start",owner.unit("front")),timeout=12.)
                owner.run(("media-ctl","-d","/dev/media0","-p"),timeout=7.)
                owner.run(("v4l2-ctl","-d","/dev/video12","--get-fmt-video"),timeout=7.)
                self.assertEqual(len(commands),3)
                for argv in (("systemctl","reboot"),
                             ("systemctl","start","sp11-camera-e004ly-one-shot.service"),
                             ("media-ctl","-d","/dev/media1","-l","bad"),
                             ("v4l2-ctl","-d","/dev/video90","--stream-to=/tmp/pixels")):
                    with self.subTest(argv=argv),self.assertRaises(SessionRejected):
                        owner.run(argv,timeout=3)
                self.assertEqual(len(commands),3)

    def test_exact_143_streamoff_invocation_report(self):
        with tempfile.TemporaryDirectory() as d:
            owner=self.fake(d)
            out=Path(d)/"output";out.mkdir()
            original="a"*32
            event={"boot_id":"fresh-boot-id","invocation_id":original,
                   "exit_code":"exited","exit_status":"143","service_result":"success"}
            event_file=out/"front-SERVICE-EXIT.json"
            log=out/"front-SERVICE-STDERR.txt"
            event_file.write_text(json.dumps(event)+"\n")
            log.write_text('E004KQ_LIFECYCLE captured=40 published=40 termination_requested=1 streamoff_completed=1\n'
                           '{"status":"STOPPED","continuous":true,"source_sequence_gaps":0}\n')
            self.assertTrue(owner.stop_proof("front",original))
            self.assertFalse(owner.stop_proof("front","b"*32))
            event["exit_status"]="0"
            event_file.write_text(json.dumps(event)+"\n")
            self.assertFalse(owner.stop_proof("front",original))
            event["exit_status"]="143"
            event_file.write_text(json.dumps(event)+"\n")
            log.write_text('E004KQ_LIFECYCLE termination_requested=1 streamoff_completed=0\n'
                           '{"status":"STOPPED","continuous":true,"source_sequence_gaps":0}\n')
            self.assertFalse(owner.stop_proof("front",original))
            log.write_text('E004KQ_LIFECYCLE termination_requested=1 streamoff_completed=1\n'
                           '{"status":"FAIL","continuous":true,"source_sequence_gaps":0}\n')
            self.assertFalse(owner.stop_proof("front",original))


if __name__=="__main__":
    unittest.main()
