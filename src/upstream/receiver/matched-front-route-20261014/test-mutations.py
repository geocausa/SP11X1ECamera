#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import re,json,subprocess,sys
golden=Path(sys.argv[1]).read_text();O=Path(sys.argv[2]);O.mkdir(parents=True,exist_ok=False)
def body(t,name):
 m=list(re.finditer(r'^.*\b'+name+r'\([^;]*?\)\n\{',t,re.M))
 assert len(m)==1,(name,len(m))
 a=m[0].start();b=t.index('{',a);d=1;i=b+1
 while d:
  d+=(t[i]=='{')-(t[i]=='}');i+=1
 return a,i,t[a:i]
variants=[
 ('skip_fresh_ack','csid_quiesce_stream','if (!time)\n\t\treturn -ETIMEDOUT;','if (time && false)\n\t\treturn -ETIMEDOUT;'),
 ('skip_csid_irq_drain','csid_quiesce_stream','synchronize_irq(csid->irq);','(void)csid->irq;'),
 ('skip_reopen_irq_restore','csid_configure_stream_checked','csid_enable_stream_irqs(csid);','(void)csid;'),
 ('hide_active_dma','vfe_output_quiesce','if (!ret && (output->gen2.active_num || output->buf[0] || output->buf[1]))','if (false)'),
 ('refill_during_drain','vfe_output_done','output->state == VFE_OUTPUT_STOPPING ?\n\t\tNULL : vfe_buf_get_pending(output)','vfe_buf_get_pending(output)'),
 ('skip_last_buffer_pause','vfe_output_done','if (ops->vfe_output_pause && output->gen2.active_num == 1 &&','if (false && ops->vfe_output_pause && output->gen2.active_num == 1 &&'),
 ('skip_vfe_irq_barrier','vfe_output_quiesce','synchronize_irq(vfe->irq);','(void)vfe->irq;'),
 ('allow_split_dma_extent','video_buf_init','sgt->nents != 1','false'),
 ('allow_dma_address_wrap','video_buf_init','(u64)sg_dma_address(sgt->sgl) > U32_MAX ||','false ||'),
 ('enable_before_address_on_resume','vfe_queue_buffer_v2','output->buf[output->gen2.active_num++] = buf;','if (output->gen2.wm_stopped) ops->vfe_output_start(vfe, output);\n\t\toutput->buf[output->gen2.active_num++] = buf;')]
records=[]
for name,fn,old,new in variants:
 a,b,s=body(golden,fn);assert old in s,(name,old)
 # All repeated CSID barriers are deliberately removed in that mutation.
 s=s.replace(old,new)
 source=O/(name+'.c');source.write_text(golden[:a]+s+golden[b:]);exe=O/name
 p=subprocess.run(['gcc','-std=gnu11','-Wall','-Wextra','-Werror','-Wno-unused-parameter','-Wno-unused-function','-fsanitize=address,undefined','-fno-omit-frame-pointer','-g',str(source),'-o',str(exe)],capture_output=True,text=True)
 (O/(name+'-compile.log')).write_text(p.stdout+p.stderr)
 if p.returncode:raise RuntimeError(name+' did not compile: '+p.stderr[-1800:])
 p=subprocess.run([str(exe)],capture_output=True,text=True);(O/(name+'-run.log')).write_text(p.stdout+p.stderr)
 assert p.returncode!=0,name+' was not rejected'
 records.append(dict(name=name,compiled=True,rejected=True,returncode=p.returncode))
result=dict(status='PASS_TEN_COMPILED_UNSAFE_QUIESCE_MUTATIONS_REJECTED',mutations=records,hardware_access=False)
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
