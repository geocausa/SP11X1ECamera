#!/usr/bin/env python3
from pathlib import Path
import json
D=Path(__file__).resolve().parent
def need(v,m):
    if not v: raise AssertionError(m)
run=(D/'run-once.sh').read_text(); pre=(D/'runtime-preflight.sh').read_text(); entry=(D/'99zzzzzz_sp11_camera_e004en_natural_cap_release').read_text()
need('--post-g3-write-policy cap-release-one-shot --allow-one-native-write' in run,'one-shot policy')
need('g4-startup-fill-shadow' not in run,'startup fill policy forbidden')
need('3f3bf8d3ea40a5045896f8ab3053bad14f09cc8fe3c328738905b33a5cf33c71' in pre,'package pin')
need('sp11_camera_e004en_natural_cap_release=1' in pre and 'sp11_camera_e004en_natural_cap_release=1' in entry,'boot marker')
j=json.loads((D/'RESULT.json').read_text()); need(j['maximum_later_native_writes']==1 and not j['synthetic_control_delta'],'safety')
print('E004EN_PREP_VERIFY=PASS NATURAL_ONE_SHOT_ONLY=YES SYNTHETIC_DELTA=NO')
