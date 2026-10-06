#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_COMPLETE_5B80A8_EPILOGUE_RETURN_TO_5DE844_FRONTIER' and s['case_count']==4
assert s['cached_pointer_RVA']=='0x1731880' and s['returned_registry_object_RVA']=='0x17a4230' and s['cached_registry_reload_executed']
assert s['cookie_check_RVA']=='0x11f0' and s['cookie_contract_exact'] and not s['cookie_value_exported'] and s['local_frame_restore_bytes']==544 and s['saved_registers_restored']
assert s['function_return_RVA']=='0x5b9068' and s['function_return_executed'] and s['caller_resume_RVA']=='0x5de844' and not s['caller_resume_executed']
assert s['returned_x0_RVA']=='0x17a4230' and s['product_scope']=='front_rear_rgb_parity' and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011LX' and n['expected_next']['second_registry_call_RVA']=='0x5de948'
print(json.dumps({'status':'PASS_E011LW_PORTABLE_REVIEW','cases':4,'next':'E011LX'},sort_keys=True))
