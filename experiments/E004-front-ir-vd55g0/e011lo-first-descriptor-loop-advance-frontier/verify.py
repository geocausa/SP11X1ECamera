#!/usr/bin/env python3
import json
from pathlib import Path
H=Path(__file__).resolve().parent;s=json.loads((H/'SOURCE-SAFE.json').read_text());n=json.loads((H/'NEXT-SOURCE.json').read_text())
assert s['status']=='PASS_FIRST_DESCRIPTOR_LOOP_ADVANCE_TO_SECOND_DESCRIPTOR_FRONTIER' and s['case_count']==4
assert s['first_descriptor_position_u32']==0 and s['first_descriptor_source_index_u32']==164 and s['first_descriptor_nested_count_u32']==1
assert s['nested_position_after_u32']==1 and not s['nested_loop_taken'] and s['outer_descriptor_position_after_u32']==1 and s['outer_loop_taken']
assert s['next_RVA']=='0x5b8bec' and not s['next_executed']
assert n['experiment']=='E011LP' and n['expected_closure']['nested_element_count_u32']==350 and n['expected_closure']['map_entry_count_u32']==350
print('{"cases": 4, "next": "E011LP", "status": "PASS_E011LO_PORTABLE_REVIEW"}')
