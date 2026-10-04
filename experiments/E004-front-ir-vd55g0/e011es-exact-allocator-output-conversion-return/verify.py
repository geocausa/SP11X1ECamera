#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(n):return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json');a=L('EXACT-API-OUTPUT-SAFE.json')
 assert s['status']=='PASS_EXACT_ALLOCATOR_OUTPUT_CONVERSION_RETURN' and s['case_count']==4 and s['rejected_altered_contracts']==736
 assert s['owned_HeapAlloc_contract_executed'] and s['original_CB16C0_allocator_executed'] and s['original_CB16C0_allocator_return_qualified']
 assert s['exact_original_API_output_return_qualified'] and s['complete_CB76B0_return_qualified'] and s['converted_UTF16_output_exact']
 assert s['next_source_RVA']=='0xcfd4e8' and s['next_parent_call_site_RVA']=='0xcfd514' and s['next_parent_call_target_RVA']=='0xcfd570'
 assert a['status']=='PASS_EXACT_38BYTE_ORIGINAL_API_OUTPUT' and a['output_bytes']==76 and a['output_characters']==38 and not a['original_size_or_conversion_result_stub']
 assert r['source_script_sha256']==sha(H/'source-private.py') and r['source_safe_sha256']==sha(H/'SOURCE-SAFE.json') and r['exact_API_output_safe_sha256']==sha(H/'EXACT-API-OUTPUT-SAFE.json')
 assert r['next_experiment']=='E011ET' and r['rejected_altered_contracts']==736
 assert f['qualified']['UTF16_allocation_bytes']==76 and f['qualified']['complete_CB76B0_return_qualified']
 assert n['experiment']=='E011ET' and n['current_camera_frontier']['source_RVA']=='0xcfd4e8' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011ES_PORTABLE_REVIEW','cases':4,'rejects':736,'next':'E011ET'}
if __name__=='__main__':print(json.dumps(check(),sort_keys=True))
