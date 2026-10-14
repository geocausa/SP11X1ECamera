#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Extract actual candidate bodies; compile with a deterministic kernel API model."""
from pathlib import Path
import json,re,hashlib,subprocess,sys
S=Path(sys.argv[1]);O=Path(sys.argv[2]);Q=Path(__file__).resolve().parent
O.mkdir(parents=True,exist_ok=False)
(O/'camss-video-lifecycle.h').write_bytes((S/'drivers/media/platform/qcom/camss/camss-video-lifecycle.h').read_bytes())
def extract(s,n):
 m=list(re.finditer(r'^.*\b'+n+r'\([^;]*?\)\n\{',s,re.M))
 if len(m)!=1:raise RuntimeError((n,len(m)))
 b=s.index('{',m[0].start());d=1;i=b+1
 while d:
  d+=(s[i]=='{')-(s[i]=='}');i+=1
 return s[m[0].start():i]
video=S/'drivers/media/platform/qcom/camss/camss-video.c'
sg=S/'drivers/media/common/videobuf2/videobuf2-dma-sg.c'
vfe=S/'drivers/media/platform/qcom/camss/camss-vfe.c'
body=extract(sg.read_text(),'vb2_dma_sg_put')+'\n'+extract(sg.read_text(),'vb2_dma_sg_get_dmabuf')+'\n'
vs=video.read_text();a=vs.index('struct camss_video_dma_hold {');b=vs.index('static int video_buf_init',a)
body+=vs[a:b]
body+='\n'+extract(vfe.read_text(),'vfe_buf_flush_pending')+'\n'+extract(vfe.read_text(),'vfe_flush_buffers')+'\n'
for n in ['video_prepare_streaming','video_start_streaming','video_stop_streaming','video_unprepare_streaming']:body+='\n'+extract(vs,n)+'\n'
test=(Q/'test-integration.c.in').read_text().replace('/* EXTRACTED_FUNCTIONS */',body)
(O/'actual-body-test.c').write_text(test)
result={'scope':'Deterministic kernel API model, actual CAMSS and VB2 DMA-SG bodies; no hardware claim','source_sha256':{str(p.relative_to(S)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [video,sg,vfe]},'runs':[]}
for compiler in ['gcc','clang']:
 exe=O/compiler
 args=[compiler,'-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-I',str(O),str(O/'actual-body-test.c'),'-o',str(exe)]
 p=subprocess.run(args,capture_output=True,text=True);(O/(compiler+'-compile.log')).write_text(p.stdout+p.stderr)
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit(p.returncode)
 p=subprocess.run([str(exe)],capture_output=True,text=True);(O/(compiler+'-run.log')).write_text(p.stdout+p.stderr)
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit(p.returncode)
 result['runs'].append({'compiler':compiler,'result':p.stdout.strip()})
result['status']='PASS_ACTUAL_BODY_INTEGRATION_MODEL'
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
