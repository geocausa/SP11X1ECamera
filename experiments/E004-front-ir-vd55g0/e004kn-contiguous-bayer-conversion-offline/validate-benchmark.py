#!/usr/bin/python3
"""Camera-free exact-output comparison and ABBA benchmark, no pixel artifacts."""
import json, os, re, subprocess, tempfile, time
from pathlib import Path
import numpy as np
HERE=Path(__file__).resolve().parent
FLAGS=['gcc','-O3','-std=c11','-Wall','-Wextra','-Werror','-pedantic','-fno-fast-math','-ffp-contract=off']
def main():
 results=[]; checks=[]
 rng=np.random.default_rng(681)
 with tempfile.TemporaryDirectory(prefix='sp11-e004kn-') as d:
  root=Path(d)
  for name,src in [('baseline',HERE.parent/'e004kk-rear4k-parallel-conversion-offline/rear-bayer-pipe.c'),('contiguous',HERE/'rear-bayer-contiguous.c')]:
   subprocess.run(FLAGS+[str(src),'-o',str(root/name)],check=True)
  random=rng.integers(0,256,size=14321824,dtype=np.uint8).tobytes()
  gradient=(np.arange(14321824,dtype=np.uint32)%251).astype(np.uint8).tobytes()
  for label,frames in [('black',[bytes(14321824)]),('white',[bytes([255])*14321824]),('random',[random]),('gradient',[gradient]),('changing',[random,gradient,random])]:
   outputs=[]
   for name in ['baseline','contiguous']:
    p=subprocess.run([str(root/name),'--frames',str(len(frames))],input=b''.join(frames),capture_output=True,timeout=30,check=True)
    assert len(p.stdout)==12441600*len(frames)
    outputs.append(p.stdout)
   assert outputs[0]==outputs[1],label
   checks.append({'case':label,'frames':len(frames),'byte_exact':True})
  for name in ['baseline','contiguous','contiguous','baseline']:
   start=time.monotonic()
   p=subprocess.Popen([str(root/name),'--frames','120'],stdin=subprocess.PIPE,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
   try:
    for _ in range(120):p.stdin.write(random)
    p.stdin.close();telemetry=p.stderr.read().decode();rc=p.wait(timeout=30)
   finally:
    if p.poll() is None:p.kill();p.wait()
   assert rc==0,telemetry
   elapsed=time.monotonic()-start
   results.append({'variant':name,'frames':120,'elapsed_s':round(elapsed,4),'fps':round(120/elapsed,3),'conversion_ms':float(re.search(r'AVERAGE_CONVERSION_MS=([0-9.]+)',telemetry)[1]),'telemetry':telemetry.strip()})
 print(json.dumps({'experiment':'E004kn','camera_free':True,'pixel_files_or_hashes_exported':False,'exact_output_checks':checks,'runs':results,'live_camera_fps_proven':False},indent=2))
if __name__=='__main__':main()
