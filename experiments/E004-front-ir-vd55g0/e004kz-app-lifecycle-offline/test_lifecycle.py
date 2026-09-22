import importlib.util,json,os,subprocess,sys,tempfile,unittest
from pathlib import Path
R=Path(__file__).resolve().parents[3]
spec=importlib.util.spec_from_file_location('cycle',R/'src/sp11-camera-stack/acceptance/client_lifecycle.py')
m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
class Tests(unittest.TestCase):
 def test_real_synthetic_client_cycles(self):
  self.assertEqual(os.geteuid(),1000)
  client=R/'experiments/E004-front-ir-vd55g0/e004kw-durable-dual-systemd-session-one-shot/direct-camera-app.py'
  for camera in ['front','rear']:
   with tempfile.TemporaryDirectory(prefix='sp11-e004kz-cycle-') as d:
    report=m.cycle(client,camera,Path(d),source='synthetic')
    self.assertEqual(report['normal_open_count'],3)
    self.assertEqual(report['phases'][2]['returncode'],-9)
    (Path(__file__).parent/(camera.upper()+'-SYNTHETIC-CYCLE.json')).write_text(json.dumps(report,indent=2)+'\n')
 def test_failure_is_not_retried(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaisesRegex(AssertionError,'CLIENT_EXIT_7'):
    m.attempt([sys.executable,'-c','raise SystemExit(7)'],Path(d)/'bad',deadline=1)
   self.assertEqual(len(list(Path(d).glob('*.jsonl'))),1)
 def test_timeout_reaps_owned_process(self):
  with tempfile.TemporaryDirectory() as d:
   pidfile=Path(d)/'pid'
   cmd=[sys.executable,'-c',f'import os,time;open({str(pidfile)!r},"w").write(str(os.getpid()));time.sleep(30)']
   with self.assertRaises(TimeoutError):m.attempt(cmd,Path(d)/'timeout',deadline=.3)
   self.assertTrue(m.group_gone(int(pidfile.read_text())))
 def test_live_cli_refuses_golden(self):
  r=subprocess.run([sys.executable,str(R/'src/sp11-camera-stack/acceptance/client_lifecycle.py'),'--camera','front','--client','/unused','--output','/unused'],capture_output=True)
  self.assertNotEqual(r.returncode,0)
if __name__=='__main__':unittest.main()
