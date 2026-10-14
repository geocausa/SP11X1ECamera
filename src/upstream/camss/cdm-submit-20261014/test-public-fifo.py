#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compile pinned public FIFO writer as an independent serialization oracle."""
from pathlib import Path
import json,re,subprocess,sys,hashlib
Q=Path(__file__).resolve().parent;R=Q.parents[3]
reference=json.loads((R/'src/upstream/camss/cdm-lifetime-reference-20261012.json').read_text())
P=Path(reference['stage'])/'source';O=Path(sys.argv[1]);O.mkdir()
for f in reference['files']:
 p=P/f['path'];assert hashlib.sha256(p.read_bytes()).hexdigest()==f['sha256']
t=(P/'camera/drivers/cam_cdm/cam_cdm_hw_core.c').read_text()
sys.path.insert(0,str(Q));from importlib import util
spec=util.spec_from_file_location('extract',Q/'test-submit.py');m=util.module_from_spec(spec);spec.loader.exec_module(m)
body=m.function(t,'cam_hw_cdm_bl_write')+'\n'+m.function(t,'cam_hw_cdm_commit_bl_write')
defs='\n'.join(l for l in t.splitlines() if l.startswith('#define CAM_CDM_FIFO_LEN_REG_'))
prefix=r'''
#include <assert.h>
#include <stdio.h>
#include "sp11-cdm21-command.h"
typedef u32 uint32_t;
#define CAM_CDM 0
#define CAM_DBG(...) ((void)0)
#define CAM_ERR(...) ((void)0)
struct cam_cdm_bl_fifo_regs {u32 bl_fifo_base,bl_fifo_len,bl_fifo_store;};
struct cam_cdm_hw_reg_offset {struct cam_cdm_bl_fifo_regs *bl_fifo_reg[4];};
struct cam_cdm {struct cam_cdm_hw_reg_offset *offsets;};
struct cam_hw_info {void *core_info;};
static u32 recorded[3];static unsigned writes;
static int cam_cdm_write_hw_reg(struct cam_hw_info *hw,u32 reg,u32 val) {
 (void)hw;assert(writes<3);assert(reg==0x50+4*writes);recorded[writes++]=val;return 0;
}
'''
tail=r'''
int main(void) {
 struct cam_cdm_bl_fifo_regs fifo={0x50,0x54,0x58};
 struct cam_cdm_hw_reg_offset offsets={{&fifo,NULL,NULL,NULL}};
 struct cam_cdm core={&offsets};struct cam_hw_info hw={&core};
 unsigned cases=0;
 for(size_t n=4;n<=0x100000;n+=4) {
  writes=0;assert(!cam_hw_cdm_bl_write(&hw,0x1000,n-1,0,true,false,0));
  assert(!cam_hw_cdm_commit_bl_write(&hw,0));
  assert(writes==3&&recorded[0]==0x1000&&recorded[1]==sp11_cdm21_command_length(n)&&recorded[2]==1);cases++;
 }
 for(u32 s=0;s<0x80000;s++)
  assert(sp11_cdm21_command_status_valid(s)==((s==4)||(s==6)));
 printf("{\"byte_length_cases\":%u,\"status_cases\":524288}\n",cases);return 0;
}
'''
for n in ['sp11-cdm.h','sp11-cdm21-command.h']:(O/n).write_bytes((Q/n if (Q/n).exists() else R/'src/upstream/isp-config'/n).read_bytes())
(O/'test.c').write_text(prefix+'\n'+defs+'\n'+body+'\n'+tail)
runs=[]
for cc in ['gcc','clang']:
 p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-I'+str(O),str(O/'test.c'),'-o',str(O/cc)],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr)
 p=subprocess.run([str(O/cc)],capture_output=True,text=True)
 if p.returncode:raise RuntimeError(p.stderr)
 runs.append({'compiler':cc,'result':json.loads(p.stdout)})
result={'status':'PASS_PINNED_PUBLIC_ACTUAL_FIFO_WRITER','reference_revision':reference['revision'],'all_reference_pins_checked':len(reference['files']),'runs':runs,'hardware':False}
(O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
