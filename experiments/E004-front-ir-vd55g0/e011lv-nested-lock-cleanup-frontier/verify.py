#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_NESTED_LOCK_CLEANUP_TO_CACHED_REGISTRY_RELOAD_FRONTIER' and s['case_count']==4
assert s['cleanup_call_RVA']=='0x5b9038' and s['cleanup_target_RVA']=='0x1b438' and s['cleanup_call_executed']
assert s['local_SP_relative']=='0x78' and s['nested_lock_object_RVA']=='0x1623598' and s['nested_lock_resource_RVA']=='0x16235a0'
assert s['vtable_RVA']=='0x1330a68' and s['vtable_slot_offset']=='0x10' and s['cleanup_method_RVA']=='0x1df90' and s['guard_check_executed'] and s['leave_critical_section_executed'] and s['cleanup_return_u32']==0
assert s['resume_RVA']=='0x5b903c' and not s['resume_executed'] and s['cached_registry_reload_RVA']=='0x5b9040' and not s['cached_registry_reload_executed']
assert s['product_scope']=='front_rear_rgb_parity' and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LW' and n['expected_closure']['caller_resume_RVA']=='0x5de844'
print(json.dumps({'status':'PASS_E011LV_PORTABLE_REVIEW','cases':4,'next':'E011LW'},sort_keys=True))
