#!/usr/bin/env python3
from pathlib import Path
import hashlib, importlib.util, json, sys
D=Path(__file__).resolve().parent
REPO=D.parents[2]
META=REPO/'experiments/E004-front-ir-vd55g0/e006b-windows-rear-dmi-source-payloads/PARTIAL-RESULT.json'
PRIVATE=REPO.parent/'private/e006b'
FILES={'startup0':'E006B-START0-SOURCE.bin','startup1':'E006B-START1-SOURCE.bin','startup2':'E006B-START2-SOURCE.bin','startup3':'E006B-START3-SOURCE.bin','steady_ac8':'E006B-STEADY-AC8-SOURCE.bin'}
s=importlib.util.spec_from_file_location('e007u_pack',D/'bpcabf411.py')
m=importlib.util.module_from_spec(s);sys.modules['e007u_pack']=m
assert s.loader;s.loader.exec_module(m)
want=m.load_and_pack()
meta=json.load(open(META));checks=[]
for cap in meta['captured']['captures']:
    label=cap['label']
    if label not in FILES: continue
    fp=PRIVATE/FILES[label]
    if not fp.exists(): continue
    blob=fp.read_bytes();base=int(cap['captured_source_window_base'],16)
    for item in cap['payloads']:
        if item['dmi_register_offset']=='0x4908' and item['selector']==1:
            rel=int(item['source_offset'],16)-base
            got=blob[rel:rel+item['payload_bytes']]
            assert item['payload_bytes']==256 and got==want
            checks.append(label)
assert len(checks)==4
safe={'schema':'E007u-private-validation-safe-v1','status':'PASS','payload_checks':4,
      'captures':checks,'payload_bytes':256,'selector':1,
      'packed_payload_sha256':hashlib.sha256(want).hexdigest(),
      'raw_windows_values_emitted':False}
(D/'PRIVATE-VALIDATION-SAFE.json').write_text(json.dumps(safe,indent=2,sort_keys=True)+'\n')
print('E007U_PRIVATE_VALIDATION_PASS checks=4 selector=1')
