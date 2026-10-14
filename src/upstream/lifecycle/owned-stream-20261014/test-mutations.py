#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Verify the actual-body tests reject unsafe lifecycle regressions."""
from pathlib import Path
import json,subprocess,sys,resource
Q=Path(__file__).resolve().parent
I,O=map(Path,sys.argv[1:3])
O.mkdir(parents=True,exist_ok=False)
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
body=(I/'actual-body-test.c').read_text()
mutations={
 'release_dma_on_fault':('if (video->lifecycle.fault && hold->exposed)','if (video->lifecycle.fault && hold->exposed && false)'),
 'drop_faulted_power':('if (video->lifecycle.fault)\n\t\treturn;','if (false)\n\t\treturn;'),
 'omit_global_fault_latch':('video->camss->stream_fault = true;','video->camss->stream_fault = false;'),
 'retain_irq_buffer_pointer':('output->buf[0] = NULL;','/* mutated: pointer retained */'),
 'stop_graph_after_failed_shutdown':('if (!video->lifecycle.fault && video->pipeline_started)','if (video->pipeline_started)'),
}
result={'status':'PASS_UNSAFE_MUTATIONS_REJECTED','scope':'Fault quarantine, power and graph retention, IRQ buffer detachment','mutations':[]}
for name,(old,new) in mutations.items():
 if body.count(old)!=1:raise RuntimeError((name,body.count(old)))
 p=O/(name+'.c');p.write_text(body.replace(old,new))
 exe=O/name
 c=subprocess.run(['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g','-I',str(Q),str(p),'-o',str(exe)],capture_output=True,text=True)
 (O/(name+'-compile.log')).write_text(c.stdout+c.stderr)
 if c.returncode:raise RuntimeError(c.stdout+c.stderr)
 r=subprocess.run([str(exe)],capture_output=True,text=True)
 (O/(name+'-run.log')).write_text(r.stdout+r.stderr)
 if not r.returncode:raise RuntimeError('UNSAFE MUTATION SURVIVED: '+name)
 result['mutations'].append({'name':name,'returncode':r.returncode,'rejected':True})
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
