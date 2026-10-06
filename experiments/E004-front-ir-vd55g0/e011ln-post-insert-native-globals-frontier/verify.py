#!/usr/bin/env python3
import json
from pathlib import Path
H=Path(__file__).resolve().parent;s=json.loads((H/'SOURCE-SAFE.json').read_text());n=json.loads((H/'NEXT-SOURCE.json').read_text())
assert s['status']=='PASS_POST_INSERT_NATIVE_GLOBALS_TO_LOOP_ADVANCE_FRONTIER' and s['case_count']==4
assert s['native_160a218_u64']==0 and not s['bit16_set'] and s['native_1608858_u32']==1 and s['fallback_nonzero_branch_taken']
assert s['branch_target_RVA']=='0x5b8dac' and not s['branch_target_executed']
assert n['experiment']=='E011LO' and n['expected_closure']['next_RVA']=='0x5b8bec'
print('{"cases": 4, "next": "E011LO", "status": "PASS_E011LN_PORTABLE_REVIEW"}')
