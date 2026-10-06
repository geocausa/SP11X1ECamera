#!/usr/bin/env python3
import sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parents[1]; S=P.parent/'service'; T=S/'tests'
for p in (P,S,T):
    if str(p) not in sys.path: sys.path.insert(0,str(p))
from product_daemon import ProductSelector,peer_in_group
from rgb_device_backend import RGBDeviceBackend
from session import RGBSession,SessionRejected
from test_rgb_device_backend import DISCOVERY,OwnerFake

class ProductSelectorTests(unittest.TestCase):
    def setUp(self):
        self.os=OwnerFake(); self.selector=ProductSelector(RGBSession(RGBDeviceBackend(DISCOVERY,self.os)))
    def test_repeated_front_rear_service_sequence(self):
        seq=['front','off','rear','front','rear','off']
        for x in seq: self.assertEqual(self.selector.dispatch(x)['status'],'OK')
        self.assertIsNone(self.selector.session.active); self.assertFalse(self.selector.session.poisoned)
        self.assertEqual(self.os.phase,set()); self.assertEqual(self.selector.session.completed_stops,4)
        self.assertEqual(self.os.invocations,{'front':2,'rear':2})
    def test_duplicate_selection_is_idempotent(self):
        self.selector.dispatch('front'); r=self.selector.dispatch('front')
        self.assertTrue(r['already_active']); self.assertEqual(self.os.invocations['front'],1)
        self.selector.dispatch('off')
    def test_status_detects_publisher_or_graph_drift(self):
        self.selector.dispatch('rear'); self.os.active=None
        with self.assertRaisesRegex(SessionRejected,'DRIFT'): self.selector.dispatch('status')
    def test_reader_blocks_switch_fail_closed(self):
        self.selector.dispatch('front'); self.os.reader_open=True
        with self.assertRaisesRegex(SessionRejected,'FDS_STILL_OPEN'): self.selector.dispatch('rear')
        self.assertTrue(self.selector.session.poisoned)
    def test_unknown_command_has_no_mutation(self):
        self.assertEqual(self.selector.dispatch('ai-effects')['status'],'REJECTED')
        self.assertEqual(self.os.commands,[])

class PeerTests(unittest.TestCase):
    def test_root_always_allowed(self): self.assertTrue(peer_in_group(1,0,0,44))
    def test_primary_group_allowed(self): self.assertTrue(peer_in_group(123,1000,44,44))
    def test_supplementary_group_allowed_and_denied(self):
        with tempfile.TemporaryDirectory() as td:
            # Patch Path so only /proc/<pid>/status is redirected.
            real=Path
            status=real(td)/'status'; status.write_text('Name:\ttest\nGroups:\t27 44 1000\n')
            def fake(arg='.'):
                if str(arg)=='/proc/123/status': return status
                return real(arg)
            with patch('product_daemon.Path',side_effect=fake):
                self.assertTrue(peer_in_group(123,1000,1000,44))
                self.assertFalse(peer_in_group(123,1000,1000,45))

if __name__=='__main__': unittest.main()
