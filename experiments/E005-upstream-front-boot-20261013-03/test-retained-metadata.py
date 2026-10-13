#!/usr/bin/env python3
# SPDX-License-Identifier: GPL-2.0-only
from pathlib import Path
import subprocess,importlib.util,sys
sys.dont_write_bytecode=True
R=Path('/home/geoca/Documents/SP11-PROJECT/06-camera/SP11X1ECamera-upstream');Q=R/'experiments/E005-upstream-front-boot-20261013-03'
spec=importlib.util.spec_from_file_location('observer',Q/'run-once.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
old=subprocess.check_output(['sudo','-n','python3','-c',"from pathlib import Path;print(Path('/var/lib/sp11-camera-upstream-front-20261013-02/PRIVATE-MEDIA.txt').read_text())"],text=True)
blocks=old.split('\n- entity');new='\n- entity'.join(b.replace('subtype Unknown','subtype Sensor') if 'msm_tpg' in b.split('\n')[0] else b for b in blocks)
enabled='\n- entity'.join(b.replace('-> "msm_csid0":0 []','-> "msm_csid0":0 [ENABLED]') if 'msm_tpg0' in b.split('\n')[0] else b for b in new.split('\n- entity'))
assert m.check_entities(new)
for i,text in enumerate([old,new.replace('[ENABLED,IMMUTABLE]','[]'),new.replace('msm_csiphy2','msm_csiphy1'),enabled,new.replace('msm_tpg2 (1 pad','msm_tpg1 (1 pad')]):
 try:m.check_entities(text)
 except RuntimeError as e:print('negative',i,'rejected',str(e))
 else:raise RuntimeError('bad evidence admitted '+str(i))
print('classification guard controls PASS')
