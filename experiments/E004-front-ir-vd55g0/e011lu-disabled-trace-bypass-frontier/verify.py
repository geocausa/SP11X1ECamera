#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_DISABLED_TRACE_BYPASS_TO_CLEANUP_CALL_FRONTIER' and s['case_count']==4
assert s['trace_flag_RVA']=='0x17a1180' and s['trace_flag_u32']==0 and not s['trace_bit3_set']
assert s['diagnostic_logging_block_start_RVA']=='0x5b8fdc' and s['diagnostic_logging_block_end_RVA']=='0x5b9030' and not s['diagnostic_logging_block_executed'] and s['diagnostic_logging_non_blocking']
assert s['branch_target_RVA']=='0x5b9034' and s['cleanup_call_RVA']=='0x5b9038' and s['cleanup_target_RVA']=='0x1b438' and not s['cleanup_call_executed']
assert s['product_scope']=='front_rear_rgb_parity' and not s['optional_ai_effects_followed'] and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LV' and n['expected_closure']['resume_RVA']=='0x5b903c'
print(json.dumps({'status':'PASS_E011LU_PORTABLE_REVIEW','cases':4,'next':'E011LV'},sort_keys=True))
