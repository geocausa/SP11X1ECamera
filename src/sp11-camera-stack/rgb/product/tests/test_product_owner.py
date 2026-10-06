#!/usr/bin/env python3
import json,sys,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
P=Path(__file__).resolve().parents[1]
if str(P) not in sys.path: sys.path.insert(0,str(P))
import product_owner
from session import SessionRejected

class ProductOwnerTests(unittest.TestCase):
    def fake(self,root):
        o=product_owner.ProductOwner.__new__(product_owner.ProductOwner)
        o.root=Path(root); o.media='/dev/media0'; o.physical=('/dev/video12','/dev/video14')
        o.boot='boot'; o._lease_fd=9; o._closed=False
        o.authorized=lambda:True; o.lease_held=lambda:True
        return o
    def test_unit_and_command_allowlist(self):
        with tempfile.TemporaryDirectory() as d:
            o=self.fake(d); calls=[]
            with patch.object(product_owner,'bounded_command',side_effect=lambda argv,timeout:calls.append((argv,timeout)) or ''):
                o.run(('systemctl','start',o.unit('front')),timeout=12)
                o.run(('media-ctl','-d','/dev/media0','-p'),timeout=7)
                o.run(('v4l2-ctl','-d','/dev/video12','--get-fmt-video'),timeout=7)
                self.assertEqual(len(calls),3)
                for argv in [('systemctl','reboot'),('systemctl','start','evil.service'),('media-ctl','-d','/dev/media1','-p'),('v4l2-ctl','-d','/dev/video90','--get-fmt-video')]:
                    with self.subTest(argv=argv),self.assertRaises(SessionRejected): o.run(tuple(argv),timeout=3)
                self.assertEqual(len(calls),3)
    def test_stop_proof_binds_invocation_and_streamoff(self):
        with tempfile.TemporaryDirectory() as d:
            o=self.fake(d); out=Path(d)/'output'; out.mkdir(); inv='a'*32
            (out/'rear-SERVICE-EXIT.json').write_text(json.dumps({'boot_id':'boot','invocation_id':inv,'exit_code':'exited','exit_status':'143','service_result':'success'})+'\n')
            (out/'rear-SERVICE-STDERR.txt').write_text('E004KQ_LIFECYCLE termination_requested=1 streamoff_completed=1\n{"status":"STOPPED","continuous":true,"source_sequence_gaps":0}\n')
            self.assertTrue(o.stop_proof('rear',inv)); self.assertFalse(o.stop_proof('rear','b'*32))
    def test_enable_contract_is_exact(self):
        good='schema=sp11-camera-rgb-product-v1\nenabled=YES\npackage_manifest_sha256='+'a'*64+'\nproduct_assets_sha256='+'c'*64+'\nsource_head='+'b'*40+'\n'
        self.assertIsNotNone(product_owner.ProductOwner._parse_enable(good))
        self.assertIsNone(product_owner.ProductOwner._parse_enable(good.replace('enabled=YES','enabled=NO')))
        self.assertIsNone(product_owner.ProductOwner._parse_enable(good+'extra=x\n'))
        self.assertIsNone(product_owner.ProductOwner._parse_enable(good.replace('source_head='+'b'*40,'source_head=bad')))


if __name__=='__main__': unittest.main()
