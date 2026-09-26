#!/usr/bin/env python3
from pathlib import Path
import json,struct,hashlib

HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
A=json.load(open(HERE/'AUTHORITY-SAFE.json'))
META=json.load(open(REPO/'experiments/E004-front-ir-vd55g0/e006b-windows-rear-dmi-source-payloads/PARTIAL-RESULT.json'))
PRIVATE=REPO.parent/'private/e006b'
FILES={'startup0':'E006B-START0-SOURCE.bin','startup1':'E006B-START1-SOURCE.bin',
       'startup2':'E006B-START2-SOURCE.bin','startup3':'E006B-START3-SOURCE.bin',
       'steady_ac8':'E006B-STEADY-AC8-SOURCE.bin'}

def pack(bank):
 out=bytearray()
 for i in range(len(bank)//2-1):
  w=(bank[2*i]&0xfff)|((bank[2*i+1]&0xfff)<<12)|((bank[2*i+2]&0xfff)<<24)
  out+=struct.pack('<Q',w)
 i=len(bank)//2-1
 out+=struct.pack('<Q',(bank[2*i]&0xfff)|((bank[2*i+1]&0xfff)<<12))
 return bytes(out)

luma=pack(A['luma_coefficients']); chroma=pack(A['chroma_coefficients'])
want={(0xa008,1):luma,(0xa008,2):luma,(0xa208,1):chroma,(0xa208,2):chroma}
checks=[]
for cap in META['captured']['captures']:
 label=cap['label']
 if label not in FILES or not (PRIVATE/FILES[label]).exists(): continue
 blob=(PRIVATE/FILES[label]).read_bytes(); base=int(cap['captured_source_window_base'],16)
 for item in cap['payloads']:
  key=(int(item['dmi_register_offset'],16),item['selector'])
  if key not in want: continue
  n=item['payload_bytes']; rel=int(item['source_offset'],16)-base
  got=blob[rel:rel+n]
  checks.append({'capture':label,'dmi_register':hex(key[0]),'selector':key[1],
                 'bytes':n,'exact':got==want[key]})
assert len(checks)==16 and all(x['exact'] for x in checks)
out={'schema':'E007v-private-validation-safe-v1','status':'PASS',
     'payload_checks':len(checks),'payload_checks_exact':sum(x['exact'] for x in checks),
     'luma_payload_sha256':hashlib.sha256(luma).hexdigest(),
     'chroma_payload_sha256':hashlib.sha256(chroma).hexdigest(),
     'raw_payload_values_emitted':False,'checks':checks}
(HERE/'PRIVATE-VALIDATION-SAFE.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('E007V_PRIVATE_VALIDATION_PASS exact=16/16')
print('raw_payload_values_emitted=false')
