#!/usr/bin/python3
import copy,runpy,unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
M=runpy.run_path(str(HERE/'validate-session.py'))
class Sustained(unittest.TestCase):
 def fixtures(self,camera):
  size=10368000 if camera=='front' else 14321824
  source=''.join(f'cap dqbuf: {i%4} seq: {i} bytesused: {size} ts: {100+i/30:.6f} (ts-monotonic, ts-src-eof)\n' for i in range(2400))
  app={'status':'PASS','source':'device','camera':camera,'device':'/dev/video91' if camera=='front' else '/dev/video90','complete_frames':1800,'requested_frames':1800,'complete_bytes':1800*(3110400 if camera=='front' else 12441600),'all_payloads_distinct':True,'normal_eos':True}
  return source,app
 def test_complete_source_and_independent_app(self):
  for c in ('front','rear'):
   s,a=self.fixtures(c);v=M['validate'](c,s,a)
   self.assertAlmostEqual(v['source_timestamp_fps'],30,places=3)
   self.assertFalse(v['permanent_service_or_windows_isp_parity_proven'])
 def test_partial_wrong_device_duplicate_or_no_eos_refused(self):
  s,a=self.fixtures('rear')
  for key,value in [('complete_frames',1799),('complete_bytes',1),('device','/dev/video91'),('all_payloads_distinct',False),('normal_eos',False),('source','synthetic')]:
   bad=copy.deepcopy(a);bad[key]=value
   with self.assertRaises(ValueError):M['validate']('rear',s,bad)
  for bad in ('',s.replace('bytesused: 14321824','bytesused: 1000',1),s.replace('seq: 1 ','seq: 0 ',1)):
   with self.assertRaises(ValueError):M['validate']('rear',bad,a)
 def test_source_and_app_bounds_remain_finite(self):
  self.assertIn('n>2400',(HERE/'front-rggb10p-to-nv12-1080.c').read_text())
  self.assertIn('n>2400',(HERE/'rear-bayer-to-nv12-4k-live-bounded.c').read_text())
  self.assertIn('MAX_FRAMES=2400',(HERE/'front-rdi-raw10-pipe-audit.c').read_text())
  for c in ('front','rear'):
   self.assertIn('--stream-count=2400',(HERE/f'publish-{c}.sh').read_text())
  self.assertIn('--frames 1800',(HERE/'run-once.sh').read_text())
if __name__=='__main__':unittest.main()
