#!/usr/bin/python3
"""Offline subprocess tests; all hardware executables replaced by synthetic stubs."""
import os, signal, subprocess, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
class Lifecycle(unittest.TestCase):
 def test_publishers_preserve_pipeline_failure_and_real_group_exit(self):
  with tempfile.TemporaryDirectory(prefix='sp11-e004kj-offline-') as d:
   root=Path(d); bin=root/'bin';bin.mkdir()
   for name,body in {'v4l2-ctl':'printf synthetic', 'gst-launch-1.0':'cat >/dev/null', 'bridge':'cat', 'fail':'cat >/dev/null; exit 17'}.items():
    p=bin/name;p.write_text('#!/bin/sh\n'+body+'\n');p.chmod(0o755)
   env={**os.environ,'PATH':str(bin)+':/usr/bin:/bin'}
   for camera in ('front','rear'):
    for fail in (False,True):
     args=['/bin/bash',str(HERE/f'publish-{camera}.sh'),'FAKE_NO_DEVICE',str(root)]
     if camera=='front':args.append(str(bin/'bridge'))
     args.extend([str(bin/('fail' if fail else 'bridge')),'FAKE_NO_DEVICE'])
     p=subprocess.Popen(args,env=env,start_new_session=True)
     self.assertEqual(p.wait(timeout=10),17 if fail else 0)
     with self.assertRaises(ProcessLookupError):os.killpg(p.pid,0)
     done=root/('FRONT-PUBLISHER-DONE.txt' if camera=='front' else 'REAR-4K-PUBLISHER-DONE.txt')
     self.assertRegex(done.read_text(),r'PUBLISHER_END_NS=\d+')
 def test_group_guard_rejects_live_process(self):
  text=(HERE/'run-once.sh').read_text()
  func=text[text.index('assert_publisher_group_exited()'):text.index('assert_idle_devices()')]
  p=subprocess.Popen(['/bin/sleep','10'],start_new_session=True)
  try:
   check=subprocess.run(['/bin/bash','-c',func+'\nassert_publisher_group_exited "$1"','bash',str(p.pid)],capture_output=True)
   self.assertNotEqual(check.returncode,0)
  finally:
   os.killpg(p.pid,signal.SIGTERM);p.wait(timeout=3)
  check=subprocess.run(['/bin/bash','-c',func+'\nassert_publisher_group_exited "$1"','bash',str(p.pid)],capture_output=True)
  self.assertEqual(check.returncode,0)
 def test_new_identity_and_neutral_handoff(self):
  run=(HERE/'run-once.sh').read_text()
  self.assertNotIn('--set-ctrl=test_pattern',run)
  self.assertEqual(run.count('assert_publisher_group_exited "$publisher_pid" || exit 1'),2)
  self.assertLess(run.index('"$O/FINAL-NEUTRAL-MEDIA.txt" --expect neutral'),run.index('LOOP_DEV=/dev/video90',run.index('LOOP_DEV=/dev/video91')))
  for script in ('install-unarmed.sh','arm-once.sh'):
   s=(HERE/script).read_text()
   self.assertIn('evidence/CONSUMED.json',s)
   self.assertNotIn('/var/lib/sp11-camera-e004kh',s)
   self.assertNotIn('/var/lib/sp11-camera-e004kd',s)
  self.assertIn('ExecStopPost=/usr/bin/systemctl --no-block reboot',(HERE/'sp11-camera-e004kj-one-shot.service').read_text())
if __name__=='__main__':unittest.main()
