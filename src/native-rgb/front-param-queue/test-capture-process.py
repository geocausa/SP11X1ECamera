#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
import os,runpy,sys,tempfile,unittest
from pathlib import Path
capture=runpy.run_path(str(Path(__file__).with_name("capture-process.py")))["capture"]
class Process(unittest.TestCase):
 def test_completed(self):
  with tempfile.TemporaryDirectory() as t:
   p,info=capture([sys.executable,"-c","print('done')"],t,os.environ.copy(),5,False)
   self.assertEqual(p.returncode,0);self.assertEqual(p.stdout.strip(),"done");self.assertFalse(info["timed_out"])
 def test_nonzero(self):
  with tempfile.TemporaryDirectory() as t:
   p,info=capture([sys.executable,"-c","raise SystemExit(7)"],t,os.environ.copy(),5,False)
   self.assertEqual(p.returncode,7);self.assertFalse(info["timed_out"])
 def test_timeout_kills_group(self):
  with tempfile.TemporaryDirectory() as t:
   p,info=capture([sys.executable,"-c","import time;time.sleep(20)"],t,os.environ.copy(),0.2,False)
   self.assertTrue(info["timed_out"]);self.assertLess(p.returncode,0)
   self.assertTrue((Path(t)/"PRIVATE-TIMEOUT-PROCESSES.json").exists())
 def test_descendant_log_fd_does_not_block_parent_wait(self):
  with tempfile.TemporaryDirectory() as t:
   code="import subprocess,sys;subprocess.Popen([sys.executable,'-c','import time;time.sleep(20)']);print('parent done')"
   p,info=capture([sys.executable,"-c",code],t,os.environ.copy(),2,False)
   self.assertEqual(p.returncode,0);self.assertFalse(info["timed_out"])
unittest.main()
