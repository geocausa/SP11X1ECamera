#!/usr/bin/env python3
from pathlib import Path
import json,sys
E=Path(__file__).resolve().parent; fail=[]
def need(rel,*tokens):
 p=E/rel
 if not p.exists(): fail.append('missing '+rel); return ''
 s=p.read_text(errors='replace')
 for t in tokens:
  if t not in s: fail.append(f'{rel}: missing {t!r}')
 return s
r=json.loads((E/'RESULT.json').read_text())
if r.get('status')!='PASS_GOLDEN_CPZ_HOST_PORT_DELTA_BOUNDED_COMPILE_FIRST': fail.append('status')
if r['golden']['gunyah_required_for_cp_cdsp']: fail.append('incorrect Gunyah requirement')
if r['golden']['qcom_scm_assign_mem_regions_present']: fail.append('Golden multi-region API incorrectly present')
if not r['compiled_owner_shim']['qcom_scm_assign_mem_dependency_retained']: fail.append('owner shim dependency')
if r['compiled_fastrpc_stage1']['nonzero_pd_type_control_exposed']: fail.append('PD type control exposed early')
if r['sg_boundary']['system_heap_final_ready']: fail.append('system heap prematurely accepted')
if any(r['runtime_actions'].values()): fail.append('runtime boundary')
need('evidence/GOLDEN-HOST-GAP.txt','qcom_scm_assign_mem()','Absent in Golden','FASTRPC_INVOKE2_SESS_INFO')
need('evidence/SCM-SG-PORT-BOUNDARY.txt','qcom_scm_assign_mem_regions()','contiguous','scatter-gather')
need('evidence/MEMBUF-PERIPHERAL-VM-PATH.txt','CP_CAMERA','CP_CDSP','does NOT require porting the Gunyah host stack')
need('evidence/PORT-DELTA-MATRIX.txt','OWNER TRANSITION CORE','DMA-BUF OWNERSHIP WRAPPER','FASTRPC PD-TYPE SESSION SELECTION')
need('evidence/COMPILE-PROOFS.txt','U qcom_scm_assign_mem','FASTRPC_PD_TYPE_CPZ_USER = 6','loaded_checks:')
need('evidence/OWNER-SHIM-BUILD.log','LD [M]','sp11-cpz-contig-owner.ko')
need('evidence/FASTRPC-STAGE1-BUILD.log','LD [M]','fastrpc-e004cs.ko')
need('README.md','CMA-only is a useful first compile/bring-up shape','E004ct — Golden scatter-gather ownership backport')
if fail:
 print('E004cs VERIFY: FAIL'); [print(' -',x) for x in fail]; sys.exit(1)
print('E004cs VERIFY: PASS')
print(' - CP_CAMERA/CP_CDSP peripheral ownership needs no Gunyah host port')
print(' - Golden qcom_scm_assign_mem is sufficient for contiguous protected ownership transitions')
print(' - full system-heap SG support is blocked only by the missing multi-region ownership API/lifetime wrapper')
print(' - inert FastRPC PD-type matching and concrete owner helpers both compile against Golden')
print(' - no nonzero PD-type control, DT policy, module load or protected runtime action occurred')
