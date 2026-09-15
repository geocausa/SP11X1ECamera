#!/usr/bin/env python3
from pathlib import Path
import json
D=Path(__file__).resolve().parent; R=D.parents[2]
def need(v,m):
    if not v: raise AssertionError(m)
run=(D/'run-once.sh').read_text(); pre=(D/'runtime-preflight.sh').read_text(); arm=(D/'arm-once.sh').read_text(); entry=(D/'99zzzzzz_sp11_camera_e004el_g4_startup_fill_shadow').read_text()
need('--post-g3-write-policy g4-startup-fill-shadow --allow-one-native-write' in run,'guarded policy/authorization')
need('--post-g3-write-policy shadow' not in run,'plain shadow left behind')
need('cap-release-one-shot' not in run,'cap release policy forbidden')
need('3f3bf8d3ea40a5045896f8ab3053bad14f09cc8fe3c328738905b33a5cf33c71' in pre,'package pin')
need('sp11_camera_e004el_g4_startup_fill_shadow=1' in pre and 'sp11_camera_e004el_g4_startup_fill_shadow=1' in entry,'boot marker')
need('saved_entry=sp11-audio-fullio-v19c' in arm,'golden saved entry')
j=json.loads((D/'RESULT.json').read_text()); need(j['later_native_write_authorized'] is False and j['synthetic_control_delta'] is False,'result safety')
print('E004EL_PREP_VERIFY=PASS G4_STARTUP_FILL_ONLY=YES LATER_NATIVE_WRITE=NO')
