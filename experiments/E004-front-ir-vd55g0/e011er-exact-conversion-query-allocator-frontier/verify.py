#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(n): return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json');a=L('EXACT-API-SAFE.json')
 assert s['status']=='PASS_EXACT_CONVERSION_QUERY_TO_ALLOCATOR_FRONTIER' and s['case_count']==4 and s['rejected_altered_contracts']==612
 assert s['exact_original_API_query_return_qualified'] and s['exact_query_return_characters']==38 and s['derived_UTF16_allocation_bytes']==76
 assert s['owned_OS_query_contract_executed'] and not s['original_CB16C0_allocator_executed']
 assert s['next_source_RVA']=='0xcb77d8' and s['next_call_target_RVA']=='0xcb16c0' and s['next_allocation_bytes']==76
 assert a['status']=='PASS_EXACT_38BYTE_ORIGINAL_API_QUERY' and a['original_API_return_characters']==38 and a['UTF16_bytes']==76 and not a['original_size_or_conversion_result_stub']
 assert r['source_script_sha256']==sha(H/'source-private.py') and r['source_safe_sha256']==sha(H/'SOURCE-SAFE.json') and r['exact_API_safe_sha256']==sha(H/'EXACT-API-SAFE.json')
 assert r['next_experiment']=='E011ES' and r['rejected_altered_contracts']==612
 assert f['qualified']['source_input_bytes_including_NUL']==38 and f['qualified']['source_input_ascii'] and f['camera_frontier']['requested_allocation_bytes']==76
 assert n['experiment']=='E011ES' and n['current_camera_frontier']['requested_allocation_bytes']==76 and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011ER_PORTABLE_REVIEW','cases':4,'rejects':612,'next':'E011ES'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
