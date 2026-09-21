#!/usr/bin/python3
"""Camera-free ABBA throughput measurement. Pixels remain in memory/pipes."""
import json, os, re, subprocess, tempfile, time
from pathlib import Path
HERE=Path(__file__).resolve().parent
BASE=HERE.parent/'e004kd-rear4k-extended-unique-app-one-shot/rear-bayer-to-nv12-4k-live-bounded.c'
FIXTURE=HERE.parent/'e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw'
FLAGS=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-fno-fast-math','-ffp-contract=off']
def thermal():
 readings={}
 for p in Path('/sys/class/thermal').glob('thermal_zone*'):
  try:readings[(p/'type').read_text().strip()]=int((p/'temp').read_text())/1000
  except (OSError,ValueError):pass
 return readings
def main():
 rows=[];before=thermal();frame=FIXTURE.read_bytes()
 assert len(frame)==14321824
 with tempfile.TemporaryDirectory(prefix='sp11-e004kk-bench-') as d:
  root=Path(d)
  for name,src,extra in [('baseline',BASE,[]),('parallel',HERE/'rear-bayer-parallel.c',['-fopenmp'])]:
   subprocess.run(FLAGS+extra+[str(src),'-o',str(root/name)],check=True)
  for name in ['baseline','parallel','parallel','baseline']:
   start=time.monotonic()
   p=subprocess.Popen([str(root/name),'--frames','120'],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,env={**os.environ,'OMP_WAIT_POLICY':'PASSIVE'})
   try:
    for _ in range(120):p.stdin.write(frame)
    p.stdin.close();text=p.stderr.read().decode();rc=p.wait(timeout=30)
   finally:
    if p.poll() is None:p.kill();p.wait()
   if rc:raise RuntimeError(text)
   elapsed=time.monotonic()-start
   rows.append({'variant':name,'frames':120,'wall_seconds':round(elapsed,4),'wall_fps':round(120/elapsed,3),'conversion_mean_ms':float(re.search(r'AVERAGE_CONVERSION_MS=([0-9.]+)',text)[1]),'telemetry':text.strip()})
 print(json.dumps({'experiment':'E004kk','camera_free':True,'pixel_files_written':False,'actual_camera_fps_proven':False,'output_sink':'dev_null','worker_limit':4,'omp_wait_policy':'PASSIVE','order':'ABBA','runs':rows,'thermal_before_c':before,'thermal_after_c':thermal()},indent=2))
if __name__=='__main__':main()
