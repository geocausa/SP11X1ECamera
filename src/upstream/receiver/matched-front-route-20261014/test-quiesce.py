#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import re,sys,subprocess,json,hashlib
Q=Path(__file__).resolve().parent;S=Path(sys.argv[1]);O=Path(sys.argv[2]);O.mkdir(parents=True,exist_ok=False)
base=S/'drivers/media/platform/qcom/camss'
def extract(text,name):
 matches=list(re.finditer(r'^.*\b'+name+r'\([^;]*?\)\n\{',text,re.M))
 if len(matches)!=1:raise RuntimeError((name,len(matches)))
 a=matches[0].start();b=text.index('{',a);d=1;i=b+1
 while d:
  d+=(text[i]=='{')-(text[i]=='}');i+=1
 return text[a:i]
def defines(text):
 result=[];lines=text.splitlines();i=0
 while i<len(lines):
  if lines[i].startswith('#define'):
   result.append(lines[i])
   while lines[i].endswith('\\'):
    i+=1;result.append(lines[i])
  i+=1
 return '\n'.join(result)
sources={n:(base/n).read_text() for n in ['camss-csid-680.c','camss-csid.c','camss-vfe-680.c','camss-vfe.c','camss-video.c']}
order=[
 ('camss-csid-680.c',['csid_mask_stream_irqs','csid_clear_stream_status','csid_stream_irqs_quiet','csid_quiesce_stream','csid_enable_stream_irqs','csid_configure_stream_checked']),
 ('camss-csid.c',['csid_set_stream']),
 ('camss-vfe-680.c',['vfe_disable_irq','vfe_output_pause','vfe_output_quiesce']),
 ('camss-vfe.c',['vfe_buf_get_pending','vfe_buf_add_pending','vfe_output_done','vfe_queue_buffer_v2','vfe_prepare_stop']),
 ('camss-video.c',['video_owned_lifecycle','video_buf_init'])]
body='\n'.join(extract(sources[n],fn) for n,names in order for fn in names)
defs=defines(sources['camss-csid-680.c'])+'\n'+defines(sources['camss-vfe-680.c'])+'\n#define CSID_RESET_TIMEOUT_MS 500\n'
test=(Q/'test-quiesce.c.in').read_text().replace('/* PRODUCTION_DEFINES */',defs).replace('/* PRODUCTION_BODIES */',body)
(O/'actual-quiesce.c').write_text(test)
runs=[]
for cc in ['gcc','clang']:
 exe=O/cc
 p=subprocess.run([cc,'-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g',str(O/'actual-quiesce.c'),'-o',str(exe)],capture_output=True,text=True)
 (O/(cc+'-compile.log')).write_text(p.stdout+p.stderr)
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit(p.returncode)
 p=subprocess.run([str(exe)],capture_output=True,text=True);(O/(cc+'-run.log')).write_text(p.stdout+p.stderr)
 if p.returncode:print(p.stdout+p.stderr);raise SystemExit(p.returncode)
 runs.append(dict(compiler=cc,output=p.stdout.strip()))
record=dict(status='PASS_ACTUAL_QUIESCE_FIFO_DMA_EXTENT_MODEL',runs=runs,source_sha256={n:hashlib.sha256((base/n).read_bytes()).hexdigest() for n in sources},actual_functions=sum(len(x[1]) for x in order),scope='Actual control/MMIO/FIFO/DMA-admission bodies with deterministic kernel/IRQ/MMIO/wait adapters; not hardware/electrical/concurrency proof')
(O/'RESULT.json').write_text(json.dumps(record,indent=2)+'\n');print(json.dumps(record))
