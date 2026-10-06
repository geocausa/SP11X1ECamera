#!/usr/bin/env python3
from pathlib import Path
import json,hashlib
H=Path(__file__).resolve().parent;L=lambda x:json.loads((H/x).read_text());S=lambda x:hashlib.sha256((H/x).read_bytes()).hexdigest();s=L('SOURCE-SAFE.json');r=L('RESULT.json');n=L('NEXT-SOURCE.json')
assert s['status']=='PASS_COMPLETE_282_STANDARD_NUMERIC_METADATA_RECORDS_TO_VENDOR_COMPONENT_FRONTIER' and s['case_count']==4
assert s['standard_component_count_u32']==282 and s['record_array_RVA']=='0x17350e0' and s['record_stride_bytes']==168
assert len(s['numeric_record_signature_sha256'])==64 and s['aggregate_element_bytes_u32']==280576
assert s['name_decoration_calls_bypassed_u32']==281 and s['name_decoration_proven_non_numeric_by_E011MA']
assert s['dynamic_count_factory_calls_u32']==6 and s['dynamic_count_helper_RVA']=='0x5ba6b0' and s['dynamic_count_helper_calls_u32']==6 and s['guard_checks_u32']==6 and s['registry_helper_calls_u32']==0
assert s['vendor_component_entry_RVA']=='0x5deb08' and not s['vendor_component_entry_executed']
assert s['product_scope']=='front_rear_rgb_parity' and not s['native_rear_runtime_allowed']
for k,x in [('source_safe_sha256','SOURCE-SAFE.json'),('frontier_safe_sha256','FRONTIER-SAFE.json'),('next_source_sha256','NEXT-SOURCE.json')]:assert r[k]==S(x)
assert r['next_experiment']=='E011MD'
print(json.dumps({'status':'PASS_E011MC_PORTABLE_REVIEW','cases':4,'next':'E011MD'},sort_keys=True))
