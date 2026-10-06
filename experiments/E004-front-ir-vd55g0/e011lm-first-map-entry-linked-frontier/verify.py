#!/usr/bin/env python3
import json
from pathlib import Path
H=Path(__file__).resolve().parent;s=json.loads((H/'SOURCE-SAFE.json').read_text());n=json.loads((H/'NEXT-SOURCE.json').read_text())
assert s['status']=='PASS_FIRST_MAP_ENTRY_LINKED_TO_CALLER_RESUME_FRONTIER' and s['case_count']==4
assert s['value_copy_bytes']==4 and s['value_node_key_storage_published'] and s['bucket_head_is_value_node'] and s['bucket_tail_is_value_node']
assert s['bucket_node_count_u32']==1 and s['map_entry_count_u32']==1 and s['insert_helper_return_u32']==0 and s['resume_RVA']=='0x5b8d54' and not s['resume_executed']
assert n['experiment']=='E011LN' and n['runtime_dependencies']['primary_global_RVA']=='0x160a218'
print('{"cases": 4, "next": "E011LN", "status": "PASS_E011LM_PORTABLE_REVIEW"}')
