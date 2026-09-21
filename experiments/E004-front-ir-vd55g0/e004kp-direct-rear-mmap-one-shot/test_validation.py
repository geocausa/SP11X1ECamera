import copy,importlib.util,json,unittest
from pathlib import Path
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v',H/'validate-session.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class Tests(unittest.TestCase):
 def test_sustained_validator(self):
  app=json.loads((H.parent/'e004km-sustained-direct-rgb-session-one-shot/evidence/REAR-DIRECT-VALIDATION.json').read_text())['direct_app']
  pub={'status':'PASS','frames':2400,'requested':2400,'source_sequence_first_last':[0,2399],'source_sequence_gaps':0,'source_span_s':80.0}
  self.assertEqual(v.validate(pub,app)['status'],'PASS')
  for key,value in [('frames',2399),('source_sequence_gaps',1),('source_span_s',0),('status','FAIL')]:
   bad=copy.deepcopy(pub);bad[key]=value
   with self.assertRaises(AssertionError):v.validate(bad,app)
  for key,value in [('device','/dev/video91'),('normal_eos',False),('distinct_payloads',1799),('complete_bytes',1)]:
   bad=copy.deepcopy(app);bad[key]=value
   with self.assertRaises(AssertionError):v.validate(pub,bad)
if __name__=='__main__':unittest.main()
