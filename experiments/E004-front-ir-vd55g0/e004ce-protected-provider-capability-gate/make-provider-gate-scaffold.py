#!/usr/bin/env python3
from pathlib import Path
import argparse, hashlib, shutil
BASE_VIDEO_SHA='2eb92e872b4bc4f0aaa2e17197707ca270e3f5f8b8d8460952599631c9b76df4'
BASE_HEADER_SHA='69fdbb6364a772d5b9fe50114878bbc7a1a1ffc61e62af1e71c79fd16e94c982'
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('source'); ap.add_argument('output'); ap.add_argument('contract'); ns=ap.parse_args()
 src=Path(ns.source); out=Path(ns.output); contract=Path(ns.contract)
 if sha(src/'camss-video.c')!=BASE_VIDEO_SHA: raise SystemExit('camss-video.c base hash mismatch')
 if sha(src/'camss-video.h')!=BASE_HEADER_SHA: raise SystemExit('camss-video.h base hash mismatch')
 if out.exists(): shutil.rmtree(out)
 shutil.copytree(src,out)
 c=out/'camss-video.c'; text=c.read_text(); marker='#include "camss-video.h"\n'
 if text.count(marker)!=1: raise SystemExit('include marker mismatch')
 text=text.replace(marker,marker+'#include "camss-protected-pipeline.h"\n',1)
 hook='\tstruct vb2_queue *q;\n\tint ret;\n\n\tvdev = &video->vdev;\n'
 hooked='\tstruct vb2_queue *q;\n\tint ret;\n\n\tcamss_protected_pipeline_compile_contract();\n\tvdev = &video->vdev;\n'
 if text.count(hook)!=1: raise SystemExit('register hook mismatch')
 c.write_text(text.replace(hook,hooked,1)); shutil.copy2(contract,out/'camss-protected-pipeline.h')
 print('E004ce provider capability scaffold generation: PASS')
 print('base_video_sha='+sha(src/'camss-video.c')); print('scaffold_video_sha='+sha(c)); print('contract_sha='+sha(out/'camss-protected-pipeline.h'))
if __name__=='__main__': main()
