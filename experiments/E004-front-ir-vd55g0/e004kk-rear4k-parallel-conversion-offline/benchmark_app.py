#!/usr/bin/python3
"""Offline bounded full 4K converter->meter->real GStreamer app benchmark."""
import json, os, re, subprocess, tempfile, time
from pathlib import Path
HERE=Path(__file__).resolve().parent;P=HERE.parent
BASE=P/'e004kd-rear4k-extended-unique-app-one-shot/rear-bayer-to-nv12-4k-live-bounded.c'
APP=P/'e004jx-rear-4k-partial-telemetry/nv12-4k-partial-telemetry-app.py'
METER=P/'e004jz-rear-4k-pipe-boundary/nv12-4k-pipe-audit.c'
FIXTURE=P/'e004dz-canonical-package-rgb-handoff/runtime-output/rear-colorbar.raw'
FLAGS=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-fno-fast-math','-ffp-contract=off']
def main():
 frame=FIXTURE.read_bytes();rows=[]
 with tempfile.TemporaryDirectory(prefix='sp11-e004kk-app-') as d:
  root=Path(d)
  for name,src in [('baseline',BASE),('pipe',HERE/'rear-bayer-pipe.c'),('meter',METER)]:
   subprocess.run(FLAGS+[str(src),'-o',str(root/name)],check=True)
  for name in ('baseline','pipe','pipe','baseline'):
   start=time.monotonic();procs=[]
   try:
    c=subprocess.Popen([str(root/name),'--frames','120'],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE);procs.append(c)
    m=subprocess.Popen([str(root/'meter'),'--frames','120','--idle-ms','6000'],stdin=c.stdout,stdout=subprocess.PIPE,stderr=subprocess.PIPE);procs.append(m);c.stdout.close()
    a=subprocess.Popen(['/usr/bin/python3',str(APP),'--frames','120','--idle-seconds','6'],stdin=m.stdout,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE);procs.append(a);m.stdout.close()
    for _ in range(120):c.stdin.write(frame)
    c.stdin.close()
    messages=[p.stderr.read().decode() for p in procs]
    codes=[p.wait(timeout=10) for p in procs]
    if codes!=[0,0,0]:raise RuntimeError(str(codes)+str(messages))
    elapsed=time.monotonic()-start
    rows.append({'variant':name,'frames':120,'wall_seconds':round(elapsed,4),'wall_fps':round(120/elapsed,3),'converter':messages[0].strip(),'byte_meter':messages[1].strip(),'app_final':messages[2].splitlines()[-1]})
   finally:
    for p in procs:
     if p.poll() is None:p.kill();p.wait()
 print(json.dumps({'experiment':'E004kk','camera_free':True,'actual_camera_fps_proven':False,'synthetic_repeated_colorbar':True,'pixel_files_written':False,'runs':rows},indent=2))
if __name__=='__main__':main()
