import copy,importlib.util,json,unittest
from pathlib import Path
H=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('v',H/'validate-session.py');v=importlib.util.module_from_spec(spec);spec.loader.exec_module(v)
class Tests(unittest.TestCase):
 def test_controlled_stop(self):
  for camera,n,w,h in [('front',1800,1920,1080),('rear',1800,3840,2160)]:
   app=json.loads((H.parent/f'e004km-sustained-direct-rgb-session-one-shot/evidence/{camera.upper()}-DIRECT-VALIDATION.json').read_text())['direct_app']
   app.update(effective_uid=1000,complete_frames=n,requested_frames=n,distinct_payloads=n,complete_bytes=n*w*h*3//2)
   pub={'status':'STOPPED','frames':n+2,'requested':2400,'source_sequence_first_last':[0,n+2],'source_sequence_gaps':0,'source_span_s':60.0}
   life=f'E004KQ_LIFECYCLE captured={n+3} published={n+2} termination_requested=1 streamoff_completed=1'
   text=life+'\n'+json.dumps(pub)
   self.assertEqual(v.validate(camera,text,app)['status'],'PASS')
   for bad in [text.replace('streamoff_completed=1','streamoff_completed=0'),text.replace('termination_requested=1','termination_requested=0'),text.replace('STOPPED','FAIL')]:
    with self.assertRaises(AssertionError):v.validate(camera,bad,app)
   for key,val in [('effective_uid',0),('normal_eos',False),('distinct_payloads',n-1),('complete_bytes',1)]:
    bad=copy.deepcopy(app);bad[key]=val
    with self.assertRaises(AssertionError):v.validate(camera,text,bad)
if __name__=='__main__':unittest.main()
