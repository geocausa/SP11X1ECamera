#!/usr/bin/python3
import os, subprocess, tempfile, unittest
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'e004kd-rear4k-extended-unique-app-one-shot/rear-bayer-to-nv12-4k-live-bounded.c'
FIXTURE=HERE.parent/'e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw'
FLAGS=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-fno-fast-math','-ffp-contract=off']
class ParallelPixels(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  cls.tmp=tempfile.TemporaryDirectory(prefix='sp11-e004kk-test-');cls.root=Path(cls.tmp.name)
  for name,src,extra in [('baseline',BASE,[]),('parallel',HERE/'rear-bayer-parallel.c',['-fopenmp']),('pipe',HERE/'rear-bayer-pipe.c',[])]:
   subprocess.run(FLAGS+extra+[str(src),'-o',str(cls.root/name)],check=True)
 @classmethod
 def tearDownClass(cls):cls.tmp.cleanup()
 def convert(self,name,data,n=1):
  return subprocess.run([str(self.root/name),'--frames',str(n)],input=data,capture_output=True,timeout=15,env={**os.environ,'OMP_WAIT_POLICY':'PASSIVE'})
 def test_byte_exact_colorbar_and_synthetic_tile_boundaries(self):
  row=bytes((x*31+(x//5)*13+(x%5)*17)&255 for x in range(5104))
  gradient=b''.join(row.translate(bytes((i+19*y)&255 for i in range(256))) for y in range(2806))
  # Test nonuniform pixels across all worker boundaries and 8-bit extremes.
  for data in (FIXTURE.read_bytes(),gradient,bytes(14321824),bytes([255])*14321824):
   a=self.convert('baseline',data);b=self.convert('parallel',data)
   c=self.convert('pipe',data);self.assertEqual(c.returncode,0,c.stderr);self.assertEqual(a.stdout,c.stdout)
   self.assertEqual((a.returncode,b.returncode),(0,0),(a.stderr,b.stderr))
   self.assertEqual(a.stdout,b.stdout);self.assertEqual(len(b.stdout),12441600)
 def test_distinct_consecutive_frames_do_not_mix_workers(self):
  a=FIXTURE.read_bytes();b=bytes((i^213 for i in a))
  reference=self.convert('baseline',a+b,2);actual=self.convert('parallel',a+b,2)
  self.assertEqual(actual.returncode,0,actual.stderr)
  self.assertEqual(actual.stdout,reference.stdout)
  pipe=self.convert('pipe',a+b,2);self.assertEqual(pipe.returncode,0,pipe.stderr);self.assertEqual(pipe.stdout,reference.stdout)
 def test_bounds_truncation_extra_input_fail(self):
  for n in (0,241,-1):self.assertEqual(self.convert('parallel',b'',n).returncode,2)
  for data in (bytes(1000),FIXTURE.read_bytes()+b'x'):
   self.assertNotEqual(self.convert('parallel',data).returncode,0)
if __name__=='__main__':unittest.main()
