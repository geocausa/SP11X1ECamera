#!/usr/bin/env python3
from pathlib import Path
import hashlib,json
HERE=Path(__file__).resolve().parent
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(n): return json.loads((HERE/n).read_text())
def check():
    s=load('SOURCE-SAFE.json')
    w=load('WINDOWS-SAFE.json')
    r=load('RESULT.json')
    f=load('FRONTIER-SAFE.json')
    n=load('NEXT-SOURCE.json')
    assert s['experiment']=='E011EI' and s['camera_count_read_source_qualified']
    assert s['source_default_stream_count']==512 and s['first_scan_slot']==3 and s['last_scan_slot']==511
    assert s['scan_slot_count']==509 and s['vector_bytes']==4096 and s['scan_end_is_exact_vector_end']
    assert w['user_mode']['native_stream_count_prestart']==512
    assert w['user_mode']['native_stream_count_at_camera_read']==512
    assert w['user_mode']['pointer_then_count_same_thread_start_path']
    assert w['kernel_reference']['rear_isp_probe']['fifo_generation_events']==81
    assert w['kernel_reference']['rear_isp_probe']['matching_generation_events']==81
    assert w['kernel_reference']['rear_isp_probe']['generation_keys_monotonic']
    assert w['kernel_reference']['rear_isp_probe']['unique_rotating_wm16_addresses']==10
    assert not w['kernel_reference']['rear_isp_probe']['irq_retirement_qualified']
    assert w['user_mode']['rear_primary']['start_success'] and w['user_mode']['rear_primary']['stop_success']
    assert w['user_mode']['front_bounded_probe']['start_success'] and w['user_mode']['front_bounded_probe']['stop_success']
    assert not w['kernel_reference']['front_same_probe']['same_rear_fifo_match_path_observed']
    assert not w['native_rear_runtime_allowed']
    assert r['source_script_sha256']==sha(HERE/'source-private.py')
    assert r['source_safe_sha256']==sha(HERE/'SOURCE-SAFE.json')
    assert r['windows_safe_sha256']==sha(HERE/'WINDOWS-SAFE.json')
    assert f['camera_frontier']['source_RVA']=='0xcc6140' and f['camera_frontier']['slot_index']==3
    assert n['experiment']=='E011EJ' and not n['native_rear_runtime_allowed']
    return {'status':'PASS_E011EI_PORTABLE_REVIEW','source_count':512,'scan_slots':509,'rear_generation_matches':81,'next':'E011EJ'}
if __name__=='__main__':
    print(json.dumps(check(),sort_keys=True))
