#!/usr/bin/env python3
from pathlib import Path
import importlib.util,json,sys,tempfile,hashlib
HERE=Path(__file__).resolve().parent
EXPECTED_CAP={7:'681f17d83d289fba57548241bbb7db4219afbfde48495d680de969274720ea2e',8:'79804d678235f53429e4690c0d5e4a905873edde6652f002c878e2fad8634d2e',9:'1bd2e7cd98eb6ebc6c4161a34b3b8c72343d6e69232b11346f65496f79e33fda'}
EXPECTED_MOD={7:'3728c5188d4cb9c55f3d2c5e1bc57064d66f58f259f30e3bc6c1742af0bab583',8:'3e2435e756166a144cefde081540fe07b854fc234b1382265c881f47b4c2ba74',9:'3728c5188d4cb9c55f3d2c5e1bc57064d66f58f259f30e3bc6c1742af0bab583'}
EXPECTED_DEMUX={'0x3b70':'0x04270427','0x3b74':'0x04280427'}
EXPECTED_AWB={'0x3d78':'0x00001c80','0x3d7c':'0x00001efc','0x3d80':'0x000008fc','0x3d84':'0x00000843','0x456c':'0x0f7e0000','0x4570':'0x0e400000'}
EXPECTED_GTM='074564f99a45d29a5dbe800c18bc0436735f70740cb8f42cd9a5c7b636ffcdfa'

def load(p,n):
 s=importlib.util.spec_from_file_location(n,p);m=importlib.util.module_from_spec(s);sys.modules[n]=m;s.loader.exec_module(m);return m
def need(v,m):
 if not v:raise AssertionError(m)
M=load(HERE/'compose-em.py','em_verify_core')
with tempfile.TemporaryDirectory(prefix='verify-em-a-') as a, tempfile.TemporaryDirectory(prefix='verify-em-b-') as b:
 ra=Path(a)/'RESULT.json';rb=Path(b)/'RESULT.json';oa=M.run(Path(a)/'caps',ra);ob=M.run(Path(b)/'caps',rb)
 need(oa['status']=='PASS_OFFLINE_COMPONENT_COMPOSITION' and ob['status']==oa['status'],'status')
 need(oa['capsule_template_reads']==oa['raw_r7_r9_capsule_reads']==oa['raw_r7_r9_dmi_slot_reads']==0,'no R7-R9 template/raw reads')
 need(oa['whole_capsule_windows_r7_r9_byte_oracle'] is False,'whole-capsule claim must stay false')
 for r in (7,8,9):
  xa=next(x for x in oa['rows'] if x['request']==r);xb=next(x for x in ob['rows'] if x['request']==r)
  pa=Path(a)/'caps'/f'E003I_EM_R{r}.bin';pb=Path(b)/'caps'/f'E003I_EM_R{r}.bin'
  need(pa.read_bytes()==pb.read_bytes(),f'R{r} deterministic bytes')
  h=hashlib.sha256(pa.read_bytes()).hexdigest();need(h==EXPECTED_CAP[r]==xa['capsule_sha256']==xb['capsule_sha256'],f'R{r} capsule hash')
  need(xa['module_sha256']==EXPECTED_MOD[r],'module hash')
  need(xa['demux']==EXPECTED_DEMUX,'demux')
  need(xa['awb_dynamic_regs']==EXPECTED_AWB and xa['awb_triangle']==5,'AWB scalar/triangle')
  need(xa['gtm_sha256']==EXPECTED_GTM,'GTM')
  regular=(r+1)&1;inverse=r&1
  for k,v in xa['bank_regs'].items():
   reg=int(k,16); want=inverse if reg in (0x5a58,0x5a5c,0x5f58,0x5f5c) else regular
   need(v==want,f'R{r} bank {k}')
 # Cross-request structural law: R7/R9 modules same parity/scalars; R8 opposite bank module.
 r7=next(x for x in oa['rows'] if x['request']==7);r9=next(x for x in oa['rows'] if x['request']==9)
 need(r7['module_sha256']==r9['module_sha256'],'R7/R9 module parity')
print('EM_VERIFY=PASS')
print(json.dumps({'status':'PASS','capsules':EXPECTED_CAP,'modules':EXPECTED_MOD,'gtm':EXPECTED_GTM},indent=2))
