#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
"""Compare generated own configuration with actual native mask-walk body."""
from pathlib import Path
import re,json,hashlib,subprocess,sys,resource
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
Q=Path(__file__).resolve().parent;R=Q.parents[3]
def function(t,name):
 m=re.search(r'static int\s+'+name+r'\s*\(',t);assert m
 a=t.index('{',m.start());d=1;b=a+1
 while d:d+=(t[b]=='{')-(t[b]=='}');b+=1
 return t[m.start():b]
def main():
 O=Path(sys.argv[1]);O.mkdir();audit=json.loads((Q/'baseline-audit.json').read_text())
 N=Path(audit['native_stage']);p=N/'native-front-cst.inc'
 assert hashlib.sha256(p.read_bytes()).hexdigest()==audit['native_source_pins'][p.name]
 data=p.read_text();body=function(data,'native_front_regmask_walk')
 rows=[]
 for line in (R/'src/native-rgb/front-ae/tuning/imx681-front-open-regs.txt').read_text().splitlines():
  line=line.split('#',1)[0].strip()
  if line:rows.append(tuple(int(v,0) for v in line.split(',')))
 nums=','.join('0x%xU'%v for row in rows for v in row)
 prefix=r'''
#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include "sp11-front-measured-config.h"
#define NATIVE_FRONT_REGMASK_MAX 32U
#define NATIVE_FRONT_REGMASK_AREA 0x7400U
#define min_t(t,a,b) ((t)(a)<(t)(b)?(t)(a):(t)(b))
static u32 get_unaligned_le32(const u8 *p) {return p[0]|(u32)p[1]<<8|(u32)p[2]<<16|(u32)p[3]<<24;}
static void put_unaligned_le32(u32 v,u8 *p) {sp11_cdm_put32(p,v);}
'''
 prefix+='static u32 native_front_reg_mask[96]={'+nums+'};\nstatic int native_front_reg_mask_count=90;\n'
 original=(Q/'sp11-front-measured-config.h').read_text()
 mutations={
 'admit_2640_domain':original.replace('domain->sensor_width != 3840 || domain->sensor_height != 2160 ||','domain->sensor_width != 3840 ||'),
 'export_private_partial_word':original.replace('0x4b6cU','0x4b68U',1),
 'export_activation':original.replace('0x4b6cU','0x4960U',1),
 'change_measured_word':original.replace('0x00000835U','0x00000834U',1),
 'write_before_validation':original.replace('\tif (!out || !domain)','\tif (out)\n\t\tout[0] = 0;\n\tif (!out || !domain)',1),
 }
 assert all(v!=original for v in mutations.values())
 (O/'sp11-cdm.h').write_bytes((R/'src/upstream/isp-config/sp11-cdm.h').read_bytes())
 runs=[]
 for cc in ['gcc','clang']:
  for label,h in [('actual',original),*mutations.items()]:
   (O/'sp11-front-measured-config.h').write_text(h)
   src=O/(cc+'-'+label+'.c');src.write_text(prefix+'\n'+body+'\n'+(Q/'test-native-main.c.in').read_text());exe=src.with_suffix('')
   p=subprocess.run([cc,'-std=gnu11','-O1','-g','-Wall','-Wextra','-Werror','-fsanitize=address,undefined','-fno-omit-frame-pointer','-I'+str(O),str(src),'-o',str(exe)],capture_output=True,text=True)
   if p.returncode:raise RuntimeError(cc+' '+label+' compile '+p.stderr)
   p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=15);(O/(cc+'-'+label+'.log')).write_text(p.stdout+p.stderr)
   if label=='actual':
    if p.returncode:raise RuntimeError(cc+' actual '+p.stderr)
    runs.append({'compiler':cc,'result':json.loads(p.stdout),'ASan_UBSan':True,'actual_native_body':True})
   elif not p.returncode:raise RuntimeError('unsafe compiled mutation survived '+label)
 (O/'sp11-front-measured-config.h').write_text(original)
 result={'status':'PASS_OWN_CONFIGURATION_MATCHES_ACTUAL_NATIVE_OVERRIDES','runs':runs,'compiled_mutations_rejected_each':list(mutations),
 'native_source_sha256':hashlib.sha256((N/'native-front-cst.inc').read_bytes()).hexdigest(),
 'header_sha256':hashlib.sha256(original.encode()).hexdigest(),'private_profile_read':False,'optical_measurement':False,'hardware':False}
 (O/'RESULT.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
if __name__=='__main__':main()
