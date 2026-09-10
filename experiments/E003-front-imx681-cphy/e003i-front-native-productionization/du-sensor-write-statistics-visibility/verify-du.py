#!/usr/bin/env python3
from pathlib import Path
import json

HERE=Path(__file__).resolve().parent
BASE=HERE.parent
CY=BASE/'cy-bounded-imx681-latch-runtime/RESULT.json'
DT=BASE/'dt-bounded-native-aec-cap-awb-hold-sensor-loop/RESULT.json'

cy=json.loads(CY.read_text())
dt=json.loads(DT.read_text())
assert cy['status']=='PASS_LIVE_LATCH_BOUNDARY'
assert cy['runtime']['executed'] is True
assert cy['runtime']['same_boot_retry_performed'] is False
assert cy['runtime']['step_after_v4l2_sequence']==0
# V4L2 sequence 0 is paired stats generation G1.
write_after_generation=cy['runtime']['step_after_v4l2_sequence']+1
first=cy['measurement']['first_significant_drop_generation']
assert cy['measurement']['observed_boundary'].startswith('G2 baseline-like; G3 first strong')
assert first==3 and write_after_generation==1
visibility_offset=first-write_after_generation
assert visibility_offset==2
assert cy['cw_module_sha256']=='72a5d1fd09cfc472520f4ddcf2eccac7f8b42b04d146882feeda6ba8027923d1'

assert dt['status']=='PASS_LIVE_SIX_FRAME_GOLDEN_RETURNED_CANDIDATE_RETIRED'
assert dt['runtime']['generations']==6
assert dt['runtime']['sensor_writes']==3
assert dt['runtime']['streamoff']=='PASS'
assert dt['runtime']['golden_return']=='PASS'
assert dt['runtime']['same_boot_retry_performed'] is False

derived=[]
for s in dt['sensor_schedule']:
    expected=s['write_after_generation']+visibility_offset
    assert s['effect_generation']==expected
    derived.append({'source_generation':s['source_generation'],
                    'write_after_generation':s['write_after_generation'],
                    'first_affected_generation':expected})
assert [x['first_affected_generation'] for x in derived]==[4,5,6]

out={
 'schema':'sp11-e003i-du-sensor-write-statistics-visibility-v1',
 'status':'PASS',
 'runtime_performed':False,
 'authority':{
   'cx':'Windows packet F selected/applied synchronously at SOF F-1; optical label intentionally left open',
   'cy':'single controlled exposure step after completed G1; G2 baseline-like; G3 first significant BHist change',
   'dt':'same CW transaction family; sensor writes released after completed G2/G3/G4'
 },
 'visibility_offset_generations':visibility_offset,
 'law':'write after completed generation N -> first affected paired statistics generation N+2',
 'dt_mapping':derived,
 'scheduler_effect_labels_validated':True,
 'continuous_automatic_exposure_proven':False
}
(HERE/'RESULT.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
print('DU_CY_VISIBILITY_OFFSET=2')
print('DU_DT_EFFECT_MAPPING=G4,G5,G6')
print('DU_SCHEDULER_EFFECT_LABELS=PASS')
print('DU_RUNTIME=0')
print('DU_VERIFY=PASS')
