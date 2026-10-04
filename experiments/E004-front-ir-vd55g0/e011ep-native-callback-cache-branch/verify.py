#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def L(n): return json.loads((H/n).read_text())
def check():
 s=L('SOURCE-SAFE.json');r=L('RESULT.json');f=L('FRONTIER-SAFE.json');n=L('NEXT-SOURCE.json');w=L('WINDOWS-SAFE.json')
 assert s['status']=='PASS_NATIVE_QUALIFIED_CALLBACK_CACHE_BRANCH' and s['case_count']==4
 assert s['native_callback_cache_slot_read_qualified'] and s['native_callback_return_one_qualified'] and s['callback_result_one_branch_qualified']
 assert s['original_CFG_nop_executed'] and s['rejected_altered_contracts']==496
 assert not s['exact_CB9F68_native_instruction_breakpoint_observed'] and not s['broad_callback_table_state_qualified']
 assert w['native_prestart_fptable_slot_populated'] and w['native_prestart_fptable_target_matches_source_identified_callback']
 assert w['native_callback_implementation_process_local_comparison_qualified'] and w['native_FrameServer_comparison_equal'] and w['native_callback_return_u32']==1
 assert w['dynamic_reference']['front_start_stop_successes']==3 and w['dynamic_reference']['rear_starts']==0 and w['returned_to_Golden_Linux']
 assert r['source_script_sha256']==sha(H/'source-private.py') and r['source_safe_sha256']==sha(H/'SOURCE-SAFE.json') and r['windows_safe_sha256']==sha(H/'WINDOWS-SAFE.json')
 assert r['next_source_RVA']=='0xcfd4e4' and r['next_call_target_RVA']=='0xcb76b0' and r['next_experiment']=='E011EQ'
 assert f['camera_frontier']['source_RVA']=='0xcfd4e4' and f['camera_frontier']['selected_mode_argument_w3']==0
 assert n['experiment']=='E011EQ' and not n['native_rear_runtime_allowed']
 return {'status':'PASS_E011EP_PORTABLE_REVIEW','cases':4,'rejects':496,'next':'E011EQ'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
