#!/usr/bin/env python3
import json
from pathlib import Path
H=Path(__file__).resolve().parent
s=json.loads((H/'SOURCE-SAFE.json').read_text());n=json.loads((H/'NEXT-SOURCE.json').read_text())
assert s['status']=='PASS_VALUE_NODE_KEY_STORAGE_TO_VALUE_COPY_FRONTIER'
assert s['case_count']==4 and s['value_node_bytes']==24 and s['key_storage_bytes']==132
assert s['key_copy_bytes']==128 and s['key_storage_tail_zero_bytes']==4
assert s['stop_RVA']=='0x5e8578' and not s['stop_executed']
assert n['experiment']=='E011LM' and n['expected_closure']['resume_RVA']=='0x5b8d54'
print('{"cases": 4, "next": "E011LM", "status": "PASS_E011LL_PORTABLE_REVIEW"}')
