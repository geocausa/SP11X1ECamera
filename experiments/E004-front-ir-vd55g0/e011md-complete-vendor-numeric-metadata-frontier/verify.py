#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_COMPLETE_519_VENDOR_NUMERIC_METADATA_RECORDS_TO_THIRD_COMPONENT_FRONTIER' and s['case_count']==4
assert s['vendor_component_count_u32']==519 and s['first_vendor_record_index_u32']==282 and s['last_vendor_record_index_u32']==800
assert len(s['flattened_vendor_tags_sha256'])==64 and len(s['numeric_record_signature_sha256'])==64 and s['aggregate_element_bytes_u32']==6071452
assert s['name_decoration_calls_bypassed_u32']==519 and s['name_decoration_proven_non_numeric_by_E011MA'] and s['registry_helper_calls_u32']==3633
assert s['accepted_prefix_array_entries_u32']==231 and s['accepted_scalar_array_entries_u32']==519
assert s['third_component_entry_RVA']=='0x5ded74' and not s['third_component_entry_executed']
assert s['product_scope']=='front_rear_rgb_parity' and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011ME'
print(json.dumps({'status':'PASS_E011MD_PORTABLE_REVIEW','cases':4,'next':'E011ME'},sort_keys=True))
