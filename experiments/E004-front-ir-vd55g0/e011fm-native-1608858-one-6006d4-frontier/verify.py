#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
H=Path(__file__).resolve().parent
def sha(n): return hashlib.sha256((H/n).read_bytes()).hexdigest()
def L(n): return json.loads((H/n).read_text())
def check():
    s=L('SOURCE-SAFE.json'); r=L('RESULT.json'); w=L('WINDOWS-SAFE.json'); f=L('FRONTIER-SAFE.json'); n=L('NEXT-SOURCE.json')
    assert s['experiment']=='E011FM' and s['status']=='PASS_NATIVE_1608858_ONE_TO_6006D4_FRONTIER'
    assert s['case_count']==4 and s['rejected_altered_contracts']==1816
    assert s['x21_owner_RVA']=='0x1608000' and s['x21_owner_source_RVA']=='0x600410'
    assert s['native_1608858_value_u32']==1 and s['native_1608858_before_reader_start_u32']==1 and s['native_1608858_after_successful_reader_start_u32']==1
    assert s['native_dependency_value_qualified'] and s['file_static_1608858_u32']==1 and s['native_matches_file_static']
    assert s['field_nonzero_branch_taken'] and s['field_nonzero_branch_target_RVA']=='0x6006d4' and s['next_source_RVA']=='0x6006d4'
    assert w['dependency_RVA']=='0x1608858' and w['native_value_before_reader_start_u32']==1 and w['native_value_after_successful_reader_start_u32']==1
    assert w['reader_start_status']=='Success' and w['expected_cbnz_branch_taken'] and w['expected_branch_target_RVA']=='0x6006d4'
    for k,nm in [('source_script_sha256','source-private.py'),('source_safe_sha256','SOURCE-SAFE.json'),('windows_safe_sha256','WINDOWS-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json')]: assert r[k]==sha(nm)
    assert r['new_front_camera_starts']==1 and r['new_rear_camera_starts']==0 and r['new_reboots']==1
    assert r['returned_to_Golden_Linux'] and not r['native_rear_runtime_allowed'] and not r['second_iteration_executed']
    assert r['next_experiment']=='E011FN' and f['camera_frontier']['source_RVA']=='0x6006d4'
    assert n['experiment']=='E011FN' and n['current_camera_frontier']['source_RVA']=='0x6006d4' and not n['native_rear_runtime_allowed']
    return {'status':'PASS_E011FM_PORTABLE_REVIEW','cases':4,'rejects':1816,'next':'E011FN'}
if __name__=='__main__': print(json.dumps(check(),sort_keys=True))
